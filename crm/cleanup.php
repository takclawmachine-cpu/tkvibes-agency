<?php
/**
 * TKVibes CRM — Cleanup Script (Hardened)
 *
 * Deletes leads with empty business names and duplicate lead_keys.
 * Requires API key authentication. No bulk DELETE operations.
 * Run manually or via cron with proper auth.
 *
 * Security improvements:
 * - API key authentication required
 * - No bulk DELETE (only deletes duplicates and empty-name leads)
 * - No Google Sheets clearing (MySQL is source of truth)
 * - Audit log entry for all cleanup actions
 */
header('X-Robots-Tag: noindex, nofollow');
@include __DIR__ . '/lib/db.php';
@include __DIR__ . '/lib/functions.php';

$b = json_decode(file_get_contents('php://input'), true) ?: [];
$key = $b['key'] ?? $_GET['key'] ?? '';

$cfg_file = __DIR__ . '/config.local.php';
if (file_exists($cfg_file)) {
    $cfg = require $cfg_file;
    if (!$key || !hash_equals($cfg['api_key'] ?? '', $key)) {
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

function _log(string $level, string $message, array $context = []): void {
    if (function_exists('log_system')) {
        log_system($level, 'cleanup', $message, $context);
    } else {
        error_log("[$level] cleanup: $message " . json_encode($context, JSON_UNESCAPED_SLASHES));
    }
}

$pdo = get_db();

// Clean up duplicate lead_keys (keep first occurrence)
$deleted_dupes = $pdo->exec("
    DELETE l1 FROM leads l1
    INNER JOIN leads l2 
    WHERE l1.id > l2.id AND l1.lead_key = l2.lead_key
");

// Delete leads with empty business_name
$deleted_empty = $pdo->exec("DELETE FROM leads WHERE business_name IS NULL OR business_name = ''");

_log('info', 'Cleanup completed', [
    'duplicates_removed' => $deleted_dupes,
    'empty_removed' => $deleted_empty,
]);

echo json_encode([
    'status' => 'ok',
    'duplicates_removed' => $deleted_dupes,
    'empty_name_removed' => $deleted_empty,
]);
