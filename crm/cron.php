<?php
/**
 * TKVibes CRM — Cron jobs
 * Run via Hostinger cron or terminal: php cron.php [--dry-run]
 * 
 * 1. Archive NOT_QUALIFIED leads older than 24h (soft-remove from dashboards)
 * 2. Optionally sync from Google Sheet (if configured)
 */

require __DIR__ . '/lib/db.php';
require __DIR__ . '/lib/functions.php';

$dry_run = in_array('--dry-run', $argv ?? []);
$report = [];

// ── 1. Archive not_qualified leads older than 24h ──────────────────────────
$pdo = get_db();
$stmt = $pdo->prepare("
    UPDATE leads 
    SET removed_at = datetime('now'),
        updated_at = datetime('now'),
        crm_status = 'not_qualified'
    WHERE crm_status = 'not_qualified'
      AND removed_at IS NULL
      AND updated_at < datetime('now', '-1 day')
");
if (!$dry_run) {
    $stmt->execute();
    $archived = $stmt->rowCount();
    $report['archived_not_qualified'] = $archived;
} else {
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM leads WHERE crm_status = 'not_qualified' AND removed_at IS NULL AND updated_at < datetime('now', '-1 day')");
    $stmt->execute();
    $report['would_archive'] = (int)$stmt->fetchColumn();
}

// ── 2. Remove stale activity logs (older than 90 days) ─────────────────────
if (!$dry_run) {
    $stmt = $pdo->prepare("DELETE FROM lead_activities WHERE created_at < datetime('now', '-90 days')");
    $stmt->execute();
    $report['cleaned_activities'] = $stmt->rowCount();
}

// ── 3. Sync from Google Sheet (if configured) ──────────────────────────────
$cfg = require __DIR__ . '/config.local.php';
if ($cfg['google_service_account'] && $cfg['google_sheet_id']) {
    try {
        require __DIR__ . '/lib/GoogleSheetsClient.php';
        $client = new GoogleSheetsClient($cfg['google_service_account'], $cfg['google_sheet_id']);
        [$header, $rows] = $client->read_sheet();
        $imported = 0;
        foreach ($rows as $row) {
            if (empty($row)) continue;
            $data = array_combine($header, array_pad($row, count($header), ''));
            $lk = $data['lead_key'] ?? '';
            if (!$lk) continue;
            $check = $pdo->prepare("SELECT lead_key FROM leads WHERE lead_key = ?");
            $check->execute([$lk]);
            if (!$check->fetch()) {
                if (!$dry_run) {
                    $ins = $pdo->prepare("INSERT INTO leads (lead_key, business_name, category, city, phone_primary, email, region, country, assigned_employee, pain_points, recommended_pitch, crm_status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', datetime('now'), datetime('now'))");
                    $ins->execute([
                        $lk, $data['business_name'] ?? '', $data['category'] ?? '',
                        $data['city'] ?? '', $data['phone_primary'] ?? '', $data['email'] ?? '',
                        $data['region'] ?? '', $data['country'] ?? '',
                        $data['assigned_employee'] ?? '', $data['pain_points'] ?? '',
                        $data['recommended_pitch'] ?? '',
                    ]);
                }
                $imported++;
            }
        }
        $report['sheet_sync_imported'] = $imported;
    } catch (Exception $e) {
        $report['sheet_sync_error'] = $e->getMessage();
    }
}

// Output report
echo json_encode($report, JSON_PRETTY_PRINT) . "\n";