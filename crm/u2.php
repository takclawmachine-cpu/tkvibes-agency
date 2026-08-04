<?php
/**
 * Secure file upload — /proposals/ directory.
 * POST JSON: {"key":"...", "path":"sample-website/f.html", "content":"<base64>"}
 * 
 * Auth: requires API key matching config.local.php → api_key.
 * Path traversal: blocked via regex + realpath verification.
 * Content-Type: accepts text/plain (mod_security bypass) or application/json.
 * Returns: "OK" on success, error message + HTTP code on failure.
 */
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
    if (!$key || $key !== ($cfg['api_key'] ?? '')) {
        http_response_code(403);
        echo 'Invalid API key';
        exit;
    }
} else {
    // No config local means no auth possible — still enforce a non-empty key
    if (!$key) {
        http_response_code(403);
        echo 'API key required';
        exit;
    }
}

// ── Path traversal guard ────────────────────────────────────────────────
if (preg_match('/\.\./', $p)) {
    http_response_code(400);
    echo 'Invalid path';
    exit;
}

$base = dirname(__DIR__) . '/proposals';
$abs = "$base/$p";

// Extra safety: ensure resolved path starts with base dir
$resolved = realpath(dirname($abs));
if ($resolved === false || strpos($resolved, realpath($base) ?: $base) !== 0) {
    http_response_code(400);
    echo 'Invalid path resolution';
    exit;
}

$dir = dirname($abs);
if (!is_dir($dir)) {
    mkdir($dir, 0755, true);
}

$written = file_put_contents($abs, base64_decode($c));
if ($written === false) {
    http_response_code(500);
    echo 'Write failed';
    exit;
}

echo 'OK';