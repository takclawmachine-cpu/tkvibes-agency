# TKVibes Agency — Summary

**What:** Public marketing site for TKVibes Digital Agency (websites, brand, SEO, ads, automation).

**Live site:** [tkvibes.in](https://tkvibes.in)

**Repo:** `https://github.com/takclawmachine-cpu/tkvibes-agency.git` (branch `main`)

**Stack:** Plain HTML + single CSS file + single JS file. No build step. No Node on server.

**Hosting:** Hostinger shared hosting (`public_html/`) via GitHub Actions FTPS deploy on every push to `main`.

## Current defaults (2026-07-26)

| Setting | Value |
|---------|--------|
| Theme default | Light (`localStorage` key: `tkvibes-theme`) |
| Max content width | `1400px` (`--container-max`) |
| Nav logo | `tk-vibes-mark.svg` (header + footer) |
| Contact form | FormSubmit → `services@tkvibes.in` |
| WhatsApp | `+91 98182 46938` |

## Key files to edit

- **Content/layout:** `*.html` (7 pages)
- **All styling:** `assets/css/styles.css`
- **All interactivity:** `assets/js/main.js`
- **Apache rules:** `.htaccess`
- **Deploy pipeline:** `.github/workflows/deploy.yml`

## Do not

- Reintroduce Next.js or a build toolchain unless explicitly requested
- Use absolute paths (`/assets/...`) — breaks `file://` local preview
- Commit FTP credentials
- Edit `styles.css` with naive search-replace on Windows if encoding breaks — file must stay **UTF-8**
