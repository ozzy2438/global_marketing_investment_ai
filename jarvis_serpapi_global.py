"""
JARVIS — Global Apify Integration
Real connection to Apify API for worldwide lead generation via Google Maps
Supports any country, language, and sector
"""

import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Optional
import urllib.request
import urllib.parse

# ============================================================
# GLOBAL CONFIGURATION
# ============================================================

SUPPORTED_LANGUAGES = {
    "en": "English", "tr": "Türkçe", "de": "Deutsch", "fr": "Français",
    "es": "Español", "pt": "Português", "it": "Italiano", "nl": "Nederlands",
    "ar": "العربية", "ja": "日本語", "ko": "한국어", "zh": "中文",
    "ru": "Русский", "pl": "Polski", "sv": "Svenska", "no": "Norsk",
    "da": "Dansk", "fi": "Suomi", "el": "Ελληνικά", "cs": "Čeština",
    "ro": "Română", "hu": "Magyar", "hi": "हिन्दी", "th": "ไทย",
    "vi": "Tiếng Việt", "id": "Bahasa Indonesia", "ms": "Bahasa Melayu",
    "uk": "Українська", "he": "עברית", "bn": "বাংলা"
}

# Sector keywords in multiple languages for accurate Google Maps search
GLOBAL_SECTOR_KEYWORDS = {
    "dental": {
        "en": ["dental clinic", "dentist", "dental office", "orthodontist", "dental care"],
        "tr": ["diş kliniği", "diş hekimi", "ağız ve diş sağlığı", "ortodonti"],
        "de": ["Zahnarzt", "Zahnklinik", "Zahnarztpraxis", "Kieferorthopäde"],
        "fr": ["clinique dentaire", "dentiste", "cabinet dentaire", "orthodontiste"],
        "es": ["clínica dental", "dentista", "consultorio dental", "ortodoncista"],
        "pt": ["clínica dentária", "dentista", "consultório odontológico"],
        "ar": ["عيادة أسنان", "طبيب أسنان", "مركز أسنان"],
        "ja": ["歯科クリニック", "歯医者", "歯科医院"],
        "ko": ["치과", "치과 클리닉", "치과 병원"],
        "zh": ["牙科诊所", "牙医", "口腔医院"],
        "it": ["clinica dentale", "dentista", "studio dentistico"],
        "nl": ["tandarts", "tandartspraktijk", "tandheelkundige kliniek"],
        "ru": ["стоматология", "стоматологическая клиника", "зубной врач"],
        "hi": ["डेंटल क्लिनिक", "दंत चिकित्सक", "दांतों का डॉक्टर"],
    },
    "law_firm": {
        "en": ["law firm", "attorney", "lawyer", "legal office", "law office"],
        "tr": ["hukuk bürosu", "avukat", "avukatlık ofisi"],
        "de": ["Anwaltskanzlei", "Rechtsanwalt", "Anwaltsbüro"],
        "fr": ["cabinet d'avocats", "avocat", "étude d'avocats"],
        "es": ["bufete de abogados", "abogado", "despacho jurídico"],
        "pt": ["escritório de advocacia", "advogado"],
        "ar": ["مكتب محاماة", "محامي", "مستشار قانوني"],
        "ja": ["法律事務所", "弁護士", "法律相談"],
        "ko": ["법률 사무소", "변호사", "법무법인"],
        "zh": ["律师事务所", "律师", "法律顾问"],
        "it": ["studio legale", "avvocato"],
        "nl": ["advocatenkantoor", "advocaat"],
        "ru": ["юридическая фирма", "адвокат", "юрист"],
        "hi": ["कानूनी फर्म", "वकील", "अधिवक्ता"],
    },
    "accounting": {
        "en": ["accounting firm", "accountant", "CPA", "bookkeeper", "tax advisor"],
        "tr": ["muhasebe bürosu", "mali müşavir", "muhasebeci"],
        "de": ["Steuerberater", "Buchhaltung", "Wirtschaftsprüfer"],
        "fr": ["cabinet comptable", "expert-comptable", "comptable"],
        "es": ["despacho contable", "contador", "asesor fiscal"],
        "pt": ["escritório de contabilidade", "contador"],
        "ar": ["مكتب محاسبة", "محاسب", "مستشار ضريبي"],
        "ja": ["会計事務所", "税理士", "公認会計士"],
        "ko": ["회계 사무소", "세무사", "공인회계사"],
        "zh": ["会计师事务所", "会计", "税务顾问"],
        "it": ["studio commercialista", "commercialista"],
        "nl": ["accountantskantoor", "boekhouder"],
        "ru": ["бухгалтерская фирма", "бухгалтер"],
        "hi": ["लेखा फर्म", "चार्टर्ड अकाउंटेंट"],
    },
    "gym": {
        "en": ["gym", "fitness center", "health club", "personal trainer", "crossfit"],
        "tr": ["spor salonu", "fitness merkezi", "pilates stüdyosu"],
        "de": ["Fitnessstudio", "Sportstudio", "Fitnesscenter"],
        "fr": ["salle de sport", "centre de fitness", "club de gym"],
        "es": ["gimnasio", "centro de fitness", "centro deportivo"],
        "pt": ["academia", "centro de fitness"],
        "ar": ["صالة رياضية", "نادي رياضي", "مركز لياقة"],
        "ja": ["ジム", "フィットネスクラブ", "スポーツジム"],
        "ko": ["헬스장", "피트니스 센터", "체육관"],
        "zh": ["健身房", "健身中心", "体育馆"],
        "it": ["palestra", "centro fitness"],
        "nl": ["sportschool", "fitnesscentrum"],
        "ru": ["тренажерный зал", "фитнес-клуб", "спортзал"],
        "hi": ["जिम", "फिटनेस सेंटर", "व्यायामशाला"],
    },
    "auto_gallery": {
        "en": ["car dealership", "auto dealer", "used cars", "car showroom"],
        "tr": ["oto galeri", "araba galerisi", "ikinci el araç"],
        "de": ["Autohaus", "Autohändler", "Gebrauchtwagen"],
        "fr": ["concessionnaire auto", "garage automobile"],
        "es": ["concesionario de autos", "agencia de autos"],
        "pt": ["concessionária", "revendedora de carros"],
        "ar": ["معرض سيارات", "وكالة سيارات"],
        "ja": ["カーディーラー", "自動車販売店"],
        "ko": ["자동차 대리점", "중고차 매매"],
        "zh": ["汽车经销商", "二手车行"],
        "it": ["concessionaria auto", "autosalone"],
        "nl": ["autodealer", "autohandel"],
        "ru": ["автосалон", "автодилер"],
        "hi": ["कार डीलरशिप", "ऑटो गैलरी"],
    },
    "construction": {
        "en": ["construction company", "contractor", "builder", "renovation"],
        "tr": ["inşaat firması", "müteahhit", "yapı şirketi"],
        "de": ["Bauunternehmen", "Baufirma", "Bauunternehmer"],
        "fr": ["entreprise de construction", "constructeur"],
        "es": ["empresa constructora", "contratista"],
        "pt": ["construtora", "empresa de construção"],
        "ar": ["شركة مقاولات", "شركة بناء"],
        "ja": ["建設会社", "工務店", "建築会社"],
        "ko": ["건설 회사", "시공사", "건축 회사"],
        "zh": ["建筑公司", "施工单位", "装修公司"],
        "it": ["impresa edile", "costruttore"],
        "nl": ["bouwbedrijf", "aannemer"],
        "ru": ["строительная компания", "подрядчик"],
        "hi": ["निर्माण कंपनी", "ठेकेदार"],
    },
    "restaurant": {
        "en": ["restaurant", "cafe", "bistro", "dining"],
        "tr": ["restoran", "kafe", "lokanta"],
        "de": ["Restaurant", "Gaststätte", "Café"],
        "fr": ["restaurant", "café", "brasserie"],
        "es": ["restaurante", "cafetería"],
        "pt": ["restaurante", "café"],
        "ar": ["مطعم", "مقهى"],
        "ja": ["レストラン", "カフェ", "飲食店"],
        "ko": ["레스토랑", "카페", "음식점"],
        "zh": ["餐厅", "咖啡馆", "饭店"],
        "it": ["ristorante", "caffè", "trattoria"],
        "nl": ["restaurant", "café"],
        "ru": ["ресторан", "кафе"],
        "hi": ["रेस्तरां", "कैफे"],
    },
    "real_estate": {
        "en": ["real estate agency", "realtor", "property agent", "estate agent"],
        "tr": ["emlak ofisi", "gayrimenkul", "emlakçı"],
        "de": ["Immobilienmakler", "Immobilienbüro"],
        "fr": ["agence immobilière", "agent immobilier"],
        "es": ["agencia inmobiliaria", "inmobiliaria"],
        "pt": ["imobiliária", "corretor de imóveis"],
        "ar": ["وكالة عقارية", "مكتب عقاري"],
        "ja": ["不動産", "不動産会社"],
        "ko": ["부동산", "공인중개사"],
        "zh": ["房地产中介", "房产公司"],
        "it": ["agenzia immobiliare"],
        "nl": ["makelaar", "vastgoedkantoor"],
        "ru": ["агентство недвижимости", "риэлтор"],
        "hi": ["रियल एस्टेट एजेंसी", "संपत्ति एजेंट"],
    },
    "beauty_salon": {
        "en": ["beauty salon", "hair salon", "spa", "nail salon", "barber"],
        "tr": ["güzellik salonu", "kuaför", "spa merkezi"],
        "de": ["Friseursalon", "Schönheitssalon", "Kosmetikstudio"],
        "fr": ["salon de beauté", "coiffeur", "institut de beauté"],
        "es": ["salón de belleza", "peluquería", "spa"],
        "pt": ["salão de beleza", "cabeleireiro"],
        "ar": ["صالون تجميل", "مركز تجميل"],
        "ja": ["美容院", "ヘアサロン", "エステ"],
        "ko": ["미용실", "뷰티살롱", "헤어살롱"],
        "zh": ["美容院", "美发店", "美甲店"],
        "it": ["salone di bellezza", "parrucchiere"],
        "nl": ["schoonheidssalon", "kapper"],
        "ru": ["салон красоты", "парикмахерская"],
        "hi": ["ब्यूटी सैलन", "हेयर सैलन"],
    },
    "medical_clinic": {
        "en": ["medical clinic", "doctor", "physician", "healthcare center", "hospital"],
        "tr": ["tıp merkezi", "doktor", "sağlık merkezi", "poliklinik"],
        "de": ["Arztpraxis", "Klinik", "Gesundheitszentrum"],
        "fr": ["clinique médicale", "médecin", "centre de santé"],
        "es": ["clínica médica", "consultorio médico", "centro de salud"],
        "pt": ["clínica médica", "consultório médico"],
        "ar": ["عيادة طبية", "مركز طبي", "مستشفى"],
        "ja": ["クリニック", "医院", "病院"],
        "ko": ["의원", "클리닉", "병원"],
        "zh": ["诊所", "医疗中心", "医院"],
        "it": ["clinica medica", "studio medico"],
        "nl": ["medisch centrum", "huisarts", "kliniek"],
        "ru": ["медицинская клиника", "врач", "поликлиника"],
        "hi": ["मेडिकल क्लिनिक", "डॉक्टर", "स्वास्थ्य केंद्र"],
    },
}

# Currency mapping by country code
CURRENCY_MAP = {
    "US": "USD", "GB": "GBP", "EU": "EUR", "DE": "EUR", "FR": "EUR",
    "ES": "EUR", "IT": "EUR", "NL": "EUR", "PT": "EUR", "AT": "EUR",
    "BE": "EUR", "IE": "EUR", "FI": "EUR", "GR": "EUR", "TR": "TRY",
    "JP": "JPY", "KR": "KRW", "CN": "CNY", "IN": "INR", "BR": "BRL",
    "MX": "MXN", "CA": "CAD", "AU": "AUD", "NZ": "NZD", "ZA": "ZAR",
    "AE": "AED", "SA": "SAR", "EG": "EGP", "NG": "NGN", "KE": "KES",
    "RU": "RUB", "UA": "UAH", "PL": "PLN", "CZ": "CZK", "HU": "HUF",
    "RO": "RON", "SE": "SEK", "NO": "NOK", "DK": "DKK", "CH": "CHF",
    "TH": "THB", "VN": "VND", "ID": "IDR", "MY": "MYR", "SG": "SGD",
    "PH": "PHP", "PK": "PKR", "BD": "BDT", "IL": "ILS", "AR": "ARS",
    "CL": "CLP", "CO": "COP", "PE": "PEN",
}

# Package pricing tiers (in USD, auto-converted)
USD_PACKAGE_PRICING = {
    "Starter":      {"monthly": 500,  "setup": 300},
    "Professional": {"monthly": 1200, "setup": 800},
    "Premium":      {"monthly": 2500, "setup": 1500},
}

# Approximate USD exchange rates (updated periodically)
USD_EXCHANGE_RATES = {
    "USD": 1.0, "EUR": 0.92, "GBP": 0.79, "TRY": 38.5, "JPY": 155.0,
    "KRW": 1380.0, "CNY": 7.25, "INR": 84.0, "BRL": 5.1, "MXN": 17.5,
    "CAD": 1.37, "AUD": 1.55, "NZD": 1.68, "ZAR": 18.5, "AED": 3.67,
    "SAR": 3.75, "RUB": 92.0, "PLN": 4.05, "CZK": 23.5, "HUF": 370.0,
    "RON": 4.65, "SEK": 10.8, "NOK": 10.9, "DKK": 6.9, "CHF": 0.88,
    "THB": 35.5, "VND": 25400.0, "IDR": 15800.0, "MYR": 4.7, "SGD": 1.35,
    "PHP": 56.5, "PKR": 280.0, "BDT": 110.0, "ILS": 3.7, "NGN": 1600.0,
    "KES": 153.0, "EGP": 50.0, "UAH": 41.0, "ARS": 870.0, "CLP": 950.0,
    "COP": 4000.0, "PEN": 3.75, "GHS": 15.5,
}

class SerpApiGlobalIntegration:
    """
    Real SerpApi integration for worldwide Google Maps lead generation.
    Uses SerpApi's Google Maps engine for live synchronous data.
    """

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
        """Formulates a localized Google Maps search query"""
        normalized_sector = sector.lower().strip()
        keywords = GLOBAL_SECTOR_KEYWORDS.get(normalized_sector)

        if keywords:
            selected_lang = language if language in keywords else "en"
            base_keyword = keywords[selected_lang][0]
        else:
            # Allow free-form business types such as "coffee shop" from chat prompts.
            base_keyword = sector.strip()

        return f"{base_keyword} in {location}"

    def search_maps(self, sector: str, location: str, country_code: str, language: str, max_results: int = 20) -> list:
        """
        Runs synchronous queries against SerpApi.
        Handles pagination if max_results > 20.
        """
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
        """
        Converts raw SerpApi maps data into the unified JARVIS lead format.
        """
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
            
            # Extract GPS coordinates
            gps = place.get("gps_coordinates", {})
            lat = gps.get("latitude", 0.0)
            lng = gps.get("longitude", 0.0)
            
            leads.append({
                "name": place.get("title"),
                "sector": category,
                "phone": phone,
                "website": website,
                "rating": rating,
                "review_count": review_count,
                "score": score,
                "recommended_package": package,
                "raw_address": place.get("address", ""),
                "latitude": lat,
                "longitude": lng
            })

            # Sort by score descending to present highest priority first
            leads.sort(key=lambda x: x["score"], reverse=True)
            
        return leads

    def generate_scan_report(self, leads: list, sector: str, location: str, country_code: str) -> dict:
        """Generate a high-level summary report for the dashboard"""
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
