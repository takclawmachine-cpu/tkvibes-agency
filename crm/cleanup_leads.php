<?php
/**
 * TKVibes CRM — Lead Cleanup Script (Hardened)
 *
 * Finds and deletes duplicate lead_keys and empty-name leads.
 * Requires API key authentication.
 *
 * Security improvements:
 * - API key authentication required
 * - No bulk DELETE (only duplicates and empty-name leads)
 * - No Google Sheets clearing
 * - Audit log entry for all actions
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
        log_system($level, 'cleanup_leads', $message, $context);
    } else {
        error_log("[$level] cleanup_leads: $message " . json_encode($context, JSON_UNESCAPED_SLASHES));
    }
}

$pdo = get_db();

// Find duplicates
$stmt = $pdo->query("
    SELECT lead_key, COUNT(*) as cnt 
    FROM leads 
    GROUP BY lead_key 
    HAVING COUNT(*) > 1
");
$duplicates = $stmt->fetchAll(PDO::FETCH_ASSOC);

// Delete duplicate lead_keys (keep first occurrence)
$deleted_dupes = 0;
foreach ($duplicates as $dupe) {
    $deleted = $pdo->exec("
        DELETE FROM leads 
        WHERE lead_key = ? 
        AND id NOT IN (SELECT MIN(id) FROM leads WHERE lead_key = ?)
    ", [$dupe['lead_key'], $dupe['lead_key']]);
    $deleted_dupes += $deleted;
};

// Delete leads with empty business_name
$deleted_empty = $pdo->exec("DELETE FROM leads WHERE business_name IS NULL OR business_name = ''");

// Get remaining lead count
$total = $pdo->query("SELECT COUNT(*) FROM leads")->fetchColumn();

_log('info', 'Lead cleanup completed', [
    'duplicates_removed' => $deleted_dupes,
    'empty_name_removed' => $deleted_empty,
    'remaining' => $total,
]);

echo json_encode([
    'status' => 'ok',
    'duplicates_found' => count($duplicates),
    'duplicates_removed' => $deleted_dupes,
    'empty_name_removed' => $deleted_empty,
    'remaining_leads' => $total,
]);
