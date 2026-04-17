"""
JARVIS — Global Scan API Endpoints
Add these to jarvis_api.py for real Apify-powered scanning
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from jarvis_serpapi_global import (
    SerpApiGlobalIntegration,
    get_supported_sectors,
    get_supported_languages,
    get_currency_for_country,
    convert_price,
    GLOBAL_SECTOR_KEYWORDS,
    CURRENCY_MAP,
    USD_PACKAGE_PRICING,
)
import uuid

router = APIRouter(prefix="/api/v1/scan", tags=["Global Scanning"])

# In-memory store for active/completed scans
active_scans = {}
scan_results = {}

# DB reference — injected by jarvis_api.py at startup so leads get persisted
db_ref = None  # Set via: jarvis_scan_api.db_ref = jarvis.db


# ============================================================
# REQUEST / RESPONSE MODELS
# ============================================================

class ScanRequest(BaseModel):
    sector: str = Field(..., description="Business sector to scan", examples=["dental", "restaurant"])
    location: str = Field(..., description="City, neighborhood, or region", examples=["Manhattan, New York", "Shibuya, Tokyo"])
    country_code: str = Field("US", description="ISO 2-letter country code", examples=["US", "GB", "DE", "JP", "TR"])
    language: str = Field("en", description="Search language code", examples=["en", "de", "ja"])
    max_results: int = Field(20, ge=1, le=500, description="Max results per search query")
    wait_for_completion: bool = Field(False, description="Wait for scan to finish (blocking)")


class MultiScanRequest(BaseModel):
    sector: str
    locations: list[str] = Field(..., min_length=1, max_length=20)
    country_code: str = "US"
    language: str = "en"
    max_per_location: int = Field(50, ge=10, le=200)


class EnrichRequest(BaseModel):
    scan_id: str
    lead_id: str


class PriceConvertRequest(BaseModel):
    amount_usd: float
    country_code: str


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/sectors")
async def list_sectors():
    """List all supported business sectors with available languages."""
    sectors = {}
    for sector, lang_map in GLOBAL_SECTOR_KEYWORDS.items():
        sectors[sector] = {
            "languages": list(lang_map.keys()),
            "sample_keywords": {lang: kws[:2] for lang, kws in lang_map.items()},
        }
    return {"sectors": sectors, "total": len(sectors)}


@router.get("/languages")
async def list_languages():
    """List all supported search languages."""
    return {"languages": get_supported_languages(), "total": len(get_supported_languages())}


@router.get("/currencies")
async def list_currencies():
    """List all supported currencies with country mappings."""
    return {"currencies": CURRENCY_MAP, "total": len(CURRENCY_MAP)}


@router.post("/convert-price")
async def convert_price_endpoint(req: PriceConvertRequest):
    """Convert USD price to local currency."""
    return convert_price(req.amount_usd, req.country_code)


@router.get("/packages")
async def list_packages(country_code: str = "US"):
    """List package pricing in local currency."""
    currency = get_currency_for_country(country_code)
    packages = {}
    for pkg, usd_prices in USD_PACKAGE_PRICING.items():
        local = convert_price(usd_prices["monthly"], country_code)
        setup = convert_price(usd_prices["setup"], country_code)
        packages[pkg] = {
            "monthly_usd": usd_prices["monthly"],
            "monthly_local": local["local"],
            "setup_usd": usd_prices["setup"],
            "setup_local": setup["local"],
            "currency": currency,
        }
    return {"packages": packages, "currency": currency, "country_code": country_code}


@router.post("/start")
async def start_scan(req: ScanRequest, background_tasks: BackgroundTasks):
    """
    Start a Google Maps scan for businesses in any location worldwide.
    Returns immediately with a scan_id to poll for results.
    """
    try:
        serp = SerpApiGlobalIntegration()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    scan_id = str(uuid.uuid4())[:12]

    if req.wait_for_completion:
        # Blocking mode — wait and return results
        raw = serp.search_maps(req.sector, req.location, req.country_code, req.language, req.max_results)
        leads = serp.process_results(raw, req.sector, req.country_code)
        report = serp.generate_scan_report(leads, req.sector, req.location, req.country_code)
        result = {
            "status": "COMPLETED",
            "scan_id": scan_id,
            "total_raw": len(raw),
            "total_leads": len(leads),
            "leads": leads,
            "report": report,
        }
        scan_results[scan_id] = result
        return result
    else:
        # Async mode — return scan_id and run in background
        active_scans[scan_id] = {
            "request": req.dict(),
            "status": "RUNNING",
        }

        # Background processing — pass location to save to DB correctly
        background_tasks.add_task(
            _run_serpapi_scan, serp, scan_id,
            req.sector, req.location, req.country_code, req.language, req.max_results
        )

        return {
            "scan_id": scan_id,
            "status": "STARTED",
            "message": f"Scanning {req.sector} in {req.location} ({req.country_code})",
            "poll_url": f"/api/v1/scan/status/{scan_id}",
            "results_url": f"/api/v1/scan/results/{scan_id}",
        }


async def _run_serpapi_scan(serp, scan_id, sector, location, country_code, language, max_results):
    """Background task: fetch SerpApi results, SAVE to database."""
    try:
        raw   = serp.search_maps(sector, location, country_code, language, max_results)
        leads = serp.process_results(raw, sector, country_code)
        report = serp.generate_scan_report(leads, sector, location, country_code)

        # ── SAVE TO DATABASE ─────────────────────────────────────
        saved = 0
        if db_ref is not None:
            for lead in leads:
                try:
                    db_ref.execute(
                        """INSERT INTO leads
                           (business_name, sector, city, district, phone, email,
                            website, google_rating, review_count, has_website,
                            has_social_media, employee_count, score,
                            package_recommendation, latitude, longitude, status, source)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', 'serpapi_scan')""",
                        (
                            lead.get("name", ""),
                            sector,
                            location,               # city
                            "",                     # district
                            lead.get("phone", ""),
                            "",                     # email
                            lead.get("website", ""),
                            lead.get("rating", 0),
                            lead.get("review_count", 0),
                            1 if lead.get("website") else 0,
                            0,                      # has_social_media
                            0,                      # employee_count
                            lead.get("score", 0),
                            lead.get("recommended_package", "Starter"),
                            lead.get("latitude", 0.0),
                            lead.get("longitude", 0.0),
                        )
                    )
                    saved += 1
                except Exception:
                    pass

        scan_results[scan_id] = {
            "status":      "COMPLETED",
            "total_raw":   len(raw),
            "total_leads": len(leads),
            "saved_to_db": saved,
            "leads":       leads,
            "report":      report,
        }
        active_scans[scan_id]["status"] = "COMPLETED"
    except Exception as e:
        scan_results[scan_id] = {"status": "FAILED", "error": str(e)}
        active_scans[scan_id]["status"] = "FAILED"


@router.get("/status/{scan_id}")
async def check_status(scan_id: str):
    """Check the status of a running scan."""
    if scan_id in scan_results:
        return {"scan_id": scan_id, "status": scan_results[scan_id].get("status", "COMPLETED")}
    if scan_id in active_scans:
        return {"scan_id": scan_id, "status": active_scans[scan_id]["status"]}

    # Status inherently tracked by the background task
    raise HTTPException(status_code=404, detail="Scan not found")


@router.get("/results/{scan_id}")
async def get_results(scan_id: str, min_score: int = 0, package: Optional[str] = None, limit: int = 50):
    """Get processed results from a completed scan with optional filters."""
    if scan_id not in scan_results:
        raise HTTPException(status_code=404, detail="Results not ready or scan not found")

    data = scan_results[scan_id]
    if data.get("status") != "COMPLETED":
        return data

    leads = data.get("leads", [])

    # Apply filters
    if min_score > 0:
        leads = [l for l in leads if l["score"] >= min_score]
    if package:
        leads = [l for l in leads if l["recommended_package"].lower() == package.lower()]

    return {
        "scan_id": scan_id,
        "total": len(leads),
        "leads": leads[:limit],
        "report": data.get("report"),
    }


@router.post("/multi")
async def start_multi_scan(req: MultiScanRequest, background_tasks: BackgroundTasks):
    """Scan multiple locations at once (e.g., all neighborhoods in a city)."""
    try:
        apify = ApifyGlobalIntegration()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    result = apify.multi_location_scan(
        sector=req.sector,
        locations=req.locations,
        country_code=req.country_code,
        language=req.language,
        max_per_location=req.max_per_location,
    )

    # Track all scans
    for scan_info in result["scans"]:
        sid = scan_info["scan"]["run_id"]
        did = scan_info["scan"]["dataset_id"]
        active_scans[sid] = {"scan": scan_info, "status": "RUNNING"}
        background_tasks.add_task(
            _poll_and_process, apify, sid, did, req.sector, req.country_code
        )

    return result


@router.post("/enrich")
async def enrich_lead(req: EnrichRequest, background_tasks: BackgroundTasks):
    """Run deep enrichment on a specific lead (website crawl, reviews, social)."""
    if req.scan_id not in scan_results:
        raise HTTPException(status_code=404, detail="Scan not found")

    leads = scan_results[req.scan_id].get("leads", [])
    lead = next((l for l in leads if l["id"] == req.lead_id), None)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    try:
        apify = ApifyGlobalIntegration()
        enrichment = apify.run_enrichment(lead)
        return enrichment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{scan_id}")
async def get_report(scan_id: str):
    """Get the AI-generated scan report with recommendations."""
    if scan_id not in scan_results:
        raise HTTPException(status_code=404, detail="Scan not found")

    data = scan_results[scan_id]
    return data.get("report", {"error": "Report not available"})


# ============================================================
# USAGE EXAMPLES (for docs)
# ============================================================

USAGE_EXAMPLES = {
    "scan_new_york_dental": {
        "sector": "dental",
        "location": "Manhattan, New York",
        "country_code": "US",
        "language": "en",
        "max_results": 100,
    },
    "scan_tokyo_restaurant": {
        "sector": "restaurant",
        "location": "Shibuya, Tokyo",
        "country_code": "JP",
        "language": "ja",
        "max_results": 50,
    },
    "scan_london_law": {
        "sector": "law_firm",
        "location": "City of London",
        "country_code": "GB",
        "language": "en",
        "max_results": 80,
    },
    "scan_dubai_real_estate": {
        "sector": "real_estate",
        "location": "Dubai Marina",
        "country_code": "AE",
        "language": "ar",
        "max_results": 60,
    },
    "scan_berlin_gym": {
        "sector": "gym",
        "location": "Berlin Mitte",
        "country_code": "DE",
        "language": "de",
        "max_results": 50,
    },
    "scan_sao_paulo_beauty": {
        "sector": "beauty_salon",
        "location": "São Paulo, Jardins",
        "country_code": "BR",
        "language": "pt",
        "max_results": 70,
    },
    "multi_scan_istanbul": {
        "sector": "dental",
        "locations": [
            "Kadıköy, Istanbul",
            "Beşiktaş, Istanbul",
            "Şişli, Istanbul",
            "Üsküdar, Istanbul",
        ],
        "country_code": "TR",
        "language": "tr",
        "max_per_location": 30,
    },
}


@router.get("/examples")
async def get_examples():
    """Get example scan configurations for different countries."""
    return {"examples": USAGE_EXAMPLES}
