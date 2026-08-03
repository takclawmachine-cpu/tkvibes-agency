# CRM — Deep Reference

## Architecture
`crm/` → `tkvibes.in/crm/` — PHP 8.x, SQLite (zero-config)

```
crm/
├── index.php         # Login
├── dashboard.php     # Employee dashboard
├── admin.php         # Admin panel (leads, employees, stats, export)
├── install.php       # First-run setup wizard
├── logout.php        # Logout
├── cron.php          # Hourly: archive NOT_QUALIFIED > 24h, cleanup logs > 90d
├── config.sample.php # Template (copy to config.local.php)
├── data/             # SQLite DB (gitignored)
├── lib/
│   ├── db.php        # PDO + schema auto-creation
│   ├── auth.php      # Session auth, roles (admin/employee)
│   ├── functions.php # Helpers
│   └── GoogleSheetsClient.php  # Lightweight Sheets API (no deps)
├── api/
│   ├── sync.php      # POST lead engine webhook (key-protected)
│   ├── leads.php     # Employee actions: tag, note, call log
│   └── employees.php # GET mapping: employee→regions
├── templates/
│   └── lead_detail.php
└── assets/
    ├── css/crm.css   # Dark theme
    └── js/crm.js     # AJAX, keyboard shortcuts
```

## API Endpoints
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/crm/api/sync.php` | POST | API key | Receive leads from engine |
| `/crm/api/leads.php` | POST | Session | Tag/note/call log |
| `/crm/api/employees.php` | GET | API key | Employee→region mapping |

## Deploy
Part of main repo — push to `main` → GitHub Actions deploys everything including `crm/`.

## Employee Workflow
1. Login → see assigned leads (filterable by status, searchable)
2. Click lead → detail: pain points, pitch, contact info, notes
3. Actions: ✅ Qualified · 📅 Callback · ❌ Not Qualified (auto-removed 24h) · 📝 Note · 📞 Call · 💬 WhatsApp · 🎯 Cold Call Training
4. NOT_QUALIFIED leads auto-archive after 24h (cron or dashboard query)

## Admin Workflow
- Stats dashboard (total, by status, region, employee)
- Employee CRUD (add/edit/delete, assign regions)
- All leads view (search, filter, export CSV, delete)
- Sync from Google Sheet (manual trigger)
- Export CSV