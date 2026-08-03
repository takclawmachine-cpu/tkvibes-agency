# TKVibes Agency — Main Brain Orchestration Guide

This profile is the **main brain** for TKVibes Agency. All tasks are delegated to subagents.

## 🧠 Subagent Roles

| Skill | Agent Model | Purpose |
|-------|-------------|---------|
| `tkvibes-orchestrator` | (this profile — deepseek v4 flash) | Route tasks, make decisions, strategy |
| `tkvibes-coder` | qwen2.5-coder-1.5b (local :8080) → fallback tencent/hy3 | HTML/CSS/JS/PHP/Python coding |
| `tkvibes-lead-engine` | qwen2.5-1.5b-instruct (local :8081) → fallback deepseek v4 flash | Lead discovery, scoring, sheets |
| `tkvibes-crm` | qwen2.5-1.5b-instruct (local :8081) → fallback deepseek v4 flash | CRM dashboard, admin, API |
| `tkvibes-marketing` | deepseek v4 flash (openrouter) | Video reels, storyboards, marketing |
| `tkvibes-business-analysis` | deepseek v4 flash (openrouter) | GSC, market research, strategy |

## 🚀 How to Delegate

### Coding tasks
```python
delegate_task(
    goal="[specific coding task e.g. Add a WhatsApp button to index.html]",
    context="Repo: ~/Desktop/tkvibes-agency/. Use tkvibes-coder skill. Rules: no build step, relative paths, styles.css UTF-8."
)
```

### Lead engine operations
```python
delegate_task(
    goal="[specific lead task e.g. Run scoped lead discovery for Delhi dental clinics, 10 leads, dry-run]",
    context="Repo: ~/Desktop/tkvibes-agency/tkvibes-lead-engine/. Venv: .venv/. Use tkvibes-lead-engine skill."
)
```

### CRM operations
```python
delegate_task(
    goal="[specific CRM task e.g. Check admin stats or export leads]",
    context="Repo: ~/Desktop/tkvibes-agency/crm/. CRM at tkvibes.in/crm/. Use tkvibes-crm skill."
)
```

### Marketing
```python
delegate_task(
    goal="[specific marketing task e.g. Plan a brand_showcase reel]",
    context="Repo: ~/Desktop/tkvibes-agency/marketing/. Use tkvibes-marketing skill."
)
```

### Business analysis
```python
delegate_task(
    goal="[specific analysis task e.g. Check GSC performance for last 30 days]",
    context="Use tkvibes-business-analysis skill. GSC at .hermes/gsc-helper.py."
)
```

## 🔑 Model Configuration

### Custom providers added to Hermes config:
- `custom:local-llm` → `http://127.0.0.1:8081/v1` (qwen2.5-1.5b-instruct)
- `custom:local-coder` → `http://127.0.0.1:8080/v1` (qwen2.5-coder-1.5b-instruct)
- Fallback: `openrouter` → `deepseek/deepseek-v4-flash`

### Start models:
```bash
cd ~/Desktop/tkvibes-agency
./start-models.sh all          # start both servers
./start-models.sh status       # check running
./start-models.sh stop         # stop both
```

## 📁 Memory Bank
Located at `memory/business-bank/INDEX.md` — the single source of truth:
- `INDEX.md` — Master overview, business flow, agent roles, commands
- `LEAD-ENGINE.md` — Deep reference for lead generation
- `CRM.md` — Deep reference for CRM
- `MARKETING.md` — Deep reference for marketing engine
- `WEBSITE.md` — Deep reference for main website

## 🎯 Decision Rules
1. **Local models are free but weak** — use for simple tasks, fallback to openrouter for anything complex
2. **Delegate coding to subagent** — always use `delegate_task` for code changes
3. **Delegate lead engine** — always use `delegate_task` for lead operations
4. **Delegate marketing** — always use `delegate_task` for video creation
5. **Delegate business analysis** — always use `delegate_task` for research/analysis
6. **This profile handles** — orchestration, strategy, user communication, complex decisions