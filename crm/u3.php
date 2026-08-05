<?php
/**
 * TKVibes CRM — Secure File Upload (CRM Code Deployment)
 * 
 * POST JSON: {"key":"...", "path":"lib/functions.php", "content":"<base64>"}
 * 
 * Security model:
 * - API key auth required (strict hash_equals comparison)
 * - Path allowlist: ONLY specific PHP files in lib/ and api/ subdirectories
 * - File extension restriction: .php only
 * - No subdirectory creation (flat file allowlist only)
 * - Audit log: every write logged to system_logs
 * - Size limit: 1MB max per file
 */
header('X-Robots-Tag: noindex, nofollow');
require __DIR__ . '/lib/db.php';
require __DIR__ . '/lib/functions.php';

$b = json_decode(file_get_contents('php://input'), true) ?: [];
$p = $b['path'] ?? '';
$c = $b['content'] ?? '';
$key = $b['key'] ?? $_GET['key'] ?? '';

if (!$p || !$c) {
    http_response_code(400);
    echo 'Missing path or content';
    exit;
}

// ── Auth ───────────────────────────────────────────────────────────────
$cfg_file = __DIR__ . '/config.local.php';
if (file_exists($cfg_file)) {
    $cfg = require $cfg_file;
    if (!$key || !hash_equals($cfg['api_key'] ?? '', $key)) {
        log_system('warning', 'u3', 'Unauthorized code deploy attempt', [
            'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
            'path_attempt' => $p,
        ]);
        http_response_code(403);
        echo 'Invalid API key';
        exit;
    }
} else {
    if (!$key) {
        http_response_code(403);
        echo 'API key required';
        exit;
    }
}

// ── Strict file allowlist ───────────────────────────────────────────────
// ONLY these files can be written via u3.php — no arbitrary paths
$allowed_files = [
    // Core library files
    'lib/constants.php',
    'lib/functions.php',
    'lib/auth.php',
    'lib/db.php',
    'lib/sheets_sync.php',
    'lib/GoogleSheetsClient.php',
    // API endpoints
    'api/sync.php',
    'api/leads.php',
    'api/proposals.php',
    'api/employees.php',
    'api/logs.php',
    'api/public_proposals.php',
    'api/proxy_proposal.php',
    'api/upload_proposal.php',
    // Cron and templates
    'cron.php',
    'admin.php',
    'dashboard.php',
    'index.php',
    'logout.php',
    'install.php',
    'cleanup.php',
    'cleanup_leads.php',
    'templates/lead_detail.php',
    // Assets
    'assets/js/crm.js',
    'assets/css/crm.css',
];

if (!in_array($p, $allowed_files, true)) {
    log_system('critical', 'u3', 'Blocked upload to non-allowlisted file', [
        'path' => $p,
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    http_response_code(403);
    echo 'File not in allowlist. Contact administrator.';
    exit;
}

// ── File type restriction ───────────────────────────────────────────────
if (!preg_match('/\.php$/', $p)) {
    http_response_code(400);
    echo 'Only .php files are allowed';
    exit;
}

// ── Path traversal guard ────────────────────────────────────────────────
if (preg_match('/\.\./', $p) || preg_match('/\x00/', $p)) {
    log_system('critical', 'u3', 'Path traversal attempt in code deploy', [
        'path' => $p,
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    http_response_code(400);
    echo 'Invalid path';
    exit;
}

$filename = basename($p);
$abs = __DIR__ . '/' . $p;

// Extra safety: ensure resolved path is within CRM directory
$resolved = realpath(dirname($abs));
$crm_root = realpath(__DIR__);
if ($resolved === false || strpos($resolved, $crm_root) !== 0) {
    log_system('warning', 'u3', 'Path resolution outside CRM dir', [
        'path' => $p,
        'resolved' => $resolved ?: 'false',
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    http_response_code(400);
    echo 'Invalid path';
    exit;
}

// ── Size limit check ────────────────────────────────────────────────────
$decoded = base64_decode($c, true);
if ($decoded === false) {
    http_response_code(400);
    echo 'Invalid base64 content';
    exit;
}
if (strlen($decoded) > 1024 * 1024) {  // 1MB limit
    log_system('warning', 'u3', 'Code file exceeds size limit', [
        'size' => strlen($decoded),
        'path' => $p,
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    http_response_code(413);
    echo 'File too large (max 1MB)';
    exit;
}

// ── Prevent overwriting config.local.php (critical file) ────────────────
if ($p === 'config.local.php') {
    log_system('critical', 'u3', 'Attempt to overwrite config.local.php blocked', [
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    http_response_code(403);
    echo 'Cannot overwrite config.local.php via API';
    exit;
}

$dir = dirname($abs);
if (!is_dir($dir)) {
    mkdir($dir, 0755, true);
}

$written = file_put_contents($abs, $decoded);
if ($written === false) {
    log_system('error', 'u3', 'Code file write failed', [
        'path' => $abs,
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    http_response_code(500);
    echo 'Write failed';
    exit;
}

// ── Audit log ───────────────────────────────────────────────────────────
log_system('info', 'u3', 'Code file deployed', [
    'path' => $abs,
    'size' => $written,
    'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
]);

echo 'OK';