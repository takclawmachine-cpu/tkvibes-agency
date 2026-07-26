# Troubleshooting

## CSS not loading locally

**Symptoms:** Page unstyled when opening `index.html` directly.

**Causes & fixes:**

1. **Absolute paths** — Use relative paths only (`assets/css/styles.css`, not `/assets/...`). Fixed in commit `5a436d9`.
2. **UTF-16 CSS** — Browsers ignore UTF-16 stylesheets. File must be UTF-8. Fixed in same commit.
3. **Wrong working directory** — Run `npx serve .` from repo root.

## Theme flash on load

**Fix:** Inline script in `<head>` on all 7 HTML pages sets classes before first paint. Do not remove it when adding pages.

## Light mode broken on dropdowns

**Symptoms:** Mobile nav menu or contact `<select>` / multi-select stay dark in light mode.

**Fix:** Add `html.light` overrides in `styles.css`. See `design-system.md` — components with hardcoded `#111827` or `rgba(8,12,18,...)` need light rules.

**Clear stale theme:** User may have `tkvibes-theme=dark` in localStorage from testing.

## StrReplace fails on `styles.css`

**Symptoms:** Patch tool can't find strings in styles.css on Windows.

**Fix:** Use a Node script to read/write UTF-8, or edit in IDE directly.

## Deploy slow or timing out

**History:** Early CI used strict FTPS + full transfer + optipng — caused socket timeouts.

**Current:** Incremental mirror, no image compression in CI, `--parallel=5`. See commit `7be7453`.

## Clean URLs 404 on local preview

**Expected:** `file://` and simple static servers don't run `.htaccess`. Use `about.html` locally or `npx serve .` which won't rewrite unless configured.

## Form not sending

- FormSubmit requires first-time email activation link
- Check network tab for formsubmit.co response
- Hidden `services` inputs only appear after multi-select choices

## Hero carousel not animating

- Requires `.hero-stack-frame` and multiple `.hero-stack-card` elements on home page
- JS skips if only one card
- Check console for errors blocking main.js

## Git push rejected / deploy didn't run

- Confirm push went to `main` on `origin`
- Check GitHub Actions tab for workflow errors
- Verify FTP secrets still valid in Hostinger panel
