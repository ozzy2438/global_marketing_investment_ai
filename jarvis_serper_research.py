#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS — Serper Web Research
Structured web-search layer for deeper candidate investigation.
"""

import json
import os
import re
import urllib.request
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


class SerperWebResearch:
    """Lightweight Serper.dev wrapper for business research."""

    ENDPOINT = "https://google.serper.dev/search"

    MARKET_PREFS = {
        "AU": {"gl": "au", "hl": "en"},
        "US": {"gl": "us", "hl": "en"},
        "GB": {"gl": "uk", "hl": "en"},
        "NZ": {"gl": "nz", "hl": "en"},
        "TR": {"gl": "tr", "hl": "tr"},
    }

    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        self.api_key = api_key or os.environ.get("SERPER_API_KEY", "").strip()
        if not self.api_key:
            raise ValueError("SERPER_API_KEY is required for web research.")
        self.endpoint = endpoint or self.ENDPOINT

    def _market_prefs(self, market_code: Optional[str]) -> Dict[str, str]:
        return self.MARKET_PREFS.get((market_code or "AU").upper(), self.MARKET_PREFS["AU"])

    def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8")
        return json.loads(raw)

    def search(
        self,
        query: str,
        market_code: str = "AU",
        num: int = 5,
        autocorrect: bool = True,
    ) -> Dict[str, Any]:
        prefs = self._market_prefs(market_code)
        payload = {
            "q": query,
            "gl": prefs["gl"],
            "hl": prefs["hl"],
            "num": num,
            "autocorrect": autocorrect,
        }
        return self._post(payload)

    def _domain(self, website: str) -> str:
        if not website:
            return ""
        parsed = urlparse(website if "://" in website else f"https://{website}")
        return parsed.netloc.replace("www.", "").strip().lower()

    def _build_queries(
        self,
        business_name: str,
        location: str = "",
        website: str = "",
        sector: str = "",
    ) -> List[Dict[str, str]]:
        quoted_name = f"\"{business_name}\""
        location_part = f" {location}" if location else ""
        sector_part = f" {sector}" if sector else ""
        domain = self._domain(website)

        queries = [
            {
                "label": "current_status",
                "query": f"{quoted_name}{location_part}{sector_part} reviews services current status",
            },
            {
                "label": "reputation_issues",
                "query": f"{quoted_name}{location_part} complaints reviews issues patient feedback",
            },
            {
                "label": "last_year_changes",
                "query": f"{quoted_name}{location_part} last year changes issues expansion closure hiring 2025",
            },
        ]

        if domain:
            queries.append(
                {
                    "label": "official_site",
                    "query": f"site:{domain} {quoted_name} about services team contact",
                }
            )

        return queries

    def _organic_items(self, payload: Dict[str, Any]) -> List[Dict[str, str]]:
        items: List[Dict[str, str]] = []
        for item in payload.get("organic", []) or []:
            title = str(item.get("title", "")).strip()
            link = str(item.get("link", "")).strip()
            snippet = str(item.get("snippet", "")).strip()
            if title or link or snippet:
                items.append({"title": title, "link": link, "snippet": snippet})
        return items

    def _knowledge_graph_item(self, payload: Dict[str, Any]) -> Optional[Dict[str, str]]:
        graph = payload.get("knowledgeGraph") or {}
        title = str(graph.get("title", "")).strip()
        link = str(graph.get("website", "") or graph.get("link", "")).strip()
        fields = []
        for key in ("type", "description"):
            if graph.get(key):
                fields.append(str(graph[key]).strip())
        snippet = " | ".join(field for field in fields if field)
        if title or link or snippet:
            return {"title": title, "link": link, "snippet": snippet}
        return None

    def _summarise_items(self, items: List[Dict[str, str]], fallback: str) -> str:
        snippets = [item["snippet"] for item in items if item.get("snippet")]
        snippets = [snippet for snippet in snippets if snippet]
        if not snippets:
            return fallback
        summary = " ".join(snippets[:2]).strip()
        summary = re.sub(r"\s+", " ", summary)
        return summary[:420]

    def _extract_challenges(self, items: List[Dict[str, str]]) -> List[str]:
        challenges = []
        seen = set()
        for item in items[:6]:
            snippet = item.get("snippet", "").strip()
            if not snippet:
                continue
            cleaned = re.sub(r"\s+", " ", snippet)
            if cleaned.lower() in seen:
                continue
            seen.add(cleaned.lower())
            challenges.append(cleaned[:220])
        return challenges[:3]

    def research_business(
        self,
        business_name: str,
        location: str = "",
        website: str = "",
        sector: str = "",
        market_code: str = "AU",
    ) -> Dict[str, Any]:
        queries = self._build_queries(business_name, location, website, sector)
        search_runs = []
        combined_items: List[Dict[str, str]] = []
        grouped_items: Dict[str, List[Dict[str, str]]] = {}

        for query_def in queries:
            payload = self.search(query_def["query"], market_code=market_code, num=5)
            items = self._organic_items(payload)
            graph_item = self._knowledge_graph_item(payload)
            if graph_item:
                items.insert(0, graph_item)
            grouped_items[query_def["label"]] = items
            for item in items:
                combined_items.append(
                    {
                        **item,
                        "query_label": query_def["label"],
                        "query": query_def["query"],
                    }
                )
            search_runs.append(
                {
                    "label": query_def["label"],
                    "query": query_def["query"],
                    "result_count": len(items),
                }
            )

        citations: List[Dict[str, str]] = []
        seen_links = set()
        for item in combined_items:
            link = item.get("link", "")
            dedupe_key = link or f"{item.get('title', '')}|{item.get('snippet', '')}"
            if dedupe_key in seen_links:
                continue
            seen_links.add(dedupe_key)
            citations.append(item)
        citations = citations[:8]

        current_status = self._summarise_items(
            grouped_items.get("current_status", []) + grouped_items.get("official_site", []),
            "Current status signals are still thin. More direct site and review research is needed.",
        )
        previous_status = self._summarise_items(
            grouped_items.get("last_year_changes", []),
            "Previous-status signals are limited in open web results.",
        )
        last_year_challenges = self._extract_challenges(grouped_items.get("reputation_issues", []) + grouped_items.get("last_year_changes", []))

        return {
            "business_name": business_name,
            "location": location,
            "sector": sector,
            "website": website,
            "market_code": (market_code or "AU").upper(),
            "current_status_summary": current_status,
            "previous_status_summary": previous_status,
            "last_year_challenges": last_year_challenges,
            "recommended_followups": [
                "Compare the official site messaging against Google reviews and public complaints.",
                "Check whether recent reviews point to operational, pricing, or service-delivery gaps.",
                "Validate any claimed issue through at least two independent public sources before using it in a proposal.",
            ],
            "search_runs": search_runs,
            "citations": citations,
        }
