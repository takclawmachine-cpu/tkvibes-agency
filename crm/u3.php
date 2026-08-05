<?php
/**
 * TKVibes CRM — Secure File Upload (CRM Code Deployment)
 * 
 * POST JSON: {"key":"...", "path":"lib/functions.php", "content":"<base64>"}
 * 
 * Security model:
 * - API key auth required (strict hash_equals comparison)
 * - Path allowlist: ONLY specific PHP files in lib/ and api/ subdirectories
 * - File extension restriction: .php, .js, .css (based on allowlist)
 * - No arbitrary directory creation (restricted to allowlisted paths)
 * - Audit log: every write logged to system_logs (if available)
 * - Size limit: 1MB max per file
 * 
 * Bootstrap-safe: uses @include for lib requires and function_exists checks
 * for log_system, so it works even when lib/functions.php is being deployed.
 */
header('X-Robots-Tag: noindex, nofollow');

// Use @include instead of require — allows u3.php to function even if
// lib/db.php or lib/functions.php are empty during initial deployment
@include __DIR__ . '/lib/db.php';
@include __DIR__ . '/lib/functions.php';

// Fallback logger — writes to error_log if log_system is not available
function _u3_log(string $level, string $message, array $context = []): void {
    if (function_exists('log_system')) {
        log_system($level, 'u3', $message, $context);
    } else {
        // Fallback: write to PHP error log
        $ctx = json_encode($context, JSON_UNESCAPED_SLASHES);
        error_log("[$level] u3: $message $ctx");
    }
}

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
        _u3_log('warning', 'Unauthorized code deploy attempt', [
            'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
            'path_attempt' => $p,
        ]);
        http_response_code(403);
        echo 'Invalid API key';
        exit;
    }
} else {
    // No config — still enforce a non-empty key
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
    // Upload endpoints
    'u2.php',
    'u3.php',
    // Assets
    'assets/js/crm.js',
    'assets/css/crm.css',
];

if (!in_array($p, $allowed_files, true)) {
    _u3_log('critical', 'Blocked upload to non-allowlisted file', [
        'path' => $p,
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    http_response_code(403);
    echo 'File not in allowlist. Contact administrator.';
    exit;
}

// ── File type restriction ───────────────────────────────────────────────
// Check extension is allowed (derived from allowlist)
$allowed_extensions = ['.php'];
foreach ($allowed_files as $f) {
    $ext = '.' . pathinfo($f, PATHINFO_EXTENSION);
    if (!in_array($ext, $allowed_extensions, true)) {
        $allowed_extensions[] = $ext;
    }
}
$file_ext = '.' . pathinfo($p, PATHINFO_EXTENSION);
if (!in_array($file_ext, $allowed_extensions, true)) {
    http_response_code(400);
    echo 'File type not allowed: ' . $file_ext;
    exit;
}

// ── Path traversal guard ─────────────────────────────────────────────────
if (preg_match('/\.\./', $p) || preg_match('/\x00/', $p)) {
    _u3_log('critical', 'Path traversal attempt in code deploy', [
        'path' => $p,
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    http_response_code(400);
    echo 'Invalid path';
    exit;
}

// ── Prevent overwriting config.local.php ────────────────────────────────
if ($p === 'config.local.php') {
    _u3_log('critical', 'Attempt to overwrite config.local.php blocked', [
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    http_response_code(403);
    echo 'Cannot overwrite config.local.php via API';
    exit;
}

$abs = __DIR__ . '/' . $p;

// Extra safety: ensure resolved path is within CRM directory
// Only check if realpath works (it may fail for nonexistent dirs)
$parent_dir = dirname($abs);
if (is_dir($parent_dir) || is_dir(__DIR__ . '/' . dirname($p))) {
    $resolved = realpath($parent_dir);
    $crm_root = realpath(__DIR__);
    if ($resolved !== false && $crm_root !== false && strpos($resolved, $crm_root) !== 0) {
        _u3_log('warning', 'Path resolution outside CRM dir', [
            'path' => $p,
            'resolved' => $resolved,
            'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
        ]);
        http_response_code(400);
        echo 'Invalid path';
        exit;
    }
}

// ── Size limit check ────────────────────────────────────────────────────
$decoded = base64_decode($c, true);
if ($decoded === false) {
    http_response_code(400);
    echo 'Invalid base64 content';
    exit;
}
if (strlen($decoded) > 1024 * 1024) {  // 1MB limit
    _u3_log('warning', 'Code file exceeds size limit', [
        'size' => strlen($decoded),
        'path' => $p,
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    http_response_code(413);
    echo 'File too large (max 1MB)';
    exit;
}

// ── Write file ────────────────────────────────────────────────────────────
$dir = dirname($abs);
if (!is_dir($dir)) {
    mkdir($dir, 0755, true);
}

$written = file_put_contents($abs, $decoded);
if ($written === false) {
    _u3_log('error', 'Code file write failed', [
        'path' => $abs,
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    http_response_code(500);
    echo 'Write failed';
    exit;
}

// ── Audit log ────────────────────────────────────────────────────────────
_u3_log('info', 'Code file deployed', [
    'path' => $abs,
    'size' => $written,
    'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
]);

echo 'OK';