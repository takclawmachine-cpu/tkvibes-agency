<?php
header('X-Robots-Tag: noindex, nofollow');
/**
 * TKVibes CRM — System Logs API
 * POST: Accept log entries from remote systems (lead engine, cron, agents).
 * GET: Return recent log entries for admin dashboard.
 * 
 * Auth: API key (same as config.local.php api_key) for POST.
 *       Session (admin) for GET.
 */
require __DIR__ . '/../lib/db.php';
require __DIR__ . '/../lib/auth.php';
require __DIR__ . '/../lib/functions.php';

$pdo = get_db();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // ── Ingest log entry ────────────────────────────────────────────────
    $cfg = require __DIR__ . '/../config.local.php';
    $body = body_json();
    
    $key = $body['key'] ?? $_GET['key'] ?? '';
    if (!$key || $key !== ($cfg['api_key'] ?? '')) {
        json_response(['error' => 'Invalid API key'], 403);
    }
    
    $level   = $body['level'] ?? 'info';
    $source  = $body['source'] ?? '';
    $message = $body['message'] ?? '';
    $context = $body['context'] ?? [];
    
    if (!in_array($level, ['info', 'warning', 'error', 'critical'], true)) {
        $level = 'info';
    }
    
    log_system($level, $source, $message, is_array($context) ? $context : []);
    json_response(['status' => 'ok']);
    
} elseif ($_SERVER['REQUEST_METHOD'] === 'GET') {
    // ── View recent logs (admin only) ───────────────────────────────────
    $emp = require_admin();
    
    $level_filter = $_GET['level'] ?? '';
    $source_filter = $_GET['source'] ?? '';
    $limit = min(100, max(10, (int)($_GET['limit'] ?? 50)));
    
    $where = [];
    $params = [];
    if ($level_filter && in_array($level_filter, ['info', 'warning', 'error', 'critical'], true)) {
        $where[] = "level = ?";
        $params[] = $level_filter;
    }
    if ($source_filter) {
        $where[] = "source LIKE ?";
        $params[] = '%' . $source_filter . '%';
    }
    
    $sql = "SELECT * FROM system_logs";
    if ($where) {
        $sql .= " WHERE " . implode(" AND ", $where);
    }
    $sql .= " ORDER BY created_at DESC LIMIT " . (int)$limit;
    
    try {
        $stmt = $pdo->prepare($sql);
        $stmt->execute($params);
        $logs = $stmt->fetchAll();
    } catch (PDOException $e) {
        $logs = [];
    }
    
    json_response(['status' => 'ok', 'logs' => $logs, 'total' => count($logs)]);
    
} else {
    http_response_code(405);
    echo "Method not allowed";
}