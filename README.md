# JARVIS AI Agency Operating System

> **A complete AI-powered agency management platform that automates lead generation, client acquisition, project management, and delivery — globally.**

JARVIS acts as your AI CEO/Assistant: it finds clients via Google Maps worldwide, scores them, generates pitch scripts, calculates ROI, creates contracts, manages revenue roadmaps, runs board meetings, and delegates technical work to Claude Code via MCP integration.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Directory Structure](#directory-structure)
4. [Prerequisites](#prerequisites)
5. [Step-by-Step Setup](#step-by-step-setup)
6. [File Descriptions](#file-descriptions)
7. [Environment Variables](#environment-variables)
8. [Database Setup](#database-setup)
9. [Running the Application](#running-the-application)
10. [API Reference](#api-reference)
11. [Global Scanning System](#global-scanning-system)
12. [Claude Code / MCP Integration](#claude-code--mcp-integration)
13. [Docker Deployment](#docker-deployment)
14. [Frontend Dashboard](#frontend-dashboard)
15. [Testing](#testing)
16. [Troubleshooting](#troubleshooting)

---

## System Overview

JARVIS consists of **13 core modules** across **14 files**:

| Module | File | Purpose |
|--------|------|---------|
| Core Engine | `jarvis_core.py` | 10 unified modules — scoring, playbooks, ROI, pitch, contracts, board meetings |
| API Server | `jarvis_api.py` | 30 RESTful endpoints via FastAPI |
| Global Scanner | `jarvis_apify_global.py` | Real Apify integration — 10 sectors, 30 languages, 42 currencies |
| Scan API | `jarvis_scan_api.py` | 14 scanning endpoints with background processing |
| MCP Bridge | `jarvis_mcp.py` | Claude Code delegation — website, chatbot, automation tasks |
| Dashboard v2 | `jarvis_dashboard_v2.html` | API-connected frontend with live data |
| Dashboard v1 | `jarvis_dashboard.html` | Static demo dashboard |
| Database Schema | `jarvis_database_schema.sql` | Full PostgreSQL schema (15 tables) |
| Dependencies | `requirements.txt` | Python package requirements |
| Docker | `Dockerfile` | Container image definition |
| Compose | `docker-compose.yml` | Multi-container orchestration |
| Env Template | `.env.example` | Environment variable template |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    JARVIS DASHBOARD (HTML/JS)                │
│              jarvis_dashboard_v2.html                        │
│         Connects to API at http://localhost:8000             │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI SERVER (jarvis_api.py)              │
│                  30 endpoints, 13 categories                 │
│                  Port: 8000                                  │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Scan Router  │  │ Core Router  │  │ MCP Router   │      │
│  │ (scan_api)   │  │ (jarvis_api) │  │ (mcp bridge) │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│ Apify API    │  │ jarvis_core  │  │ Claude Code      │
│ (Google Maps)│  │ (10 modules) │  │ (MCP Protocol)   │
│              │  │              │  │                  │
│ 10 sectors   │  │ • Scoring    │  │ • Website build  │
│ 30 languages │  │ • Playbooks  │  │ • Chatbot dev    │
│ 42 currencies│  │ • ROI Calc   │  │ • Automation     │
│              │  │ • Pitch Gen  │  │ • Deployment     │
│              │  │ • Contracts  │  │                  │
│              │  │ • Revenue    │  │ 6 sectors ×      │
│              │  │ • Board AI   │  │ 3 project types  │
│              │  │ • CRM        │  │ = 18 templates   │
└──────────────┘  └──────┬───────┘  └──────────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │   SQLite DB  │
                  │  (jarvis.db) │
                  │  15 tables   │
                  └──────────────┘
```

---

## Directory Structure

Create this exact folder structure in your VS Code project:

```
jarvis-agency-os/
│
├── README.md                        ← This file
│
├── .env                             ← Your actual environment variables (create from .env.example)
├── .env.example                     ← Template for environment variables
├── .gitignore                       ← Git ignore rules
│
├── requirements.txt                 ← Python dependencies
├── Dockerfile                       ← Docker container definition
├── docker-compose.yml               ← Docker Compose orchestration
│
├── jarvis_core.py                   ← CORE: All 10 business logic modules (1,051 lines)
├── jarvis_api.py                    ← API: FastAPI server with 30 endpoints (555 lines)
├── jarvis_apify_global.py           ← SCANNER: Real Apify Google Maps integration (global)
├── jarvis_scan_api.py               ← SCAN API: 14 scanning endpoints with background tasks
├── jarvis_mcp.py                    ← MCP: Claude Code bridge for technical task delegation
│
├── jarvis_database_schema.sql       ← DATABASE: Full PostgreSQL schema (15 tables)
├── jarvis.db                        ← DATABASE: SQLite file (auto-created on first run)
│
├── frontend/
│   ├── jarvis_dashboard_v2.html     ← DASHBOARD: API-connected frontend (primary)
│   └── jarvis_dashboard.html        ← DASHBOARD: Static demo version (reference only)
│
└── tests/
    └── test_jarvis.py               ← Test suite (create as needed)
```

> **IMPORTANT**: All `.py` files must be in the **root directory** (same level) because they import each other directly. For example, `jarvis_api.py` does `from jarvis_core import JARVIS` and `jarvis_scan_api.py` does `from jarvis_apify_global import ApifyGlobalIntegration`.

---

## Prerequisites

- **Python 3.10+** (3.11 or 3.12 recommended)
- **pip** (Python package manager)
- **Git** (for version control)
- **VS Code** (recommended IDE)
- **Apify Account** — Free tier at [apify.com](https://apify.com) (for live Google Maps scanning)
- **Docker** (optional, for containerized deployment)

---

## Step-by-Step Setup

### Step 1: Create the Project Directory

```bash
mkdir jarvis-agency-os
cd jarvis-agency-os
mkdir frontend tests
```

### Step 2: Place All Files

Download all files from the conversation and place them as follows:

| File | Place In |
|------|----------|
| `jarvis_core.py` | `jarvis-agency-os/` (root) |
| `jarvis_api.py` | `jarvis-agency-os/` (root) |
| `jarvis_apify_global.py` | `jarvis-agency-os/` (root) |
| `jarvis_scan_api.py` | `jarvis-agency-os/` (root) |
| `jarvis_mcp.py` | `jarvis-agency-os/` (root) |
| `jarvis_database_schema.sql` | `jarvis-agency-os/` (root) |
| `requirements.txt` | `jarvis-agency-os/` (root) |
| `Dockerfile` | `jarvis-agency-os/` (root) |
| `docker-compose.yml` | `jarvis-agency-os/` (root) |
| `.env.example` | `jarvis-agency-os/` (root) |
| `jarvis_dashboard_v2.html` | `jarvis-agency-os/frontend/` |
| `jarvis_dashboard.html` | `jarvis-agency-os/frontend/` |

### Step 3: Create Virtual Environment

```bash
python -m venv venv

# Activate:
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` contains:

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.2
python-dotenv==1.0.0
aiohttp==3.9.1
python-multipart==0.0.6
```

> **Note**: If you need additional packages for production, also install:
> ```bash
> pip install psycopg2-binary redis celery gunicorn
> ```

### Step 5: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# Required
APIFY_API_TOKEN=your_apify_api_token_here

# Optional (for future integrations)
DATABASE_URL=sqlite:///jarvis.db
SECRET_KEY=your-secret-key-change-this
CLAUDE_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key
```

**To get your Apify API token:**
1. Go to [apify.com](https://apify.com) and create a free account
2. Navigate to Settings → Integrations → API Tokens
3. Create a new token and copy it into your `.env` file

### Step 6: Wire the Scan Router into the Main API

Open `jarvis_api.py` and add these lines near the top (after the existing imports):

```python
# Add this import at the top of jarvis_api.py
from jarvis_scan_api import router as scan_router

# Add this line after the app is created (after the CORS middleware section)
app.include_router(scan_router)
```

This connects the 14 global scanning endpoints to the main FastAPI server.

### Step 7: Initialize the Database

The database auto-initializes when you first run the app. However, if you want to use PostgreSQL instead of SQLite:

```bash
# For PostgreSQL (optional):
psql -U postgres -c "CREATE DATABASE jarvis;"
psql -U postgres -d jarvis -f jarvis_database_schema.sql
```

For SQLite (default — no action needed), the `jarvis.db` file is created automatically.

### Step 8: Start the Server

```bash
uvicorn jarvis_api:app --reload --host 0.0.0.0 --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### Step 9: Verify the API

Open your browser:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs) — Interactive API documentation
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc) — Alternative docs
- **Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### Step 10: Open the Dashboard

Open `frontend/jarvis_dashboard_v2.html` in your browser. It connects to `http://localhost:8000` automatically.

> **Tip**: For development, use VS Code's Live Server extension to serve the HTML file.

---

## File Descriptions

### `jarvis_core.py` — Core Engine (1,051 lines)

The heart of JARVIS. Contains 10 unified modules in a single file:

| Class | Purpose |
|-------|---------|
| `DatabaseManager` | SQLite connection, 15-table initialization, CRUD operations |
| `LeadScoringEngine` | AI-readiness scoring (0-100) across 5 categories |
| `PlaybookManager` | Sector-specific strategy templates (6 sectors, 18+ strategies) |
| `ROICalculator` | Revenue projection, ROI %, payback period calculation |
| `PitchScriptGenerator` | 4 pitch types (cold call, email, WhatsApp, demo) × 6 sectors |
| `RevenueRoadmapEngine` | 6-month revenue plans with sales funnel metrics |
| `ContractGenerator` | Auto-generated 10-clause service contracts |
| `BoardMeetingAI` | Agency health score, financial summary, AI recommendations |
| `ApifyIntegration` | Legacy Apify integration (Turkey-focused, kept for backward compat) |
| `JARVIS` | Main orchestrator class — initializes all modules, processes commands |

**Usage:**
```python
from jarvis_core import JARVIS

jarvis = JARVIS()
jarvis.start()

# Analyze a lead
result = jarvis.analyze_lead({
    "business_name": "NYC Dental Spa",
    "sector": "dental",
    "has_website": True,
    "google_rating": 4.8,
    "review_count": 342,
})

# Process natural language commands
response = jarvis.process_command("Scan dental clinics in Manhattan")
```

### `jarvis_api.py` — FastAPI Server (555 lines, 30 endpoints)

RESTful API layer. All endpoints are prefixed with `/api/`.

**Key imports it needs:**
```python
from jarvis_core import JARVIS          # Core engine
from jarvis_scan_api import router      # Global scan endpoints (you must add this)
```

### `jarvis_apify_global.py` — Global Apify Integration (32,636 chars)

Real Apify API integration for worldwide Google Maps scraping.

**Key features:**
- 10 business sectors with keywords in 14 languages each
- 30 supported search languages
- 42 currency auto-conversions
- AI-readiness scoring with signal detection
- Multi-location parallel scanning
- Lead enrichment pipeline (website crawl, reviews, social media)

**Standalone usage:**
```python
from jarvis_apify_global import ApifyGlobalIntegration

client = ApifyGlobalIntegration(api_token="your_token")

# Start a scan
scan = client.start_scan(
    sector="dental",
    location="Manhattan, New York",
    country_code="US",
    language="en",
    max_results=100
)

# Check status
status = client.check_scan_status(scan["run_id"])

# Fetch and process results
raw = client.fetch_results(scan["dataset_id"])
leads = client.process_results(raw, "dental", "US")
```

### `jarvis_scan_api.py` — Scan API Router (14 endpoints)

FastAPI router that exposes the global scanning system as API endpoints.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/scan/sectors` | List all 10 sectors with language support |
| GET | `/api/v1/scan/languages` | List all 30 supported languages |
| GET | `/api/v1/scan/currencies` | List all 42 currencies |
| POST | `/api/v1/scan/convert-price` | Convert USD to any local currency |
| GET | `/api/v1/scan/packages` | Package pricing by country |
| POST | `/api/v1/scan/start` | **Start a live Google Maps scan** |
| GET | `/api/v1/scan/status/{scan_id}` | Check scan progress |
| GET | `/api/v1/scan/results/{scan_id}` | Get scored leads with filters |
| POST | `/api/v1/scan/multi` | Multi-location parallel scan |
| POST | `/api/v1/scan/enrich` | Deep-enrich a specific lead |
| GET | `/api/v1/scan/report/{scan_id}` | AI-generated scan report |
| GET | `/api/v1/scan/examples` | Example scan configs for 7 countries |

### `jarvis_mcp.py` — Claude Code / MCP Bridge (686 lines)

Delegates technical implementation tasks to Claude Code via MCP (Model Context Protocol).

**Key classes:**
- `ClaudeCodeBridge` — Creates projects, generates tasks, builds prompts for Claude Code
- `JARVISOrchestrator` — Full pipeline from lead → project → delivery
- 18 technical templates (6 sectors × 3 project types: website, chatbot, automation)
- 5 MCP server configurations (jarvis-agency, filesystem, github, puppeteer, sqlite)

**Estimated delivery timelines:**

| Sector | Starter | Professional | Premium |
|--------|---------|-------------|---------|
| Dental | 7 days | 12 days | 16 days |
| Law Firm | 8 days | 14 days | 19 days |
| Gym | 6 days | 10 days | 14 days |
| Restaurant | 5 days | 9 days | 13 days |
| Real Estate | 7 days | 13 days | 18 days |

### `jarvis_database_schema.sql` — Database Schema (15 tables)

Full PostgreSQL-compatible schema. Tables:

1. `users` — Agency owners/agents
2. `leads` — Prospective clients from scans
3. `customers` — Converted clients
4. `interactions` — All touchpoints (calls, emails, meetings)
5. `playbooks` — Strategy templates by sector
6. `offers` — Package offers sent to leads
7. `case_studies` — Success stories for pitching
8. `projects` — Active client projects
9. `tasks` — Project tasks and subtasks
10. `contracts` — Generated service contracts
11. `revenue_roadmap` — Monthly revenue plans
12. `board_meetings` — AI board meeting reports
13. `map_scans` — Google Maps scan history
14. `pitch_scripts` — Generated pitch scripts
15. `settings` — System configuration

### `jarvis_dashboard_v2.html` — Frontend Dashboard

Single-page HTML/CSS/JS dashboard that connects to the API.

**Features:**
- Dark theme, responsive layout
- 12-item sidebar navigation
- Real-time stats (MRR, active clients, pipeline value, lead pool)
- Hot leads table with score badges
- Agency health score ring chart
- Sales pipeline visualization
- Map scan modal (trigger scans from UI)
- ROI calculator (live API calls)
- Playbook browser
- JARVIS AI chat widget (bottom-right corner)

**API Connection:**
The dashboard connects to `http://localhost:8000` by default. To change this, edit the `API_BASE` constant at the top of the JavaScript section in the HTML file.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `APIFY_API_TOKEN` | **Yes** (for scanning) | Your Apify API token for Google Maps scraping |
| `DATABASE_URL` | No | Database connection string. Default: `sqlite:///jarvis.db` |
| `SECRET_KEY` | No | JWT secret for authentication (future use) |
| `CLAUDE_API_KEY` | No | Anthropic API key for Claude Code integration |
| `OPENAI_API_KEY` | No | OpenAI API key (alternative AI provider) |
| `PORT` | No | Server port. Default: `8000` |

---

## Database Setup

### Option A: SQLite (Default — Zero Config)

SQLite is used by default. The database file `jarvis.db` is auto-created when you first run the application. No setup needed.

### Option B: PostgreSQL (Production)

1. Install PostgreSQL
2. Create the database:
   ```bash
   psql -U postgres -c "CREATE DATABASE jarvis;"
   ```
3. Run the schema:
   ```bash
   psql -U postgres -d jarvis -f jarvis_database_schema.sql
   ```
4. Update `.env`:
   ```env
   DATABASE_URL=postgresql://postgres:password@localhost:5432/jarvis
   ```
5. Update `jarvis_core.py` to use `psycopg2` instead of `sqlite3` (replace the `DatabaseManager` class connection logic).

---

## Running the Application

### Development Mode

```bash
# Terminal 1: Start the API server
uvicorn jarvis_api:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Open the dashboard
# Option A: Simply open the HTML file in your browser
open frontend/jarvis_dashboard_v2.html

# Option B: Use VS Code Live Server extension
# Right-click jarvis_dashboard_v2.html → "Open with Live Server"
```

### Production Mode

```bash
gunicorn jarvis_api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## API Reference

### Core Endpoints (jarvis_api.py — 30 endpoints)

#### System
- `GET /api/health` — Health check
- `GET /api/version` — Version info

#### Leads
- `POST /api/leads/analyze` — Analyze a business lead (returns score, package, ROI)
- `GET /api/leads` — List all leads
- `GET /api/leads/{id}` — Get lead details
- `POST /api/leads/bulk-analyze` — Analyze multiple leads
- `PUT /api/leads/{id}/status` — Update lead status

#### Scanning
- `POST /api/scan` — Start a map scan (legacy, Turkey-focused)
- `GET /api/scan/{id}` — Get scan results

#### ROI
- `POST /api/roi/calculate` — Calculate ROI for a lead
- `POST /api/roi/compare` — Compare ROI across packages

#### Playbooks
- `GET /api/playbooks` — List all playbooks
- `GET /api/playbooks/{sector}` — Get sector-specific playbook

#### Pitch Scripts
- `POST /api/pitch/generate` — Generate pitch scripts for a lead

#### Contracts
- `POST /api/contracts/generate` — Generate a service contract
- `GET /api/contracts/{id}` — Get contract details

#### Revenue
- `POST /api/revenue/plan` — Generate revenue roadmap
- `POST /api/revenue/save` — Save a revenue plan

#### Board Meeting
- `POST /api/board-meeting` — Generate AI board meeting report
- `GET /api/board-meeting/history` — Past reports

#### Dashboard
- `GET /api/dashboard/stats` — Dashboard statistics
- `GET /api/dashboard/pipeline` — Sales pipeline data

#### Customers
- `GET /api/customers` — List customers
- `POST /api/customers/convert/{id}` — Convert lead to customer

#### Settings
- `GET /api/settings` — Get settings
- `PUT /api/settings/{key}` — Update a setting

#### JARVIS AI
- `POST /api/command` — Natural language command processing

### Global Scan Endpoints (jarvis_scan_api.py — 14 endpoints)

All prefixed with `/api/v1/scan/`. See the [Scan API section](#jarvis_scan_apipy--scan-api-router-14-endpoints) above for the full list.

---

## Global Scanning System

### Supported Sectors (10)

`dental`, `law_firm`, `accounting`, `gym`, `auto_gallery`, `construction`, `restaurant`, `real_estate`, `beauty_salon`, `medical_clinic`

### Supported Languages (30)

English, Türkçe, Deutsch, Français, Español, Português, Italiano, Nederlands, العربية, 日本語, 한국어, 中文, Русский, Polski, Svenska, Norsk, Dansk, Suomi, Ελληνικά, Čeština, Română, Magyar, हिन्दी, ไทย, Tiếng Việt, Bahasa Indonesia, Bahasa Melayu, Українська, עברית, বাংলা

### Supported Currencies (42)

USD, EUR, GBP, TRY, JPY, KRW, CNY, INR, BRL, MXN, CAD, AUD, NZD, ZAR, AED, SAR, RUB, PLN, CZK, HUF, RON, SEK, NOK, DKK, CHF, THB, VND, IDR, MYR, SGD, PHP, PKR, BDT, ILS, NGN, KES, EGP, UAH, ARS, CLP, COP, PEN

### Example: Scan Dental Clinics in Tokyo

```bash
curl -X POST http://localhost:8000/api/v1/scan/start \
  -H "Content-Type: application/json" \
  -d '{
    "sector": "dental",
    "location": "Shibuya, Tokyo",
    "country_code": "JP",
    "language": "ja",
    "max_results": 50
  }'
```

Response:
```json
{
  "scan_id": "abc123",
  "status": "STARTED",
  "poll_url": "/api/v1/scan/status/abc123",
  "results_url": "/api/v1/scan/results/abc123"
}
```

### Scoring Algorithm

Each lead is scored 0-100 across 5 categories:

| Category | Max Points | Signals |
|----------|-----------|---------|
| Online Presence | 25 | Has website, phone, Google Maps listing |
| Reviews & Reputation | 25 | Review count, average rating |
| Business Maturity | 20 | Multiple categories, rich media, opening hours |
| AI Opportunity | 15 | No website (high opp), social-only website |
| Engagement Potential | 15 | Phone + website combo, unclaimed listing |

**Package Recommendation:**
- 75-100 → **Premium** ($2,500/mo USD)
- 55-74 → **Professional** ($1,200/mo USD)
- 35-54 → **Starter** ($500/mo USD)
- 0-34 → **Nurture** (not ready yet)

Prices auto-convert to local currency based on country code.

---

## Claude Code / MCP Integration

### How It Works

1. JARVIS identifies a client need (e.g., "dental clinic needs a website")
2. `JARVISOrchestrator` creates a project with tasks
3. `ClaudeCodeBridge` generates detailed prompts for each task
4. Tasks are delegated to Claude Code via MCP protocol
5. Claude Code builds the actual product (website, chatbot, etc.)

### MCP Server Configuration

The system configures 5 MCP servers:

| Server | Purpose |
|--------|---------|
| `jarvis-agency` | Main JARVIS tools and context |
| `filesystem` | File system access for code generation |
| `github` | Repository management and deployment |
| `puppeteer` | Browser automation and testing |
| `sqlite` | Database operations |

### Setting Up Claude Code

1. Install Claude Code CLI: Follow [Anthropic's documentation](https://docs.anthropic.com/en/docs/claude-code)
2. Configure MCP servers in your Claude Code settings
3. Set `CLAUDE_API_KEY` in your `.env` file
4. The `jarvis_mcp.py` module handles the rest

---

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Using Dockerfile Directly

```bash
# Build
docker build -t jarvis-agency-os .

# Run
docker run -d \
  --name jarvis \
  -p 8000:8000 \
  -e APIFY_API_TOKEN=your_token \
  -v $(pwd)/jarvis.db:/app/jarvis.db \
  jarvis-agency-os
```

### Docker Compose File Reference

```yaml
version: '3.8'
services:
  jarvis:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./jarvis.db:/app/jarvis.db
    restart: unless-stopped
```

---

## Frontend Dashboard

### Connecting to the API

The dashboard (`jarvis_dashboard_v2.html`) connects to `http://localhost:8000` by default.

To change the API URL, find this line in the HTML file's `<script>` section:

```javascript
const API_BASE = "http://localhost:8000";
```

Change it to your production URL when deploying.

### Dashboard Features

- **Stats Grid**: MRR, Active Clients, Pipeline Value, Lead Pool
- **Hot Leads Table**: Top leads sorted by score with action buttons
- **Agency Health Score**: Ring chart showing overall agency health (0-100)
- **Sales Pipeline**: Visual funnel (Lead → Contact → Demo → Proposal → Close)
- **Map Scanner**: Modal to trigger Google Maps scans from the UI
- **ROI Calculator**: Calculate ROI for any sector/package combination
- **Playbook Browser**: Browse sector-specific strategy templates
- **JARVIS Chat**: AI chat widget for natural language commands

---

## Testing

### Quick Smoke Test

```bash
# 1. Check health
curl http://localhost:8000/api/health

# 2. Analyze a lead
curl -X POST http://localhost:8000/api/leads/analyze \
  -H "Content-Type: application/json" \
  -d '{"business_name": "NYC Dental Spa", "sector": "dental", "has_website": true, "google_rating": 4.8, "review_count": 342}'

# 3. Calculate ROI
curl -X POST http://localhost:8000/api/roi/calculate \
  -H "Content-Type: application/json" \
  -d '{"sector": "dental", "package": "Premium"}'

# 4. Generate pitch scripts
curl -X POST http://localhost:8000/api/pitch/generate \
  -H "Content-Type: application/json" \
  -d '{"business_name": "NYC Dental Spa", "sector": "dental", "contact_name": "Dr. Smith"}'

# 5. List supported sectors
curl http://localhost:8000/api/v1/scan/sectors

# 6. Get package pricing for Japan
curl "http://localhost:8000/api/v1/scan/packages?country_code=JP"
```

### Python Test

```python
# test_jarvis.py
from jarvis_core import JARVIS

jarvis = JARVIS()
result = jarvis.start()
print(f"Tables: {result['tables_created']}, Modules: {result['modules_loaded']}")

# Test scoring
score = jarvis.analyze_lead({
    "business_name": "Test Clinic",
    "sector": "dental",
    "has_website": True,
    "google_rating": 4.5,
    "review_count": 100,
})
print(f"Score: {score['score']}/100, Package: {score['package']}")
assert score['score'] > 0
print("All tests passed!")
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: jarvis_core` | Make sure all `.py` files are in the same directory |
| `APIFY_API_TOKEN not set` | Create `.env` file with your token, or set env var |
| `Port 8000 already in use` | Use `--port 8001` or kill the existing process |
| `CORS errors in dashboard` | Ensure FastAPI CORS middleware is configured (it is by default) |
| `Database locked` | Stop other processes using `jarvis.db`, or switch to PostgreSQL |
| `Scan returns empty results` | Check Apify token validity, check sector/location spelling |
| `Dashboard not loading data` | Verify API is running on port 8000, check browser console |

### Logs

```bash
# Verbose logging
uvicorn jarvis_api:app --reload --log-level debug

# Docker logs
docker-compose logs -f jarvis
```

---

## Summary of All Files

| # | File | Size | Lines | Description |
|---|------|------|-------|-------------|
| 1 | `jarvis_core.py` | 38.8 KB | 1,051 | Core engine — 10 modules |
| 2 | `jarvis_api.py` | 20.1 KB | 555 | FastAPI server — 30 endpoints |
| 3 | `jarvis_apify_global.py` | 32.6 KB | ~850 | Global Apify integration |
| 4 | `jarvis_scan_api.py` | 12.0 KB | ~350 | Scan API router — 14 endpoints |
| 5 | `jarvis_mcp.py` | 28.1 KB | 686 | Claude Code / MCP bridge |
| 6 | `jarvis_dashboard_v2.html` | 40.4 KB | 734 | Dashboard UI (API-connected) |
| 7 | `jarvis_dashboard.html` | 26.1 KB | ~500 | Dashboard UI (static demo) |
| 8 | `jarvis_database_schema.sql` | 10.8 KB | ~200 | PostgreSQL schema (15 tables) |
| 9 | `requirements.txt` | 184 B | 6 | Python dependencies |
| 10 | `Dockerfile` | 317 B | 10 | Docker image definition |
| 11 | `docker-compose.yml` | 556 B | 15 | Docker Compose config |
| 12 | `.env.example` | 160 B | 5 | Environment variable template |
| | **Total** | **~210 KB** | **~5,000** | |

---

## What's Next (Future Enhancements)

- **WhatsApp Business API** — Automated client outreach via Twilio/360dialog
- **Telegram Bot** — Command interface for JARVIS on mobile
- **Authentication** — JWT-based user auth with role management
- **PostgreSQL Migration** — Production database with connection pooling
- **Redis Caching** — Cache scan results and frequently accessed data
- **Celery Workers** — Background task queue for heavy operations
- **Stripe Integration** — Automated billing for agency clients
- **Multi-tenant** — Support multiple agency accounts
- **AI Voice Interface** — Voice commands via Whisper API
- **Analytics Dashboard** — Advanced charts with historical data

---

*Built with JARVIS AI Agency OS — Your AI-powered agency management platform.*
