#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS AI Agency Operating System — Core Package
=================================================
Tüm 10 modülü içeren birleşik Python paketi.

Modüller:
1. Database Manager
2. Lead Scoring Engine
3. Playbook Templates
4. ROI Calculator
5. Pitch Script Generator
6. Revenue Roadmap Engine
7. Contract Generator
8. Board Meeting AI
9. Apify Integration
10. Dashboard Server

Kullanım:
    from jarvis_core import JARVIS
    jarvis = JARVIS()
    jarvis.start()
"""

import json
import psycopg2
from psycopg2.extras import RealDictCursor
import openai
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math
import hashlib
from dotenv import load_dotenv
from jarvis_serpapi_global import SerpApiGlobalIntegration

load_dotenv()

# ============================================
# 1. DATABASE MANAGER
# ============================================
class DatabaseManager:
    """JARVIS Database Manager — PostgreSQL Backend"""

    def __init__(self):
        self.conn = None

    def connect(self):
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(
                host=os.environ.get("DB_HOST", "localhost"),
                port=os.environ.get("DB_PORT", "5432"),
                dbname=os.environ.get("DB_NAME", "osmanorka"),
                user=os.environ.get("DB_USER", "osmanorka"),
                password=os.environ.get("DB_PASSWORD", "")
            )
        return self.conn

    def initialize(self):
        """Create all tables if they don't exist in PostgreSQL"""
        conn = self.connect()
        cursor = conn.cursor()

        tables = {
            "users": """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    role TEXT DEFAULT 'agent',
                    agency_name TEXT,
                    monthly_target REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "leads": """
                CREATE TABLE IF NOT EXISTS leads (
                    id SERIAL PRIMARY KEY,
                    business_name TEXT NOT NULL,
                    sector TEXT,
                    city TEXT,
                    district TEXT,
                    phone TEXT,
                    email TEXT,
                    website TEXT,
                    google_rating REAL,
                    review_count INTEGER DEFAULT 0,
                    has_website INTEGER DEFAULT 0,
                    has_social_media INTEGER DEFAULT 0,
                    employee_count INTEGER,
                    score INTEGER,
                    package_recommendation TEXT,
                    latitude REAL,
                    longitude REAL,
                    status TEXT DEFAULT 'new',
                    source TEXT DEFAULT 'map_scan',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "customers": """
                CREATE TABLE IF NOT EXISTS customers (
                    id SERIAL PRIMARY KEY,
                    lead_id INTEGER REFERENCES leads(id),
                    business_name TEXT NOT NULL,
                    contact_person TEXT,
                    package TEXT,
                    monthly_fee REAL,
                    contract_start DATE,
                    contract_end DATE,
                    status TEXT DEFAULT 'active',
                    health_score INTEGER DEFAULT 100,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "interactions": """
                CREATE TABLE IF NOT EXISTS interactions (
                    id SERIAL PRIMARY KEY,
                    lead_id INTEGER REFERENCES leads(id),
                    customer_id INTEGER REFERENCES customers(id),
                    type TEXT,
                    channel TEXT,
                    content TEXT,
                    outcome TEXT,
                    scheduled_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "playbooks": """
                CREATE TABLE IF NOT EXISTS playbooks (
                    id SERIAL PRIMARY KEY,
                    sector TEXT NOT NULL,
                    name TEXT NOT NULL,
                    strategies TEXT,
                    duration_months INTEGER,
                    target_roi REAL,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "offers": """
                CREATE TABLE IF NOT EXISTS offers (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    package TEXT,
                    sector TEXT,
                    base_price REAL,
                    features TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "case_studies": """
                CREATE TABLE IF NOT EXISTS case_studies (
                    id SERIAL PRIMARY KEY,
                    customer_id INTEGER REFERENCES customers(id),
                    sector TEXT,
                    title TEXT,
                    before_metrics TEXT,
                    after_metrics TEXT,
                    roi_achieved REAL,
                    testimonial TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "projects": """
                CREATE TABLE IF NOT EXISTS projects (
                    id SERIAL PRIMARY KEY,
                    customer_id INTEGER REFERENCES customers(id),
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'planning',
                    start_date DATE,
                    end_date DATE,
                    budget REAL,
                    progress INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "tasks": """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    project_id INTEGER REFERENCES projects(id),
                    assigned_to TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'todo',
                    due_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "contracts": """
                CREATE TABLE IF NOT EXISTS contracts (
                    id SERIAL PRIMARY KEY,
                    customer_id INTEGER REFERENCES customers(id),
                    contract_text TEXT,
                    package TEXT,
                    monthly_fee REAL,
                    total_value REAL,
                    duration_months INTEGER,
                    signed_at TIMESTAMP,
                    status TEXT DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "revenue_roadmap": """
                CREATE TABLE IF NOT EXISTS revenue_roadmap (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    target_mrr REAL,
                    current_mrr REAL DEFAULT 0,
                    plan_data TEXT,
                    month INTEGER,
                    year INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "board_meetings": """
                CREATE TABLE IF NOT EXISTS board_meetings (
                    id SERIAL PRIMARY KEY,
                    meeting_date DATE,
                    health_score INTEGER,
                    report_data TEXT,
                    recommendations TEXT,
                    tasks_assigned TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "map_scans": """
                CREATE TABLE IF NOT EXISTS map_scans (
                    id SERIAL PRIMARY KEY,
                    city TEXT,
                    district TEXT,
                    sector TEXT,
                    total_found INTEGER DEFAULT 0,
                    qualified INTEGER DEFAULT 0,
                    scan_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "pitch_scripts": """
                CREATE TABLE IF NOT EXISTS pitch_scripts (
                    id SERIAL PRIMARY KEY,
                    lead_id INTEGER REFERENCES leads(id),
                    script_type TEXT,
                    content TEXT,
                    sector TEXT,
                    is_sent INTEGER DEFAULT 0,
                    response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "settings": """
                CREATE TABLE IF NOT EXISTS settings (
                    id SERIAL PRIMARY KEY,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )"""
        }

        for name, sql in tables.items():
            cursor.execute(sql)

        conn.commit()
        return len(tables)

    def execute(self, query, params=None):
        if not self.conn or self.conn.closed:
            self.connect()
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        # Adapt SQLite '?' placeholders to PostgreSQL '%s'
        pg_query = query.replace("?", "%s")
        if params:
            cursor.execute(pg_query, params)
        else:
            cursor.execute(pg_query)
        self.conn.commit()
        return cursor

    def fetch_all(self, query, params=None):
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def fetch_one(self, query, params=None):
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def close(self):
        if self.conn:
            self.conn.close()


# ============================================
# 2. LEAD SCORING ENGINE
# ============================================
class LeadScoringEngine:
    """Lead puanlama motoru — 5 kategori, 0-100"""

    SECTOR_AI_NEED = {
        "dental": 90, "law_firm": 75, "accounting": 70,
        "gym": 80, "auto_gallery": 85, "construction": 65,
        "restaurant": 80, "hotel": 85, "education": 75,
        "healthcare": 90, "real_estate": 80, "retail": 70
    }

    PACKAGES = {
        (80, 101): {"name": "Premium", "price_range": "15.000-25.000 TL/ay"},
        (60, 80):  {"name": "Professional", "price_range": "8.000-15.000 TL/ay"},
        (40, 60):  {"name": "Starter", "price_range": "3.000-8.000 TL/ay"},
        (0, 40):   {"name": "Nurture", "price_range": "Henüz hazır değil"}
    }

    def calculate_score(self, lead_data: Dict) -> Dict:
        scores = {}

        # 1. Online Presence (0-25)
        op = 0
        if lead_data.get("has_website"): op += 10
        if lead_data.get("has_social_media"): op += 8
        if lead_data.get("google_maps_listed"): op += 7
        scores["online_presence"] = min(op, 25)

        # 2. Reviews & Reputation (0-25)
        rr = 0
        rating = lead_data.get("google_rating", 0)
        reviews = lead_data.get("review_count", 0)
        if rating >= 4.5: rr += 12
        elif rating >= 4.0: rr += 9
        elif rating >= 3.5: rr += 6
        elif rating >= 3.0: rr += 3
        if reviews >= 100: rr += 13
        elif reviews >= 50: rr += 10
        elif reviews >= 20: rr += 7
        elif reviews >= 5: rr += 4
        scores["reviews_reputation"] = min(rr, 25)

        # 3. Business Size (0-20)
        bs = 0
        emp = lead_data.get("employee_count", 0)
        if emp >= 50: bs += 12
        elif emp >= 20: bs += 9
        elif emp >= 10: bs += 7
        elif emp >= 5: bs += 5
        if lead_data.get("multiple_locations"): bs += 8
        scores["business_size"] = min(bs, 20)

        # 4. Sector AI Need (0-15)
        sector = lead_data.get("sector", "").lower()
        need = self.SECTOR_AI_NEED.get(sector, 50)
        scores["sector_ai_need"] = round(need * 15 / 100)

        # 5. Engagement Signals (0-15)
        es = 0
        if lead_data.get("responded_before"): es += 5
        if lead_data.get("visited_website"): es += 4
        if lead_data.get("opened_email"): es += 3
        if lead_data.get("social_active"): es += 3
        scores["engagement"] = min(es, 15)

        total = sum(scores.values())

        # Package recommendation
        package = {"name": "Nurture", "price_range": "Henüz hazır değil"}
        for (low, high), pkg in self.PACKAGES.items():
            if low <= total < high:
                package = pkg
                break

        return {
            "total_score": total,
            "breakdown": scores,
            "package_recommendation": package["name"],
            "price_range": package["price_range"],
            "priority": "🔴 Yüksek" if total >= 75 else "🟡 Orta" if total >= 50 else "🟢 Düşük"
        }


# ============================================
# 3. PLAYBOOK TEMPLATES
# ============================================
class PlaybookManager:
    """Sektör bazlı playbook şablonları"""

    PLAYBOOKS = {
        "dental": {
            "name": "Diş Klinik AI Dönüşüm Playbook",
            "strategies": [
                "Online randevu sistemi + AI chatbot",
                "Google Reviews otomasyonu",
                "Tedavi hatırlatma WhatsApp botu",
                "Sosyal medya içerik otomasyonu",
                "Hasta memnuniyet analizi",
                "SEO + Google Ads optimizasyonu",
                "Referans programı otomasyonu",
                "Tedavi planı görselleştirme",
                "Bekleme odası dijital deneyim",
                "Rakip analiz dashboard"
            ],
            "duration_months": 6,
            "target_roi": 300,
            "avg_patient_value": 5000,
            "monthly_new_patients_target": 30
        },
        "law_firm": {
            "name": "Hukuk Bürosu AI Playbook",
            "strategies": [
                "Müvekkil intake chatbot",
                "Dava takip otomasyonu",
                "Belge analiz AI",
                "Randevu ve hatırlatma sistemi",
                "Hukuki içerik pazarlama",
                "Müvekkil portal",
                "Fatura ve tahsilat otomasyonu",
                "Rakip fiyat analizi",
                "Referans takip sistemi",
                "Performans dashboard"
            ],
            "duration_months": 6,
            "target_roi": 250,
            "avg_case_value": 15000,
            "monthly_new_clients_target": 10
        },
        "accounting": {
            "name": "Muhasebe Bürosu AI Playbook",
            "strategies": [
                "Belge toplama otomasyonu",
                "Müşteri portal + dosya paylaşım",
                "Vergi takvimi hatırlatma",
                "AI destekli veri girişi",
                "Müşteri onboarding otomasyonu",
                "Raporlama dashboard",
                "Fatura takip sistemi",
                "Mevzuat güncelleme botu",
                "Müşteri memnuniyet takibi",
                "Cross-sell analiz motoru"
            ],
            "duration_months": 4,
            "target_roi": 200,
            "avg_client_value": 3000,
            "monthly_new_clients_target": 15
        },
        "gym": {
            "name": "Spor Salonu AI Playbook",
            "strategies": [
                "Üyelik satış chatbot",
                "Kişisel antrenman planı AI",
                "Devamsızlık takip + motivasyon",
                "Sosyal medya içerik üretimi",
                "Üye referans programı",
                "Diyet ve beslenme botu",
                "Sınıf rezervasyon sistemi",
                "Üye retention analizi",
                "Kampanya otomasyonu",
                "Rakip fiyat takibi"
            ],
            "duration_months": 4,
            "target_roi": 250,
            "avg_membership_value": 1500,
            "monthly_new_members_target": 40
        },
        "auto_gallery": {
            "name": "Oto Galeri AI Playbook",
            "strategies": [
                "Araç sorgulama WhatsApp botu",
                "Stok yönetim otomasyonu",
                "Fiyat karşılaştırma motoru",
                "Sahibinden/Arabam entegrasyonu",
                "Müşteri takip CRM",
                "Araç değerleme AI",
                "Sosyal medya ilan otomasyonu",
                "Kredi hesaplama botu",
                "Satış sonrası takip",
                "Pazar analiz dashboard"
            ],
            "duration_months": 5,
            "target_roi": 350,
            "avg_sale_value": 500000,
            "monthly_sales_target": 15
        },
        "construction": {
            "name": "İnşaat Firması AI Playbook",
            "strategies": [
                "Proje teklif otomasyonu",
                "Müşteri adayı takip CRM",
                "3D görselleştirme entegrasyonu",
                "Şantiye ilerleme raporlama",
                "Tedarikçi yönetim sistemi",
                "Maliyet tahmin AI",
                "Sosyal medya proje vitrin",
                "Müşteri iletişim portali",
                "Sözleşme yönetimi",
                "Rakip proje takibi"
            ],
            "duration_months": 8,
            "target_roi": 200,
            "avg_project_value": 2000000,
            "monthly_leads_target": 20
        }
    }

    def get_playbook(self, sector: str) -> Dict:
        return self.PLAYBOOKS.get(sector, {})

    def get_all_sectors(self) -> List[str]:
        return list(self.PLAYBOOKS.keys())

    def get_strategies(self, sector: str) -> List[str]:
        pb = self.PLAYBOOKS.get(sector, {})
        return pb.get("strategies", [])


# ============================================
# 4. ROI CALCULATOR
# ============================================
class ROICalculator:
    """Sektör + paket bazlı ROI hesaplama"""

    PACKAGE_PRICES = {
        "Starter": {"min": 3000, "max": 8000, "avg": 5000},
        "Professional": {"min": 8000, "max": 15000, "avg": 11000},
        "Premium": {"min": 15000, "max": 25000, "avg": 19000}
    }

    SECTOR_MULTIPLIERS = {
        "dental": {"revenue_per_new": 5000, "conversion_boost": 0.35, "retention_boost": 0.20},
        "law_firm": {"revenue_per_new": 15000, "conversion_boost": 0.25, "retention_boost": 0.15},
        "accounting": {"revenue_per_new": 3000, "conversion_boost": 0.30, "retention_boost": 0.25},
        "gym": {"revenue_per_new": 1500, "conversion_boost": 0.40, "retention_boost": 0.30},
        "auto_gallery": {"revenue_per_new": 50000, "conversion_boost": 0.20, "retention_boost": 0.10},
        "construction": {"revenue_per_new": 200000, "conversion_boost": 0.15, "retention_boost": 0.10}
    }

    def calculate(self, sector: str, package: str, current_monthly_customers: int = 10) -> Dict:
        pkg = self.PACKAGE_PRICES.get(package, self.PACKAGE_PRICES["Professional"])
        mult = self.SECTOR_MULTIPLIERS.get(sector, self.SECTOR_MULTIPLIERS["dental"])

        monthly_cost = pkg["avg"]
        new_customers = round(current_monthly_customers * mult["conversion_boost"])
        retained = round(current_monthly_customers * mult["retention_boost"])
        total_new_value = new_customers * mult["revenue_per_new"]
        retention_value = retained * mult["revenue_per_new"] * 0.3

        monthly_revenue = total_new_value + retention_value
        annual_revenue = monthly_revenue * 12
        annual_cost = monthly_cost * 12
        roi_percent = round(((annual_revenue - annual_cost) / annual_cost) * 100)
        payback_days = round((monthly_cost / monthly_revenue) * 30) if monthly_revenue > 0 else 999

        return {
            "monthly_cost": monthly_cost,
            "monthly_revenue_generated": monthly_revenue,
            "annual_revenue": annual_revenue,
            "annual_cost": annual_cost,
            "net_profit": annual_revenue - annual_cost,
            "roi_percent": roi_percent,
            "payback_days": payback_days,
            "new_customers_per_month": new_customers,
            "retained_customers": retained
        }


# ============================================
# 5. PITCH SCRIPT GENERATOR
# ============================================
class PitchScriptGenerator:
    """4 tür pitch script üretici"""

    PERSUASION_TACTICS = {
        "scarcity": "Bu ay sadece {limit} yeni müşteri alıyoruz",
        "social_proof": "{sector} sektöründe {count}+ işletme AI çözümlerimizi kullanıyor",
        "authority": "Google ve Meta sertifikalı ekibimiz",
        "reciprocity": "Size ücretsiz bir {gift} hazırladık",
        "urgency": "Bu teklif {days} gün geçerli",
        "loss_aversion": "Her ay AI kullanmadan {loss} TL potansiyel gelir kaybediyorsunuz"
    }

    def generate(self, lead_data: Dict, sector: str, score_data: Dict) -> Dict:
        business = lead_data.get("business_name", "İşletme")
        contact = lead_data.get("contact_person", "Yetkili")
        package = score_data.get("package_recommendation", "Professional")
        price = score_data.get("price_range", "8.000-15.000 TL/ay")

        scripts = {
            "cold_call": self._cold_call(business, contact, sector, package, price),
            "email": self._email(business, contact, sector, package, price),
            "whatsapp": self._whatsapp(business, contact, sector, package),
            "demo_presentation": self._demo(business, sector, package, price, score_data)
        }

        return scripts

    def _cold_call(self, business, contact, sector, package, price):
        return f"""📞 SOĞUK ARAMA SCRIPTI — {business}

Merhaba, {contact} Bey/Hanım, ben [İsim], [Ajans Adı]'ndan arıyorum.

{business} için özel bir araştırma yaptık ve çok ilginç bulgularımız var.
Sektörünüzdeki rakiplerinizin %60'ı artık AI destekli sistemler kullanıyor.

Size 15 dakikalık bir demo gösterebilirsem, {business} için aylık 
tahmini {price} yatırımla nasıl 3-5x geri dönüş sağlayabileceğinizi gösterebilirim.

Bu hafta 15 dakikanız var mı?

[OBJECTION HANDLING]
- "İlgilenmiyorum" → Anlıyorum, sadece rakiplerinizin ne yaptığını göstermek istiyorum
- "Bütçemiz yok" → Ücretsiz analiz raporu sunabiliriz, karar sizin
- "Düşüneyim" → Tabii, yarın sizi tekrar arayabilir miyim?"""

    def _email(self, business, contact, sector, package, price):
        return f"""📧 E-POSTA SCRIPTI — {business}

Konu: {business} için AI Dönüşüm Raporu (Ücretsiz)

Merhaba {contact} Bey/Hanım,

{business}'i inceledik ve sektörünüze özel bir AI dönüşüm raporu hazırladık.

Bulgularımız:
• Online görünürlüğünüzü %40 artırabilecek 3 kritik alan tespit ettik
• Rakiplerinizin %60'ı AI chatbot kullanıyor — siz henüz kullanmıyorsunuz
• Aylık tahmini {price} yatırımla 3-5x ROI potansiyeli

Ücretsiz raporunuzu görmek için bu maile yanıt vermeniz yeterli.

{self.PERSUASION_TACTICS['scarcity'].format(limit=5)}

Saygılarımla,
[İsim] — [Ajans Adı]"""

    def _whatsapp(self, business, contact, sector, package):
        return f"""💬 WHATSAPP SCRIPTI — {business}

Merhaba {contact} Bey/Hanım 👋

Ben [İsim], [Ajans Adı]'ndan.

{business} için ücretsiz bir AI analiz raporu hazırladık 📊

Rakiplerinizin online stratejilerini inceledik ve size özel 
3 kritik öneri belirledik.

Raporu göndermemi ister misiniz? 🚀"""

    def _demo(self, business, sector, package, price, score_data):
        return f"""🎯 DEMO SUNUM SCRIPTI — {business}

SLIDE 1: Hoş Geldiniz
"{business} için AI Dönüşüm Planı"

SLIDE 2: Mevcut Durum Analizi
• Lead Skoru: {score_data.get('total_score', 0)}/100
• Öneri: {package} Paket
• Fiyat: {price}

SLIDE 3: Sektör Analizi
• Rakip karşılaştırma
• AI kullanım oranları
• Kaçırılan fırsatlar

SLIDE 4: Çözüm Önerisi
• {package} paket detayları
• Uygulama takvimi
• Beklenen sonuçlar

SLIDE 5: ROI Projeksiyonu
• Yatırım: {price}
• Beklenen getiri: 3-5x
• Geri ödeme süresi: ~30 gün

SLIDE 6: Sonraki Adımlar
• Bugün karar → %10 erken kayıt indirimi
• Bu hafta başlangıç
• 30 gün para iade garantisi"""


# ============================================
# 6. REVENUE ROADMAP ENGINE
# ============================================
class RevenueRoadmapEngine:
    """6 aylık gelir yol haritası"""

    def generate(self, target_mrr: float, current_mrr: float = 0,
                 avg_deal_size: float = 10000, close_rate: float = 0.20) -> Dict:

        gap = target_mrr - current_mrr
        deals_needed = math.ceil(gap / avg_deal_size)
        demos_needed = math.ceil(deals_needed / close_rate)
        contacts_needed = math.ceil(demos_needed / 0.30)
        leads_needed = math.ceil(contacts_needed / 0.15)

        months = []
        cumulative_mrr = current_mrr
        monthly_deals = math.ceil(deals_needed / 6)

        for m in range(1, 7):
            ramp = min(1.0, 0.4 + (m * 0.12))
            month_deals = round(monthly_deals * ramp)
            month_revenue = month_deals * avg_deal_size
            cumulative_mrr += month_revenue

            months.append({
                "month": m,
                "target_deals": month_deals,
                "target_revenue": month_revenue,
                "cumulative_mrr": cumulative_mrr,
                "leads_needed": round(leads_needed / 6 * (1.2 if m <= 2 else 0.9)),
                "demos_needed": round(demos_needed / 6 * ramp),
                "ramp_factor": f"{ramp:.0%}",
                "milestone": self._get_milestone(m)
            })

        return {
            "target_mrr": target_mrr,
            "current_mrr": current_mrr,
            "gap": gap,
            "total_deals_needed": deals_needed,
            "funnel": {
                "leads": leads_needed,
                "contacts": contacts_needed,
                "demos": demos_needed,
                "closes": deals_needed
            },
            "monthly_plan": months
        }

    def _get_milestone(self, month):
        milestones = {
            1: "🏗️ Altyapı + İlk müşteriler",
            2: "📈 Pipeline doldurma",
            3: "🔥 Hızlanma fazı",
            4: "💪 Tam kapasite",
            5: "🚀 Ölçeklendirme",
            6: "🎯 Hedef yakalama"
        }
        return milestones.get(month, "")


# ============================================
# 7. CONTRACT GENERATOR
# ============================================
class ContractGenerator:
    """Otomatik sözleşme üretici"""

    PACKAGE_DETAILS = {
        "Starter": {"duration": 3, "setup_fee": 2000, "sla_response": "48 saat"},
        "Professional": {"duration": 6, "setup_fee": 5000, "sla_response": "24 saat"},
        "Premium": {"duration": 12, "setup_fee": 0, "sla_response": "4 saat"}
    }

    def generate(self, client_data: Dict, sector: str, package: str, monthly_fee: float) -> str:
        pkg = self.PACKAGE_DETAILS.get(package, self.PACKAGE_DETAILS["Professional"])
        duration = pkg["duration"]
        total = monthly_fee * duration
        today = datetime.now().strftime("%d.%m.%Y")
        end_date = (datetime.now() + timedelta(days=duration*30)).strftime("%d.%m.%Y")

        contract = f"""
{'='*60}
         HİZMET SÖZLEŞMESİ — {package.upper()} PAKET
{'='*60}

Sözleşme No: JRV-{datetime.now().strftime('%Y%m%d')}-{hashlib.md5(client_data.get('business_name','').encode()).hexdigest()[:6].upper()}
Tarih: {today}

MADDE 1 — TARAFLAR
Hizmet Veren: [Ajans Adı] ("Ajans")
Hizmet Alan: {client_data.get('business_name', '')} ("Müşteri")
Yetkili: {client_data.get('contact_person', '')}
Adres: {client_data.get('address', '')}

MADDE 2 — HİZMET KAPSAMI
Sektör: {sector}
Paket: {package}
AI çözümleri, otomasyon sistemleri ve dijital dönüşüm hizmetleri

MADDE 3 — SÜRE
Başlangıç: {today}
Bitiş: {end_date}
Süre: {duration} ay

MADDE 4 — ÜCRET
Aylık Hizmet Bedeli: {monthly_fee:,.0f} TL + KDV
Kurulum Ücreti: {pkg['setup_fee']:,.0f} TL + KDV
Toplam Sözleşme Değeri: {total:,.0f} TL + KDV
Ödeme: Her ayın 1-5'i arası

MADDE 5 — SLA (Hizmet Seviyesi)
Yanıt Süresi: {pkg['sla_response']}
Uptime Garantisi: %99.5
Aylık Raporlama: Evet

MADDE 6 — GİZLİLİK
Taraflar birbirlerinin ticari sırlarını koruyacaktır.

MADDE 7 — FİKRİ MÜLKİYET
Geliştirilen AI modelleri ve sistemler ajansa aittir.
Müşteri kullanım lisansına sahiptir.

MADDE 8 — FESİH
30 gün önceden yazılı bildirim ile feshedilebilir.
Erken fesih cezası: Kalan sürenin %50'si

MADDE 9 — UYUŞMAZLIK
İstanbul Mahkemeleri ve İcra Daireleri yetkilidir.

MADDE 10 — İMZALAR

Ajans: _______________     Müşteri: _______________
Tarih: {today}            Tarih: {today}
{'='*60}"""
        return contract


# ============================================
# 8. BOARD MEETING AI
# ============================================
class BoardMeetingAI:
    """Haftalık yönetim kurulu toplantısı AI"""

    def generate_report(self, agency_data: Dict) -> Dict:
        health = self._calculate_health(agency_data)
        financial = self._financial_summary(agency_data)
        pipeline = self._pipeline_analysis(agency_data)
        churn = self._churn_detection(agency_data)
        recommendations = self._generate_recommendations(agency_data, health)
        tasks = self._assign_tasks(recommendations)

        return {
            "date": datetime.now().strftime("%d.%m.%Y"),
            "health_score": health,
            "financial": financial,
            "pipeline": pipeline,
            "churn_risks": churn,
            "recommendations": recommendations,
            "weekly_tasks": tasks
        }

    def _calculate_health(self, data):
        score = 50
        mrr = data.get("mrr", 0)
        target = data.get("target_mrr", 100000)
        progress = mrr / target if target > 0 else 0
        score += round(progress * 20)

        churn = data.get("churn_rate", 0)
        if churn < 5: score += 15
        elif churn < 10: score += 10
        elif churn < 15: score += 5

        pipeline = data.get("pipeline_value", 0)
        if pipeline > mrr * 3: score += 15
        elif pipeline > mrr * 2: score += 10
        elif pipeline > mrr: score += 5

        return min(100, max(0, score))

    def _financial_summary(self, data):
        mrr = data.get("mrr", 0)
        costs = data.get("monthly_costs", 0)
        return {
            "mrr": mrr,
            "arr": mrr * 12,
            "costs": costs,
            "profit": mrr - costs,
            "margin": f"{((mrr-costs)/mrr*100):.1f}%" if mrr > 0 else "0%"
        }

    def _pipeline_analysis(self, data):
        leads = data.get("active_leads", [])
        hot = [l for l in leads if l.get("score", 0) >= 75]
        return {
            "total_leads": len(leads),
            "hot_leads": len(hot),
            "pipeline_value": data.get("pipeline_value", 0),
            "expected_closes": len(hot)
        }

    def _churn_detection(self, data):
        customers = data.get("customers", [])
        risks = []
        for c in customers:
            if c.get("health_score", 100) < 60:
                risks.append({
                    "customer": c.get("name", ""),
                    "health": c.get("health_score", 0),
                    "action": "Acil görüşme planla"
                })
        return risks

    def _generate_recommendations(self, data, health):
        recs = []
        if health < 60:
            recs.append({"priority": "🔴 Kritik", "text": "Müşteri kaybı riski yüksek, retention kampanyası başlat"})
        if data.get("mrr", 0) < data.get("target_mrr", 0) * 0.5:
            recs.append({"priority": "🔴 Kritik", "text": "MRR hedefin çok altında, satış hızını artır"})
        if len(data.get("active_leads", [])) < 20:
            recs.append({"priority": "🟡 Büyüme", "text": "Lead havuzu düşük, yeni harita taraması başlat"})
        recs.append({"priority": "🟢 Optimizasyon", "text": "Mevcut müşterilere upsell kampanyası planla"})
        return recs

    def _assign_tasks(self, recommendations):
        tasks = []
        for i, rec in enumerate(recommendations):
            tasks.append({
                "task": rec["text"],
                "priority": rec["priority"],
                "due": (datetime.now() + timedelta(days=7)).strftime("%d.%m.%Y"),
                "assigned_to": "JARVIS Auto-Assign"
            })
        return tasks


# ============================================
# 9. APIFY INTEGRATION
# ============================================
# SerpApi Integration has been moved to jarvis_serpapi_global.py


# ============================================
# 10. JARVIS MAIN CLASS
# ============================================
class JARVIS:
    """JARVIS AI Agency OS — Ana sınıf"""

    SEARCH_VERBS = (
        "find", "show", "list", "search", "look up", "lookup", "recommend",
        "locate", "get me", "bul", "goster", "göster", "listele", "ara",
    )

    NUMBER_WORDS = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "bir": 1, "iki": 2, "uc": 3, "üç": 3, "dort": 4, "dört": 4,
        "bes": 5, "beş": 5, "alti": 6, "altı": 6, "yedi": 7,
        "sekiz": 8, "dokuz": 9, "on": 10,
    }

    COUNTRY_HINTS = {
        "australia": "AU",
        "melbourne": "AU",
        "victoria": "AU",
        "vic": "AU",
        "sydney": "AU",
        "brisbane": "AU",
        "perth": "AU",
        "adelaide": "AU",
        "craigieburn": "AU",
        "uk": "GB",
        "united kingdom": "GB",
        "london": "GB",
        "england": "GB",
        "usa": "US",
        "united states": "US",
        "new york": "US",
        "san francisco": "US",
        "los angeles": "US",
        "canada": "CA",
        "toronto": "CA",
        "vancouver": "CA",
    }

    def __init__(self):
        self.db = DatabaseManager()
        self.scoring = LeadScoringEngine()
        self.playbooks = PlaybookManager()
        self.roi = ROICalculator()
        self.pitch = PitchScriptGenerator()
        self.roadmap = RevenueRoadmapEngine()
        self.contracts = ContractGenerator()
        self.board = BoardMeetingAI()
        self.serpapi = SerpApiGlobalIntegration()
        self.version = "1.0.0"
        self.name = "JARVIS"

    def start(self):
        """JARVIS'i başlat"""
        tables = self.db.initialize()
        return {
            "status": "active",
            "version": self.version,
            "tables_created": tables,
            "modules": [
                "DatabaseManager", "LeadScoringEngine", "PlaybookManager",
                "ROICalculator", "PitchScriptGenerator", "RevenueRoadmapEngine",
                "ContractGenerator", "BoardMeetingAI", "SerpApiIntegration"
            ]
        }

    def scan_area(self, city: str, district: str, sector: str):
        """Bölge taraması başlat"""
        search_input = self.apify.build_search_input(city, district, sector)
        return {"status": "scan_ready", "input": search_input}

    def analyze_lead(self, lead_data: Dict):
        """Lead analizi — skor + paket + ROI + pitch"""
        score = self.scoring.calculate_score(lead_data)
        sector = lead_data.get("sector", "dental")
        package = score["package_recommendation"]

        roi = self.roi.calculate(sector, package, lead_data.get("monthly_customers", 10))
        scripts = self.pitch.generate(lead_data, sector, score)
        playbook = self.playbooks.get_playbook(sector)

        return {
            "score": score,
            "roi": roi,
            "pitch_scripts": scripts,
            "playbook": playbook.get("name", ""),
            "strategies": playbook.get("strategies", [])[:5]
        }

    def generate_contract(self, client_data: Dict, sector: str, package: str, monthly_fee: float):
        """Sözleşme oluştur"""
        return self.contracts.generate(client_data, sector, package, monthly_fee)

    def weekly_board_meeting(self, agency_data: Dict):
        """Haftalık yönetim kurulu raporu"""
        return self.board.generate_report(agency_data)

    def revenue_plan(self, target: float, current: float = 0):
        """Gelir yol haritası"""
        return self.roadmap.generate(target, current)

    def _extract_business_search(self, command: str) -> Optional[Dict]:
        """Parse prompts like 'find five coffee shops in Craigieburn'."""
        normalized = command.strip()
        lower = normalized.lower()

        if not any(verb in lower for verb in self.SEARCH_VERBS):
            return None

        location_match = re.search(
            r"\b(?:in|near|around|within|at)\b\s+(.+?)(?:[?.!]\s*)?$",
            normalized,
            flags=re.IGNORECASE,
        )
        if not location_match:
            return None

        location = location_match.group(1).strip(" ,?.!")
        location = re.sub(
            r"^(?:the\s+suburb\s+of|suburb\s+of|city\s+of|area\s+of)\s+",
            "",
            location,
            flags=re.IGNORECASE,
        ).strip()
        location = re.sub(r"\s+(?:for me|please)$", "", location, flags=re.IGNORECASE).strip()
        if not location:
            return None

        subject = normalized[:location_match.start()].strip(" ,?.!")
        subject = re.sub(
            r"^(?:could you|can you|please|would you|i need you to)\s+",
            "",
            subject,
            flags=re.IGNORECASE,
        ).strip()

        verb_pattern = "|".join(re.escape(verb) for verb in self.SEARCH_VERBS)
        subject = re.sub(
            rf"^(?:{verb_pattern})\s+",
            "",
            subject,
            flags=re.IGNORECASE,
        ).strip()
        subject = re.sub(r"^(?:me\s+|us\s+|some\s+|the\s+|top\s+|best\s+)", "", subject, flags=re.IGNORECASE)

        count = self._extract_count(subject)
        subject = re.sub(r"^\d+\s+", "", subject).strip()
        for word in sorted(self.NUMBER_WORDS.keys(), key=len, reverse=True):
            subject = re.sub(rf"^{re.escape(word)}\s+", "", subject, flags=re.IGNORECASE)

        rating_threshold = None
        if re.search(r"\b(very high|highest|top rated|best rated|excellent|high feedback|high ratings?)\b", lower):
            rating_threshold = 4.5
        elif re.search(r"\b(good ratings?|well rated)\b", lower):
            rating_threshold = 4.2

        subject = re.split(r"\b(?:with|that have|having)\b", subject, maxsplit=1, flags=re.IGNORECASE)[0].strip(" ,?.!")
        subject = re.sub(r"\b(near me|around me)\b", "", subject, flags=re.IGNORECASE).strip(" ,?.!")
        subject = self._normalize_business_type(subject)
        if not subject:
            return None

        return {
            "count": count,
            "business_type": subject,
            "location": location,
            "country_code": self._infer_country_code(location, normalized),
            "language": "en",
            "rating_threshold": rating_threshold,
            "max_results": min(max(count * 4, 10), 20),
        }

    def _extract_count(self, text: str) -> int:
        digit_match = re.search(r"\b(\d{1,2})\b", text)
        if digit_match:
            return max(1, min(int(digit_match.group(1)), 10))

        lower = text.lower()
        for word, value in self.NUMBER_WORDS.items():
            if re.search(rf"\b{re.escape(word)}\b", lower):
                return value
        return 5

    def _normalize_business_type(self, value: str) -> str:
        normalized = value.strip().lower()
        replacements = {
            "coffee shops": "coffee shop",
            "cafes": "cafe",
            "restaurants": "restaurant",
            "law firms": "law firm",
            "dentists": "dentist",
            "gyms": "gym",
        }
        normalized = replacements.get(normalized, normalized)
        return re.sub(r"\s+", " ", normalized).strip()

    def _infer_country_code(self, location: str, command: str) -> str:
        haystack = f"{location} {command}".lower()
        for hint, country_code in self.COUNTRY_HINTS.items():
            if hint in haystack:
                return country_code
        return "US"

    def _format_business_search_response(self, request: Dict, leads: List[Dict]) -> str:
        if not leads:
            return (
                f"I couldn't find any {request['business_type']} results in {request['location']} right now. "
                "Try a broader location or a different business type."
            )

        filtered = leads
        threshold = request.get("rating_threshold")
        if threshold is not None:
            matching = [lead for lead in leads if lead.get("rating", 0) >= threshold]
            if matching:
                filtered = matching

        ranked = sorted(
            filtered,
            key=lambda lead: (
                lead.get("rating", 0),
                lead.get("review_count", 0),
                1 if lead.get("website") else 0,
            ),
            reverse=True,
        )
        selected = ranked[:request["count"]]

        lines = [
            f"I found {len(selected)} {request['business_type']} results in {request['location']}."
        ]
        if threshold is not None:
            lines[0] += f" Prioritised ratings of {threshold:.1f}+ where available."

        for index, lead in enumerate(selected, start=1):
            rating = lead.get("rating", 0)
            rating_text = f"{rating:.1f}★" if rating else "No rating"
            reviews = lead.get("review_count", 0)
            review_text = f"{reviews} reviews" if reviews else "review count unavailable"
            line = f"{index}. {lead.get('name', 'Unknown')} — {rating_text} ({review_text})"

            details = []
            if lead.get("raw_address"):
                details.append(lead["raw_address"])
            if lead.get("phone"):
                details.append(lead["phone"])
            if lead.get("website"):
                details.append(lead["website"])

            if details:
                line += f"\n   {' | '.join(details)}"

            lines.append(line)

        return "\n".join(lines)

    def _handle_business_search(self, request: Dict) -> str:
        raw_results = self.serpapi.search_maps(
            request["business_type"],
            request["location"],
            request["country_code"],
            request["language"],
            request["max_results"],
        )
        leads = self.serpapi.process_results(
            raw_results,
            request["business_type"],
            request["country_code"],
        )
        return self._format_business_search_response(request, leads)

    def _general_chat_fallback(self, command: str) -> str:
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if api_key:
            try:
                client = openai.OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model=os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are JARVIS, an AI agency assistant. Answer briefly and directly. "
                                "You can help with local business discovery, lead analysis, ROI planning, "
                                "pitch scripts, contracts, board reports, and revenue plans. "
                                "If a request is outside those capabilities, say so and suggest a nearby supported action."
                            ),
                        },
                        {"role": "user", "content": command},
                    ],
                    max_tokens=220,
                )
                message = response.choices[0].message.content if response.choices else ""
                if message:
                    return message.strip()
            except Exception:
                pass

        return (
            f'I understood your request: "{command}". '
            "I can currently help with business discovery, lead analysis, ROI calculations, "
            "pitch scripts, contracts, board reports, and revenue plans. "
            "For example: 'Find 5 coffee shops in Craigieburn, Melbourne'."
        )

    def process_command(self, command: str) -> str:
        """Doğal dil komut işleme"""
        cmd = command.lower().strip()

        business_search = self._extract_business_search(command)
        if business_search:
            try:
                return self._handle_business_search(business_search)
            except Exception as exc:
                return (
                    "I understood that as a business search, but the live lookup failed. "
                    f"Details: {exc}"
                )

        if "tara" in cmd or "scan" in cmd:
            return "🗺️ Harita taraması başlatılıyor..."
        elif "analiz" in cmd or "score" in cmd:
            return "📊 Lead analizi yapılıyor..."
        elif "pitch" in cmd or "script" in cmd:
            return "📝 Pitch scripti hazırlanıyor..."
        elif "sözleşme" in cmd or "contract" in cmd:
            return "📄 Sözleşme oluşturuluyor..."
        elif "toplantı" in cmd or "board" in cmd:
            return "🏛️ Yönetim kurulu raporu hazırlanıyor..."
        elif "hedef" in cmd or "roadmap" in cmd:
            return "🎯 Gelir yol haritası oluşturuluyor..."
        elif "roi" in cmd:
            return "💰 ROI hesaplanıyor..."
        else:
            return self._general_chat_fallback(command)


# ============================================
# QUICK START
# ============================================
if __name__ == "__main__":
    jarvis = JARVIS()
    result = jarvis.start()
    print(f"🤖 {jarvis.name} v{jarvis.version} aktif!")
    print(f"📦 {result['tables_created']} tablo oluşturuldu")
    print(f"🔧 {len(result['modules'])} modül yüklendi")
    print(f"Modüller: {', '.join(result['modules'])}")
