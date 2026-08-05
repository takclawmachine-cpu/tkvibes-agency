# TKVibes AI CRM — Architecture Diagrams

> **Note:** All diagrams below are in Mermaid format. Render with any Mermaid-compatible viewer (GitHub, VS Code, mermaid.live, Obsidian).

---

## 1. Current State Architecture (High Level)

```mermaid
graph TB
    subgraph "LEAD ENGINE (Python 3.11)"
        GP["Google Places API"]
        PY_RUN["run.py Pipeline<br/>discover → enrich → score → assign"]
        PY_GEN["generate_proposals.py<br/>template-v2.html + OpenRouter AI"]
        PY_GIT["git_publish.py<br/>git push → build raw URLs"]
        PY_PUSH["push_leads() → sync.php<br/>per-lead HTTP POST"]
        PY_SHEET["SheetWriter (gspread)<br/>upsert to Sheets"]
    end

    subgraph "CRM (PHP 8.x on Hostinger)"
        PHP_DB[("SQLite/MySQL<br/>47-col leads table<br/>proposals HTML in DB")]
        SYNC["sync.php<br/>bulk lead upsert"]
        LEADS["leads.php<br/>tag/note/call/update"]
        PROPOSALS["proposals.php<br/>upload + job queue"]
        EMPLOYEES["employees.php<br/>region mapping"]
        CRON["cron.php (5 tasks)<br/>sheet sync, write-back, job recovery"]
        AUTH["auth.php<br/>session-based login"]
        SHEETS_CLIENT["GoogleSheetsClient.php<br/>JWT auth, no caching"]
        U2U3["u2.php / u3.php<br/>file upload endpoints"]
    end

    subgraph "GOOGLE WORKSPACE"
        GSUITE["Google Sheets (Leads tab)<br/>Master + per-job worksheets"]
    end

    subgraph "VERSION CONTROL"
        GH["GitHub Repo<br/>raw.githubusercontent.com"]
        GITHUB_ACTIONS["GitHub Actions<br/>FTP mirror → Hostinger"]
    end

    subgraph "DATA HANDOFF"
        JSON_EXPORT["leads_export.json<br/>file-based handoff"]
        GEN_RESULTS["_generation_results.json<br/>empty lead_key bug"]
    end

    %% Data flows
    GP -->|places.googleapis.com| PY_RUN
    PY_RUN -->|enrich/score| PY_GEN
    PY_GEN -->|HTML files| JSON_EXPORT
    PY_GEN -->|HTML files| GEN_RESULTS
    PY_GIT -->|copy + git push| GH
    PY_GIT -->|POST per-lead| SYNC
    PY_PUSH -->|POST batch| SYNC
    PY_SHEET -->|gspread API| GSUITE

    PY_GEN -->|reads| JSON_EXPORT
    PY_GIT -->|reads| GEN_RESULTS
    PY_GIT -->|reads| JSON_EXPORT

    SYNC -->|INSERT/UPDATE| PHP_DB
    LEADS -->|field updates| PHP_DB
    LEADS -->|sheets_writeback| GoogleSheetsClient
    CRON -->|import from| GSUITE
    CRON -->|write-back to| GSUITE
    CRON -->|recover jobs| PHP_DB
    GoogleSheetsClient -->|JWT token| GoogleAPIs["Google APIs"]

    SYNC -->|auto-create job| PHP_DB
    PROPOSALS -->|POST HTML| PHP_DB
    PROPOSALS -->|mark completed| PHP_DB

    GH -->|raw URLs| SYNC
    GITHUB_ACTIONS -->|lftp FTPS mirror| Hostinger["Hostinger /public_html/"]

    U2U3 -->|write files| Hostinger

    classDef engine fill:#1e3a5c,stroke:#475569,color:#f0f9ff
    classDef crm fill:#581c87,stroke:#a855f7,color:#faf5ff
    classDef store fill:#713f12,stroke:#d97706,color:#fef3c7
    classDef flow fill:#064e3b,stroke:#22c55e,color:#dcfce7
    classDef danger fill:#7f1d1d,stroke:#ef4444,color:#fee2e2

    class GP,PY_RUN,PY_GEN,PY_GIT,PY_PUSH,PY_SHEET engine
    class SYNC,LEADS,PROPOSALS,EMPLOYEES,CRON,AUTH,SHEETS_CLIENT,U2U3 crm
    class PHP_DB,GSUITE,GH,JSON_EXPORT,GEN_RESULTS store
    class Hostinger,GoogleAPIs flow
```

---

## 2. Current State Data Flow (Detailed)

```mermaid
sequenceDiagram
    participant GP as Google Places API
    participant LE as Lead Engine (Python)
    participant CRM as CRM (PHP/SQLite)
    participant GS as Google Sheets
    participant DB as SQLite DB
    participant GH as GitHub
    participant HI as Hostinger

    Note over LE,DB: PHASE 1: Discovery

    GP->>LE: Text Search API<br/>(cities × categories)
    LE->>LE: enrich() — normalize phone, classify website
    LE->>LE: score_lead() — points-based scoring
    LE->>LE: dedupe() — fuzzy name match within city
    LE->>LE: assign_employees() — country_assignment from config

    Note over LE,DB: PHASE 2: Three-Way Sync (non-transactional)

    LE->>CRM: POST sync.php<br/>(batch upsert, per-lead HTTP)
    CRM->>DB: INSERT/UPDATE leads<br/>(ON CONFLICT DO UPDATE)<br/>Auto-create proposal_generation_jobs
    CRM-->>LE: {added: N, updated: M, total: 40}

    LE->>GS: SheetWriter.upsert()<br/>(append new leads only)
    LE->>GS: SheetWriter.write_job()<br/>(clear + full rewrite of job tab)

    Note over LE,DB: PHASE 3: Proposal Generation

    LE->>LE: generate_proposals.py<br/>(template-v2.html + AI spec)
    LE->>LE: git_publish.py<br/>(copy to "Sample Webpages/" dir + git push)
    LE->>CRM: POST proposals.php<br/>(HTML stored in DB LONGTEXT)
    CRM->>DB: INSERT/UPDATE proposals<br/>(full HTML in column)
    CRM->>DB: UPDATE leads SET sample_site_url<br/>(hardcoded GitHub URL)
    CRM->>DB: UPDATE proposal_generation_jobs<br/>(mark completed)

    Note over LE,HI: PHASE 4: Hostinger Deployment

    GITHUB->>HI: GitHub Actions<br/>(lftp mirror to /public_html/)
    
    Note over LE,HI: Alternative: Direct Upload

    LE->>HI: upload_proposals.py → u2.php<br/>(base64 + text/plain bypass)
    LE->>HI: deploy_crm.py → u3.php<br/>(PHP file deployment)
```

---

## 3. Target State Architecture (Post-Refactor)

```mermaid
graph TB
    subgraph "AGENT 1: Lead Discovery Agent"
        direction TB
        A1_INPUT["Input:<br/>config.yaml (cities, categories)"]
        A1["LeadEngineAgent<br/>trace_id: LEAD-{uuid}"]
        A1_API["Google Places API<br/>+ tenacity retry"]
        A1_OUTPUT["Output:<br/>leads_batch.{json,trace_id}"]
        A1_INPUT --> A1 --> A1_API --> A1_OUTPUT
        classDef agent1 fill:#1e3a5c,stroke:#38bdf8,color:#f0f9ff
        class A1,A1_INPUT,A1_API,A1_OUTPUT agent1
    end

    subgraph "AGENT 2: Lead Processing Agent"
        direction TB
        A2_INPUT["Input:<br/>leads_batch.json"]
        A2["ProcessingAgent<br/>trace_id: PROC-{uuid}"]
        A2_ENRICH["enrich.py<br/>(phone, website classify)"]
        A2_SCORE["score.py<br/>(points-based tiering)"]
        A2_DEDUPE["dedupe.py<br/>(exact + fuzzy)"]
        A2_ASSIGN["assign.py<br/>(country/region → employee_id)"]
        A2_OUTPUT["Output:<br/>processed_leads.{json,trace_id}"]
        A2_INPUT --> A2 --> A2_ENRICH --> A2_SCORE --> A2_DEDUPE --> A2_ASSIGN --> A2_OUTPUT
        classDef agent2 fill:#581c87,stroke:#a855f7,color:#faf5ff
        class A2,A2_INPUT,A2_ENRICH,A2_SCORE,A2_DEDUPE,A2_ASSIGN,A2_OUTPUT agent2
    end

    subgraph "AGENT 3: Proposal Generation Agent"
        direction TB
        A3_INPUT["Input:<br/>proc_leads.json"]
        A3["ProposalAgent<br/>trace_id: PROP-{uuid}"]
        A3_AI["ai_site_generator.py<br/>(LLM: layout + content)"]
        A3_FILE["FileStore<br/>(S3-compatible or<br/>Hostinger file store)"]
        A3_OUTPUT["Output:<br/>proposals/{slug}/<br/>+ db: proposal_jobs"]
        A3_INPUT --> A3 --> A3_AI --> A3_FILE --> A3_OUTPUT
        classDef agent3 fill:#713f12,stroke:#d97706,color:#fef3c7
        class A3,A3_INPUT,A3_AI,A3_FILE,A3_OUTPUT agent3
    end

    subgraph "AGENT 4: CRM Sync Agent"
        direction TB
        A4_INPUT["Input:<br/>proc_leads.json"]
        A4["CRMSyncAgent<br/>trace_id: CRM-{uuid}"]
        A4_DB["MySQL/PostgreSQL<br/>(single source of truth)"]
        A4_OUTPUT["Output:<br/>db: leads table<br/>+ system_logs"]
        A4_INPUT --> A4 --> A4_DB --> A4_OUTPUT
        classDef agent4 fill:#064e3b,stroke:#22c55e,color:#dcfce7
        class A4,A4_INPUT,A4_DB,A4_OUTPUT agent4
    end

    subgraph "AGENT 5: Deployment Agent"
        direction TB
        A5_INPUT["Input:<br/>proposals/{slug}/"]
        A5["DeployAgent<br/>trace_id: DEPLOY-{uuid}"]
        A5_FTP["Hostinger FTPS<br/>(single target)"]
        A5_OUTPUT["Output:<br/>proposals on Hostinger<br/>+ CRM URL update"]
        A5_INPUT --> A5 --> A5_FTP --> A5_OUTPUT
        classDef agent5 fill:#450a0a,stroke:#ef4444,color:#fee2e2
        class A5,A5_INPUT,A5_FTP,A5_OUTPUT agent5
    end

    subgraph "SHARED INFRASTRUCTURE"
        DB_SHARED["MySQL Database<br/>(single source of truth)"]
        LOGS["Structured Logs<br/>(trace_id + JSON)"]
        API_GATE["API Gateway<br/>(rate limit + auth)"]
        CONFIG["Central Config<br/>(env vars + vault)"]
    end

    A1_OUTPUT --> A2_INPUT
    A2_OUTPUT --> A3_INPUT
    A2_OUTPUT --> A4_INPUT
    A3_OUTPUT --> A5_INPUT
    A4 --> A4_DB
    A5 --> A4_DB

    A1 -.-> LOGS
    A2 -.-> LOGS
    A3 -.-> LOGS
    A4 -.-> LOGS
    A5 -.-> LOGS

    classDef shared fill:#1e293b,stroke:#64748b,color:#e2e8f0
    class DB_SHARED,LOGS,API_GATE,CONFIG shared
```

---

## 4. Agent Responsibility Matrix

```mermaid
graph LR
    subgraph "Agent Responsibilities (Post-Refactor)"
        LEAD["LeadEngineAgent<br/><b>Input:</b> config.yaml<br/><b>Output:</b> leads_batch.json<br/><b>Tools:</b> Google Places API, httpx<br/><b>No writes to:</b> CRM DB, Sheets, files"]
        PROC["ProcessingAgent<br/><b>Input:</b> leads_batch.json<br/><b>Output:</b> processed_leads.json<br/><b>Tools:</b> enrich, score, dedupe, assign<br/><b>No writes to:</b> CRM DB, Sheets, GitHub"]
        PROP["ProposalAgent<br/><b>Input:</b> processed_leads.json<br/><b>Output:</b> proposals/{slug}/<br/><b>Tools:</b> OpenRouter LLM, FileStore<br/><b>No writes to:</b> CRM DB, Sheets"]
        CRM["CRMSyncAgent<br/><b>Input:</b> processed_leads.json<br/><b>Output:</b> CRM DB<br/><b>Tools:</b> MySQL, Google Sheets API<br/><b>No writes to:</b> proposals/{slug}/, GitHub"]
        DEPLOY["DeployAgent<br/><b>Input:</b> proposals/{slug}/<br/><b>Output:</b> Hostinger /proposals/ + CRM URL update<br/><b>Tools:</b> FTPS, CRM API<br/><b>No writes to:</b> CRM DB directly (API only)"]
    end

    LEAD == "leads_batch.json\n(trace_id)" ==> PROC
    PROC == "processed_leads.json\n(trace_id)" ==> PROP
    PROC == "processed_leads.json\n(trace_id)" ==> CRM
    PROP == "proposals/{slug}/\n(trace_id)" ==> DEPLOY
    DEPLOY ==>|"PATCH /leads/{lead_key}"| CRM

    classDef agent fill:#1e3a5c,stroke:#38bdf8,color:#f0f9ff,stroke-width:2
    classDef flow fill:#38bdf8,stroke:#38bdf8,color:#0f172a,stroke-width:2
    class LEAD,PROC,PROP,CRM,DEPLOY agent
```

---

## 5. Deployment Conflict Diagram (Current State Problem)

```mermaid
graph TD
    subgraph "FIVE COMPETING DEPLOYMENT PATHS"
        P1["FLOW A: Lead Engine → GitHub<br/>generate_proposals → git_publish<br/>→ git commit+push<br/>→ raw.githubusercontent.com URLs<br/>→ sync.php updates CRM"]
        P2["FLOW B: GitHub Actions → Hostinger<br/>git push → deploy.yml<br/>→ lftp mirror to /public_html/<br/>→ overwrites everything"]
        P3["FLOW C: Direct Upload → Hostinger<br/>upload_proposals.py → u2.php<br/>→ /proposals/sample-website/<br/>→ batch_upload_proposals.py<br/>→ git commit (but no CRM update)"]
        P4["FLOW D: CRM Deploy → Hostinger<br/>deploy_crm.py → u3.php<br/>→ /crm/*.php files<br/>→ overwrites PHP code"]
        P5["FLOW E: Server-side Local Deploy<br/>deploy_proposals.php (cron)<br/>→ scans DB for GitHub URLs<br/>→ copies to /proposals/<br/>→ OVERWRITES GitHub URLs in DB<br/>→ breaks proxy_proposal.php"]
    end

    P1 -.->|"Competing URL formats"| P5
    P2 -.->|"Overwrites files from P1,P3"| P5
    P3 -.->|"No CRM update, relies on P5"| P5
    P4 -.->|"Overwrites CRM code while cron runs"| P1

    classDef flowA fill:#1e3a5c,stroke:#38bdf8
    classDef flowB fill:#581c87,stroke:#a855f7
    classDef flowC fill:#713f12,stroke:#d97706
    classDef flowD fill:#064e3b,stroke:#22c55e
    classDef flowE fill:#7f1d1d,stroke:#ef4444,color:#fee2e2
    classDef conflict fill:#7f1d1d,stroke:#ef4444,stroke-width:3,color:#fee2e2

    class P1 flowA
    class P2 flowB
    class P3 flowC
    class P4 flowD
    class P5 conflict

    classDef conflict-arrow stroke:#ef4444,stroke-width:3,stroke-dasharray:8,4
    P1 -.->|conflict| P5
    P2 -.->|conflict| P5
    P3 -.->|conflict| P5
    P4 -.->|conflict| P1
```

---

## 6. Security Posture Diagram

```mermaid
graph TB
    subgraph "Auth & Session"
        AUTH["auth.php<br/>Session-based auth<br/>CSRF: ✅ Fixed<br/>Session timeout: ❌ Missing<br/>Cookie flags: ❌ Missing (Secure/SameSite<br/>Session fixation: ✅ session_regenerate_id"]
        ADMIN["admin.php<br/>Admin panel<br/>Password reset: ⚠️ prompt()<br/>CSRF: ✅ Fixed<br/>Rate limit: ❌ Missing"]
    end

    subgraph "API Security"
        SYNC["sync.php<br/>API key auth ✅<br/>Rate limit: ❌<br/>Input validation: ⚠️ Minimal<br/>Batch size limit: ❌"]
        LEADS_API["leads.php<br/>Session + API key<br/>CSRF: ✅ Fixed<br/>JSON body: ✅ Fixed<br/>Field name SQLi: ✅ Fixed<br/>Rate limit: ❌"]
        PROPOSALS_API["proposals.php<br/>API key auth ✅<br/>Auto-create leads: ⚠️ Creates orphans<br/>Hardcoded GH URL: ❌"]
        EMP_API["employees.php<br/>API key auth ✅<br/>Rate limit: ❌"]
        U2["u2.php<br/>API key auth ✅ (Fixed)<br/>Path traversal: ⚠️ Regex only<br/>File type: ❌ No restriction<br/>Audit log: ❌ No"]
        U3["u3.php<br/>API key auth ✅ (Fixed)<br/>Writes to /crm/: ⚠️ Any file<br/>Path traversal: ⚠️ Same regex gap"]
    end

    subgraph "Credential Management"
        CONFIG["config.yaml<br/>API key in plaintext ❌<br/>gitignored: ✅ (.env only)<br/>BUT deploy_crm.py has hardcoded key ❌"]
        ENV["process_proposal_jobs.py<br/>Hardcoded API key ❌<br/>batch_upload_proposals.py<br/>Hardcoded API key ❌"]
        SAKEY["Google service account JSON<br/>In repo (credentials/)<br/>gitignored in crm/ ✅<br/>NOT gitignored in tkvibes-lead-engine/ ❌"]
    end

    subgraph "Network Security"
        HTTPS["HTTPS: ⚠️ Not enforced in .htaccess<br/>(need to verify)"]
        RATE["Rate limiting: ❌ None on any endpoint"]
        HSTS["HSTS header: ❌ Not configured"]
        IPFILTER["IP filtering: ❌ None"]
    end

    AUTH -- session --> ADMIN
    AUTH -- session --> LEADS_API

    SYNC --> CONFIG
    LEADS_API --> CONFIG
    PROPOSALS_API --> CONFIG
    EMP_API --> CONFIG
    U2 --> CONFIG
    U3 --> CONFIG
    CONFIG --> ENV
    CONFIG --> SAKEY

    HTTPS --> RATE
    RATE --> HSTS
    HSTS --> IPFILTER

    classDef ok fill:#064e3b,stroke:#22c55e,color:#dcfce7
    classDef warn fill:#78350f,stroke:#f59e0b,color:#fef3c7
    classDef critical fill:#7f1d1d,stroke:#ef4444,color:#fee2e2
    classDef open fill:#1e293b,stroke:#64748b,color:#e2e8f0,stroke-width:2

    class AUTH,LEADS_API,EMP_API ok
    class ADMIN,PROPOSALS_API,U2,U3,SAKEY,HTTPS,RATE warn
    class SYNC,CONFIG,ENV,U3,CONFIG,ENV,U2,U3 critical
    class IPFILTER,HSTS open
```

---

## 7. Three Data Stores → Single Source of Truth Migration

```mermaid
graph LR
    subgraph "CURRENT: Three Data Stores"
        DB1["SQLite DB<br/>(CRM source of truth)<br/>leads, proposals, activities"]
        SHEET1["Google Sheets<br/>(Lead engine source)<br/>Leads tab + per-job tabs"]
        JSON1["JSON Files<br/>(handoff format)<br/>leads_export.json<br/>_generation_results.json"]
    end

    subgraph "CURRENT: Data Flow (Circular)"
        F1["Engine writes<br/>to DB via sync.php"]
        F2["Engine writes<br/>to Sheets via gspread"]
        F3["CRM reads from<br/>Sheets (cron task #3)"]
        F4["CRM writes back<br/>to Sheets (cron task #4)"]
        F5["Engine reads<br/>from JSON export"]
    end

    DB1 --- F1
    SHEET1 --- F2
    SHEET1 --- F3
    SHEET1 --- F4
    JSON1 --- F5
    F1 --- DB1
    F2 --- SHEET1
    F3 --- DB1
    F4 --- SHEET1

    style DB1 fill:#7f1d1d,stroke:#ef4444
    style SHEET1 fill:#7f1d1d,stroke:#ef4444
    style JSON1 fill:#7f1d1d,stroke:#ef4444

    subgraph "TARGET: Single Source of Truth"
        DB2["MySQL/PostgreSQL<br/>(single source of truth)<br/>leads, proposals<br/>(file paths, not HTML)<br/>activities, system_logs<br/>proposal_generation_jobs"]
    end

    subgraph "TARGET: Data Flow (Linear)"
        G1["Engine discovers leads"]
        G2["Engine processes + enriches"]
        G3["Engine writes to DB via sync.php (transactional)"]
        G4["CRM reads from DB (no sheet sync needed)"]
        G5["Proposal agent reads from DB jobs queue"]
        G6["Deploy agent writes files, URL to DB"]
    end

    G1 --> G2 --> G3 --> DB2
    DB2 --> G4
    DB2 --> G5
    G5 --> G6 --> DB2

    style DB2 fill:#064e3b,stroke:#22c55e
```
