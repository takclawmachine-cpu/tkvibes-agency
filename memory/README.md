# TKVibes Agency — Memory Bank

Persistent project knowledge for humans and AI agents. Read **`summary.md`** first, then drill into topic files as needed.

## Index

| File | Purpose |
|------|---------|
| [summary.md](./summary.md) | Quick context — start here |
| [items.yaml](./items.yaml) | Atomic facts (machine-readable) |
| [architecture.md](./architecture.md) | Stack, folder layout, hosting |
| [design-system.md](./design-system.md) | Theme, CSS variables, UI components |
| [features.md](./features.md) | Pages, JS behavior, forms |
| [brand-and-content.md](./brand-and-content.md) | Logo, contact, copy conventions |
| [deployment.md](./deployment.md) | CI/CD, secrets, Hostinger |
| [troubleshooting.md](./troubleshooting.md) | Known issues and fixes |
| [changelog.md](./changelog.md) | Migration history and major changes |

## Maintenance rules

1. Update `items.yaml` when a durable fact changes (URLs, defaults, secrets names, etc.).
2. Append significant work to `changelog.md` with date and reason.
3. Keep `summary.md` in sync with current defaults (theme, container width, deploy target).
4. Do **not** store passwords or FTP credentials in this folder — only secret **names**.

## Related docs

- [README.md](../README.md) — public project overview
- [AGENTS.md](../AGENTS.md) — short agent entry point
