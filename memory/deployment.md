# Deployment

## Pipeline

**Workflow:** `.github/workflows/deploy.yml`  
**Name:** Deploy to Hostinger  
**Trigger:** Push to `main`, or manual `workflow_dispatch`  
**Concurrency:** `deploy-hostinger` — cancel in-progress runs

### Steps

1. Checkout repo
2. Verify `index.html`, `assets/css/styles.css`, `assets/js/main.js` exist
3. Install `lftp`
4. Mirror repo → Hostinger via FTPS

### lftp settings

- FTPS forced, certificate verify off (Hostinger cert/host mismatch)
- `mirror --reverse --only-newer --ignore-time --no-perms --parallel=5`
- Target: `/public_html/`

### Excluded from deploy

- `.git*`, `.github/**`
- `scripts/**`
- `README.md`, `AGENTS.md`
- `memory/**` (agent docs)
- `.gitignore`

## GitHub secrets (repository settings)

| Secret | Purpose |
|--------|---------|
| `FTP_USER` | Hostinger FTP username |
| `FTP_PASS` | Hostinger FTP password |
| `FTP_HOST` | FTP host (often IP or Hostinger hostname) |

Never commit these values. Document only the names.

## Server requirements

- Apache with `mod_rewrite`, `mod_deflate`, `mod_expires`, `mod_headers` (typical on Hostinger)
- No Node.js, no PHP required for the static site itself
- FormSubmit handles contact form backend externally

## Manual deploy alternative

Upload all files except excluded paths to `public_html/` via Hostinger File Manager or FTP client. Preserve `.htaccess`.

## Performance notes

- CI previously ran `optipng` on every deploy — **removed** in commit `7be7453` for speed
- FTP uses `--ignore-time` instead of full transfer every run
- `--parallel=5` for concurrent uploads

## Rollback

Revert commit on `main` and push, or redeploy a previous commit via git revert. No database migrations.

## Local vs production

| Concern | Local | Production |
|---------|-------|------------|
| URLs | `about.html` or `/about` with server | Clean URLs via `.htaccess` |
| Form | FormSubmit works if online | Same |
| Theme | localStorage per browser | Same |
