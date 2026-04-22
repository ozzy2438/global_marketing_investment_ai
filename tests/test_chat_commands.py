#!/usr/bin/env python3

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jarvis_core
from jarvis_serper_research import SerperWebResearch


class DummySerpApi:
    def search_maps(self, sector, location, country_code, language, max_results):
        return [
            {
                "title": "HWY Espresso",
                "rating": 5.0,
                "reviews": 18,
                "address": "330 Hume Hwy, Craigieburn VIC 3064",
                "phone": "",
                "website": "",
                "gps_coordinates": {"latitude": -37.59, "longitude": 144.94},
            },
            {
                "title": "Earl of Brew",
                "rating": 4.7,
                "reviews": 297,
                "address": "Unit 5/330 Brookfield Blvd, Craigieburn VIC 3064",
                "phone": "(03) 9745 0951",
                "website": "",
                "gps_coordinates": {"latitude": -37.60, "longitude": 144.92},
            },
        ]

    def process_results(self, raw_data, category, country_code):
        leads = []
        for place in raw_data:
            leads.append(
                {
                    "name": place["title"],
                    "sector": category,
                    "phone": place["phone"],
                    "website": place["website"],
                    "rating": place["rating"],
                    "review_count": place["reviews"],
                    "score": 70,
                    "recommended_package": "Professional",
                    "raw_address": place["address"],
                    "latitude": place["gps_coordinates"]["latitude"],
                    "longitude": place["gps_coordinates"]["longitude"],
                }
            )
        return leads


@pytest.fixture
def jarvis(monkeypatch):
    monkeypatch.setenv("SERPAPI_API_KEY", "test-key")
    monkeypatch.setattr(jarvis_core, "SerpApiGlobalIntegration", DummySerpApi)
    return jarvis_core.JARVIS()


def test_knowledge_library_sync_indexes_structured_sources_and_skips_binaries(tmp_path):
    nested = tmp_path / "sales"
    nested.mkdir()
    (nested / "offers.summary.md").write_text(
        "# Offer Notes\n"
        "Author: Internal Team\n"
        "Workflow: offer_design\n"
        "Tags: offers, pricing\n\n"
        "Use value-based pricing for high-impact proposals.\n"
        "- Package outcomes instead of deliverables.\n",
        encoding="utf-8",
    )
    (tmp_path / "raw-book.pdf").write_bytes(b"%PDF-1.4")

    library = jarvis_core.KnowledgeLibrary(db=None, library_dir=str(tmp_path))
    report = library.sync_directory(persist=False)

    assert report["synced_sources"] == 1
    assert report["synced_snippets"] >= 1
    assert "sales/offers.summary.md" in report["indexed_files"]
    assert any(item["file"] == "raw-book.pdf" for item in report["skipped_files"])


def test_knowledge_library_search_matches_offer_design(tmp_path):
    payload = {
        "sources": [
            {
                "source_key": "100m-offers",
                "title": "$100M Offers",
                "author": "Alex Hormozi",
                "workflow_stage": "offer_design",
                "summary": "Package technical work as commercial outcomes.",
                "tags": ["offers", "pricing"],
                "insights": [
                    {
                        "content": "Price around impact and risk reduction rather than effort.",
                        "workflow_stage": "offer_design",
                        "tags": ["pricing", "roi"],
                        "importance": 92,
                    }
                ],
            },
            {
                "source_key": "hooked",
                "title": "Hooked",
                "author": "Nir Eyal",
                "workflow_stage": "habit_design",
                "summary": "Use triggers and rewards for re-engagement.",
                "tags": ["retention", "engagement"],
                "insights": [
                    {
                        "content": "Design retention loops around triggers and repeat behaviour.",
                        "workflow_stage": "habit_design",
                        "tags": ["retention"],
                        "importance": 80,
                    }
                ],
            },
        ]
    }
    (tmp_path / "book_playbooks.json").write_text(json.dumps(payload), encoding="utf-8")

    library = jarvis_core.KnowledgeLibrary(db=None, library_dir=str(tmp_path))
    library.sync_directory(persist=False)
    result = library.search("How should we package the offer and price the proposal?", limit=2)

    assert result["matches"]
    assert result["matches"][0]["source_key"] == "100m-offers"


def test_serper_research_builds_structured_business_summary(monkeypatch):
    researcher = SerperWebResearch(api_key="test-key")

    def fake_search(query, market_code="AU", num=5, autocorrect=True):
        if "complaints reviews issues" in query:
            return {
                "organic": [
                    {
                        "title": "Patient review summary",
                        "link": "https://example.com/reviews",
                        "snippet": "Patients mentioned waiting times and inconsistent follow-up after treatment.",
                    }
                ]
            }
        if "last year changes issues" in query:
            return {
                "organic": [
                    {
                        "title": "2025 update",
                        "link": "https://example.com/2025-update",
                        "snippet": "Last year the clinic expanded services and adjusted staffing after a busy growth period.",
                    }
                ]
            }
        return {
            "knowledgeGraph": {
                "title": "Dental Advance",
                "description": "Dental clinic in Melbourne CBD",
                "website": "https://dentaladvance.example",
            },
            "organic": [
                {
                    "title": "Official site",
                    "link": "https://dentaladvance.example",
                    "snippet": "Provides general dentistry, cosmetic treatments, and consultations in Melbourne CBD.",
                }
            ],
        }

    monkeypatch.setattr(researcher, "search", fake_search)
    result = researcher.research_business(
        business_name="Dental Advance",
        location="Melbourne CBD",
        website="https://dentaladvance.example",
        sector="dental",
        market_code="AU",
    )

    assert result["current_status_summary"]
    assert result["previous_status_summary"]
    assert result["last_year_challenges"]
    assert result["citations"]
    assert any(item["label"] == "reputation_issues" for item in result["search_runs"])


def test_extract_business_search_request(jarvis):
    request = jarvis._extract_business_search(
        "Could you find five coffee shops with very high feedback ratings in the suburb of Craigieburn, Melbourne for me?"
    )

    assert request is not None
    assert request["count"] == 5
    assert request["business_type"] == "coffee shop"
    assert request["location"] == "Craigieburn, Melbourne"
    assert request["country_code"] == "AU"
    assert request["rating_threshold"] == 4.5


def test_process_command_returns_ranked_business_results(jarvis):
    response = jarvis.process_command(
        "Could you find five coffee shops with very high feedback ratings in the suburb of Craigieburn, Melbourne for me?"
    )

    assert "I found" in response
    assert "HWY Espresso" in response
    assert "Earl of Brew" in response
    assert "JARVIS hazır. Ne yapmamı istersin?" not in response


def test_handle_command_returns_plot_ready_candidates(jarvis):
    result = jarvis.handle_command(
        "Could you find five coffee shops with very high feedback ratings in the suburb of Craigieburn, Melbourne for me?"
    )

    assert result["action"] == "plot_map_results"
    assert result["candidate_count"] == 2
    assert len(result["leads"]) == 2
    assert result["selected_lead"]["lead_key"]
    assert result["leads"][0]["investment_score"] >= result["leads"][1]["investment_score"]
    assert result["suggested_questions"]


def test_handle_command_can_analyze_candidate_pool(jarvis):
    search = jarvis.handle_command(
        "Could you find five coffee shops with very high feedback ratings in the suburb of Craigieburn, Melbourne for me?"
    )
    result = jarvis.handle_command(
        "Which one should we invest in first?",
        candidate_context=search["leads"],
    )

    assert result["action"] == "candidate_pool_analysis"
    assert "investment priority" in result["response"].lower()
    assert "HWY Espresso" in result["response"] or "Earl of Brew" in result["response"]


def test_handle_command_can_analyze_selected_lead(jarvis):
    search = jarvis.handle_command(
        "Could you find five coffee shops with very high feedback ratings in the suburb of Craigieburn, Melbourne for me?"
    )
    selected = search["selected_lead"]
    result = jarvis.handle_command(
        "What are the shortcomings of this option?",
        selected_lead=selected,
        candidate_context=search["leads"],
    )

    assert result["action"] == "focus_selected_lead"
    assert selected["name"] in result["response"]
    assert "shortcomings" in result["response"].lower()


def test_compare_candidates_returns_structured_summary(jarvis):
    search = jarvis.handle_command(
        "Could you find five coffee shops with very high feedback ratings in the suburb of Craigieburn, Melbourne for me?"
    )

    comparison = jarvis.compare_candidates(search["leads"], "AU")

    assert comparison["market_profile"]["market_code"] == "AU"
    assert comparison["top_recommendation"]["lead_key"]
    assert comparison["ranked_candidates"][0]["recommended_service_type"]
    assert "strongest current target" in comparison["summary"]


def test_build_proposal_brief_returns_structured_fields(jarvis):
    search = jarvis.handle_command(
        "Could you find five coffee shops with very high feedback ratings in the suburb of Craigieburn, Melbourne for me?"
    )

    brief = jarvis.build_proposal_brief(search["selected_lead"], "AU")

    assert brief["lead_key"] == search["selected_lead"]["lead_key"]
    assert brief["recommended_platform_type"]
    assert brief["recommended_service_type"]
    assert brief["proposal_readiness"] in {"Ready now", "Needs qualification", "Monitor"}
    assert brief["decision_trace"]
    assert brief["recommended_playbooks"]
    assert "Recommended playbooks" in brief["playbook_guidance"]


def test_general_fallback_is_not_static_canned_text(jarvis, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = jarvis.process_command("What can you help me with today?")

    assert "What can you help me with today?" in response
    assert "JARVIS hazır. Ne yapmamı istersin?" not in response


def test_general_fallback_can_use_knowledge_library(jarvis, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = jarvis.process_command("Which playbook should we use for pricing and proposal offers?")

    assert "Relevant playbooks from the knowledge library" in response
    assert "$100M Offers" in response
