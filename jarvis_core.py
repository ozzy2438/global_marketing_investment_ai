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
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import math
import hashlib
import uuid
from dotenv import load_dotenv
from jarvis_serpapi_global import SerpApiGlobalIntegration
from jarvis_serper_research import SerperWebResearch

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
                )""",
            "candidate_decisions": """
                CREATE TABLE IF NOT EXISTS candidate_decisions (
                    id SERIAL PRIMARY KEY,
                    lead_key TEXT UNIQUE NOT NULL,
                    lead_name TEXT NOT NULL,
                    raw_address TEXT,
                    sector TEXT,
                    market_code TEXT DEFAULT 'AU',
                    decision_status TEXT DEFAULT 'monitor',
                    recommended_platform TEXT,
                    recommended_service TEXT,
                    proposal_recommended INTEGER DEFAULT 0,
                    proposal_readiness TEXT,
                    commercial_priority TEXT,
                    owner TEXT,
                    next_action TEXT,
                    follow_up_date DATE,
                    confidence INTEGER DEFAULT 60,
                    operator_notes TEXT,
                    candidate_snapshot TEXT,
                    analysis_snapshot TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "knowledge_sources": """
                CREATE TABLE IF NOT EXISTS knowledge_sources (
                    id SERIAL PRIMARY KEY,
                    source_key TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    author TEXT,
                    source_type TEXT DEFAULT 'summary',
                    source_path TEXT,
                    workflow_stage TEXT,
                    summary TEXT,
                    tags TEXT,
                    status TEXT DEFAULT 'ready',
                    metadata_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "knowledge_snippets": """
                CREATE TABLE IF NOT EXISTS knowledge_snippets (
                    id SERIAL PRIMARY KEY,
                    source_id INTEGER REFERENCES knowledge_sources(id),
                    snippet_key TEXT UNIQUE NOT NULL,
                    content TEXT NOT NULL,
                    insight_type TEXT,
                    workflow_stage TEXT,
                    tags TEXT,
                    importance INTEGER DEFAULT 50,
                    metadata_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "conversation_sessions": """
                CREATE TABLE IF NOT EXISTS conversation_sessions (
                    session_id TEXT PRIMARY KEY,
                    title TEXT,
                    mode TEXT DEFAULT 'chat',
                    market_code TEXT DEFAULT 'AU',
                    metadata_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            "conversation_messages": """
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    message_type TEXT DEFAULT 'text',
                    metadata_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
# 2. MARKET PROFILE MANAGER
# ============================================
class MarketProfileManager:
    """Market-aware commercial and presentation defaults."""

    DEFAULT_MARKET = os.environ.get("JARVIS_DEFAULT_MARKET", "AU").upper()

    PROFILES = {
        "AU": {
            "market_code": "AU",
            "market_name": "Australia",
            "presentation_locale": "en-AU",
            "currency_code": "AUD",
            "currency_symbol": "A$",
            "monthly_suffix": "/month",
            "package_bands": {
                "Starter": {"min": 3500, "max": 6500, "avg": 5000},
                "Professional": {"min": 6500, "max": 12000, "avg": 9000},
                "Premium": {"min": 12000, "max": 20000, "avg": 16000},
            },
            "contract_defaults": {
                "jurisdiction": "Victoria, Australia",
                "governing_law": "laws of Victoria, Australia",
                "invoice_terms": "Net 14 days",
            },
            "outreach_defaults": ["Email", "Phone", "LinkedIn"],
            "sector_assumptions": {
                "dental": "Focus on booking efficiency, review growth, and retention systems.",
                "restaurant": "Focus on repeat visits, loyalty, and reputation management.",
                "law_firm": "Focus on intake quality, case follow-up, and trust signals.",
                "accounting": "Focus on recurring client management and workflow visibility.",
            },
        },
        "US": {
            "market_code": "US",
            "market_name": "United States",
            "presentation_locale": "en-US",
            "currency_code": "USD",
            "currency_symbol": "$",
            "monthly_suffix": "/month",
            "package_bands": {
                "Starter": {"min": 2500, "max": 5000, "avg": 3500},
                "Professional": {"min": 5000, "max": 9000, "avg": 7000},
                "Premium": {"min": 9000, "max": 15000, "avg": 12000},
            },
            "contract_defaults": {
                "jurisdiction": "State selected per client contract",
                "governing_law": "state law specified in the agreement",
                "invoice_terms": "Net 15 days",
            },
            "outreach_defaults": ["Email", "Phone", "LinkedIn"],
            "sector_assumptions": {
                "dental": "Emphasise patient acquisition and chair utilisation.",
                "restaurant": "Emphasise owned customer lists and repeat-visit campaigns.",
            },
        },
        "GB": {
            "market_code": "GB",
            "market_name": "United Kingdom",
            "presentation_locale": "en-GB",
            "currency_code": "GBP",
            "currency_symbol": "£",
            "monthly_suffix": "/month",
            "package_bands": {
                "Starter": {"min": 2000, "max": 4000, "avg": 2800},
                "Professional": {"min": 4000, "max": 7500, "avg": 5600},
                "Premium": {"min": 7500, "max": 13000, "avg": 9800},
            },
            "contract_defaults": {
                "jurisdiction": "England and Wales",
                "governing_law": "laws of England and Wales",
                "invoice_terms": "Net 14 days",
            },
            "outreach_defaults": ["Email", "Phone", "LinkedIn"],
            "sector_assumptions": {
                "law_firm": "Emphasise intake quality, compliance-safe processes, and pipeline clarity.",
                "accounting": "Emphasise recurring service retention and client communications.",
            },
        },
        "NZ": {
            "market_code": "NZ",
            "market_name": "New Zealand",
            "presentation_locale": "en-NZ",
            "currency_code": "NZD",
            "currency_symbol": "NZ$",
            "monthly_suffix": "/month",
            "package_bands": {
                "Starter": {"min": 3000, "max": 5500, "avg": 4200},
                "Professional": {"min": 5500, "max": 10000, "avg": 7600},
                "Premium": {"min": 10000, "max": 17000, "avg": 13500},
            },
            "contract_defaults": {
                "jurisdiction": "New Zealand",
                "governing_law": "laws of New Zealand",
                "invoice_terms": "Net 14 days",
            },
            "outreach_defaults": ["Email", "Phone", "LinkedIn"],
            "sector_assumptions": {
                "restaurant": "Emphasise loyalty, local awareness, and repeat bookings.",
            },
        },
        "TR": {
            "market_code": "TR",
            "market_name": "Turkey",
            "presentation_locale": "tr-TR",
            "currency_code": "TRY",
            "currency_symbol": "₺",
            "monthly_suffix": "/ay",
            "package_bands": {
                "Starter": {"min": 3000, "max": 8000, "avg": 5000},
                "Professional": {"min": 8000, "max": 15000, "avg": 11000},
                "Premium": {"min": 15000, "max": 25000, "avg": 19000},
            },
            "contract_defaults": {
                "jurisdiction": "Istanbul, Turkey",
                "governing_law": "laws of the Republic of Turkey",
                "invoice_terms": "Monthly advance payment",
            },
            "outreach_defaults": ["WhatsApp", "Phone", "Email"],
            "sector_assumptions": {
                "dental": "Emphasise review growth and appointment reminders.",
            },
        },
    }

    SCORE_THRESHOLDS = (
        (80, "Premium"),
        (60, "Professional"),
        (40, "Starter"),
        (0, "Nurture"),
    )

    def get_profile(self, market_code: Optional[str] = None) -> Dict[str, Any]:
        code = (market_code or self.DEFAULT_MARKET or "AU").upper()
        return deepcopy(self.PROFILES.get(code, self.PROFILES["AU"]))

    def format_money(self, amount: float, market_code: Optional[str] = None, decimals: int = 0) -> str:
        profile = self.get_profile(market_code)
        formatted = f"{amount:,.{decimals}f}" if decimals else f"{amount:,.0f}"
        return f"{profile['currency_symbol']}{formatted}"

    def get_package_prices(self, market_code: Optional[str] = None) -> Dict[str, Dict[str, float]]:
        return self.get_profile(market_code)["package_bands"]

    def package_for_score(self, total_score: int, market_code: Optional[str] = None) -> Dict[str, Any]:
        prices = self.get_package_prices(market_code)
        profile = self.get_profile(market_code)

        package_name = "Nurture"
        for threshold, candidate in self.SCORE_THRESHOLDS:
            if total_score >= threshold:
                package_name = candidate
                break

        if package_name == "Nurture":
            return {
                "name": "Nurture",
                "price_range": "Not proposal-ready yet",
                "market_code": profile["market_code"],
                "currency_code": profile["currency_code"],
                "currency_symbol": profile["currency_symbol"],
            }

        band = prices[package_name]
        return {
            "name": package_name,
            "price_range": (
                f"{self.format_money(band['min'], profile['market_code'])}-"
                f"{self.format_money(band['max'], profile['market_code'])}{profile['monthly_suffix']}"
            ),
            "monthly_avg": band["avg"],
            "market_code": profile["market_code"],
            "currency_code": profile["currency_code"],
            "currency_symbol": profile["currency_symbol"],
        }


# ============================================
# 3. LEAD SCORING ENGINE
# ============================================
class LeadScoringEngine:
    """Lead scoring engine with market-aware packaging."""

    SECTOR_AI_NEED = {
        "dental": 90, "law_firm": 75, "accounting": 70,
        "gym": 80, "auto_gallery": 85, "construction": 65,
        "restaurant": 80, "hotel": 85, "education": 75,
        "healthcare": 90, "real_estate": 80, "retail": 70
    }

    def __init__(self, market_profiles: MarketProfileManager, default_market: str = "AU"):
        self.market_profiles = market_profiles
        self.default_market = default_market

    def calculate_score(self, lead_data: Dict, market_code: Optional[str] = None) -> Dict:
        scores = {}
        market = market_code or lead_data.get("market_code") or self.default_market

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
        package = self.market_profiles.package_for_score(total, market)

        return {
            "total_score": total,
            "breakdown": scores,
            "package_recommendation": package["name"],
            "price_range": package["price_range"],
            "market_code": package["market_code"],
            "currency_code": package["currency_code"],
            "priority": "High" if total >= 75 else "Medium" if total >= 50 else "Low",
        }


# ============================================
# 3. PLAYBOOK TEMPLATES
# ============================================
class PlaybookManager:
    """Sector playbooks written for global English markets."""

    PLAYBOOKS = {
        "dental": {
            "name": "Dental Growth and Retention Playbook",
            "strategies": [
                "Online booking flow with AI intake assistant",
                "Review growth and reputation monitoring",
                "Treatment reminder sequences via email, SMS, or optional messaging apps",
                "Social proof and before/after content workflows",
                "Patient satisfaction pulse surveys",
                "Local SEO plus paid search optimisation",
                "Referral and recall automation",
                "Treatment plan explainer content",
                "Front-desk follow-up dashboard",
                "Competitor visibility monitoring"
            ],
            "duration_months": 6,
            "target_roi": 300,
            "avg_patient_value": 5000,
            "monthly_new_patients_target": 30
        },
        "law_firm": {
            "name": "Law Firm Intake and Trust Playbook",
            "strategies": [
                "Lead qualification assistant for enquiries",
                "Matter follow-up and milestone automation",
                "Document collection and review workflows",
                "Consultation scheduling and reminders",
                "Authority-building content engine",
                "Client portal and intake visibility",
                "Billing and collections follow-up",
                "Competitor positioning review",
                "Referral source tracking",
                "Pipeline and case-stage reporting"
            ],
            "duration_months": 6,
            "target_roi": 250,
            "avg_case_value": 15000,
            "monthly_new_clients_target": 10
        },
        "accounting": {
            "name": "Accounting Firm Client Operations Playbook",
            "strategies": [
                "Document collection and deadline automation",
                "Client portal plus secure file exchange",
                "Tax and compliance reminder sequences",
                "AI-assisted data entry and categorisation",
                "Client onboarding workflow",
                "Portfolio reporting dashboard",
                "Invoice follow-up automation",
                "Regulation change update assistant",
                "Client satisfaction monitoring",
                "Cross-sell and service-gap analysis"
            ],
            "duration_months": 4,
            "target_roi": 200,
            "avg_client_value": 3000,
            "monthly_new_clients_target": 15
        },
        "gym": {
            "name": "Fitness Retention and Membership Playbook",
            "strategies": [
                "Membership sales assistant",
                "Personal training and onboarding prompts",
                "Attendance risk monitoring and win-back campaigns",
                "Content calendar for classes and transformations",
                "Member referral automation",
                "Nutrition and goal-support messaging",
                "Class booking optimisation",
                "Retention and churn analysis",
                "Campaign automation for offers and trials",
                "Competitor pricing watch"
            ],
            "duration_months": 4,
            "target_roi": 250,
            "avg_membership_value": 1500,
            "monthly_new_members_target": 40
        },
        "auto_gallery": {
            "name": "Dealership Lead Response Playbook",
            "strategies": [
                "Vehicle enquiry assistant across web and messaging channels",
                "Inventory and response automation",
                "Price and market comparison engine",
                "Marketplace listing sync",
                "Sales CRM and follow-up sequences",
                "Trade-in valuation workflows",
                "Listing content automation",
                "Finance qualification prompts",
                "Post-sale review and referral follow-up",
                "Local market intelligence dashboard"
            ],
            "duration_months": 5,
            "target_roi": 350,
            "avg_sale_value": 500000,
            "monthly_sales_target": 15
        },
        "construction": {
            "name": "Construction Proposal and Pipeline Playbook",
            "strategies": [
                "Proposal generation and qualification workflows",
                "Lead CRM and estimation pipeline",
                "Visual scope and concept presentation",
                "Project progress reporting",
                "Supplier coordination workflows",
                "Cost estimation support",
                "Portfolio and proof content engine",
                "Client communication portal",
                "Contract and milestone tracking",
                "Competitor and tender monitoring"
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
# 4. KNOWLEDGE LIBRARY
# ============================================
class KnowledgeLibrary:
    """Indexes structured playbook summaries and notes for retrieval."""

    WORKFLOW_KEYWORDS = {
        "offer_design": ("offer", "offers", "pricing", "price", "package", "irresistible", "value"),
        "discovery_pitch": ("pitch", "sale", "sales", "discovery", "pain point", "pain points", "objection", "wow", "challenger"),
        "retention_analytics": ("churn", "retention", "cohort", "analytics", "remarketing", "re-engagement", "reactivation"),
        "messaging": ("website", "headline", "landing page", "copy", "cta", "storybrand", "message"),
        "habit_design": ("hooked", "trigger", "reward", "investment", "habit", "engagement"),
    }

    def __init__(self, db: Optional[DatabaseManager] = None, library_dir: Optional[str] = None):
        self.db = db
        self.library_dir = library_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "playbooks",
        )
        self.last_sync_report: Dict[str, Any] = {
            "synced_sources": 0,
            "synced_snippets": 0,
            "indexed_files": [],
            "skipped_files": [],
        }
        self.sources_cache: List[Dict[str, Any]] = []
        self.snippets_cache: List[Dict[str, Any]] = []

    def _slugify(self, value: str) -> str:
        cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower())
        return cleaned.strip("-") or "source"

    def _normalise_list(self, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return [str(value).strip()]

    def _source_key(self, record: Dict[str, Any], source_path: str) -> str:
        if record.get("source_key"):
            return str(record["source_key"])
        base = record.get("title") or os.path.basename(source_path)
        return self._slugify(base)

    def _build_snippet(self, source_key: str, snippet: Dict[str, Any], index: int, fallback_stage: str, fallback_tags: List[str]) -> Dict[str, Any]:
        content = str(snippet.get("content", "")).strip()
        if not content:
            return {}
        return {
            "source_key": source_key,
            "snippet_key": snippet.get("snippet_key") or f"{source_key}-{index}",
            "content": content,
            "insight_type": snippet.get("insight_type", "insight"),
            "workflow_stage": snippet.get("workflow_stage", fallback_stage),
            "tags": self._normalise_list(snippet.get("tags") or fallback_tags),
            "importance": int(snippet.get("importance", 50)),
            "metadata": snippet.get("metadata", {}),
        }

    def _normalise_source_record(self, record: Dict[str, Any], source_path: str) -> Dict[str, Any]:
        source_key = self._source_key(record, source_path)
        tags = self._normalise_list(record.get("tags"))
        workflow_stage = record.get("workflow_stage", "general")
        insights = []
        for index, snippet in enumerate(record.get("insights", []), start=1):
            normalised = self._build_snippet(source_key, snippet, index, workflow_stage, tags)
            if normalised:
                insights.append(normalised)

        if not insights and record.get("summary"):
            insights.append(
                {
                    "snippet_key": f"{source_key}-summary",
                    "content": str(record["summary"]).strip(),
                    "insight_type": "summary",
                    "workflow_stage": workflow_stage,
                    "tags": tags,
                    "importance": int(record.get("importance", 60)),
                    "metadata": {},
                }
            )

        return {
            "source_key": source_key,
            "title": str(record.get("title", source_key)).strip(),
            "author": str(record.get("author", "")).strip(),
            "source_type": record.get("source_type", "summary"),
            "source_path": source_path,
            "workflow_stage": workflow_stage,
            "summary": str(record.get("summary", "")).strip(),
            "tags": tags,
            "status": record.get("status", "ready"),
            "metadata": record.get("metadata", {}),
            "insights": insights,
        }

    def _load_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)

        if isinstance(payload, dict) and "sources" in payload:
            records = payload["sources"]
        elif isinstance(payload, list):
            records = payload
        elif isinstance(payload, dict):
            records = [payload]
        else:
            records = []

        return [self._normalise_source_record(record, file_path) for record in records]

    def _load_summary_file(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as handle:
            raw = handle.read()

        lines = [line.rstrip() for line in raw.splitlines()]
        title = os.path.splitext(os.path.basename(file_path))[0]
        author = ""
        workflow_stage = "general"
        tags: List[str] = []
        summary_lines: List[str] = []
        insight_lines: List[str] = []
        parsing_metadata = True

        for line in lines:
            stripped = line.strip()
            if not stripped and parsing_metadata:
                parsing_metadata = False
                continue
            if parsing_metadata and stripped.startswith("# "):
                title = stripped[2:].strip()
                continue
            if parsing_metadata and ":" in stripped:
                key, value = stripped.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                if key == "author":
                    author = value
                    continue
                if key == "workflow":
                    workflow_stage = value
                    continue
                if key == "tags":
                    tags = self._normalise_list(value)
                    continue

            if stripped.startswith(("-", "*")):
                insight_lines.append(stripped[1:].strip())
            elif stripped:
                summary_lines.append(stripped)

        summary = " ".join(summary_lines[:3]).strip()
        return [
            self._normalise_source_record(
                {
                    "title": title,
                    "author": author,
                    "workflow_stage": workflow_stage,
                    "tags": tags,
                    "summary": summary,
                    "insights": [
                        {"content": insight, "workflow_stage": workflow_stage, "tags": tags}
                        for insight in insight_lines
                    ],
                },
                file_path,
            )
        ]

    def _persist_source(self, source: Dict[str, Any]) -> int:
        if not self.db:
            return 0

        self.db.execute(
            """
            INSERT INTO knowledge_sources (
                source_key, title, author, source_type, source_path,
                workflow_stage, summary, tags, status, metadata_json, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT (source_key) DO UPDATE SET
                title = EXCLUDED.title,
                author = EXCLUDED.author,
                source_type = EXCLUDED.source_type,
                source_path = EXCLUDED.source_path,
                workflow_stage = EXCLUDED.workflow_stage,
                summary = EXCLUDED.summary,
                tags = EXCLUDED.tags,
                status = EXCLUDED.status,
                metadata_json = EXCLUDED.metadata_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                source["source_key"],
                source["title"],
                source["author"],
                source["source_type"],
                source["source_path"],
                source["workflow_stage"],
                source["summary"],
                json.dumps(source["tags"], ensure_ascii=False),
                source["status"],
                json.dumps(source.get("metadata", {}), ensure_ascii=False),
            ),
        )
        row = self.db.fetch_one(
            "SELECT id FROM knowledge_sources WHERE source_key = ?",
            (source["source_key"],),
        )
        return int(row["id"]) if row else 0

    def _persist_snippets(self, source_id: int, snippets: List[Dict[str, Any]]) -> None:
        if not self.db or not source_id:
            return
        self.db.execute("DELETE FROM knowledge_snippets WHERE source_id = ?", (source_id,))
        for snippet in snippets:
            self.db.execute(
                """
                INSERT INTO knowledge_snippets (
                    source_id, snippet_key, content, insight_type,
                    workflow_stage, tags, importance, metadata_json, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    source_id,
                    snippet["snippet_key"],
                    snippet["content"],
                    snippet["insight_type"],
                    snippet["workflow_stage"],
                    json.dumps(snippet["tags"], ensure_ascii=False),
                    snippet["importance"],
                    json.dumps(snippet.get("metadata", {}), ensure_ascii=False),
                ),
            )

    def sync_directory(self, persist: bool = True) -> Dict[str, Any]:
        report = {
            "synced_sources": 0,
            "synced_snippets": 0,
            "indexed_files": [],
            "skipped_files": [],
            "library_dir": self.library_dir,
            "synced_at": datetime.now().isoformat(),
        }

        sources: List[Dict[str, Any]] = []
        snippets: List[Dict[str, Any]] = []

        if not os.path.isdir(self.library_dir):
            self.last_sync_report = report
            self.sources_cache = []
            self.snippets_cache = []
            return report

        for root, dirnames, filenames in os.walk(self.library_dir):
            dirnames[:] = [dirname for dirname in dirnames if not dirname.startswith(".")]
            for entry in sorted(filename for filename in filenames if not filename.startswith(".")):
                file_path = os.path.join(root, entry)
                relative_path = os.path.relpath(file_path, self.library_dir)
                lower = relative_path.lower()

                if lower.endswith((".pdf", ".epub", ".mobi")):
                    report["skipped_files"].append(
                        {
                            "file": relative_path,
                            "reason": "Binary book files are not indexed automatically. Add a structured summary or notes file instead.",
                        }
                    )
                    continue

                loaded_sources: List[Dict[str, Any]] = []
                if lower.endswith(".json"):
                    loaded_sources = self._load_json_file(file_path)
                elif lower.endswith(".summary.md") or lower.endswith(".summary.txt"):
                    loaded_sources = self._load_summary_file(file_path)
                else:
                    continue

                if not loaded_sources:
                    continue

                report["indexed_files"].append(relative_path)
                for source in loaded_sources:
                    sources.append(source)
                    snippets.extend(source["insights"])
                    if persist:
                        source_id = self._persist_source(source)
                        self._persist_snippets(source_id, source["insights"])

        self.sources_cache = sources
        self.snippets_cache = snippets
        report["synced_sources"] = len(sources)
        report["synced_snippets"] = len(snippets)
        self.last_sync_report = report
        return report

    def _ensure_loaded(self) -> None:
        if not self.sources_cache and not self.snippets_cache:
            self.sync_directory(persist=False)

    def _parse_json_field(self, value: Any) -> Any:
        if isinstance(value, (list, dict)):
            return value
        if value in (None, ""):
            return []
        try:
            return json.loads(value)
        except Exception:
            return []

    def get_sources(self, limit: int = 50) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        if self.db:
            try:
                rows = self.db.fetch_all(
                    "SELECT * FROM knowledge_sources ORDER BY title ASC LIMIT ?",
                    (limit,),
                )
            except Exception:
                rows = []
            if rows:
                return [
                    {
                        **dict(row),
                        "tags": self._parse_json_field(row.get("tags")),
                        "metadata": self._parse_json_field(row.get("metadata_json")),
                    }
                    for row in rows
                ]
        return self.sources_cache[:limit]

    def get_status(self) -> Dict[str, Any]:
        self._ensure_loaded()
        if self.db:
            try:
                source_count = self.db.fetch_one("SELECT COUNT(*) AS c FROM knowledge_sources")
                snippet_count = self.db.fetch_one("SELECT COUNT(*) AS c FROM knowledge_snippets")
            except Exception:
                source_count = None
                snippet_count = None
            return {
                **self.last_sync_report,
                "source_count": int(source_count["c"]) if source_count else len(self.sources_cache),
                "snippet_count": int(snippet_count["c"]) if snippet_count else len(self.snippets_cache),
            }
        return {
            **self.last_sync_report,
            "source_count": len(self.sources_cache),
            "snippet_count": len(self.snippets_cache),
        }

    def _workflow_matches(self, query: str) -> List[str]:
        lower = query.lower()
        matches = []
        for workflow, keywords in self.WORKFLOW_KEYWORDS.items():
            if any(keyword in lower for keyword in keywords):
                matches.append(workflow)
        return matches

    def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        self._ensure_loaded()
        tokens = {token for token in re.findall(r"[a-z0-9]+", query.lower()) if len(token) > 2}
        workflows = self._workflow_matches(query)

        source_map = {source["source_key"]: dict(source) for source in self.sources_cache}
        for source in source_map.values():
            source["matched_insights"] = []
            source["score"] = 0

        for snippet in self.snippets_cache:
            source = source_map.get(snippet["snippet_key"].rsplit("-", 1)[0])
            if not source:
                source = source_map.get(snippet.get("source_key", ""))
            if not source:
                continue

            haystack = " ".join(
                [
                    source.get("title", ""),
                    source.get("author", ""),
                    source.get("summary", ""),
                    " ".join(source.get("tags", [])),
                    snippet.get("content", ""),
                    " ".join(snippet.get("tags", [])),
                    snippet.get("workflow_stage", ""),
                    snippet.get("insight_type", ""),
                ]
            ).lower()

            score = 0
            for token in tokens:
                if token in source.get("title", "").lower():
                    score += 8
                elif token in haystack:
                    score += 3

            if workflows and snippet.get("workflow_stage") in workflows:
                score += 10
            if workflows and source.get("workflow_stage") in workflows:
                score += 10

            score += min(int(snippet.get("importance", 50)) // 20, 5)

            if score > 0:
                source["score"] += score
                source["matched_insights"].append(
                    {
                        "content": snippet["content"],
                        "workflow_stage": snippet.get("workflow_stage", ""),
                        "insight_type": snippet.get("insight_type", "insight"),
                        "importance": int(snippet.get("importance", 50)),
                        "score": score,
                    }
                )

        ranked_sources = [
            source
            for source in source_map.values()
            if source["matched_insights"] or (workflows and source.get("workflow_stage") in workflows)
        ]
        ranked_sources.sort(key=lambda source: (source["score"], len(source["matched_insights"])), reverse=True)

        matches = []
        for source in ranked_sources[:limit]:
            source["matched_insights"].sort(key=lambda item: (item["score"], item["importance"]), reverse=True)
            matches.append(
                {
                    "source_key": source["source_key"],
                    "title": source["title"],
                    "author": source.get("author", ""),
                    "workflow_stage": source.get("workflow_stage", ""),
                    "summary": source.get("summary", ""),
                    "tags": source.get("tags", []),
                    "score": source["score"],
                    "matched_insights": source["matched_insights"][:3],
                }
            )

        return {
            "query": query,
            "workflow_matches": workflows,
            "matches": matches,
            "status": self.get_status(),
        }


# ============================================
# 5. CONVERSATION MEMORY
# ============================================
class ConversationMemory:
    """Persistent chat and voice session memory."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def _parse_json_field(self, value: Any, fallback: Any) -> Any:
        if isinstance(value, (dict, list)):
            return value
        if value in (None, ""):
            return fallback
        try:
            return json.loads(value)
        except Exception:
            return fallback

    def _hydrate_session(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not row:
            return None
        record = dict(row)
        record["metadata"] = self._parse_json_field(record.get("metadata_json"), {})
        return record

    def _hydrate_message(self, row: Dict[str, Any]) -> Dict[str, Any]:
        record = dict(row)
        record["metadata"] = self._parse_json_field(record.get("metadata_json"), {})
        return record

    def ensure_session(
        self,
        session_id: Optional[str] = None,
        market_code: str = "AU",
        mode: str = "chat",
        title: str = "JARVIS Conversation",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        existing = self.get_session(session_id) if session_id else None
        if existing:
            return existing

        resolved_session_id = session_id or uuid.uuid4().hex
        self.db.execute(
            """
            INSERT INTO conversation_sessions (
                session_id, title, mode, market_code, metadata_json, updated_at
            )
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT (session_id) DO UPDATE SET
                title = EXCLUDED.title,
                mode = EXCLUDED.mode,
                market_code = EXCLUDED.market_code,
                metadata_json = EXCLUDED.metadata_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                resolved_session_id,
                title,
                mode,
                market_code,
                json.dumps(metadata or {}, ensure_ascii=False),
            ),
        )
        return self.get_session(resolved_session_id) or {
            "session_id": resolved_session_id,
            "title": title,
            "mode": mode,
            "market_code": market_code,
            "metadata": metadata or {},
        }

    def get_session(self, session_id: Optional[str]) -> Optional[Dict[str, Any]]:
        if not session_id:
            return None
        row = self.db.fetch_one(
            "SELECT * FROM conversation_sessions WHERE session_id = ?",
            (session_id,),
        )
        return self._hydrate_session(row)

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        message_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        if not session_id or not content.strip():
            return None
        self.db.execute(
            """
            INSERT INTO conversation_messages (
                session_id, role, content, message_type, metadata_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session_id,
                role,
                content.strip(),
                message_type,
                json.dumps(metadata or {}, ensure_ascii=False),
            ),
        )
        self.db.execute(
            "UPDATE conversation_sessions SET updated_at = CURRENT_TIMESTAMP WHERE session_id = ?",
            (session_id,),
        )
        row = self.db.fetch_one(
            "SELECT * FROM conversation_messages WHERE session_id = ? ORDER BY id DESC LIMIT 1",
            (session_id,),
        )
        return self._hydrate_message(row) if row else None

    def get_messages(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        rows = self.db.fetch_all(
            """
            SELECT * FROM conversation_messages
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (session_id, limit),
        )
        hydrated = [self._hydrate_message(row) for row in rows]
        hydrated.reverse()
        return hydrated

    def get_prompt_history(self, session_id: str, limit: int = 8) -> List[Dict[str, str]]:
        messages = self.get_messages(session_id, limit)
        return [
            {"role": message["role"], "content": message["content"]}
            for message in messages
            if message.get("role") in {"user", "assistant"} and message.get("content")
        ]


# ============================================
# 6. ROI CALCULATOR
# ============================================
class ROICalculator:
    """Sector ROI calculator with market-aware package pricing."""

    PACKAGE_PRICES = {
        "Starter": {"min": 3500, "max": 6500, "avg": 5000},
        "Professional": {"min": 6500, "max": 12000, "avg": 9000},
        "Premium": {"min": 12000, "max": 20000, "avg": 16000}
    }

    SECTOR_MULTIPLIERS = {
        "dental": {"revenue_per_new": 1800, "conversion_boost": 0.28, "retention_boost": 0.16},
        "law_firm": {"revenue_per_new": 4000, "conversion_boost": 0.18, "retention_boost": 0.12},
        "accounting": {"revenue_per_new": 1200, "conversion_boost": 0.22, "retention_boost": 0.18},
        "gym": {"revenue_per_new": 900, "conversion_boost": 0.32, "retention_boost": 0.22},
        "auto_gallery": {"revenue_per_new": 6500, "conversion_boost": 0.12, "retention_boost": 0.08},
        "construction": {"revenue_per_new": 18000, "conversion_boost": 0.10, "retention_boost": 0.06},
        "restaurant": {"revenue_per_new": 60, "conversion_boost": 0.35, "retention_boost": 0.26},
        "real_estate": {"revenue_per_new": 3000, "conversion_boost": 0.14, "retention_boost": 0.10},
    }

    def __init__(self, market_profiles: MarketProfileManager, default_market: str = "AU"):
        self.market_profiles = market_profiles
        self.default_market = default_market

    def calculate(self, sector: str, package: str, current_monthly_customers: int = 10, market_code: Optional[str] = None) -> Dict:
        market = market_code or self.default_market
        pkg = self.market_profiles.get_package_prices(market).get(package, self.market_profiles.get_package_prices(market)["Professional"])
        mult = self.SECTOR_MULTIPLIERS.get(sector, self.SECTOR_MULTIPLIERS["dental"])
        profile = self.market_profiles.get_profile(market)

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
            "retained_customers": retained,
            "market_code": profile["market_code"],
            "currency_code": profile["currency_code"],
            "currency_symbol": profile["currency_symbol"],
        }


# ============================================
# 5. PITCH SCRIPT GENERATOR
# ============================================
class PitchScriptGenerator:
    """Pitch script generator for operator-led outreach."""

    PERSUASION_TACTICS = {
        "scarcity": "We are only onboarding {limit} new clients this month",
        "social_proof": "{count}+ businesses in {sector} have adopted AI-led growth systems",
        "authority": "Our team specialises in practical revenue and CRM automation",
        "reciprocity": "We prepared a free {gift} for your team",
        "urgency": "This proposal window stays open for {days} days",
        "loss_aversion": "Each month without follow-up automation can leave {loss} in recoverable revenue on the table",
    }

    def __init__(self, market_profiles: MarketProfileManager, default_market: str = "AU"):
        self.market_profiles = market_profiles
        self.default_market = default_market

    def generate(self, lead_data: Dict, sector: str, score_data: Dict, market_code: Optional[str] = None) -> Dict:
        business = lead_data.get("business_name", "Business")
        contact = lead_data.get("contact_person", "there")
        package = score_data.get("package_recommendation", "Professional")
        price = score_data.get(
            "price_range",
            self.market_profiles.package_for_score(score_data.get("total_score", 65), market_code or self.default_market)["price_range"],
        )

        scripts = {
            "cold_call": self._cold_call(business, contact, sector, package, price),
            "email": self._email(business, contact, sector, package, price),
            "whatsapp": self._whatsapp(business, contact, sector, package),
            "demo_presentation": self._demo(business, sector, package, price, score_data)
        }

        return scripts

    def _cold_call(self, business, contact, sector, package, price):
        return f"""PHONE SCRIPT — {business}

Hi {contact}, this is [Name] from [Agency].

We reviewed {business} and found a few clear commercial opportunities in {sector}. If I can show you a 15-minute plan, I can walk through how a {package.lower()} engagement in the {price} range could improve follow-up, conversion, and repeat business.

Would you be open to a short discovery call this week?

Objection handling:
- "Not interested" -> Understood. I can still send a short benchmark snapshot so you can compare your current funnel with local competitors.
- "No budget" -> Fair. We can start with a scoped audit and only propose what is commercially justified.
- "Let me think about it" -> Absolutely. Is there a better day for a quick follow-up?"""

    def _email(self, business, contact, sector, package, price):
        return f"""EMAIL SCRIPT — {business}

Subject: Opportunity snapshot for {business}

Hi {contact},

We reviewed {business} and built a short operator brief around its current acquisition, conversion, and retention gaps.

Key points:
- there are clear opportunities to improve owned lead capture and follow-up
- the business could likely support a {package.lower()} engagement in the {price} range
- the commercial upside comes from faster response, better pipeline visibility, and stronger repeat-customer workflows

If useful, I can send over the one-page summary and suggested next steps.

Best,
[Name]
[Agency]"""

    def _whatsapp(self, business, contact, sector, package):
        return f"""MESSAGING SCRIPT — {business}

Hi {contact}, this is [Name] from [Agency].

We reviewed {business} and found a few practical growth opportunities around lead capture, follow-up, and customer retention.

If helpful, I can send a short summary and a suggested {package.lower()} rollout. Would you like me to share it?"""

    def _demo(self, business, sector, package, price, score_data):
        return f"""DEMO OUTLINE — {business}

Slide 1: Why {business} is worth reviewing now
Slide 2: Current commercial score -> {score_data.get('total_score', 0)}/100
Slide 3: Main gaps -> acquisition, conversion, retention, operations, visibility
Slide 4: Recommended offer -> {package} package in the {price} range
Slide 5: Expected outcome -> cleaner funnel, faster follow-up, stronger repeat business
Slide 6: Next step -> discovery workshop and scoped proposal"""


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
    """Market-aware service agreement generator."""

    PACKAGE_DETAILS = {
        "Starter": {"duration": 3, "setup_fee": 2000, "sla_response": "48 saat"},
        "Professional": {"duration": 6, "setup_fee": 5000, "sla_response": "24 saat"},
        "Premium": {"duration": 12, "setup_fee": 0, "sla_response": "4 saat"}
    }

    def __init__(self, market_profiles: MarketProfileManager, default_market: str = "AU"):
        self.market_profiles = market_profiles
        self.default_market = default_market

    def generate(self, client_data: Dict, sector: str, package: str, monthly_fee: float, market_code: Optional[str] = None) -> str:
        pkg = self.PACKAGE_DETAILS.get(package, self.PACKAGE_DETAILS["Professional"])
        duration = pkg["duration"]
        total = monthly_fee * duration
        profile = self.market_profiles.get_profile(market_code or self.default_market)
        today = datetime.now().strftime("%d %b %Y")
        end_date = (datetime.now() + timedelta(days=duration*30)).strftime("%d %b %Y")
        money = self.market_profiles.format_money
        agreement_id = hashlib.md5(client_data.get("business_name", "").encode()).hexdigest()[:6].upper()

        contract = f"""
{'='*60}
         SERVICES AGREEMENT — {package.upper()} PACKAGE
{'='*60}

Agreement No: JRV-{datetime.now().strftime('%Y%m%d')}-{agreement_id}
Date: {today}

1. Parties
Service Provider: [Agency Name]
Client: {client_data.get('business_name', '')}
Primary Contact: {client_data.get('contact_person', '')}
Address: {client_data.get('address', '')}

2. Scope
Sector: {sector}
Package: {package}
Scope covers commercial systems, CRM/workflow design, automation, and reporting.

3. Term
Start Date: {today}
End Date: {end_date}
Duration: {duration} months

4. Fees
Monthly Fee: {money(monthly_fee, profile['market_code'])} + applicable taxes
Setup Fee: {money(pkg['setup_fee'], profile['market_code'])} + applicable taxes
Total Contract Value: {money(total, profile['market_code'])} + applicable taxes
Payment Terms: {profile['contract_defaults']['invoice_terms']}

5. Service Levels
Response Time: {pkg['sla_response']}
Reporting: Monthly commercial and workflow review
Availability Target: 99.5%

6. Confidentiality
Both parties will protect confidential business information disclosed during delivery.

7. Intellectual Property
The client receives a usage licence for delivered systems, templates, and automations as defined in the final scope.

8. Termination
Either party may terminate with 30 days' written notice unless otherwise agreed in writing.

9. Governing Law
This agreement is governed by the {profile['contract_defaults']['governing_law']}.
Jurisdiction: {profile['contract_defaults']['jurisdiction']}

10. Signatures

Agency: _______________     Client: _______________
Date: {today}              Date: {today}
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

    STRATEGY_KEYWORDS = {
        "invest": ("invest", "investment", "priority", "best option", "which one", "worth backing", "worth investing"),
        "shortcomings": ("shortcoming", "shortcomings", "weakness", "weaknesses", "gap", "gaps", "issue", "issues"),
        "crm": ("crm", "platform", "customer platform", "customer system", "sales system", "pipeline"),
        "proposal": ("proposal", "submit", "pitch", "offer", "outreach", "send"),
    }

    KNOWLEDGE_KEYWORDS = (
        "book", "books", "playbook", "playbooks", "offer", "offers", "pitch",
        "pain point", "pain points", "storybrand", "hooked", "churn",
        "retention", "sales", "pricing", "remarketing", "re-engagement",
    )

    def __init__(self):
        self.db = DatabaseManager()
        self.market_profiles = MarketProfileManager()
        self.default_market = self.market_profiles.DEFAULT_MARKET
        self.scoring = LeadScoringEngine(self.market_profiles, self.default_market)
        self.playbooks = PlaybookManager()
        self.knowledge = KnowledgeLibrary(self.db)
        self.memory = ConversationMemory(self.db)
        self.roi = ROICalculator(self.market_profiles, self.default_market)
        self.pitch = PitchScriptGenerator(self.market_profiles, self.default_market)
        self.roadmap = RevenueRoadmapEngine()
        self.contracts = ContractGenerator(self.market_profiles, self.default_market)
        self.board = BoardMeetingAI()
        try:
            self.serpapi = SerpApiGlobalIntegration()
        except Exception:
            self.serpapi = None
        try:
            self.web_research = SerperWebResearch()
        except Exception:
            self.web_research = None
        self.version = "2.0.0"
        self.name = "JARVIS"

    def start(self):
        """JARVIS'i başlat"""
        tables = self.db.initialize()
        knowledge_sync = self.knowledge.sync_directory(persist=True)
        return {
            "status": "active",
            "version": self.version,
            "tables_created": tables,
            "knowledge_sources_synced": knowledge_sync["synced_sources"],
            "modules": [
                "DatabaseManager", "MarketProfileManager", "LeadScoringEngine", "PlaybookManager",
                "KnowledgeLibrary", "ConversationMemory",
                "ROICalculator", "PitchScriptGenerator", "RevenueRoadmapEngine",
                "ContractGenerator", "BoardMeetingAI", "SerpApiIntegration", "SerperWebResearch"
            ]
        }

    def scan_area(self, city: str, district: str, sector: str):
        """Bölge taraması başlat"""
        search_input = self.apify.build_search_input(city, district, sector)
        return {"status": "scan_ready", "input": search_input}

    def analyze_lead(self, lead_data: Dict, market_code: Optional[str] = None):
        """Lead analysis with score, ROI, pitch, and playbook."""
        resolved_market = market_code or lead_data.get("market_code") or self.default_market
        score = self.scoring.calculate_score(lead_data, resolved_market)
        sector = lead_data.get("sector", "dental")
        package = score["package_recommendation"]

        roi = self.roi.calculate(sector, package, lead_data.get("monthly_customers", 10), resolved_market)
        scripts = self.pitch.generate(lead_data, sector, score, resolved_market)
        playbook = self.playbooks.get_playbook(sector)

        return {
            "score": score,
            "roi": roi,
            "pitch_scripts": scripts,
            "playbook": playbook.get("name", ""),
            "strategies": playbook.get("strategies", [])[:5],
            "market_profile": self.market_profiles.get_profile(resolved_market),
        }

    def generate_contract(self, client_data: Dict, sector: str, package: str, monthly_fee: float, market_code: Optional[str] = None):
        """Generate a market-aware contract."""
        return self.contracts.generate(client_data, sector, package, monthly_fee, market_code or self.default_market)

    def weekly_board_meeting(self, agency_data: Dict):
        """Haftalık yönetim kurulu raporu"""
        return self.board.generate_report(agency_data)

    def revenue_plan(self, target: float, current: float = 0):
        """Gelir yol haritası"""
        return self.roadmap.generate(target, current)

    def get_market_profile(self, market_code: Optional[str] = None) -> Dict[str, Any]:
        return self.market_profiles.get_profile(market_code or self.default_market)

    def sync_knowledge_library(self) -> Dict[str, Any]:
        return self.knowledge.sync_directory(persist=True)

    def search_knowledge(self, query: str, limit: int = 5) -> Dict[str, Any]:
        return self.knowledge.search(query, limit)

    def deep_research_candidate(self, candidate: Dict[str, Any], market_code: Optional[str] = None) -> Dict[str, Any]:
        if not self.web_research:
            raise RuntimeError("Serper web research is not configured. Add SERPER_API_KEY to enable deep research.")
        lead = self._enrich_candidate(candidate, market_code)
        return self.web_research.research_business(
            business_name=lead.get("name", ""),
            location=lead.get("raw_address", ""),
            website=lead.get("website", ""),
            sector=lead.get("sector", ""),
            market_code=lead.get("market_code", market_code or self.default_market),
        )

    def ensure_conversation_session(
        self,
        session_id: Optional[str] = None,
        market_code: Optional[str] = None,
        mode: str = "chat",
        title: str = "JARVIS Conversation",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.memory.ensure_session(
            session_id=session_id,
            market_code=(market_code or self.default_market).upper(),
            mode=mode,
            title=title,
            metadata=metadata,
        )

    def get_conversation_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.memory.get_session(session_id)

    def get_conversation_messages(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        return self.memory.get_messages(session_id, limit)

    def get_conversation_prompt_history(self, session_id: str, limit: int = 8) -> List[Dict[str, str]]:
        return self.memory.get_prompt_history(session_id, limit)

    def append_conversation_message(
        self,
        session_id: str,
        role: str,
        content: str,
        message_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        return self.memory.add_message(session_id, role, content, message_type, metadata)

    def _knowledge_query_for_candidate(self, lead: Dict[str, Any], intent: Optional[str] = None) -> str:
        enriched = lead if lead.get("gap_scores") else self._enrich_candidate(lead)
        highest_gap = max(enriched.get("gap_scores", {"conversion_gap": 0}), key=enriched.get("gap_scores", {"conversion_gap": 0}).get)
        gap_terms = {
            "acquisition_gap": "offer positioning acquisition website messaging",
            "retention_gap": "retention churn re-engagement loyalty lifecycle",
            "conversion_gap": "sales conversion pain points pitch follow-up",
            "operations_gap": "crm operations workflow pipeline handoff",
            "visibility_gap": "storybrand messaging reviews reputation local seo",
        }
        intent_terms = {
            "invest": "best idea commercial priority decision framework",
            "shortcomings": "pain points diagnostic weaknesses commercial gaps",
            "crm": "crm customer platform retention funnel follow-up",
            "proposal": "offer pricing challenger pitch proposal wow",
        }
        query_parts = [
            intent_terms.get(intent or "", "offer pitch retention messaging"),
            gap_terms.get(highest_gap, ""),
            enriched.get("recommended_service_type", ""),
            enriched.get("platform_type", ""),
            enriched.get("sector", ""),
        ]
        return " ".join(part for part in query_parts if part)

    def _recommended_playbooks(self, lead: Dict[str, Any], intent: Optional[str] = None, limit: int = 2) -> List[Dict[str, Any]]:
        query = self._knowledge_query_for_candidate(lead, intent)
        return self.search_knowledge(query, limit).get("matches", [])

    def _format_playbook_guidance(self, matches: List[Dict[str, Any]], heading: str = "Playbook guidance") -> str:
        if not matches:
            return ""
        lines = [heading + ":"]
        for match in matches:
            insight = match.get("matched_insights", [{}])[0].get("content") or match.get("summary", "")
            lines.append(f"- {match['title']}: {insight}")
        return "\n".join(lines)

    def _resolve_market_code(
        self,
        explicit_market_code: Optional[str] = None,
        selected_lead: Optional[Dict] = None,
        candidate_context: Optional[List[Dict]] = None,
        command: Optional[str] = None,
    ) -> str:
        if explicit_market_code:
            return explicit_market_code.upper()
        if selected_lead and selected_lead.get("market_code"):
            return str(selected_lead["market_code"]).upper()
        if candidate_context:
            first = candidate_context[0]
            if first.get("market_code"):
                return str(first["market_code"]).upper()
        if command:
            return self._infer_country_code("", command)
        return self.default_market

    def _json_load_if_needed(self, value: Any, fallback: Any) -> Any:
        if value in (None, ""):
            return fallback
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value)
        except Exception:
            return fallback

    def _hydrate_candidate_decision_row(self, row: Optional[Dict]) -> Optional[Dict[str, Any]]:
        if not row:
            return None
        record = dict(row)
        record["proposal_recommended"] = bool(record.get("proposal_recommended"))
        record["candidate_snapshot"] = self._json_load_if_needed(record.get("candidate_snapshot"), {})
        record["analysis_snapshot"] = self._json_load_if_needed(record.get("analysis_snapshot"), {})
        return record

    def compare_candidates(self, candidates: List[Dict], market_code: Optional[str] = None) -> Dict[str, Any]:
        ranked = self._rank_candidates(candidates, market_code)
        if not ranked:
            return {
                "market_profile": self.get_market_profile(market_code),
                "ranked_candidates": [],
                "summary": "No candidates are loaded yet.",
                "top_recommendation": None,
                "recommended_playbooks": [],
            }

        leader = ranked[0]
        playbooks = self._recommended_playbooks(leader, "invest", limit=2)
        summary = (
            f"{leader['name']} is the strongest current target because {leader['fit_summary'].lower()} "
            f"and its proposal readiness is {leader['proposal_readiness'].lower()}."
        )
        if playbooks:
            summary += " Strategy anchors: " + ", ".join(match["title"] for match in playbooks) + "."
        return {
            "market_profile": self.get_market_profile(market_code),
            "ranked_candidates": ranked,
            "summary": summary,
            "top_recommendation": {
                "lead_key": leader["lead_key"],
                "name": leader["name"],
                "investment_score": leader["investment_score"],
                "proposal_readiness": leader["proposal_readiness"],
                "recommended_service": leader["recommended_service_type"],
            },
            "recommended_playbooks": playbooks,
        }

    def build_proposal_brief(self, candidate: Dict, market_code: Optional[str] = None) -> Dict[str, Any]:
        lead = self._enrich_candidate(candidate, market_code)
        playbooks = self._recommended_playbooks(lead, "proposal", limit=3)
        return {
            "lead_key": lead["lead_key"],
            "target_business": lead["name"],
            "market_profile": self.get_market_profile(lead["market_code"]),
            "recommended_platform_type": lead["platform_type"],
            "recommended_service_type": lead["recommended_service_type"],
            "recommended_delivery_shape": lead["recommended_delivery_shape"],
            "proposal_readiness": lead["proposal_readiness"],
            "proposal_recommendation": lead["proposal_recommendation"],
            "fit_summary": lead["fit_summary"],
            "risk_summary": lead["risk_summary"],
            "commercial_priority": lead["commercial_priority"],
            "problem_statement": lead["problem_statement"],
            "expected_business_outcome": lead["expected_business_outcome"],
            "proposed_scope": lead["proposed_scope"],
            "decision_trace": lead["decision_trace"],
            "recommended_playbooks": playbooks,
            "playbook_guidance": self._format_playbook_guidance(playbooks, "Recommended playbooks"),
        }

    def get_candidate_decision(self, lead_key: str) -> Optional[Dict[str, Any]]:
        row = self.db.fetch_one(
            "SELECT * FROM candidate_decisions WHERE lead_key = ?",
            (lead_key,),
        )
        return self._hydrate_candidate_decision_row(row)

    def get_candidate_decisions(self, limit: int = 50) -> List[Dict[str, Any]]:
        rows = self.db.fetch_all(
            "SELECT * FROM candidate_decisions ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        )
        return [self._hydrate_candidate_decision_row(row) for row in rows]

    def save_candidate_decision(
        self,
        candidate: Dict[str, Any],
        decision_status: str = "monitor",
        recommended_platform: Optional[str] = None,
        recommended_service: Optional[str] = None,
        proposal_recommended: Optional[bool] = None,
        owner: str = "",
        next_action: str = "",
        follow_up_date: Optional[str] = None,
        confidence: int = 60,
        operator_notes: str = "",
        market_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        lead = self._enrich_candidate(candidate, market_code)
        existing = self.get_candidate_decision(lead["lead_key"]) or {}

        payload = {
            "lead_key": lead["lead_key"],
            "lead_name": lead["name"],
            "raw_address": lead.get("raw_address", ""),
            "sector": lead.get("sector", ""),
            "market_code": lead["market_code"],
            "decision_status": decision_status or existing.get("decision_status") or "monitor",
            "recommended_platform": recommended_platform or existing.get("recommended_platform") or lead["platform_type"],
            "recommended_service": recommended_service or existing.get("recommended_service") or lead["recommended_service_type"],
            "proposal_recommended": int(
                proposal_recommended
                if proposal_recommended is not None
                else existing.get("proposal_recommended", lead["proposal_readiness"] == "Ready now")
            ),
            "proposal_readiness": lead["proposal_readiness"],
            "commercial_priority": lead["commercial_priority"],
            "owner": owner if owner != "" else existing.get("owner", ""),
            "next_action": next_action if next_action != "" else existing.get("next_action", ""),
            "follow_up_date": follow_up_date if follow_up_date is not None else existing.get("follow_up_date"),
            "confidence": max(0, min(100, int(confidence if confidence is not None else existing.get("confidence", 60)))),
            "operator_notes": operator_notes if operator_notes != "" else existing.get("operator_notes", ""),
            "candidate_snapshot": json.dumps(candidate, ensure_ascii=False),
            "analysis_snapshot": json.dumps(lead, ensure_ascii=False),
        }

        self.db.execute(
            """
            INSERT INTO candidate_decisions (
                lead_key, lead_name, raw_address, sector, market_code, decision_status,
                recommended_platform, recommended_service, proposal_recommended,
                proposal_readiness, commercial_priority, owner, next_action,
                follow_up_date, confidence, operator_notes, candidate_snapshot,
                analysis_snapshot, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT (lead_key) DO UPDATE SET
                lead_name = EXCLUDED.lead_name,
                raw_address = EXCLUDED.raw_address,
                sector = EXCLUDED.sector,
                market_code = EXCLUDED.market_code,
                decision_status = EXCLUDED.decision_status,
                recommended_platform = EXCLUDED.recommended_platform,
                recommended_service = EXCLUDED.recommended_service,
                proposal_recommended = EXCLUDED.proposal_recommended,
                proposal_readiness = EXCLUDED.proposal_readiness,
                commercial_priority = EXCLUDED.commercial_priority,
                owner = EXCLUDED.owner,
                next_action = EXCLUDED.next_action,
                follow_up_date = EXCLUDED.follow_up_date,
                confidence = EXCLUDED.confidence,
                operator_notes = EXCLUDED.operator_notes,
                candidate_snapshot = EXCLUDED.candidate_snapshot,
                analysis_snapshot = EXCLUDED.analysis_snapshot,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                payload["lead_key"],
                payload["lead_name"],
                payload["raw_address"],
                payload["sector"],
                payload["market_code"],
                payload["decision_status"],
                payload["recommended_platform"],
                payload["recommended_service"],
                payload["proposal_recommended"],
                payload["proposal_readiness"],
                payload["commercial_priority"],
                payload["owner"],
                payload["next_action"],
                payload["follow_up_date"],
                payload["confidence"],
                payload["operator_notes"],
                payload["candidate_snapshot"],
                payload["analysis_snapshot"],
            ),
        )
        return self.get_candidate_decision(payload["lead_key"]) or {}

    def update_candidate_workflow(self, lead_key: str, **updates: Any) -> Optional[Dict[str, Any]]:
        existing = self.get_candidate_decision(lead_key)
        if not existing:
            return None
        candidate = existing.get("candidate_snapshot") or existing.get("analysis_snapshot") or {"lead_key": lead_key}
        return self.save_candidate_decision(
            candidate=candidate,
            decision_status=updates.get("decision_status", existing.get("decision_status", "monitor")),
            recommended_platform=updates.get("recommended_platform", existing.get("recommended_platform")),
            recommended_service=updates.get("recommended_service", existing.get("recommended_service")),
            proposal_recommended=updates.get("proposal_recommended", existing.get("proposal_recommended")),
            owner=updates.get("owner", existing.get("owner", "")),
            next_action=updates.get("next_action", existing.get("next_action", "")),
            follow_up_date=updates.get("follow_up_date", existing.get("follow_up_date")),
            confidence=updates.get("confidence", existing.get("confidence", 60)),
            operator_notes=updates.get("operator_notes", existing.get("operator_notes", "")),
            market_code=updates.get("market_code", existing.get("market_code", self.default_market)),
        )

    def _lead_key(self, lead: Dict) -> str:
        candidate_name = lead.get("name") or lead.get("business_name") or ""
        raw = "|".join(
            str(value)
            for value in (
                candidate_name,
                lead.get("raw_address", ""),
                lead.get("latitude", ""),
                lead.get("longitude", ""),
                lead.get("phone", ""),
                lead.get("website", ""),
            )
        )
        return hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]

    def _detect_strategy_intent(self, command: str) -> Optional[str]:
        lower = command.lower()
        for intent, keywords in self.STRATEGY_KEYWORDS.items():
            if any(keyword in lower for keyword in keywords):
                return intent
        return None

    def _assess_gap_scores(self, lead: Dict[str, Any]) -> Dict[str, int]:
        rating = float(lead.get("rating", 0) or 0)
        review_count = int(lead.get("review_count", 0) or 0)
        has_website = bool(lead.get("website") or lead.get("has_website"))
        has_phone = bool(lead.get("phone"))
        sector = (lead.get("sector") or "").lower()

        acquisition_gap = 55
        retention_gap = 45
        conversion_gap = 50
        operations_gap = 40
        visibility_gap = 50

        if not has_website:
            acquisition_gap += 25
            conversion_gap += 18
            operations_gap += 10
        else:
            acquisition_gap -= 12
            conversion_gap -= 8

        if not has_phone:
            conversion_gap += 10
            operations_gap += 8
        else:
            conversion_gap -= 4

        if review_count < 25:
            visibility_gap += 22
        elif review_count < 100:
            visibility_gap += 10
        else:
            visibility_gap -= 10
            retention_gap += 8

        if rating and rating < 4.2:
            visibility_gap += 18
        elif rating >= 4.7:
            visibility_gap -= 12
            retention_gap += 6

        if any(token in sector for token in ("restaurant", "cafe", "coffee", "gym", "dental")):
            retention_gap += 10
        if sector in ("law_firm", "accounting", "construction", "real_estate"):
            operations_gap += 12
            conversion_gap += 6

        return {
            "acquisition_gap": max(0, min(100, acquisition_gap)),
            "retention_gap": max(0, min(100, retention_gap)),
            "conversion_gap": max(0, min(100, conversion_gap)),
            "operations_gap": max(0, min(100, operations_gap)),
            "visibility_gap": max(0, min(100, visibility_gap)),
        }

    def _infer_platform_strategy(self, lead: Dict[str, Any], gap_scores: Dict[str, int]) -> Dict[str, str]:
        sector = (lead.get("sector") or "").lower()
        has_website = bool(lead.get("website") or lead.get("has_website"))
        highest_gap = max(gap_scores, key=gap_scores.get)

        if not has_website:
            return {
                "platform_type": "Owned funnel and customer capture platform",
                "why": "The business still depends too heavily on third-party discovery, so the first move is an owned website and lead capture layer.",
            }

        if highest_gap == "retention_gap" and any(token in sector for token in ("restaurant", "cafe", "coffee", "gym", "dental")):
            return {
                "platform_type": "Customer retention and nurture platform",
                "why": "Repeat purchases, recalls, and loyalty mechanics are likely the fastest commercial win for this sector.",
            }

        if highest_gap == "operations_gap":
            return {
                "platform_type": "Delivery workflow and CRM operations layer",
                "why": "The business most likely needs cleaner handoffs, follow-up visibility, and day-to-day workflow discipline.",
            }

        return {
            "platform_type": "Sales CRM and follow-up automation",
            "why": "The next win is tighter lead capture, response handling, and pipeline visibility rather than a heavy bespoke platform.",
        }

    def _recommend_service(self, lead: Dict[str, Any], gap_scores: Dict[str, int]) -> Dict[str, str]:
        highest_gap = max(gap_scores, key=gap_scores.get)
        if not (lead.get("website") or lead.get("has_website")):
            return {
                "service_type": "Owned funnel launch",
                "delivery_shape": "Landing pages, forms, analytics, and CRM routing",
            }
        if highest_gap == "visibility_gap":
            return {
                "service_type": "Visibility and reputation engine",
                "delivery_shape": "Review growth, local SEO, and social proof workflow",
            }
        if highest_gap == "retention_gap":
            return {
                "service_type": "Retention and reactivation system",
                "delivery_shape": "Lifecycle campaigns, offer automation, and repeat-visit workflows",
            }
        if highest_gap == "operations_gap":
            return {
                "service_type": "Pipeline and workflow operating system",
                "delivery_shape": "CRM, task orchestration, reporting, and team follow-up rules",
            }
        return {
            "service_type": "CRM and follow-up optimisation",
            "delivery_shape": "Lead routing, sales stages, reminders, and visibility dashboards",
        }

    def _enrich_candidate(self, lead: Dict, market_code: Optional[str] = None) -> Dict[str, Any]:
        enriched = dict(lead)
        enriched["name"] = lead.get("name") or lead.get("business_name") or "Unknown business"
        enriched["lead_key"] = self._lead_key(lead)
        enriched["market_code"] = self._resolve_market_code(market_code, lead)
        profile = self.get_market_profile(enriched["market_code"])

        rating = float(lead.get("rating", 0) or 0)
        review_count = int(lead.get("review_count", 0) or 0)
        has_website = bool(lead.get("website") or lead.get("has_website"))
        has_phone = bool(lead.get("phone"))
        base_score = int(lead.get("score", 0) or 0)
        gap_scores = self._assess_gap_scores(enriched)
        service = self._recommend_service(enriched, gap_scores)

        strengths: List[str] = []
        shortcomings: List[str] = []

        if rating >= 4.7:
            strengths.append(f"Strong reputation at {rating:.1f} stars.")
        elif rating >= 4.4:
            strengths.append(f"Good local reputation at {rating:.1f} stars.")
        elif rating > 0:
            shortcomings.append(f"Reputation can be improved from {rating:.1f} stars.")

        if review_count >= 250:
            strengths.append(f"High review volume with {review_count} reviews.")
        elif review_count >= 75:
            strengths.append(f"Solid social proof with {review_count} reviews.")
        else:
            shortcomings.append("Limited review volume weakens social proof.")

        if has_website:
            strengths.append("Has a website, so CRM and automation can attach to an owned funnel.")
        else:
            shortcomings.append("No owned website detected, so lead capture is dependent on third-party platforms.")

        if has_phone:
            strengths.append("Phone contact is visible for direct outreach.")
        else:
            shortcomings.append("No phone number surfaced in search results.")

        investment_score = base_score or 55
        if not has_website:
            investment_score += 18
        if rating >= 4.7:
            investment_score += 10
        elif rating >= 4.4:
            investment_score += 6
        elif 0 < rating < 4.2:
            investment_score -= 8

        if review_count >= 250:
            investment_score += 10
        elif review_count >= 100:
            investment_score += 6
        elif review_count < 25:
            investment_score -= 5

        if has_phone:
            investment_score += 4

        investment_score += round(gap_scores["retention_gap"] * 0.06)
        investment_score += round(gap_scores["visibility_gap"] * 0.04)
        investment_score = max(0, min(100, investment_score))

        if investment_score >= 78:
            invest_recommendation = "High-priority investment candidate"
            proposal_readiness = "Ready now"
            proposal_recommendation = "Submit a discovery proposal now."
            commercial_priority = "High"
        elif investment_score >= 62:
            invest_recommendation = "Promising candidate worth qualifying"
            proposal_readiness = "Needs qualification"
            proposal_recommendation = "Submit a proposal after a short qualification call."
            commercial_priority = "Medium"
        else:
            invest_recommendation = "Lower-priority candidate for now"
            proposal_readiness = "Monitor"
            proposal_recommendation = "Do not rush a proposal; monitor or qualify later."
            commercial_priority = "Low"

        platform = self._infer_platform_strategy(enriched, gap_scores)
        decision_trace = [
            f"Investment score {investment_score}/100 based on reviews, contactability, and digital ownership.",
            f"Top gap area: {max(gap_scores, key=gap_scores.get).replace('_', ' ')}.",
            f"Recommended service: {service['service_type']}.",
        ]
        fit_summary = (
            f"{enriched['name']} shows enough traction to justify {service['service_type'].lower()} because "
            f"{strengths[0].lower() if strengths else 'there is a clear commercial gap to close'}"
        )
        risk_summary = shortcomings[0] if shortcomings else "No major delivery risk is visible from public data alone."
        problem_statement = (
            f"{enriched['name']} appears to have the strongest opportunity around "
            f"{max(gap_scores, key=gap_scores.get).replace('_', ' ')} and follow-up discipline."
        )
        expected_business_outcome = (
            "Improve lead capture quality, reduce response leakage, and create a clearer path to repeat revenue."
        )
        proposed_scope = [
            platform["platform_type"],
            service["delivery_shape"],
            "Operator reporting, decision tracking, and proposal handoff brief",
        ]

        enriched.update(
            {
                "investment_score": investment_score,
                "invest_recommendation": invest_recommendation,
                "investment_priority": commercial_priority,
                "proposal_recommendation": proposal_recommendation,
                "proposal_readiness": proposal_readiness,
                "shortcomings": shortcomings,
                "strengths": strengths,
                "platform_type": platform["platform_type"],
                "platform_reason": platform["why"],
                "recommended_service_type": service["service_type"],
                "recommended_delivery_shape": service["delivery_shape"],
                "gap_scores": gap_scores,
                "decision_trace": decision_trace,
                "fit_summary": fit_summary,
                "risk_summary": risk_summary,
                "commercial_priority": commercial_priority,
                "opportunity_summary": strengths[0] if strengths else "Moderate opportunity.",
                "problem_statement": problem_statement,
                "expected_business_outcome": expected_business_outcome,
                "proposed_scope": proposed_scope,
                "market_profile": {
                    "market_code": profile["market_code"],
                    "market_name": profile["market_name"],
                    "currency_code": profile["currency_code"],
                    "currency_symbol": profile["currency_symbol"],
                    "presentation_locale": profile["presentation_locale"],
                },
            }
        )
        return enriched

    def _rank_candidates(self, leads: List[Dict], market_code: Optional[str] = None) -> List[Dict]:
        enriched = [self._enrich_candidate(lead, market_code) for lead in leads]
        return sorted(
            enriched,
            key=lambda lead: (
                lead.get("investment_score", 0),
                lead.get("rating", 0),
                lead.get("review_count", 0),
            ),
            reverse=True,
        )

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

        ranked = self._rank_candidates(filtered, request.get("country_code"))
        selected = ranked[:request["count"]]

        lines = [
            f"I found {len(selected)} {request['business_type']} results in {request['location']}."
        ]
        if threshold is not None:
            lines[0] += f" Prioritised ratings of {threshold:.1f}+ where available."
        lines.append("The map can now plot these candidates. Hover markers for details and click one to focus the chat on it.")

        for index, lead in enumerate(selected, start=1):
            rating = lead.get("rating", 0)
            rating_text = f"{rating:.1f}★" if rating else "No rating"
            reviews = lead.get("review_count", 0)
            review_text = f"{reviews} reviews" if reviews else "review count unavailable"
            line = (
                f"{index}. {lead.get('name', 'Unknown')} — {rating_text} ({review_text})"
                f" | Investment score {lead.get('investment_score', 0)}/100"
            )

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

    def _handle_business_search(self, request: Dict) -> Dict[str, Any]:
        if not self.serpapi:
            raise RuntimeError("SerpApi is not configured. Add SERPAPI_API_KEY to enable live business search.")
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

        filtered = leads
        threshold = request.get("rating_threshold")
        if threshold is not None:
            matching = [lead for lead in leads if lead.get("rating", 0) >= threshold]
            if matching:
                filtered = matching

        ranked = self._rank_candidates(filtered, request["country_code"])
        selected = ranked[:request["count"]]
        comparison = self.compare_candidates(selected, request["country_code"])

        return {
            "response": self._format_business_search_response(request, selected),
            "action": "plot_map_results",
            "leads": selected,
            "candidate_count": len(selected),
            "selected_lead": selected[0] if selected else None,
            "comparison": comparison,
            "market_profile": self.get_market_profile(request["country_code"]),
            "suggested_questions": [
                "Which one should we invest in first?",
                "What are the shortcomings of each?",
                "Should we build a CRM or customer platform here?",
                "Which one deserves a proposal now?",
            ],
        }

    def _format_candidate_snapshot(self, lead: Dict) -> str:
        shortcomings = lead.get("shortcomings") or ["No major gaps flagged yet."]
        return (
            f"{lead.get('name', 'This business')} has an investment score of {lead.get('investment_score', 0)}/100. "
            f"Recommendation: {lead.get('invest_recommendation', 'Review manually')}. "
            f"Main shortcoming: {shortcomings[0]}. "
            f"Recommended platform: {lead.get('platform_type', 'TBD')}."
        )

    def _analyze_selected_candidate(self, command: str, selected_lead: Dict) -> str:
        lead = self._enrich_candidate(selected_lead)
        intent = self._detect_strategy_intent(command)
        playbook_note = self._format_playbook_guidance(
            self._recommended_playbooks(lead, intent or "invest", limit=2)
        )

        if intent == "invest":
            response = (
                f"{lead['name']} is a {lead['invest_recommendation'].lower()} with an investment score of "
                f"{lead['investment_score']}/100. The strongest signals are "
                f"{'; '.join(lead['strengths'][:2]) or 'limited but workable traction'}"
            )
            return f"{response}\n{playbook_note}" if playbook_note else response

        if intent == "shortcomings":
            response = (
                f"{lead['name']} shortcomings: " +
                "; ".join(lead["shortcomings"][:3])
            )
            return f"{response}\n{playbook_note}" if playbook_note else response

        if intent == "crm":
            response = (
                f"For {lead['name']}, I would start with a {lead['platform_type'].lower()}. "
                f"The recommended service is {lead['recommended_service_type'].lower()}. "
                f"Reason: {lead['platform_reason']}"
            )
            return f"{response}\n{playbook_note}" if playbook_note else response

        if intent == "proposal":
            response = (
                f"For {lead['name']}, my proposal recommendation is: {lead['proposal_recommendation']} "
                f"Fit summary: {lead['fit_summary']} Risk: {lead['risk_summary']}"
            )
            return f"{response}\n{playbook_note}" if playbook_note else response

        response = (
            self._format_candidate_snapshot(lead) + " Ask me about investment priority, shortcomings, "
            "CRM/platform choice, or proposal readiness for this selected lead."
        )
        return f"{response}\n{playbook_note}" if playbook_note else response

    def _analyze_candidate_pool(self, command: str, candidate_context: List[Dict]) -> str:
        if not candidate_context:
            return "I need a set of plotted candidates first. Ask me to find businesses, then I can compare them."

        ranked = self._rank_candidates(candidate_context)
        intent = self._detect_strategy_intent(command)
        top = ranked[: min(5, len(ranked))]
        playbook_note = self._format_playbook_guidance(
            self._recommended_playbooks(top[0], intent or "invest", limit=2)
        )

        if intent == "shortcomings":
            lines = ["Shortcomings across the current options:"]
            for idx, lead in enumerate(top, start=1):
                items = "; ".join(lead["shortcomings"][:2]) if lead["shortcomings"] else "No major gap flagged"
                lines.append(f"{idx}. {lead['name']} — {items}")
            response = "\n".join(lines)
            return f"{response}\n{playbook_note}" if playbook_note else response

        if intent == "crm":
            lines = ["Platform recommendation across the current options:"]
            for idx, lead in enumerate(top, start=1):
                lines.append(
                    f"{idx}. {lead['name']} — {lead['platform_type']} / {lead['recommended_service_type']}: "
                    f"{lead['platform_reason']}"
                )
            response = "\n".join(lines)
            return f"{response}\n{playbook_note}" if playbook_note else response

        if intent == "proposal":
            lines = ["Proposal priority across the current options:"]
            for idx, lead in enumerate(top, start=1):
                lines.append(
                    f"{idx}. {lead['name']} — {lead['proposal_recommendation']} "
                    f"(investment score {lead['investment_score']}/100, readiness {lead['proposal_readiness']})"
                )
            response = "\n".join(lines)
            return f"{response}\n{playbook_note}" if playbook_note else response

        best = top[0]
        runners_up = ", ".join(f"{lead['name']} ({lead['investment_score']}/100)" for lead in top[1:3])
        response = (
            f"My first investment priority is {best['name']} at {best['investment_score']}/100 because "
            f"{best['fit_summary'].lower()}"
        )
        if runners_up:
            response += f" Next in line: {runners_up}."
        response += " Ask me about shortcomings, CRM/platform choice, or proposal readiness if you want the next decision layer."
        return f"{response}\n{playbook_note}" if playbook_note else response

    def _knowledge_chat_response(self, command: str) -> Optional[str]:
        lower = command.lower()
        if not any(keyword in lower for keyword in self.KNOWLEDGE_KEYWORDS):
            return None

        result = self.search_knowledge(command, limit=3)
        matches = result.get("matches", [])
        if not matches:
            return None

        lines = ["Relevant playbooks from the knowledge library:"]
        for index, match in enumerate(matches, start=1):
            line = f"{index}. {match['title']}"
            if match.get("author"):
                line += f" by {match['author']}"
            if match.get("workflow_stage"):
                line += f" [{match['workflow_stage']}]"
            line += f" — {match['summary']}"
            lines.append(line)
            for insight in match.get("matched_insights", [])[:2]:
                lines.append(f"   - {insight['content']}")

        lines.append(
            "For copyrighted books, keep the system on structured summaries, notes, and extracted frameworks you are allowed to use. "
            "Do not rely on raw unlicensed book files as the retrieval corpus."
        )
        return "\n".join(lines)

    def _general_chat_fallback(
        self,
        command: str,
        selected_lead: Optional[Dict] = None,
        candidate_context: Optional[List[Dict]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        if selected_lead:
            selected_note = self._format_candidate_snapshot(self._enrich_candidate(selected_lead))
            return (
                f"{selected_note} You can ask whether to invest, what the shortcomings are, "
                "which platform fits, or whether to send a proposal."
            )

        if candidate_context:
            return self._analyze_candidate_pool("which one should we invest in", candidate_context)

        knowledge_response = self._knowledge_chat_response(command)
        if knowledge_response:
            return knowledge_response

        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if api_key:
            try:
                client = openai.OpenAI(api_key=api_key)
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are JARVIS, an AI agency assistant. Answer briefly and directly. "
                            "You can help with local business discovery, lead analysis, ROI planning, "
                            "pitch scripts, contracts, board reports, and revenue plans. "
                            "If a request is outside those capabilities, say so and suggest a nearby supported action."
                        ),
                    },
                ]
                for item in (conversation_history or [])[-8:]:
                    role = item.get("role")
                    content = str(item.get("content", "")).strip()
                    if role in {"user", "assistant"} and content:
                        messages.append({"role": role, "content": content})
                messages.append({"role": "user", "content": command})
                response = client.chat.completions.create(
                    model=os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
                    messages=messages,
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

    def handle_command(
        self,
        command: str,
        selected_lead: Optional[Dict] = None,
        candidate_context: Optional[List[Dict]] = None,
        market_code: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Structured natural-language command handling for chat and map workflows."""
        cmd = command.lower().strip()
        candidate_context = candidate_context or []
        resolved_market = self._resolve_market_code(market_code, selected_lead, candidate_context, command)

        business_search = self._extract_business_search(command)
        if business_search:
            business_search["country_code"] = resolved_market or business_search["country_code"]
            try:
                return self._handle_business_search(business_search)
            except Exception as exc:
                return {
                    "response": (
                        "I understood that as a business search, but the live lookup failed. "
                        f"Details: {exc}"
                    ),
                    "action": None,
                    "leads": [],
                    "market_profile": self.get_market_profile(resolved_market),
                }

        if selected_lead and (
            self._detect_strategy_intent(command) or any(token in cmd for token in ("this one", "this option", "selected"))
        ):
            enriched = self._enrich_candidate(selected_lead, resolved_market)
            return {
                "response": self._analyze_selected_candidate(command, enriched),
                "action": "focus_selected_lead",
                "selected_lead": enriched,
                "leads": self._rank_candidates(candidate_context, resolved_market),
                "proposal_brief": self.build_proposal_brief(enriched, resolved_market),
                "market_profile": self.get_market_profile(resolved_market),
            }

        if candidate_context and (
            self._detect_strategy_intent(command) or any(token in cmd for token in ("these", "them", "options", "which one"))
        ):
            ranked = self._rank_candidates(candidate_context, resolved_market)
            return {
                "response": self._analyze_candidate_pool(command, ranked),
                "action": "candidate_pool_analysis",
                "selected_lead": selected_lead,
                "leads": ranked,
                "comparison": self.compare_candidates(ranked, resolved_market),
                "market_profile": self.get_market_profile(resolved_market),
            }

        if "tara" in cmd or "scan" in cmd:
            return {"response": "Opening a fresh market scan.", "action": "open_scan_modal", "leads": [], "market_profile": self.get_market_profile(resolved_market)}
        if "analiz" in cmd or "score" in cmd:
            return {"response": "Preparing a structured candidate analysis.", "action": None, "leads": [], "market_profile": self.get_market_profile(resolved_market)}
        if "pitch" in cmd or "script" in cmd:
            return {"response": "Preparing outreach messaging.", "action": None, "leads": [], "market_profile": self.get_market_profile(resolved_market)}
        if "sözleşme" in cmd or "contract" in cmd:
            return {"response": "Preparing a market-aware contract draft.", "action": None, "leads": [], "market_profile": self.get_market_profile(resolved_market)}
        if "toplantı" in cmd or "board" in cmd:
            return {"response": "Preparing an operator review summary.", "action": None, "leads": [], "market_profile": self.get_market_profile(resolved_market)}
        if "hedef" in cmd or "roadmap" in cmd:
            return {"response": "Building a revenue roadmap.", "action": None, "leads": [], "market_profile": self.get_market_profile(resolved_market)}
        if "roi" in cmd:
            return {"response": "Calculating ROI using the current market profile.", "action": None, "leads": [], "market_profile": self.get_market_profile(resolved_market)}

        return {
            "response": self._general_chat_fallback(command, selected_lead, candidate_context, conversation_history),
            "action": None,
            "selected_lead": self._enrich_candidate(selected_lead, resolved_market) if selected_lead else None,
            "leads": self._rank_candidates(candidate_context, resolved_market) if candidate_context else [],
            "comparison": self.compare_candidates(candidate_context, resolved_market) if candidate_context else None,
            "market_profile": self.get_market_profile(resolved_market),
        }

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
        return self.default_market

    def process_command(self, command: str) -> str:
        """Doğal dil komut işleme"""
        return self.handle_command(command).get("response", "")


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
