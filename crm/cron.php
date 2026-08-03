<?php
/**
 * TKVibes CRM — Cron jobs
 * Run via Hostinger cron or terminal: php cron.php [--dry-run]
 * 
 * 1. Archive NOT_QUALIFIED leads older than 24h (soft-remove from dashboards)
 * 2. Clean up activity logs older than 90 days
 * 3. Sync from Google Sheet (import new leads + update existing lead data)
 * 4. Write back CRM state changes to Google Sheet (crm_status, notes, etc.)
 */

require __DIR__ . '/lib/db.php';
require __DIR__ . '/lib/functions.php';
require_once __DIR__ . '/lib/sheets_sync.php';

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
        $client = get_sheets_client();
        if (!$client) {
            throw new RuntimeException('Failed to initialize Sheets client');
        }
        [$header, $rows] = $client->read_sheet();
        if (empty($header)) {
            $report['sheet_sync'] = 'Sheet is empty or has no header row.';
        } else {
            $imported = 0;
            $updated = 0;
            $allowed_fields = [
                'business_name', 'category', 'owner_name', 'phone_primary', 'phone_secondary',
                'whatsapp', 'email', 'address', 'city', 'pincode', 'region', 'country',
                'website_url', 'website_quality', 'rating', 'review_count', 'years_in_business',
                'socials', 'pain_points', 'recommended_pitch', 'notes', 'contact_channel',
                'opening_hours', 'has_website', 'source', 'source_url', 'lead_score', 'lead_tier',
                'assigned_employee', 'outreach_status', 'wa_link',
            ];
            foreach ($rows as $row) {
                if (empty($row)) continue;
                $data = array_combine($header, array_pad($row, count($header), ''));
                $lk = $data['lead_key'] ?? '';
                if (!$lk) continue;

                $check = $pdo->prepare("SELECT lead_key FROM leads WHERE lead_key = ?");
                $check->execute([$lk]);
                $exists = $check->fetch();

                // Build field list from allowed sheet columns
                $set_parts = [];
                $set_params = [];
                foreach ($allowed_fields as $f) {
                    if (isset($data[$f]) && $data[$f] !== '') {
                        $set_parts[] = "$f = ?";
                        $set_params[] = $data[$f];
                    }
                }
                if (empty($set_parts)) continue;

                if ($exists) {
                    if (!$dry_run) {
                        $set_parts[] = "updated_at = datetime('now')";
                        $set_params[] = $lk;
                        $pdo->prepare("UPDATE leads SET " . implode(', ', $set_parts) . " WHERE lead_key = ?")
                            ->execute($set_params);
                    }
                    $updated++;
                } else {
                    if (!$dry_run) {
                        $cols = ['lead_key', 'crm_status', 'created_at', 'updated_at'];
                        $vals = ['?', "'new'", "datetime('now')", "datetime('now')"];
                        $params = [$lk];
                        foreach ($allowed_fields as $f) {
                            if (isset($data[$f]) && $data[$f] !== '') {
                                $cols[] = $f;
                                $vals[] = '?';
                                $params[] = $data[$f];
                            }
                        }
                        $pdo->prepare("INSERT INTO leads (" . implode(',', $cols) . ") VALUES (" . implode(',', $vals) . ")")
                            ->execute($params);
                    }
                    $imported++;
                }
            }
            $report['sheet_sync'] = "$imported new, $updated updated";
        }
    } catch (Throwable $e) {
        $report['sheet_sync_error'] = $e->getMessage();
    }
}

// ── 4. Write back CRM state changes to Google Sheet ────────────────────────
// Find leads that were updated in CRM since last sync but not yet written back
// This is best-effort; the real-time write-back from leads.php handles most cases.
// This cron catches any that were missed (e.g. server restart, offline sheets).
$sheet_columns = ['crm_status', 'crm_notes', 'last_contacted_at', 'next_callback_at'];
$client = get_sheets_client();
if ($client) {
    $written_back = 0;
    $errors = 0;
    $stmt = $pdo->query("SELECT lead_key, crm_status, crm_notes, last_contacted_at, next_callback_at FROM leads WHERE updated_at > datetime('now', '-1 hour') LIMIT 50");
    while ($lead = $stmt->fetch()) {
        $fields = [];
        foreach ($sheet_columns as $col) {
            if (!empty($lead[$col])) {
                $fields[$col] = $lead[$col];
            }
        }
        if (!empty($fields)) {
            try {
                if (!$dry_run) {
                    $client->update_lead_fields($lead['lead_key'], $fields);
                }
                $written_back++;
            } catch (Throwable $e) {
                $errors++;
                error_log("Cron write-back failed for {$lead['lead_key']}: " . $e->getMessage());
            }
        }
    }
    if ($written_back > 0 || $errors > 0) {
        $report['cron_writeback'] = "$written_back OK, $errors errors";
    }
}

// Output report
echo json_encode($report, JSON_PRETTY_PRINT) . "\n";