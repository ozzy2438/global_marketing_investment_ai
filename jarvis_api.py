#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS AI Agency OS — FastAPI Backend
======================================
RESTful API endpoints for all JARVIS modules.

Başlatma:
    uvicorn jarvis_api:app --reload --port 8000

Docs:
    http://localhost:8000/docs (Swagger UI)
    http://localhost:8000/redoc (ReDoc)
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field
import io
import openai
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import json
import os

# Load .env FIRST — before any module reads env vars
from dotenv import load_dotenv
load_dotenv()

# JARVIS Core import
from jarvis_core import JARVIS

# Global Scan router import — 14 Apify-powered endpoints
import jarvis_scan_api
from jarvis_scan_api import router as scan_router

# ============================================
# APP INITIALIZATION
# ============================================
app = FastAPI(
    title="JARVIS AI Agency OS",
    description="AI Agency Operating System — Full API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS — Frontend bağlantısı için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wire the global scan router (/api/v1/scan/*)
app.include_router(scan_router)

# JARVIS instance
jarvis = JARVIS()
startup_result = jarvis.start()

# Inject DB into scan module so completed scans auto-save leads to SQLite
jarvis_scan_api.db_ref = jarvis.db


# ============================================
# PYDANTIC MODELS (Request/Response)
# ============================================

# --- Lead Models ---
class LeadInput(BaseModel):
    business_name: str = Field(..., example="İzmir Dentalizm")
    sector: str = Field(..., example="dental")
    city: str = Field(default="İstanbul", example="İzmir")
    district: str = Field(default="", example="Karşıyaka")
    contact_person: str = Field(default="", example="Dr. Mehmet")
    phone: str = Field(default="", example="+90 532 XXX XX XX")
    email: str = Field(default="", example="info@dentalizm.com")
    website: str = Field(default="", example="https://dentalizm.com")
    has_website: bool = Field(default=False)
    has_social_media: bool = Field(default=False)
    google_maps_listed: bool = Field(default=True)
    google_rating: float = Field(default=0, ge=0, le=5)
    review_count: int = Field(default=0, ge=0)
    employee_count: int = Field(default=0, ge=0)
    monthly_customers: int = Field(default=10, ge=0)
    multiple_locations: bool = Field(default=False)
    responded_before: bool = Field(default=False)
    visited_website: bool = Field(default=False)
    opened_email: bool = Field(default=False)
    social_active: bool = Field(default=False)

class LeadScoreResponse(BaseModel):
    total_score: int
    breakdown: Dict
    package_recommendation: str
    price_range: str
    priority: str

class FullAnalysisResponse(BaseModel):
    score: Dict
    roi: Dict
    pitch_scripts: Dict
    playbook: str
    strategies: List[str]

# --- Scan Models ---
class ScanInput(BaseModel):
    city: str = Field(..., example="İzmir")
    district: str = Field(..., example="Karşıyaka")
    sector: str = Field(..., example="dental")

# --- ROI Models ---
class ROIInput(BaseModel):
    sector: str = Field(..., example="dental")
    package: str = Field(..., example="Premium")
    current_monthly_customers: int = Field(default=10, ge=0)

# --- Contract Models ---
class ContractInput(BaseModel):
    business_name: str = Field(..., example="İzmir Dentalizm")
    contact_person: str = Field(default="", example="Dr. Mehmet")
    address: str = Field(default="", example="Karşıyaka, İzmir")
    sector: str = Field(..., example="dental")
    package: str = Field(..., example="Premium")
    monthly_fee: float = Field(..., example=19000)

# --- Revenue Models ---
class RevenueInput(BaseModel):
    target_mrr: float = Field(..., example=100000)
    current_mrr: float = Field(default=0, example=15000)
    avg_deal_size: float = Field(default=10000, example=10000)
    close_rate: float = Field(default=0.20, ge=0, le=1)

# --- Board Meeting Models ---
class CustomerHealth(BaseModel):
    name: str
    health_score: int = Field(ge=0, le=100)

class ActiveLead(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)

class BoardMeetingInput(BaseModel):
    mrr: float = Field(default=0)
    target_mrr: float = Field(default=100000)
    monthly_costs: float = Field(default=0)
    churn_rate: float = Field(default=0)
    pipeline_value: float = Field(default=0)
    active_leads: List[ActiveLead] = Field(default=[])
    customers: List[CustomerHealth] = Field(default=[])

# --- Pitch Models ---
class PitchInput(BaseModel):
    business_name: str = Field(..., example="İzmir Dentalizm")
    contact_person: str = Field(default="Yetkili")
    sector: str = Field(..., example="dental")
    score_data: Dict = Field(default={})

# --- Command Model ---
class CommandInput(BaseModel):
    command: str = Field(..., description="Kullanıcı doğal dil komutu")

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text for OpenAI TTS generation")


# ============================================
# API ENDPOINTS
# ============================================

# --- Health & Status ---
@app.get("/", tags=["System"])
async def root():
    return {
        "name": "JARVIS AI Agency OS",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "leads": "/api/leads/*",
            "scan": "/api/scan",
            "roi": "/api/roi",
            "contracts": "/api/contracts",
            "revenue": "/api/revenue",
            "board": "/api/board-meeting",
            "playbooks": "/api/playbooks",
            "command": "/api/command"
        }
    }

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": startup_result["modules"],
        "tables": startup_result["tables_created"]
    }


# --- Lead Scoring & Analysis ---
@app.post("/api/leads/score", response_model=LeadScoreResponse, tags=["Leads"])
async def score_lead(lead: LeadInput):
    """Lead puanlama — 0-100 skor + paket önerisi"""
    score = jarvis.scoring.calculate_score(lead.dict())
    return score

@app.post("/api/leads/analyze", tags=["Leads"])
async def analyze_lead(lead: LeadInput):
    """Full lead analizi — skor + ROI + pitch + playbook"""
    analysis = jarvis.analyze_lead(lead.dict())
    return analysis

@app.post("/api/leads/save", tags=["Leads"])
async def save_lead(lead: LeadInput):
    """Lead'i veritabanına kaydet"""
    score = jarvis.scoring.calculate_score(lead.dict())

    jarvis.db.execute(
        """INSERT INTO leads (business_name, sector, city, district, phone, email, 
           website, google_rating, review_count, has_website, has_social_media, 
           employee_count, score, package_recommendation, latitude, longitude, status, source)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0.0, 0.0, 'new', 'api')""",
        (lead.business_name, lead.sector, lead.city, lead.district, lead.phone,
         lead.email, lead.website, lead.google_rating, lead.review_count,
         int(lead.has_website), int(lead.has_social_media), lead.employee_count,
         score["total_score"], score["package_recommendation"])
    )

    return {"status": "saved", "score": score}

@app.get("/api/leads", tags=["Leads"])
async def list_leads(
    status: Optional[str] = Query(None, description="Filter by status"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    min_score: Optional[int] = Query(None, description="Minimum score"),
    limit: int = Query(50, ge=1, le=200)
):
    """Lead listesi — filtreleme destekli"""
    query = "SELECT * FROM leads WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)
    if sector:
        query += " AND sector = ?"
        params.append(sector)
    if min_score:
        query += " AND score >= ?"
        params.append(min_score)

    query += f" ORDER BY score DESC LIMIT {limit}"

    results = jarvis.db.fetch_all(query, params if params else None)
    return {"leads": [dict(r) for r in results], "count": len(results)}

@app.get("/api/leads/{lead_id}", tags=["Leads"])
async def get_lead(lead_id: int):
    """Tek lead detayı"""
    result = jarvis.db.fetch_one("SELECT * FROM leads WHERE id = ?", (lead_id,))
    if not result:
        raise HTTPException(status_code=404, detail="Lead bulunamadı")
    return dict(result)

@app.put("/api/leads/{lead_id}/status", tags=["Leads"])
async def update_lead_status(lead_id: int, status: str = Query(...)):
    """Lead durumunu güncelle"""
    valid = ["new", "contacted", "demo_scheduled", "proposal_sent", "negotiation", "won", "lost"]
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"Geçersiz durum. Geçerli: {valid}")

    jarvis.db.execute("UPDATE leads SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (status, lead_id))
    return {"status": "updated", "lead_id": lead_id, "new_status": status}


# --- Map Scanning ---
@app.post("/api/scan", tags=["Scanning"])
async def scan_area(scan: ScanInput):
    """Bölge taraması — Apify input oluştur"""
    result = jarvis.scan_area(scan.city, scan.district, scan.sector)
    return result

@app.post("/api/scan/report", tags=["Scanning"])
async def scan_report(scan: ScanInput, results: List[Dict] = []):
    """Tarama raporu oluştur"""
    report = jarvis.apify.generate_scan_report(scan.city, scan.district, scan.sector, results)
    return report


# --- ROI Calculator ---
@app.post("/api/roi", tags=["ROI"])
async def calculate_roi(roi_input: ROIInput):
    """ROI hesaplama — sektör + paket bazlı"""
    result = jarvis.roi.calculate(roi_input.sector, roi_input.package, roi_input.current_monthly_customers)
    return result

@app.get("/api/roi/compare/{sector}", tags=["ROI"])
async def compare_packages(sector: str, customers: int = Query(default=10)):
    """Tüm paketleri karşılaştır"""
    comparison = {}
    for pkg in ["Starter", "Professional", "Premium"]:
        comparison[pkg] = jarvis.roi.calculate(sector, pkg, customers)
    return {"sector": sector, "comparison": comparison}


# --- Playbooks ---
@app.get("/api/playbooks", tags=["Playbooks"])
async def list_playbooks():
    """Tüm sektör playbook'ları"""
    sectors = jarvis.playbooks.get_all_sectors()
    playbooks = {}
    for s in sectors:
        pb = jarvis.playbooks.get_playbook(s)
        playbooks[s] = {
            "name": pb["name"],
            "duration_months": pb["duration_months"],
            "target_roi": pb["target_roi"],
            "strategy_count": len(pb["strategies"])
        }
    return {"playbooks": playbooks}

@app.get("/api/playbooks/{sector}", tags=["Playbooks"])
async def get_playbook(sector: str):
    """Sektör playbook detayı"""
    pb = jarvis.playbooks.get_playbook(sector)
    if not pb:
        raise HTTPException(status_code=404, detail="Sektör bulunamadı")
    return pb

@app.get("/api/playbooks/{sector}/strategies", tags=["Playbooks"])
async def get_strategies(sector: str):
    """Sektör stratejileri"""
    strategies = jarvis.playbooks.get_strategies(sector)
    if not strategies:
        raise HTTPException(status_code=404, detail="Sektör bulunamadı")
    return {"sector": sector, "strategies": strategies}


# --- Pitch Scripts ---
@app.post("/api/pitch", tags=["Pitch"])
async def generate_pitch(pitch_input: PitchInput):
    """Pitch script üret — 4 tür"""
    lead_data = {
        "business_name": pitch_input.business_name,
        "contact_person": pitch_input.contact_person
    }
    score_data = pitch_input.score_data or {
        "total_score": 70,
        "package_recommendation": "Professional",
        "price_range": "8.000-15.000 TL/ay"
    }
    scripts = jarvis.pitch.generate(lead_data, pitch_input.sector, score_data)
    return {"scripts": scripts}

@app.post("/api/pitch/save", tags=["Pitch"])
async def save_pitch(lead_id: int, script_type: str, content: str, sector: str):
    """Pitch scripti kaydet"""
    jarvis.db.execute(
        "INSERT INTO pitch_scripts (lead_id, script_type, content, sector) VALUES (?, ?, ?, ?)",
        (lead_id, script_type, content, sector)
    )
    return {"status": "saved"}


# --- Contracts ---
@app.post("/api/contracts/generate", tags=["Contracts"])
async def generate_contract(contract_input: ContractInput):
    """Sözleşme oluştur"""
    client_data = {
        "business_name": contract_input.business_name,
        "contact_person": contract_input.contact_person,
        "address": contract_input.address
    }
    contract = jarvis.generate_contract(
        client_data, contract_input.sector,
        contract_input.package, contract_input.monthly_fee
    )
    return {"contract": contract}

@app.post("/api/contracts/save", tags=["Contracts"])
async def save_contract(contract_input: ContractInput):
    """Sözleşmeyi kaydet"""
    client_data = {
        "business_name": contract_input.business_name,
        "contact_person": contract_input.contact_person,
        "address": contract_input.address
    }
    contract_text = jarvis.generate_contract(
        client_data, contract_input.sector,
        contract_input.package, contract_input.monthly_fee
    )

    pkg_details = jarvis.contracts.PACKAGE_DETAILS.get(contract_input.package, {})
    duration = pkg_details.get("duration", 6)
    total = contract_input.monthly_fee * duration

    jarvis.db.execute(
        """INSERT INTO contracts (contract_text, package, monthly_fee, total_value, duration_months, status)
           VALUES (?, ?, ?, ?, ?, 'draft')""",
        (contract_text, contract_input.package, contract_input.monthly_fee, total, duration)
    )
    return {"status": "saved", "contract": contract_text}


# --- Revenue Roadmap ---
@app.post("/api/revenue/plan", tags=["Revenue"])
async def revenue_plan(revenue_input: RevenueInput):
    """Gelir yol haritası oluştur"""
    plan = jarvis.roadmap.generate(
        revenue_input.target_mrr, revenue_input.current_mrr,
        revenue_input.avg_deal_size, revenue_input.close_rate
    )
    return plan

@app.post("/api/revenue/save", tags=["Revenue"])
async def save_revenue_plan(revenue_input: RevenueInput):
    """Gelir planını kaydet"""
    plan = jarvis.roadmap.generate(
        revenue_input.target_mrr, revenue_input.current_mrr,
        revenue_input.avg_deal_size, revenue_input.close_rate
    )

    jarvis.db.execute(
        """INSERT INTO revenue_roadmap (target_mrr, current_mrr, plan_data, month, year)
           VALUES (?, ?, ?, ?, ?)""",
        (revenue_input.target_mrr, revenue_input.current_mrr,
         json.dumps(plan, ensure_ascii=False),
         datetime.now().month, datetime.now().year)
    )
    return {"status": "saved", "plan": plan}


# --- Board Meeting ---
@app.post("/api/board-meeting", tags=["Board Meeting"])
async def board_meeting(meeting_input: BoardMeetingInput):
    """Haftalık yönetim kurulu raporu"""
    agency_data = {
        "mrr": meeting_input.mrr,
        "target_mrr": meeting_input.target_mrr,
        "monthly_costs": meeting_input.costs if hasattr(meeting_input, 'costs') else meeting_input.monthly_costs,
        "churn_rate": meeting_input.churn_rate,
        "pipeline_value": meeting_input.pipeline_value,
        "active_leads": [l.dict() for l in meeting_input.active_leads],
        "customers": [c.dict() for c in meeting_input.customers]
    }
    report = jarvis.weekly_board_meeting(agency_data)

    # Kaydet
    jarvis.db.execute(
        """INSERT INTO board_meetings (meeting_date, health_score, report_data, recommendations, tasks_assigned)
           VALUES (?, ?, ?, ?, ?)""",
        (datetime.now().date().isoformat(), report["health_score"],
         json.dumps(report, ensure_ascii=False),
         json.dumps(report["recommendations"], ensure_ascii=False),
         json.dumps(report["weekly_tasks"], ensure_ascii=False))
    )

    return report

@app.get("/api/board-meeting/history", tags=["Board Meeting"])
async def board_meeting_history(limit: int = Query(default=10)):
    """Geçmiş toplantı raporları"""
    results = jarvis.db.fetch_all(
        "SELECT * FROM board_meetings ORDER BY created_at DESC LIMIT ?", (limit,)
    )
    return {"meetings": [dict(r) for r in results]}


# --- Natural Language Command ---
@app.post("/api/command", tags=["JARVIS AI"])
async def process_command(cmd: CommandInput):
    """Doğal dil komut işleme"""
    response = jarvis.process_command(cmd.command)
    return {"command": cmd.command, "response": response}

@app.post("/api/tts", tags=["JARVIS AI"])
async def generate_speech(tts: TTSRequest):
    """OpenAI TTS (Text to Speech) dönüşümü"""
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    if not client.api_key or client.api_key == "sk-proj-placeholder":
        raise HTTPException(status_code=400, detail="OpenAI API Key is missing or default")
        
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=tts.text
        )
        return StreamingResponse(io.BytesIO(response.content), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Dashboard Stats ---
@app.get("/api/dashboard/stats", tags=["Dashboard"])
async def dashboard_stats():
    """Dashboard istatistikleri"""
    total_leads = jarvis.db.fetch_one("SELECT COUNT(*) as c FROM leads")
    hot_leads = jarvis.db.fetch_one("SELECT COUNT(*) as c FROM leads WHERE score >= 75")
    customers = jarvis.db.fetch_one("SELECT COUNT(*) as c FROM customers WHERE status = 'active'")
    contracts = jarvis.db.fetch_one("SELECT COUNT(*) as c FROM contracts")

    return {
        "total_leads": total_leads["c"] if total_leads else 0,
        "hot_leads": hot_leads["c"] if hot_leads else 0,
        "active_customers": customers["c"] if customers else 0,
        "total_contracts": contracts["c"] if contracts else 0,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/dashboard/pipeline", tags=["Dashboard"])
async def dashboard_pipeline():
    """Satış pipeline durumu"""
    statuses = ["new", "contacted", "demo_scheduled", "proposal_sent", "negotiation", "won", "lost"]
    pipeline = {}
    for s in statuses:
        result = jarvis.db.fetch_one("SELECT COUNT(*) as c FROM leads WHERE status = ?", (s,))
        pipeline[s] = result["c"] if result else 0
    return {"pipeline": pipeline}


# --- Customers ---
@app.get("/api/customers", tags=["Customers"])
async def list_customers(status: Optional[str] = None):
    """Müşteri listesi"""
    query = "SELECT * FROM customers"
    params = []
    if status:
        query += " WHERE status = ?"
        params.append(status)
    query += " ORDER BY created_at DESC"

    results = jarvis.db.fetch_all(query, params if params else None)
    return {"customers": [dict(r) for r in results]}

@app.post("/api/customers/convert/{lead_id}", tags=["Customers"])
async def convert_lead(lead_id: int, package: str = Query(...), monthly_fee: float = Query(...)):
    """Lead'i müşteriye dönüştür"""
    lead = jarvis.db.fetch_one("SELECT * FROM leads WHERE id = ?", (lead_id,))
    if not lead:
        raise HTTPException(status_code=404, detail="Lead bulunamadı")

    jarvis.db.execute(
        """INSERT INTO customers (lead_id, business_name, package, monthly_fee, 
           contract_start, status) VALUES (?, ?, ?, ?, ?, 'active')""",
        (lead_id, lead["business_name"], package, monthly_fee, datetime.now().date().isoformat())
    )

    jarvis.db.execute("UPDATE leads SET status = 'won' WHERE id = ?", (lead_id,))

    return {"status": "converted", "lead_id": lead_id, "package": package}


# --- Settings ---
@app.get("/api/settings", tags=["Settings"])
async def get_settings():
    """Tüm ayarlar"""
    results = jarvis.db.fetch_all("SELECT * FROM settings")
    return {r["key"]: r["value"] for r in results}

@app.put("/api/settings/{key}", tags=["Settings"])
async def update_setting(key: str, value: str = Query(...)):
    """Ayar güncelle"""
    jarvis.db.execute(
        """INSERT INTO settings (key, value, updated_at) 
           VALUES (?, ?, CURRENT_TIMESTAMP) 
           ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP""",
        (key, value)
    )
    return {"status": "updated", "key": key, "value": value}


# ============================================
# STARTUP EVENT
# ============================================
@app.on_event("startup")
async def startup():
    print("🤖 JARVIS API Server başlatılıyor...")
    print(f"📦 {startup_result['tables_created']} tablo hazır")
    print(f"🔧 {len(startup_result['modules'])} modül aktif")
    print("🌐 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
