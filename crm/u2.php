<?php
/**
 * TKVibes CRM — Secure File Upload Proxy (Sample Websites & Pitch Decks)
 * 
 * POST JSON: {"key":"...", "path":"sample-website/filename.html", "content":"<base64>"}
 * 
 * Security model:
 * - API key auth required (from config.local.php)
 * - Path allowlist: only "sample-website/" and "pitch-deck/" subdirectories
 * - File extension restriction: .html only
 * - Path traversal protection: regex + realpath + basename enforcement
 * - Audit log: every write logged to system_logs
 * - Size limit: 2MB max per file
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
        log_system('warning', 'u2', 'Unauthorized upload attempt', [
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

// ── Path allowlist ─────────────────────────────────────────────────────
$allowed_dirs = ['sample-website/', 'pitch-deck/'];
$subpath = substr($p, 0, strpos($p, '/') + 1);
if (!in_array($subpath, $allowed_dirs, true)) {
    log_system('warning', 'u2', 'Blocked upload to forbidden path', [
        'path' => $p,
        'subpath' => $subpath,
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    http_response_code(403);
    echo 'Forbidden path: only sample-website/ and pitch-deck/ are allowed';
    exit;
}

// ── File type restriction ───────────────────────────────────────────────
if (!preg_match('/\.html$/', $p)) {
    log_system('warning', 'u2', 'Blocked non-HTML upload', [
        'path' => $p,
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    http_response_code(400);
    echo 'Only .html files are allowed';
    exit;
}

$filename = basename($p);

// ── Path traversal guard ────────────────────────────────────────────────
if (preg_match('/\.\./', $p) || preg_match('/\x00/', $p)) {
    log_system('critical', 'u2', 'Path traversal attempt blocked', [
        'path' => $p,
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    http_response_code(400);
    echo 'Invalid path';
    exit;
}

$base = dirname(__DIR__) . '/proposals';
$abs = $base . '/' . $subpath . $filename;

// Extra safety: ensure resolved path starts with the allowed subdirectory
$resolved = realpath(dirname($abs));
$base_real = realpath($base);
if ($resolved === false || ($base_real !== false && strpos($resolved, $base_real) !== 0)) {
    log_system('warning', 'u2', 'Path resolution failed', [
        'path' => $p,
        'resolved' => $resolved ?: 'false',
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    http_response_code(400);
    echo 'Invalid path resolution';
    exit;
}

// ── Size limit check ────────────────────────────────────────────────────
$decoded = base64_decode($c, true);
if ($decoded === false) {
    http_response_code(400);
    echo 'Invalid base64 content';
    exit;
}
if (strlen($decoded) > 2 * 1024 * 1024) {  // 2MB limit
    log_system('warning', 'u2', 'Upload exceeds size limit', [
        'size' => strlen($decoded),
        'path' => $p,
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    http_response_code(413);
    echo 'File too large (max 2MB)';
    exit;
}

$dir = dirname($abs);
if (!is_dir($dir)) {
    mkdir($dir, 0755, true);
}

$written = file_put_contents($abs, $decoded);
if ($written === false) {
    log_system('error', 'u2', 'File write failed', [
        'path' => $abs,
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    http_response_code(500);
    echo 'Write failed';
    exit;
}

// ── Audit log ───────────────────────────────────────────────────────────
log_system('info', 'u2', 'File uploaded successfully', [
    'path' => $abs,
    'size' => $written,
    'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
]);

echo 'OK';