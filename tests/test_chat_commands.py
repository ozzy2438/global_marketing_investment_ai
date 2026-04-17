#!/usr/bin/env python3

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jarvis_core


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


def test_general_fallback_is_not_static_canned_text(jarvis, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = jarvis.process_command("What can you help me with today?")

    assert "What can you help me with today?" in response
    assert "JARVIS hazır. Ne yapmamı istersin?" not in response
