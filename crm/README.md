# TKVibes CRM — Employee Dashboard + Admin Panel

A PHP-based CRM for TKVibes Agency employees. Integrates with the lead engine (Google Sheets → CRM sync) and provides dashboards for employees and admins.

## Architecture

```
crm/                     # → tkvibes.com/crm/
├── index.php            # Login
├── dashboard.php        # Employee dashboard (lead list + detail + actions)
├── admin.php            # Admin dashboard (overview, manage employees, all leads)
├── install.php          # First-run setup wizard
├── logout.php           # Logout
├── cron.php             # CLI/cron job: archive, cleanup, sync
├── config.sample.php    # Configuration template (copy to config.local.php)
├── config.local.php     # (gitignored) Actual config — DB creds, API key, etc.
├── .htaccess            # Security: deny access to config, DB, data/
├── .gitignore
├── data/                # SQLite database location (gitignored)
├── lib/
│   ├── db.php           # PDO connection + schema auto-creation
│   ├── auth.php         # Session-based auth, roles
│   ├── functions.php    # Helpers: queries, escaping, formatting
│   └── GoogleSheetsClient.php  # Lightweight Google Sheets API (no deps)
├── api/
│   ├── sync.php         # Engine webhook: POST leads from Python lead engine
│   ├── leads.php        # Employee actions: tag, note, call log
│   └── employees.php    # GET mapping for engine to fetch employee→regions
├── templates/
│   └── lead_detail.php  # Lead detail view (included by dashboard.php)
└── assets/
    ├── css/crm.css      # Dark theme stylesheet
    └── js/crm.js        # Dashboard interactions, AJAX, keyboard shortcuts
```

## Setup

### 1. Deploy to Hostinger

The `crm/` folder is part of the tkvibes-agency repo. Push to `main` → GitHub Actions deploys to Hostinger `public_html/`. The CRM will be at `https://tkvibes.com/crm/`.

### 2. Run Setup Wizard

Visit `https://tkvibes.com/crm/install.php` and follow the steps:

1. **Database**: Choose SQLite (zero-config, recommended) or MySQL
2. **Security**: Auto-generated secret key + API key
3. **Admin account**: Create your first admin user

### 3. Configure the Lead Engine

In `config.yaml` of the lead engine, set:

```yaml
crm:
  api_url: "https://tkvibes.com/crm"
  api_key: "<the-api-key-from-install>"
```

## Employee Workflow

1. **Login** → assigned leads appear in the dashboard
2. **Filter** by status (New / Qualified / Callback / Not Qualified) or search
3. **Click a lead** → view full detail: pain points, recommended pitch, all contact info, notes
4. **Actions**:
   - ✅ **Qualified** → lead stays in dashboard
   - 📅 **Callback Pending** → visible until resolved
   - ❌ **Not Qualified** → auto-removed after 24 hours
   - 📝 **Add Note** → log call outcome, follow-up
   - 📞 **Call** / 💬 **WhatsApp** → instant contact buttons
   - 🎯 **Cold Call Training** → instant access to training manual

## Admin Workflow

1. **Overview** → stats dashboard (total leads, by status, by region, by employee)
2. **Employees** → add/edit/delete employees, assign regions (e.g. "Delhi NCR" → "India")
3. **All Leads** → view, search, filter, export CSV, delete leads
4. **Sync from Sheet** → import leads from Google Sheet (if service account configured)
5. **Export** → CSV download of filtered leads

## Cron Jobs

On Hostinger, set up a cron job to run hourly:

```bash
php /home/u1234567/public_html/crm/cron.php
```

This:
- Archives NOT_QUALIFIED leads older than 24h
- Cleans up activity logs older than 90 days
- Optionally syncs new leads from Google Sheet

## 24h Removal Rule

Leads tagged as "Not Qualified" disappear from employee dashboards 24 hours after tagging. They remain in the admin view and are archived (can be recovered if needed). Both the cron job and the dashboard query enforce this rule.

## API Key Security

The sync API (`api/sync.php` and `api/employees.php`) is protected by the shared API key from `config.local.php`. The lead engine sends this key in the POST body or GET parameter. Keep this key secret — it's the only authentication for the sync endpoint.

## Future Features

- Call outcome tracking (callback scheduled → date picker)
- Performance stats per employee (calls made, qualified rate)
- Email notifications on new lead assignment
- Lead scoring based on activity
- Bulk actions (multi-select → tag/assign)
- API for external integrations