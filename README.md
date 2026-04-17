# JARVIS Operator Cockpit

JARVIS is now positioned as an **agency-owned operator cockpit** for **Australia-first, global English markets**.

The product focus in this phase is not “an autonomous AI agency that does everything.” The current focus is:

- discovering and mapping candidate businesses
- scoring them for investment and proposal priority
- identifying shortcomings and opportunity gaps
- recommending whether the right next sale is a CRM, customer platform, retention system, or broader service package
- saving operator decisions with notes, ownership, and follow-up actions
- producing structured proposal briefs that can feed downstream delivery

The repo still contains some Turkey-origin references and legacy implementation ideas, especially in older delivery-oriented files. The main dashboard, chat flow, and current decision logic are now aligned to the Australia/global-English direction.

## Product direction

### What JARVIS is now
- A human-in-the-loop cockpit for agency operators.
- A decision engine for candidate evaluation, not a “magic autopilot.”
- An Australia-first commercial layer with global-English fallback.

### What JARVIS is not yet
- A fully autonomous outreach engine.
- A multi-tenant SaaS.
- A complete delivery automation platform.

### Phase 1 operator jobs
1. Discover and map candidates.
2. Compare them and decide which opportunity deserves attention.
3. Convert that decision into a proposal-ready workflow record.

## Current architecture

```text
frontend/jarvis_dashboard_v2.html
    ↓
jarvis_api.py
    ↓
jarvis_core.py
    ├─ market-aware scoring and ROI
    ├─ candidate enrichment and comparison
    ├─ decision persistence
    ├─ proposal brief generation
    └─ playbooks and contracts
    ↓
PostgreSQL
```

Supporting components:

- `jarvis_serpapi_global.py`: live Google Maps business discovery
- `jarvis_scan_api.py`: broader background scanning endpoints
- `jarvis_mcp.py`: downstream delivery lane and legacy MCP-oriented implementation templates

## Key capabilities

### 1. Market-aware decision engine
JARVIS now separates:

- presentation locale
- market/commercial defaults
- sector playbook logic

The default market profile is Australia, with support profiles for:

- Australia
- United States
- United Kingdom
- New Zealand
- Turkey

Each market profile carries:

- locale
- currency
- package price bands
- contract defaults
- outreach defaults
- sector assumption notes

### 2. Structured candidate analysis
Every mapped candidate can now carry:

- `investment_score`
- `commercial_priority`
- `proposal_readiness`
- `shortcomings`
- `strengths`
- `gap_scores`
  - acquisition
  - retention
  - conversion
  - operations
  - visibility
- `platform_type`
- `recommended_service_type`
- `recommended_delivery_shape`
- `fit_summary`
- `risk_summary`
- `decision_trace`

### 3. Persistent operator decisions
Candidate decisions are no longer chat-only. Saved records now support:

- `invest` / `monitor` / `reject`
- recommended platform
- recommended service
- proposal recommended or not
- owner
- next action
- follow-up date
- confidence
- operator notes

These records are stored in the `candidate_decisions` table.

### 4. Proposal intelligence
JARVIS can now return a structured proposal brief for a focused lead:

- target business
- recommended platform type
- recommended service type
- recommended delivery shape
- proposal readiness
- fit summary
- risk summary
- commercial priority
- problem statement
- expected business outcome
- proposed scope
- decision trace

### 5. Operator-first dashboard
`frontend/jarvis_dashboard_v2.html` is now built around:

- live candidate map
- focused lead panel
- pooled comparison table
- saved decision worklist
- market-aware ROI view
- settings for market defaults

## Current workflow

### Live search and comparison
1. Ask JARVIS in chat for businesses in a suburb or location.
2. Results are plotted immediately as circular markers on the map.
3. Hover to inspect public signals.
4. Click a marker or comparison row to focus that lead.
5. Review the structured decision panel.

### Operator decision
1. Choose `invest`, `monitor`, or `reject`.
2. Review or edit platform and service recommendations.
3. Set owner, next action, follow-up date, and confidence.
4. Save the decision into the worklist.

### Proposal handoff
1. Load the proposal brief for the focused lead.
2. Use the structured scope and rationale for downstream delivery.
3. Keep MCP / Cloud Code as a secondary execution lane, not the main product promise.

## API overview

### Core system
- `GET /health`
- `GET /api/market-config`
- `GET /api/dashboard/stats`
- `GET /api/dashboard/pipeline`
- `GET /api/dashboard/decision-overview`

### Candidate intelligence
- `POST /api/command`
- `POST /api/candidates/compare`
- `POST /api/candidates/proposal`
- `POST /api/candidates/decision`
- `GET /api/candidates/decisions`
- `GET /api/candidates/decision/{lead_key}`
- `PUT /api/candidates/decision/{lead_key}/workflow`

### Leads and analysis
- `POST /api/leads/score`
- `POST /api/leads/analyze`
- `POST /api/leads/save`
- `GET /api/leads`
- `GET /api/leads/{lead_id}`

### Commercial tooling
- `POST /api/roi`
- `GET /api/roi/compare/{sector}`
- `POST /api/pitch`
- `POST /api/contracts/generate`
- `POST /api/revenue/plan`

### Scanning
- `POST /api/v1/scan/start`
- `GET /api/v1/scan/status/{scan_id}`
- `GET /api/v1/scan/results/{scan_id}`

## Running locally

### 1. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Create `.env` with at least:

```env
SERPAPI_API_KEY=your_serpapi_key
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password
OPENAI_API_KEY=optional_for_chat_fallback_and_tts
JARVIS_DEFAULT_MARKET=AU
```

Notes:

- PostgreSQL is the current persistence target.
- `OPENAI_API_KEY` is optional for the operator workflow, but needed for the OpenAI-backed general chat fallback and TTS endpoint.
- SerpApi is required for live business search from chat.

### 3. Start the backend

```bash
uvicorn jarvis_api:app --reload --host 0.0.0.0 --port 8000
```

Important URLs:

- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### 4. Start the frontend

Serve the `frontend/` directory with any static server, for example:

```bash
python3 -m http.server 3000 --directory frontend
```

Then open:

- `http://localhost:3000/jarvis_dashboard_v2.html`

## Testing

Run the targeted chat-command suite:

```bash
./venv/bin/pytest tests/test_chat_commands.py -q
```

Recommended verification flow:

1. Search for businesses through chat.
2. Confirm markers appear on the map.
3. Focus one candidate from the map or comparison table.
4. Save an operator decision.
5. Confirm the decision appears in the worklist.
6. Confirm the structured proposal brief is visible in the selected-candidate panel.

## Repo map

- `jarvis_core.py`: market profiles, scoring, playbooks, ROI, contracts, decision persistence, proposal logic
- `jarvis_api.py`: REST API for the cockpit
- `jarvis_serpapi_global.py`: live business search
- `jarvis_scan_api.py`: scan endpoints
- `frontend/jarvis_dashboard_v2.html`: operator cockpit UI
- `jarvis_mcp.py`: downstream delivery / legacy MCP layer
- `tests/test_chat_commands.py`: targeted tests for the chat-driven decision workflow

## Near-term roadmap

### Now
- stronger decision quality
- better candidate comparison
- clearer operator workflow
- Australia-first commercial defaults

### Next
- richer CRM workflow state
- proposal templates
- better sector depth
- stronger delivery handoff

### Later
- autonomous outreach
- deeper execution automation
- fuller delivery orchestration

