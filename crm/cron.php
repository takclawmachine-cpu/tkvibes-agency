<?php
/**
 * TKVibes CRM — Cron Jobs
 * Scheduled tasks: Google Sheets sync (disabled), lead reassignment, proposal job recovery.
 *
 * Security improvements:
 * - File-based locking prevents concurrent execution
 * - MySQL-compatible SQL throughout
 * - Trace ID support for job recovery
 * - Audit logging for all cron actions
 */
header('X-Robots-Tag: noindex, nofollow');
require __DIR__ . '/lib/db.php';
require __DIR__ . '/lib/functions.php';
require_once __DIR__ . '/lib/sheets_sync.php';
require_once __DIR__ . '/lib/constants.php';

$pdo = get_db();
$driver = $pdo->getAttribute(PDO::ATTR_DRIVER_NAME);
$now_expr = $driver === 'sqlite' ? "datetime('now')" : "NOW()";
$time_func = $driver === 'sqlite' ? "datetime('now'" : "DATE_SUB(NOW()";

// ── File-based lock to prevent concurrent cron execution ────────────────────
$lock_file = sys_get_temp_dir() . "/tkvibes_cron.lock";
$lock_fh = null;

if (file_exists($lock_file)) {
    $lock_age = time() - filemtime($lock_file);
    if ($lock_age < 300) {  // Lock is fresh — another cron is running
        echo json_encode(["status" => "skipped", "reason" => "cron already running"], JSON_PRETTY_PRINT) . "\n";
        exit;
    }
    // Stale lock — remove it
    unlink($lock_file);
}

$lock_fh = fopen($lock_file, "w");
if (!$lock_fh || !flock($lock_fh, LOCK_EX | LOCK_NB)) {
    echo json_encode(["status" => "skipped", "reason" => "could not acquire lock"], JSON_PRETTY_PRINT) . "\n";
    exit;
}
fwrite($lock_fh, getmypid());
fflush($lock_fh);

// Ensure lock is released on exit
register_shutdown_function(function() use ($lock_fh, $lock_file) {
    if ($lock_fh) {
        flock($lock_fh, LOCK_UN);
        fclose($lock_fh);
    }
    if (file_exists($lock_file)) {
        unlink($lock_file);
    }
});

$trace_id = "cron-" . date('YmdHis');
log_system('info', 'cron', 'Cron job started', ['trace_id' => $trace_id]);

$dry_run = in_array('--dry-run', $argv ?? []);
$report = [];

// ── 1. Archive not_qualified leads older than 24h ──────────────────────────
$stmt = $pdo->prepare("
    UPDATE leads 
    SET removed_at = $now_expr,
        updated_at = $now_expr,
        crm_status = 'not_qualified'
    WHERE crm_status = 'not_qualified'
      AND removed_at IS NULL
      AND updated_at < " . ($driver === 'sqlite' ? "datetime('now', '-1 day')" : "DATE_SUB(NOW(), INTERVAL 1 DAY)") . "
");
if (!$dry_run) {
    $stmt->execute();
    $archived = $stmt->rowCount();
    $report['archived_not_qualified'] = $archived;
} else {
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM leads WHERE crm_status = 'not_qualified' AND removed_at IS NULL AND updated_at < " . ($driver === 'sqlite' ? "datetime('now', '-1 day')" : "DATE_SUB(NOW(), INTERVAL 1 DAY)"));
    $stmt->execute();
    $report['would_archive'] = (int)$stmt->fetchColumn();
}

// ── 2. Remove stale activity logs (older than 90 days) ─────────────────────
if (!$dry_run) {
    $stmt = $pdo->prepare("DELETE FROM lead_activities WHERE created_at < " . ($driver === 'sqlite' ? "datetime('now', '-90 days')" : "DATE_SUB(NOW(), INTERVAL 90 DAY)"));
    $stmt->execute();
    $report['cleaned_activities'] = $stmt->rowCount();
}

// ── 3. Sync from Google Sheet (DISABLED in production) ────────────────────
// With MySQL as source of truth, sheet sync is no longer needed.
// Kept for backward compatibility but disabled by default.
$cfg = require __DIR__ . '/config.local.php';
if ($cfg['google_service_account'] && $cfg['google_sheet_id'] && !empty($cfg['enable_sheet_sync'])) {
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
            $allowed_fields = SHEET_IMPORT_FIELDS;
            foreach ($rows as $row) {
                if (empty($row)) continue;
                $data = array_combine($header, array_pad($row, count($header), ''));
                $lk = $data['lead_key'] ?? '';
                if (!$lk) continue;

                $check = $pdo->prepare("SELECT lead_key FROM leads WHERE lead_key = ?");
                $check->execute([$lk]);
                $exists = $check->fetch();

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
                        $set_parts[] = "updated_at = $now_expr";
                        $set_params[] = $lk;
                        $pdo->prepare("UPDATE leads SET " . implode(', ', $set_parts) . " WHERE lead_key = ?")
                            ->execute($set_params);
                    }
                    $updated++;
                } else {
                    if (!$dry_run) {
                        $cols = ['lead_key', 'crm_status', 'created_at', 'updated_at'];
                        $vals = ['?', "'new'", $now_expr, $now_expr];
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
        log_system('error', 'cron', 'Sheet sync failed', ['error' => $e->getMessage()]);
    }
} else {
    $report['sheet_sync'] = 'disabled (MySQL is source of truth)';
}

// ── 4. Write back CRM state changes to Google Sheet (DISABLED) ──────────────
// With MySQL as source of truth, write-back is no longer needed.
$report['cron_writeback'] = 'disabled (MySQL is source of truth)';

// ── 5. Recover orphaned 'running' proposal jobs & process pending ──────────
try {
    // First: recover orphaned 'running' jobs that have no heartbeat (>10 min stale)
    $stale_time = $driver === 'sqlite' ? "datetime('now', '-10 minutes')" : "DATE_SUB(NOW(), INTERVAL 10 MINUTE)";
    $recovery_sql = "SELECT id, lead_key FROM proposal_generation_jobs 
                     WHERE status = 'running' AND updated_at < $stale_time";
    $stmt = $pdo->query($recovery_sql);
    $recovered = 0;
    while ($job = $stmt->fetch()) {
        if (!$dry_run) {
            $pdo->prepare("UPDATE proposal_generation_jobs SET status = 'pending', updated_at = $now_expr WHERE id = ?")
                ->execute([$job['id']]);
            log_system('info', 'cron', 'Recovered orphaned job', [
                'job_id' => $job['id'],
                'lead_key' => $job['lead_key'],
                'trace_id' => $trace_id,
            ]);
        }
        $recovered++;
    }
    if ($recovered > 0) {
        $report['proposal_jobs_recovered'] = "$recovered orphaned jobs recovered";
    }

    // Then: count pending jobs (actual processing is done by process_proposal_jobs.py agent)
    $pending_sql = "SELECT id, lead_key, feedback, created_at FROM proposal_generation_jobs 
                    WHERE status = 'pending' ORDER BY created_at ASC LIMIT 10";
    $stmt = $pdo->query($pending_sql);
    $pending_jobs = $stmt->fetchAll();
    if (!empty($pending_jobs)) {
        $report['proposal_jobs_pending'] = count($pending_jobs) . ' jobs awaiting external processor';
        foreach ($pending_jobs as $j) {
            log_system('info', 'cron', 'Pending proposal job found', [
                'job_id' => $j['id'],
                'lead_key' => $j['lead_key'],
                'trace_id' => $trace_id,
            ]);
        }
    }
} catch (Throwable $e) {
    $report['proposal_jobs_error'] = $e->getMessage();
    log_system('error', 'cron', 'Proposal jobs error', ['error' => $e->getMessage()]);
}

// ── Cleanup old sync_log entries (older than 5 minutes, for idempotency dedup) ─
if (!$dry_run) {
    $cleanup_sql = "DELETE FROM sync_log WHERE status = 'processing' AND created_at < " .
                   ($driver === 'sqlite' ? "datetime('now', '-10 minutes')" : "DATE_SUB(NOW(), INTERVAL 10 MINUTE)");
    $pdo->exec($cleanup_sql);
}

log_system('info', 'cron', 'Cron job completed', [
    'trace_id' => $trace_id,
    'report' => json_encode($report),
]);

// Output report
echo json_encode($report, JSON_PRETTY_PRINT) . "\n";
