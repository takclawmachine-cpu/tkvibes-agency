#!/bin/bash
# Deploy CRM files to Hostinger via FTPS
# Usage: HOSTINGER_FTP_PASS='password' bash .ftp-deploy.sh
#
# This script should be run when the GitHub Actions FTPS deploy is not working
# or when HTTP-based file uploads (u3.php) are blocked by Hostinger's WAF.
#
# Hostinger FTP credentials (from hPanel):
#   Host: 217.21.90.110, Port: 21
#   Username: u990668815@tkvibes.in
#   Password: Set HOSTINGER_FTP_PASS env var (never hardcode)
#   Root directory: /public_html

set -e

FTP_HOST="217.21.90.110"
FTP_PORT="21"
FTP_USER="u990668815@tkvibes.in"
FTP_PASS="${HOSTINGER_FTP_PASS:-}"
FTP_ROOT="/public_html"

if [ -z "$FTP_PASS" ]; then
    echo "ERROR: Set HOSTINGER_FTP_PASS environment variable"
    echo "Usage: HOSTINGER_FTP_PASS='your_password' bash .ftp-deploy.sh"
    exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Deploying to $FTP_HOST:$FTP_PORT as $FTP_USER..."

# Use lftp if available, otherwise fall back to Python ftplib
if command -v lftp &>/dev/null; then
    lftp -c "
        set ftp:ssl-allow yes;
        set ftp:ssl-protect-data yes;
        set ftp:ssl-force yes;
        set ssl:verify-certificate no;
        set ftp:passive-mode yes;
        set net:timeout 120;
        set net:max-retries 15;
        open -u '$FTP_USER','$FTP_PASS' $FTP_HOST:$FTP_PORT;
        mirror --reverse --verbose --overwrite --ignore-time --no-perms --parallel=3 \
          --exclude '.git/' --exclude '.github/' --exclude 'tkvibes-lead-engine/' \
          --exclude '*.pyc' --exclude '__pycache__/' --exclude '.venv/' --exclude 'node_modules/' \
          '$REPO_ROOT/crm' '$FTP_ROOT/crm/' --exclude 'test*' --exclude '*.txt';
        bye;
    "
else
    echo "lftp not found, using Python ftplib..."
    python -c "
import ftplib, ssl, os, io

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

ftp = ftplib.FTP_TLS(context=context)
ftp.connect('$FTP_HOST', $FTP_PORT, timeout=30)
ftp.login('$FTP_USER', '$FTP_PASS')
ftp.prot_p()

files = [
    'lib/constants.php', 'lib/functions.php', 'lib/auth.php', 'lib/db.php',
    'lib/sheets_sync.php', 'lib/GoogleSheetsClient.php',
    'api/sync.php', 'api/leads.php', 'api/proposals.php', 'api/employees.php',
    'api/logs.php', 'api/public_proposals.php', 'api/proxy_proposal.php',
    'api/upload_proposal.php', 'cron.php', 'admin.php', 'dashboard.php',
    'index.php', 'logout.php', 'install.php', 'templates/lead_detail.php',
    'u2.php', 'u3.php', 'assets/js/crm.js', 'assets/css/crm.css', '.htaccess',
]

ok = fail = 0
for f in files:
    local = os.path.join('$REPO_ROOT/crm', f)
    if not os.path.isfile(local):
        print(f'  SKIP {f}')
        fail += 1
        continue
    remote_dir = os.path.dirname(f)
    if remote_dir:
        try:
            ftp.cwd(f'$FTP_ROOT/crm/{remote_dir}')
        except:
            try:
                ftp.cwd('$FTP_ROOT/crm')
                for d in remote_dir.split('/'):
                    try:
                        ftp.cwd(d)
                    except:
                        ftp.mkd(d)
                        ftp.cwd(d)
            except:
                pass
    with open(local, 'rb') as fh:
        ftp.storbinary(f'STOR {os.path.basename(f)}', fh)
    sz = os.path.getsize(local)
    print(f'  ✅ {f} ({sz} bytes)')
    ok += 1

ftp.quit()
print(f'Done: {ok} uploaded, {fail} failed')
"
fi
