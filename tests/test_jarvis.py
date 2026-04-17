#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS AI Agency OS — Test Suite
==================================
Tüm 10 modülü ve API endpoint'lerini doğrulayan pytest testleri.

Çalıştırma:
    cd jarvis-Investment-Support-Agent
    pytest tests/ -v
"""

import sys
import os
import json
import pytest

# Root dizini path'e ekle (modüller root'ta)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis_core import (
    JARVIS,
    DatabaseManager,
    LeadScoringEngine,
    PlaybookManager,
    ROICalculator,
    PitchScriptGenerator,
    RevenueRoadmapEngine,
    ContractGenerator,
    BoardMeetingAI,
)


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture(scope="session")
def jarvis():
    """In-memory JARVIS instance for the entire test session."""
    j = JARVIS(db_path=":memory:")
    j.start()
    return j


@pytest.fixture
def sample_lead():
    return {
        "business_name": "Sydney Dental Spa",
        "sector": "dental",
        "city": "Sydney",
        "district": "CBD",
        "contact_person": "Dr. Emma",
        "phone": "+61 2 9999 0000",
        "email": "info@sydneydentalspa.com.au",
        "website": "https://sydneydentalspa.com.au",
        "has_website": True,
        "has_social_media": True,
        "google_maps_listed": True,
        "google_rating": 4.8,
        "review_count": 342,
        "employee_count": 12,
        "monthly_customers": 80,
        "multiple_locations": False,
        "responded_before": False,
        "visited_website": False,
        "opened_email": False,
        "social_active": True,
    }


@pytest.fixture
def sample_lead_low_score():
    """A lead with minimal information — should score low."""
    return {
        "business_name": "Small Shop",
        "sector": "retail",
        "has_website": False,
        "has_social_media": False,
        "google_maps_listed": False,
        "google_rating": 0,
        "review_count": 0,
        "employee_count": 1,
        "monthly_customers": 2,
    }


# ============================================================
# 1. DATABASE MANAGER
# ============================================================

class TestDatabaseManager:
    def test_initialization_creates_15_tables(self):
        db = DatabaseManager(":memory:")
        table_count = db.initialize()
        assert table_count == 15, f"Expected 15 tables, got {table_count}"

    def test_execute_and_fetch(self):
        db = DatabaseManager(":memory:")
        db.initialize()
        db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?)",
            ("test_key", "test_value")
        )
        row = db.fetch_one("SELECT value FROM settings WHERE key = ?", ("test_key",))
        assert row is not None
        assert row["value"] == "test_value"

    def test_fetch_all_returns_list(self):
        db = DatabaseManager(":memory:")
        db.initialize()
        results = db.fetch_all("SELECT * FROM leads")
        assert isinstance(results, list)


# ============================================================
# 2. LEAD SCORING ENGINE
# ============================================================

class TestLeadScoringEngine:
    def test_score_returns_dict(self, sample_lead):
        engine = LeadScoringEngine()
        result = engine.calculate_score(sample_lead)
        assert isinstance(result, dict)

    def test_score_within_range(self, sample_lead):
        engine = LeadScoringEngine()
        result = engine.calculate_score(sample_lead)
        assert 0 <= result["total_score"] <= 100

    def test_high_quality_lead_scores_high(self, sample_lead):
        engine = LeadScoringEngine()
        result = engine.calculate_score(sample_lead)
        assert result["total_score"] >= 50, "A fully furnished lead should score >= 50"

    def test_empty_lead_scores_low(self, sample_lead_low_score):
        engine = LeadScoringEngine()
        result = engine.calculate_score(sample_lead_low_score)
        assert result["total_score"] < 40

    def test_package_recommendation_is_valid(self, sample_lead):
        engine = LeadScoringEngine()
        result = engine.calculate_score(sample_lead)
        assert result["package_recommendation"] in ["Premium", "Professional", "Starter", "Nurture"]

    def test_score_breakdown_has_5_categories(self, sample_lead):
        engine = LeadScoringEngine()
        result = engine.calculate_score(sample_lead)
        expected_keys = {"online_presence", "reviews_reputation", "business_size", "sector_ai_need", "engagement"}
        assert set(result["breakdown"].keys()) == expected_keys

    def test_priority_field_present(self, sample_lead):
        engine = LeadScoringEngine()
        result = engine.calculate_score(sample_lead)
        assert "priority" in result
        assert result["priority"]  # not empty


# ============================================================
# 3. PLAYBOOK MANAGER
# ============================================================

class TestPlaybookManager:
    def test_get_all_sectors_returns_list(self):
        pm = PlaybookManager()
        sectors = pm.get_all_sectors()
        assert isinstance(sectors, list)
        assert len(sectors) >= 6

    def test_dental_playbook_exists(self):
        pm = PlaybookManager()
        pb = pm.get_playbook("dental")
        assert pb
        assert "name" in pb
        assert "strategies" in pb

    def test_strategies_are_nonempty(self):
        pm = PlaybookManager()
        strategies = pm.get_strategies("dental")
        assert isinstance(strategies, list)
        assert len(strategies) >= 5

    def test_unknown_sector_returns_empty(self):
        pm = PlaybookManager()
        pb = pm.get_playbook("nonexistent_sector_xyz")
        assert pb == {}

    def test_all_playbooks_have_required_fields(self):
        pm = PlaybookManager()
        required = {"name", "strategies", "duration_months", "target_roi"}
        for sector in pm.get_all_sectors():
            pb = pm.get_playbook(sector)
            assert required.issubset(pb.keys()), f"{sector} missing fields"


# ============================================================
# 4. ROI CALCULATOR
# ============================================================

class TestROICalculator:
    def test_returns_dict(self):
        roi = ROICalculator()
        result = roi.calculate("dental", "Premium")
        assert isinstance(result, dict)

    def test_roi_positive_for_premium_dental(self):
        roi = ROICalculator()
        result = roi.calculate("dental", "Premium", 30)
        assert result["roi_percent"] > 0

    def test_monthly_cost_matches_package(self):
        roi = ROICalculator()
        result = roi.calculate("dental", "Starter", 10)
        assert result["monthly_cost"] == ROICalculator.PACKAGE_PRICES["Starter"]["avg"]

    def test_all_packages_dental(self):
        roi = ROICalculator()
        for pkg in ["Starter", "Professional", "Premium"]:
            result = roi.calculate("dental", pkg)
            assert "roi_percent" in result
            assert "payback_days" in result

    def test_all_sectors_calculate(self):
        roi = ROICalculator()
        for sector in ["dental", "law_firm", "accounting", "gym", "auto_gallery", "construction"]:
            result = roi.calculate(sector, "Professional")
            assert result["monthly_cost"] > 0


# ============================================================
# 5. PITCH SCRIPT GENERATOR
# ============================================================

class TestPitchScriptGenerator:
    def test_generates_4_scripts(self, sample_lead):
        psg = PitchScriptGenerator()
        score_data = {"package_recommendation": "Premium", "price_range": "15.000-25.000 TL/ay", "total_score": 85}
        result = psg.generate(sample_lead, "dental", score_data)
        assert isinstance(result, dict)
        assert len(result) == 4

    def test_all_script_types_present(self, sample_lead):
        psg = PitchScriptGenerator()
        score_data = {"package_recommendation": "Professional", "price_range": "8.000-15.000 TL/ay", "total_score": 70}
        result = psg.generate(sample_lead, "dental", score_data)
        expected_keys = {"cold_call", "email", "whatsapp", "demo_presentation"}
        assert set(result.keys()) == expected_keys

    def test_scripts_contain_business_name(self, sample_lead):
        psg = PitchScriptGenerator()
        score_data = {"package_recommendation": "Professional", "price_range": "8.000-15.000 TL/ay", "total_score": 70}
        result = psg.generate(sample_lead, "dental", score_data)
        for script_type, content in result.items():
            assert sample_lead["business_name"] in content, f"{script_type} missing business name"


# ============================================================
# 6. REVENUE ROADMAP ENGINE
# ============================================================

class TestRevenueRoadmapEngine:
    def test_generates_6_months(self):
        rre = RevenueRoadmapEngine()
        result = rre.generate(100000, 0)
        assert len(result["monthly_plan"]) == 6

    def test_target_mrr_correct(self):
        rre = RevenueRoadmapEngine()
        result = rre.generate(150000, 20000)
        assert result["target_mrr"] == 150000
        assert result["current_mrr"] == 20000
        assert result["gap"] == 130000

    def test_funnel_has_4_stages(self):
        rre = RevenueRoadmapEngine()
        result = rre.generate(100000)
        funnel = result["funnel"]
        assert set(funnel.keys()) == {"leads", "contacts", "demos", "closes"}

    def test_funnel_is_descending(self):
        rre = RevenueRoadmapEngine()
        result = rre.generate(100000)
        f = result["funnel"]
        assert f["leads"] >= f["contacts"] >= f["demos"] >= f["closes"]


# ============================================================
# 7. CONTRACT GENERATOR
# ============================================================

class TestContractGenerator:
    def test_generates_string(self):
        cg = ContractGenerator()
        client = {"business_name": "Test Clinic", "contact_person": "Dr. Test", "address": "Sydney CBD"}
        result = cg.generate(client, "dental", "Premium", 19000)
        assert isinstance(result, str)
        assert len(result) > 100

    def test_contract_contains_business_name(self):
        cg = ContractGenerator()
        client = {"business_name": "Harbour Dental", "contact_person": "Dr. Sarah", "address": "Sydney"}
        result = cg.generate(client, "dental", "Premium", 19000)
        assert "Harbour Dental" in result

    def test_contract_contains_package_name(self):
        cg = ContractGenerator()
        client = {"business_name": "Test Co", "contact_person": "Mr. Test", "address": "Melbourne"}
        result = cg.generate(client, "gym", "Professional", 11000)
        assert "PROFESSIONAL" in result.upper()

    def test_contract_has_10_articles(self):
        cg = ContractGenerator()
        client = {"business_name": "Test", "contact_person": "Test", "address": "Test"}
        result = cg.generate(client, "dental", "Starter", 5000)
        # Check MADDE 1 through MADDE 10
        for i in range(1, 11):
            assert f"MADDE {i}" in result


# ============================================================
# 8. BOARD MEETING AI
# ============================================================

class TestBoardMeetingAI:
    def test_generates_report(self):
        bm = BoardMeetingAI()
        data = {
            "mrr": 50000, "target_mrr": 100000,
            "monthly_costs": 10000, "churn_rate": 3,
            "pipeline_value": 200000,
            "active_leads": [{"name": "Lead A", "score": 80}],
            "customers": [{"name": "Client A", "health_score": 90}]
        }
        result = bm.generate_report(data)
        required = {"date", "health_score", "financial", "pipeline", "recommendations", "weekly_tasks"}
        assert required.issubset(result.keys())

    def test_health_score_in_range(self):
        bm = BoardMeetingAI()
        data = {"mrr": 80000, "target_mrr": 100000, "monthly_costs": 5000,
                "churn_rate": 2, "pipeline_value": 250000, "active_leads": [], "customers": []}
        result = bm.generate_report(data)
        assert 0 <= result["health_score"] <= 100

    def test_churn_detection_flags_unhealthy(self):
        bm = BoardMeetingAI()
        data = {
            "mrr": 50000, "target_mrr": 100000, "monthly_costs": 10000,
            "churn_rate": 5, "pipeline_value": 150000,
            "active_leads": [],
            "customers": [{"name": "At-Risk Client", "health_score": 40}]
        }
        result = bm.generate_report(data)
        assert len(result["churn_risks"]) >= 1


# ============================================================
# 9. JARVIS MAIN ORCHESTRATOR
# ============================================================

class TestJARVIS:
    def test_start_initializes_all_modules(self, jarvis):
        result = jarvis.start()
        assert result["status"] == "active"
        assert result["tables_created"] == 15
        assert len(result["modules"]) == 9

    def test_analyze_lead_returns_full_bundle(self, jarvis, sample_lead):
        result = jarvis.analyze_lead(sample_lead)
        assert "score" in result
        assert "roi" in result
        assert "pitch_scripts" in result
        assert "strategies" in result

    def test_analyze_lead_score_positive(self, jarvis, sample_lead):
        result = jarvis.analyze_lead(sample_lead)
        assert result["score"]["total_score"] > 0

    def test_generate_contract(self, jarvis):
        client = {"business_name": "Global Dental", "contact_person": "Dr. Global", "address": "London"}
        contract = jarvis.generate_contract(client, "dental", "Premium", 19000)
        assert "Global Dental" in contract

    def test_revenue_plan(self, jarvis):
        plan = jarvis.revenue_plan(100000, 20000)
        assert plan["target_mrr"] == 100000
        assert len(plan["monthly_plan"]) == 6

    def test_process_command_scan(self, jarvis):
        response = jarvis.process_command("tara")
        assert response  # Not empty

    def test_process_command_roi(self, jarvis):
        response = jarvis.process_command("ROI hesapla")
        assert "ROI" in response or "hesaplan" in response

    def test_scan_area_returns_apify_input(self, jarvis):
        result = jarvis.scan_area("Sydney", "CBD", "dental")
        assert result["status"] == "scan_ready"
        assert "input" in result


# ============================================================
# 10. INTEGRATION — Full Lead Pipeline
# ============================================================

class TestLeadPipeline:
    def test_full_pipeline(self, jarvis, sample_lead):
        """End-to-end: analyze → contract → board meeting."""
        # 1. Analyze
        analysis = jarvis.analyze_lead(sample_lead)
        assert analysis["score"]["total_score"] > 0

        package = analysis["score"]["package_recommendation"]
        assert package in ["Premium", "Professional", "Starter", "Nurture"]

        # 2. Generate contract
        client = {
            "business_name": sample_lead["business_name"],
            "contact_person": sample_lead["contact_person"],
            "address": sample_lead["city"]
        }
        contract = jarvis.generate_contract(client, sample_lead["sector"], package, 15000)
        assert sample_lead["business_name"] in contract

        # 3. Board meeting
        board_data = {
            "mrr": 45000, "target_mrr": 100000, "monthly_costs": 8000,
            "churn_rate": 2, "pipeline_value": 180000,
            "active_leads": [{"name": sample_lead["business_name"], "score": analysis["score"]["total_score"]}],
            "customers": []
        }
        report = jarvis.weekly_board_meeting(board_data)
        assert report["health_score"] >= 0

    def test_multi_sector_scoring(self, jarvis):
        """Score the same base lead across all sectors."""
        base = {
            "business_name": "Test Business",
            "has_website": True, "has_social_media": True,
            "google_maps_listed": True, "google_rating": 4.5,
            "review_count": 100, "employee_count": 10
        }
        sectors = ["dental", "law_firm", "accounting", "gym", "auto_gallery", "construction"]
        for sector in sectors:
            lead = {**base, "sector": sector}
            result = jarvis.analyze_lead(lead)
            assert result["score"]["total_score"] >= 0, f"Failed for sector: {sector}"
