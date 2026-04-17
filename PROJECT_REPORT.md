# Global Marketing Investment AI

## Project Report: JARVIS AI Agency OS / Investment Support Agent

This repository now contains the first project report for the current JARVIS AI Agency OS / Investment Support Agent implementation.

## Executive Summary

JARVIS is an AI-powered agency operating system built to support lead generation, qualification, outreach preparation, ROI modelling, contract generation, and operational reporting from a single codebase. The project combines a FastAPI backend, a static HTML dashboard frontend, a PostgreSQL-oriented core layer with SQLite-style local usage patterns, and Google Maps business discovery via SerpApi-powered scanning.

The platform is structured as an operator dashboard rather than a consumer app. Its primary value is helping an agency or investment-support workflow identify high-value businesses, assess sales opportunities, and generate action-ready commercial outputs quickly.

## Current Scope

- Global business discovery using Google Maps / SerpApi lookups
- Lead scoring and prioritisation
- ROI estimation and package recommendation
- Pitch-script generation
- Contract drafting
- Revenue roadmap generation
- Board-meeting style operational summaries
- Interactive dashboard with built-in JARVIS chat

## Technical Stack

- Backend: Python, FastAPI, Uvicorn
- Frontend: Static HTML, CSS, JavaScript
- Data layer: PostgreSQL-oriented schema and query layer, local database file present
- Integrations: SerpApi, OpenAI TTS, MCP bridge hooks
- Tooling: Docker, Docker Compose, pytest

## Key Application Files

- `jarvis_core.py`: Core orchestration and business logic
- `jarvis_api.py`: REST API surface
- `jarvis_scan_api.py`: Business discovery and scan endpoints
- `jarvis_serpapi_global.py`: SerpApi-backed Google Maps search integration
- `frontend/jarvis_dashboard_v2.html`: Main dashboard UI
- `requirements.txt`: Python dependency set
- `docker-compose.yml`: Local service orchestration

## Architecture Summary

The frontend dashboard calls the FastAPI backend over HTTP. The backend exposes operational endpoints for scoring, analysis, scanning, ROI, contracts, playbooks, revenue planning, and board reporting. Business discovery is driven through SerpApi queries, then normalised into the JARVIS lead format. The dashboard includes a chat interface that now routes natural-language local business search prompts into live ranked lookup results instead of returning a fixed fallback message.

## Notable Delivered Improvements

- Backend and frontend were brought up and verified locally
- Chat handling was corrected so natural-language prompts no longer collapse into the same canned response
- Free-form business search requests such as local coffee-shop discovery now resolve to live ranked results
- Frontend chat rendering was updated to display multiline responses safely
- Focused regression tests were added for chat command parsing and fallback behavior

## Operational Status

Working:

- API server startup
- Dashboard startup
- Live business lookup through `/api/command`
- Structured scan endpoints
- Health endpoint at `/health`

Known gap:

- Text-to-speech currently fails because the configured OpenAI API key is invalid or placeholder, causing `/api/tts` to return `401`

## Local Run Path

Backend:

```bash
./venv/bin/python -m uvicorn jarvis_api:app --host 0.0.0.0 --port 8000
```

Frontend:

```bash
./venv/bin/python -m http.server 3000 --directory frontend
```

Primary URLs:

- Dashboard: `http://localhost:3000/jarvis_dashboard_v2.html`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## Project Assessment

This is a strong prototype-to-product codebase with meaningful breadth across sales operations, business discovery, and agency workflow automation. The most important next step is tightening production readiness around configuration handling, database consistency, authentication, and external API reliability. The system already demonstrates useful end-to-end behavior for operator workflows and is materially more valuable now that chat requests can trigger live business discovery instead of only fixed canned responses.

## Report Metadata

- Added: 2026-04-17
- Source project: JARVIS AI Agency OS / Investment Support Agent
- Report status: initial submission
