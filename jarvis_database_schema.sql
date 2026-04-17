
-- ============================================
-- JARVIS AI AGENCY OS - DATABASE SCHEMA
-- ============================================

-- 1. USERS (Agency Owners)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    agency_name VARCHAR(255),
    phone VARCHAR(50),
    language VARCHAR(10) DEFAULT 'tr',
    avatar_url TEXT,
    revenue_goal DECIMAL(12,2) DEFAULT 0,
    claude_code_token TEXT,
    apify_api_key TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. LEADS (Potential Customers found via Map/Scraping)
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    business_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),          -- 'dental', 'accounting', 'auto_gallery', 'construction', 'gym', etc.
    niche VARCHAR(100),
    address TEXT,
    city VARCHAR(100),
    district VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Turkey',
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    phone VARCHAR(50),
    email VARCHAR(255),
    website VARCHAR(500),
    instagram_url VARCHAR(500),
    google_rating DECIMAL(2,1),
    google_review_count INTEGER DEFAULT 0,
    potential_score INTEGER DEFAULT 0,   -- 0-100 scoring
    score_breakdown JSONB,               -- detailed scoring factors
    status VARCHAR(50) DEFAULT 'new',    -- new, contacted, demo_scheduled, proposal_sent, converted, lost
    source VARCHAR(50) DEFAULT 'map_scan', -- map_scan, manual, referral, import
    notes TEXT,
    last_contacted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. CUSTOMERS (Converted Leads)
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    lead_id UUID REFERENCES leads(id),
    business_name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    sector VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    website VARCHAR(500),
    package_type VARCHAR(50),        -- 'starter', 'professional', 'premium'
    monthly_fee DECIMAL(10,2),
    contract_start DATE,
    contract_end DATE,
    status VARCHAR(50) DEFAULT 'active', -- active, paused, churned
    total_revenue DECIMAL(12,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. INTERACTIONS (All communication logs)
CREATE TABLE interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    lead_id UUID REFERENCES leads(id),
    customer_id UUID REFERENCES customers(id),
    channel VARCHAR(50) NOT NULL,     -- 'email', 'whatsapp', 'instagram', 'phone', 'in_person'
    direction VARCHAR(10),            -- 'inbound', 'outbound'
    interaction_type VARCHAR(50),     -- 'cold_outreach', 'follow_up', 'demo', 'proposal', 'support'
    subject VARCHAR(255),
    content TEXT,
    summary TEXT,                     -- AI-generated summary
    outcome VARCHAR(100),
    scheduled_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. PLAYBOOKS (Sector-specific strategies)
CREATE TABLE playbooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    sector VARCHAR(100) NOT NULL,
    description TEXT,
    strategy_type VARCHAR(100),       -- 'database_reactivation', 'new_patient_acquisition', 'upsell', etc.
    duration_days INTEGER,
    target_roi_percent INTEGER,
    steps JSONB,                      -- ordered list of steps with timelines
    kpis JSONB,                       -- key performance indicators
    is_template BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 6. OFFERS (Service packages / proposals)
CREATE TABLE offers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    package_type VARCHAR(50),         -- 'starter', 'professional', 'premium'
    description TEXT,
    features JSONB,                   -- list of included features
    price DECIMAL(10,2),
    currency VARCHAR(10) DEFAULT 'TRY',
    roi_estimate JSONB,               -- projected ROI breakdown
    case_study_ids UUID[],
    is_template BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 7. CASE STUDIES (Success stories for pitching)
CREATE TABLE case_studies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    client_name VARCHAR(255),
    challenge TEXT,
    solution TEXT,
    results TEXT,
    metrics JSONB,                    -- { "revenue_increase": "45%", "new_patients": 30, ... }
    testimonial TEXT,
    is_public BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 8. PROJECTS (Active service delivery projects)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    playbook_id UUID REFERENCES playbooks(id),
    offer_id UUID REFERENCES offers(id),
    status VARCHAR(50) DEFAULT 'planning', -- planning, in_progress, delivered, completed, on_hold
    start_date DATE,
    end_date DATE,
    budget DECIMAL(10,2),
    claude_code_project_id VARCHAR(255),   -- linked Claude Code project
    progress_percent INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 9. TASKS (Recurring and one-time tasks)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id),
    customer_id UUID REFERENCES customers(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    task_type VARCHAR(50),            -- 'report', 'outreach', 'setup', 'review', 'meeting'
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, urgent
    status VARCHAR(50) DEFAULT 'pending',  -- pending, in_progress, completed, cancelled
    is_recurring BOOLEAN DEFAULT false,
    recurrence_rule VARCHAR(100),     -- 'every_monday', 'monthly_1st', 'weekly_friday', etc.
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 10. CONTRACTS (Generated contracts)
CREATE TABLE contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id),
    title VARCHAR(255),
    content TEXT,                      -- contract body (HTML/Markdown)
    terms JSONB,                      -- structured terms
    total_value DECIMAL(12,2),
    currency VARCHAR(10) DEFAULT 'TRY',
    status VARCHAR(50) DEFAULT 'draft', -- draft, sent, signed, expired, cancelled
    signed_at TIMESTAMP,
    valid_until DATE,
    pdf_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 11. REVENUE ROADMAP
CREATE TABLE revenue_roadmap (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    target_monthly_revenue DECIMAL(12,2),
    target_annual_revenue DECIMAL(12,2),
    current_mrr DECIMAL(12,2) DEFAULT 0,
    avg_deal_size DECIMAL(10,2),
    required_leads_per_month INTEGER,
    required_demos_per_month INTEGER,
    required_closes_per_month INTEGER,
    conversion_rate_lead_to_demo DECIMAL(5,2),
    conversion_rate_demo_to_close DECIMAL(5,2),
    milestones JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 12. BOARD MEETINGS (AI-powered status reviews)
CREATE TABLE board_meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    meeting_date DATE DEFAULT CURRENT_DATE,
    agenda JSONB,
    summary TEXT,                      -- AI-generated meeting summary
    kpi_snapshot JSONB,               -- snapshot of all KPIs at meeting time
    decisions JSONB,                  -- action items decided
    next_steps JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 13. MAP SCANS (History of lead generation scans)
CREATE TABLE map_scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    sector VARCHAR(100),
    location_query VARCHAR(255),      -- e.g. "İzmir Karşıyaka"
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    radius_km INTEGER DEFAULT 5,
    results_count INTEGER DEFAULT 0,
    leads_generated INTEGER DEFAULT 0,
    scan_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 14. PITCH SCRIPTS (AI-generated sales scripts)
CREATE TABLE pitch_scripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    lead_id UUID REFERENCES leads(id),
    sector VARCHAR(100),
    script_type VARCHAR(50),          -- 'cold_call', 'email', 'whatsapp', 'demo_presentation'
    title VARCHAR(255),
    content TEXT,
    persuasion_tactics JSONB,         -- which tactics are used
    personalization_data JSONB,       -- data used to personalize
    is_template BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 15. SETTINGS
CREATE TABLE settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    setting_key VARCHAR(100) NOT NULL,
    setting_value TEXT,
    category VARCHAR(50),             -- 'integrations', 'preferences', 'notifications'
    UNIQUE(user_id, setting_key)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX idx_leads_user_status ON leads(user_id, status);
CREATE INDEX idx_leads_sector ON leads(sector);
CREATE INDEX idx_leads_score ON leads(potential_score DESC);
CREATE INDEX idx_leads_location ON leads(city, district);
CREATE INDEX idx_customers_user ON customers(user_id);
CREATE INDEX idx_interactions_lead ON interactions(lead_id);
CREATE INDEX idx_interactions_customer ON interactions(customer_id);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_due ON tasks(due_date);
CREATE INDEX idx_projects_user ON projects(user_id);
CREATE INDEX idx_map_scans_user ON map_scans(user_id);
