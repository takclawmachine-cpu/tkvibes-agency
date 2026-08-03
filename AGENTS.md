# TKVibes Agency — Agent guide

Public static site at **tkvibes.in**. Read the memory bank before making non-trivial changes.

## Start here

1. **[memory/summary.md](memory/summary.md)** — current defaults and key files
2. **[memory/items.yaml](memory/items.yaml)** — atomic facts (machine-readable)
3. Topic files in **[memory/](memory/)** as needed

## Hard rules

- **No build step** — do not add Next.js, Vite, or npm build unless explicitly requested
- **Relative paths only** — `/assets/...` breaks local `file://` preview
- **`styles.css` must stay UTF-8** — use Node scripts to patch if editor tools fail on Windows
- **No FTP secrets in repo** — only document secret names (`FTP_USER`, `FTP_PASS`, `FTP_HOST`)
- **Light theme is default** — `localStorage` key `tkvibes-theme`; inline head script prevents flash
- **New dropdowns/overlays** need `html.light` CSS overrides if they use hardcoded dark colors

## Edit map

| Task | File(s) |
|------|---------|
| Page content / structure | `*.html` |
| All styling | `assets/css/styles.css` |
| Interactivity | `assets/js/main.js` |
| Clean URLs / cache | `.htaccess` |
| Deploy | `.github/workflows/deploy.yml` |
| Project knowledge | `memory/*` |

## Stack

HTML + one CSS + one JS → Hostinger `public_html/` via GitHub Actions FTPS on push to `main`.

## Local preview

```bash
npx serve .
```

## After significant changes

Update `memory/changelog.md` and relevant facts in `memory/items.yaml`.
