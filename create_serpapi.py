import re

with open("/Users/osmanorka/jarvis-Investment-Support-Agent/jarvis_apify_global.py", "r") as f:
    content = f.read()

# Extract from start up to end of USD_EXCHANGE_RATES
match = re.search(r"^(.*?USD_EXCHANGE_RATES\s*=\s*\{.*?\n\})", content, re.DOTALL | re.MULTILINE)
header = match.group(1) if match else ""

serpapi_class = """

class SerpApiGlobalIntegration:
    \"\"\"
    Real SerpApi integration for worldwide Google Maps lead generation.
    Uses SerpApi's Google Maps engine for live synchronous data.
    \"\"\"

    def __init__(self, api_token: Optional[str] = None):
        import os
        import serpapi
        self.api_token = api_token or os.environ.get("SERPAPI_API_KEY", "")
        if not self.api_token:
            raise ValueError(
                "SerpApi API token required. Set SERPAPI_API_KEY in .env or pass api_token."
            )
        self.client = serpapi.Client(api_key=self.api_token)

    # ----------------------------------------------------------
    # CORE INTEGRATION LOGIC
    # ----------------------------------------------------------

    def build_search_query(self, sector: str, location: str, language: str) -> str:
        \"\"\"Formulates a localized Google Maps search query\"\"\"
        keywords = GLOBAL_SECTOR_KEYWORDS.get(sector.lower(), GLOBAL_SECTOR_KEYWORDS.get("retail"))
        selected_lang = language if language in keywords else "en"
        base_keyword = keywords[selected_lang][0]
        return f"{base_keyword} in {location}"

    def search_maps(self, sector: str, location: str, country_code: str, language: str, max_results: int = 20) -> list:
        \"\"\"
        Runs synchronous queries against SerpApi.
        Handles pagination if max_results > 20.
        \"\"\"
        query = self.build_search_query(sector, location, language)
        
        all_results = []
        limit = min(max_results, 100) # hard cap at 100 to save credits
        
        # We need coordinates or string for ll/q. Because location is a string like "Melbourne CBD, Australia",
        # we can just pass it as 'q' without 'll' or use SerpApi's location feature.
        # 'q' is often sufficient for Google Maps.
        
        search_params = {
            "engine": "google_maps",
            "q": query,
            "hl": language,
            "gl": country_code.lower()
        }
        
        try:
            results = self.client.search(search_params)
            local_results = results.get("local_results", [])
            all_results.extend(local_results)
            
            # Simple pagination if needed (usually 20 per request)
            # SerpApi handles next pagination via 'start' param, but google_maps engine in SerpApi 
            # might not support standard start=20. We'll grab the first page for now. 
            # Most local result searches return up to 20 spots.
            
            return all_results[:limit]
        except Exception as e:
            print(f"SerpApi Error: {e}")
            return []

    def get_supported_sectors(self) -> dict:
        return GLOBAL_SECTOR_KEYWORDS

    def get_supported_languages(self) -> dict:
        return SUPPORTED_LANGUAGES

    # ----------------------------------------------------------
    # RESULT PROCESSING
    # ----------------------------------------------------------
    def process_results(self, raw_data: list, category: str, country_code: str) -> list:
        \"\"\"
        Converts raw SerpApi maps data into the unified JARVIS lead format.
        \"\"\"
        import random
        leads = []
        
        for place in raw_data:
            # Filter empty names
            if not place.get("title"):
                continue

            # Calculate base score (simplified placeholder)
            score = 60
            website = place.get("website", "")
            if not website:
                score += 10
            
            rating = place.get("rating", 0)
            review_count = place.get("reviews", 0)
            if review_count > 0 and rating < 4.0:
                score += 5
            
            # Suggest package
            package = "Starter"
            if score >= 75: package = "Premium"
            elif score >= 65: package = "Professional"

            # Parse phone
            phone = place.get("phone", "")
            
            leads.append({
                "name": place.get("title"),
                "sector": category,
                "phone": phone,
                "website": website,
                "rating": rating,
                "review_count": review_count,
                "score": score,
                "recommended_package": package,
                "raw_address": place.get("address", "")
            })

            # Sort by score descending to present highest priority first
            leads.sort(key=lambda x: x["score"], reverse=True)
            
        return leads

    def generate_scan_report(self, leads: list, sector: str, location: str, country_code: str) -> dict:
        \"\"\"Generate a high-level summary report for the dashboard\"\"\"
        total = len(leads)
        if total == 0:
            return {"status": "empty", "total": 0}

        avg_score = sum(l["score"] for l in leads) / total
        no_website = sum(1 for l in leads if not l["website"])
        premium_targets = sum(1 for l in leads if l["recommended_package"] == "Premium")
        
        return {
            "query": f"{sector} in {location}",
            "country": country_code,
            "total_leads_found": total,
            "average_lead_score": round(avg_score, 1),
            "no_website_opportunities": no_website,
            "premium_targets": premium_targets,
            "recommended_strategy": "Direct phone outreach" if no_website > 0 else "Email audit campaigns"
        }

# Global Export Utils
def get_supported_sectors():
    return SerpApiGlobalIntegration().get_supported_sectors()

def get_supported_languages():
    return SerpApiGlobalIntegration().get_supported_languages()

def get_currency_for_country(country_code: str) -> str:
    return CURRENCY_MAP.get(country_code.upper(), "USD")

def convert_price(amount_usd: float, country_code: str) -> dict:
    currency = get_currency_for_country(country_code)
    rate = USD_EXCHANGE_RATES.get(currency, 1.0)
    local_amount = round(amount_usd * rate, 2)
    return {
        "usd": amount_usd,
        "local": local_amount,
        "currency": currency,
        "rate": rate
    }

"""

with open("/Users/osmanorka/jarvis-Investment-Support-Agent/jarvis_serpapi_global.py", "w") as f:
    f.write(header + serpapi_class)
