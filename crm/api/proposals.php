<?php
header('X-Robots-Tag: noindex, nofollow');
/**
 * TKVibes CRM — Proposals API (Hardened)
 *
 * POST: Upload a proposal (sample site or pitch deck HTML).
 *   Protected by API key.
 *   Body: lead_key, type (sample_site|pitch_deck), html (raw HTML content), file_name, trace_id
 *
 * GET (action=generate): Create a proposal generation job.
 *   Params: lead_key, feedback (optional if no proposals exist)
 *
 * GET (action=status): Get generation jobs for a lead.
 *   Params: lead_key
 *
 * GET (action=api_pending): List pending/stale-running jobs (API key auth).
 *
 * GET (action=api_complete): Mark a job as completed/failed (API key auth).
 *   Params: job_id, status (completed|failed|running)
 *
 * GET (action=api_feedback): Get job feedback (API key auth).
 *   Params: job_id
 *
 * GET (action=feedback): Check if proposals exist and get latest job.
 *   Params: lead_key
 *
 * GET (no action): Download/view a proposal.
 *   Params: lead_key, type, mode (view|download)
 */
require __DIR__ . '/../lib/db.php';
require __DIR__ . '/../lib/auth.php';
require_once __DIR__ . '/../lib/constants.php';
require __DIR__ . '/../lib/functions.php';

$pdo = get_db();
$driver = $pdo->getAttribute(PDO::ATTR_DRIVER_NAME);
$now_expr = $driver === 'sqlite' ? "datetime('now')" : "NOW()";

// ── POST: Upload proposal ───────────────────────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $cfg = require __DIR__ . '/../config.local.php';
    $body = body_json();

    $key = $body['key'] ?? $_GET['key'] ?? '';
    if (!$key || !hash_equals($cfg['api_key'] ?? '', $key)) {
        json_response(['error' => 'Invalid API key'], 403);
    }

    $lead_key = $body['lead_key'] ?? '';
    $type     = $body['type'] ?? '';
    $html     = $body['html'] ?? '';
    $filename = $body['file_name'] ?? '';
    $trace_id = $body['trace_id'] ?? $_SERVER['HTTP_X_TRACE_ID'] ?? '';

    if (!$lead_key || !$type || !$html) {
        json_response(['error' => 'lead_key, type, and html are required'], 400);
    }
    if (!in_array($type, PROPOSAL_TYPES, true)) {
        json_response(['error' => 'type must be sample_site or pitch_deck'], 400);
    }

    // Verify lead exists — do NOT auto-create orphan leads (C3 fix)
    $lead = get_lead($lead_key);
    if (!$lead) {
        log_system('warning', 'proposals', 'Proposal upload for non-existent lead rejected', [
            'lead_key' => $lead_key,
            'type' => $type,
            'trace_id' => $trace_id,
        ]);
        json_response(['error' => 'Lead not found: ' . $lead_key], 404);
    }

    // Migration safety: ensure trace_id column exists on proposals table
    $has_proposals_trace_id = false;
    try {
        $pdo->query("SELECT trace_id FROM proposals LIMIT 1");
        $has_proposals_trace_id = true;
    } catch (PDOException $e) {
        try {
            $pdo->exec($driver === 'sqlite' ? "ALTER TABLE proposals ADD COLUMN trace_id TEXT DEFAULT ''" : "ALTER TABLE proposals ADD COLUMN trace_id VARCHAR(64) DEFAULT ''");
            $has_proposals_trace_id = true;
        } catch (PDOException $e2) {}
    }

    // Upsert proposal — driver-compatible
    if ($driver === 'sqlite') {
        $insert_fields = "lead_key, type, html, file_name" . ($has_proposals_trace_id ? ", trace_id" : "") . ", created_at, updated_at";
        $insert_values = "?, ?, ?, ?" . ($has_proposals_trace_id ? ", ?" : "") . ", $now_expr, $now_expr";
        $stmt = $pdo->prepare("
            INSERT INTO proposals ($insert_fields)
            VALUES ($insert_values)
            ON CONFLICT(lead_key, type) DO UPDATE SET
                html = excluded.html,
                file_name = excluded.file_name" . ($has_proposals_trace_id ? ",
                trace_id = excluded.trace_id" : "") . ",
                updated_at = $now_expr
        ");
    } else {
        $insert_fields = "lead_key, type, html, file_name" . ($has_proposals_trace_id ? ", trace_id" : "") . ", created_at, updated_at";
        $insert_values = "?, ?, ?, ?" . ($has_proposals_trace_id ? ", ?" : "") . ", $now_expr, $now_expr";
        $stmt = $pdo->prepare("
            INSERT INTO proposals ($insert_fields)
            VALUES ($insert_values)
            ON DUPLICATE KEY UPDATE
                html = VALUES(html),
                file_name = VALUES(file_name)" . ($has_proposals_trace_id ? ",
                trace_id = VALUES(trace_id)" : "") . ",
                updated_at = $now_expr
        ");
    }

    $exec_params = [$lead_key, $type, $html, $filename];
    if ($has_proposals_trace_id) {
        $exec_params[] = $trace_id ?: uniqid('prop_');
    }
    $stmt->execute($exec_params);

    // Also update the lead's sample_site_url / pitch_deck_url field
    // Use GitHub repo from config (not hardcoded)
    $github_repo = $cfg['github_repo'] ?? 'takclawmachine-cpu/tkvibes-agency';
    $github_branch = $cfg['github_branch'] ?? 'main';

    // Build slug from lead_key (matching Python slugify)
    $slug = preg_replace('/[^a-z0-9\s-]/', '', strtolower(trim($lead_key)));
    $slug = preg_replace('/\s+/', '-', $slug);
    $slug = preg_replace('/-{2,}/', '-', $slug);
    $slug = substr($slug, 0, 60);

    // Check if trace_id column exists (migration safety)
    $has_trace_id = false;
    try {
        $pdo->query("SELECT trace_id FROM leads LIMIT 1");
        $has_trace_id = true;
    } catch (PDOException $e) {
        // Column doesn't exist — migrate
        $alter = $driver === 'sqlite' ? "ALTER TABLE leads ADD COLUMN trace_id TEXT DEFAULT ''" : "ALTER TABLE leads ADD COLUMN trace_id VARCHAR(64) DEFAULT ''";
        try { $pdo->exec($alter); $has_trace_id = true; } catch (PDOException $e2) {}
    }

    if ($type === 'sample_site') {
        $github_url = "https://raw.githubusercontent.com/{$github_repo}/{$github_branch}/Sample%20Webpages%20and%20pitch%20deck/sample%20website/{$slug}.html";
        $update_sql = $has_trace_id
            ? "UPDATE leads SET sample_site_url = COALESCE(NULLIF(sample_site_url, ''), ?), trace_id = ?, updated_at = $now_expr WHERE lead_key = ?"
            : "UPDATE leads SET sample_site_url = COALESCE(NULLIF(sample_site_url, ''), ?), updated_at = $now_expr WHERE lead_key = ?";
        $pdo->prepare($update_sql)->execute($has_trace_id ? [$github_url, $trace_id ?: uniqid('prop_'), $lead_key] : [$github_url, $lead_key]);
    } elseif ($type === 'pitch_deck') {
        $github_url = "https://raw.githubusercontent.com/{$github_repo}/{$github_branch}/Sample%20Webpages%20and%20pitch%20deck/pitch%20deck/{$slug}.html";
        $update_sql = $has_trace_id
            ? "UPDATE leads SET pitch_deck_url = COALESCE(NULLIF(pitch_deck_url, ''), ?), trace_id = ?, updated_at = $now_expr WHERE lead_key = ?"
            : "UPDATE leads SET pitch_deck_url = COALESCE(NULLIF(pitch_deck_url, ''), ?), updated_at = $now_expr WHERE lead_key = ?";
        $pdo->prepare($update_sql)->execute($has_trace_id ? [$github_url, $trace_id ?: uniqid('prop_'), $lead_key] : [$github_url, $lead_key]);
    }

    // Mark any pending/running generation jobs as completed when a proposal is uploaded
    $pdo->prepare("UPDATE proposal_generation_jobs SET status = 'completed', updated_at = $now_expr WHERE lead_key = ? AND status IN ('pending', 'running')")
        ->execute([$lead_key]);

    log_system('info', 'proposals', 'Proposal uploaded', [
        'lead_key' => $lead_key,
        'type' => $type,
        'trace_id' => $trace_id,
    ]);

    json_response(['status' => 'ok', 'lead_key' => $lead_key, 'type' => $type]);
}

// ── GET endpoints ───────────────────────────────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $action = $_GET['action'] ?? '';

    if ($action === 'generate') {
        // ── Generate proposal job ──────────────────────────────────────
        $emp = require_auth();
        $lead_key = $_GET['lead_key'] ?? '';
        $feedback = $_GET['feedback'] ?? '';

        if (!$lead_key) {
            json_response(['error' => 'lead_key is required'], 400);
        }

        $lead = get_lead($lead_key);
        if (!$lead) {
            json_response(['error' => 'Lead not found'], 404);
        }
        if (!lead_accessible_to($emp, $lead)) {
            json_response(['error' => 'Access denied'], 403);
        }

        // Ensure the proposal_generation_jobs table exists
        try {
            $pdo->query("SELECT 1 FROM proposal_generation_jobs LIMIT 1");
        } catch (PDOException $e) {
            // Table doesn't exist — create it (driver-specific)
            $pdo->exec("CREATE TABLE IF NOT EXISTS proposal_generation_jobs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_key    TEXT    NOT NULL,
                feedback    TEXT    NOT NULL DEFAULT '',
                status      TEXT    NOT NULL DEFAULT 'pending',
                trace_id    TEXT    NOT NULL DEFAULT '',
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (lead_key) REFERENCES leads(lead_key) ON DELETE CASCADE
            )");
        }

        // Check if proposals already exist
        $has_sample = lead_has_proposal($lead_key, 'sample_site');
        $has_deck = lead_has_proposal($lead_key, 'pitch_deck');

        // Check if a pending/running job already exists
        try {
            $stmt = $pdo->prepare("SELECT id FROM proposal_generation_jobs WHERE lead_key = ? AND status IN ('pending', 'running') LIMIT 1");
            $stmt->execute([$lead_key]);
            $existing = $stmt->fetch();
        } catch (PDOException $e) {
            $existing = false;
        }

        if ($existing) {
            json_response(['error' => 'A generation job is already in progress'], 409);
        }

        // If proposals already exist, feedback is required
        if (($has_sample || $has_deck) && empty($feedback)) {
            json_response(['error' => 'Feedback is required when re-generating'], 400);
        }

        // Create the job
        try {
            $trace_id = $_SERVER['HTTP_X_TRACE_ID'] ?? uniqid('prop_');
            $stmt = $pdo->prepare(
                "INSERT INTO proposal_generation_jobs (lead_key, feedback, status, trace_id, created_at, updated_at)
                 VALUES (?, ?, 'pending', ?, $now_expr, $now_expr)"
            );
            $stmt->execute([$lead_key, $feedback, $trace_id]);
            $job_id = $pdo->lastInsertId();
            log_system('info', 'proposals', 'Generation job created', [
                'job_id' => (int)$job_id,
                'lead_key' => $lead_key,
                'trace_id' => $trace_id,
            ]);
            json_response(['status' => 'ok', 'job_id' => (int)$job_id]);
        } catch (PDOException $e) {
            json_response(['error' => 'Database error creating job: ' . $e->getMessage()], 500);
        }

    } elseif ($action === 'status') {
        // ── Get job status ────────────────────────────────────────────
        $emp = require_auth();
        $lead_key = $_GET['lead_key'] ?? '';

        if (!$lead_key) {
            json_response(['error' => 'lead_key is required'], 400);
        }

        $lead = get_lead($lead_key);
        if (!$lead) {
            json_response(['error' => 'Lead not found'], 404);
        }
        if (!lead_accessible_to($emp, $lead)) {
            json_response(['error' => 'Access denied'], 403);
        }

        try {
            $stmt = $pdo->prepare("SELECT * FROM proposal_generation_jobs WHERE lead_key = ? ORDER BY created_at DESC");
            $stmt->execute([$lead_key]);
            $jobs = $stmt->fetchAll();
        } catch (PDOException $e) {
            $jobs = [];
        }

        json_response(['status' => 'ok', 'jobs' => $jobs]);

    } elseif ($action === 'api_pending') {
        // ── API: list pending jobs (API key auth) ──────────────────────
        $cfg = require __DIR__ . '/../config.local.php';
        $key = $_GET['key'] ?? '';
        if (!$key || !hash_equals($cfg['api_key'] ?? '', $key)) {
            json_response(['error' => 'Invalid API key'], 403);
        }
        try {
            // Return jobs that are pending, or running but stale (>10 min)
            $stale_time = $driver === 'sqlite' ? "datetime('now', '-10 minutes')" : "DATE_SUB(NOW(), INTERVAL 10 MINUTE)";
            $stmt = $pdo->query("SELECT * FROM proposal_generation_jobs WHERE status IN ('pending', 'running') OR (status = 'running' AND updated_at < $stale_time) ORDER BY created_at ASC LIMIT 10");
            $jobs = $stmt->fetchAll();
        } catch (PDOException $e) {
            $jobs = [];
        }
        json_response(['status' => 'ok', 'jobs' => $jobs]);

    } elseif ($action === 'api_complete') {
        // ── API: mark a job as completed/failed (API key auth) ──────────
        $cfg = require __DIR__ . '/../config.local.php';
        $key = $_GET['key'] ?? '';
        if (!$key || !hash_equals($cfg['api_key'] ?? '', $key)) {
            json_response(['error' => 'Invalid API key'], 403);
        }
        $job_id = (int)($_GET['job_id'] ?? 0);
        $status = $_GET['status'] ?? 'completed';
        if (!$job_id) {
            json_response(['error' => 'job_id is required'], 400);
        }
        if (!in_array($status, PROPOSAL_JOB_STATUSES, true)) {
            json_response(['error' => 'Invalid status'], 400);
        }
        $pdo->prepare("UPDATE proposal_generation_jobs SET status = ?, updated_at = $now_expr WHERE id = ?")
            ->execute([$status, $job_id]);
        json_response(['status' => 'ok']);

    } elseif ($action === 'api_feedback') {
        // ── API: get feedback for a job (API key auth) ─────────────────
        $cfg = require __DIR__ . '/../config.local.php';
        $key = $_GET['key'] ?? '';
        if (!$key || !hash_equals($cfg['api_key'] ?? '', $key)) {
            json_response(['error' => 'Invalid API key'], 403);
        }
        $job_id = (int)($_GET['job_id'] ?? 0);
        if (!$job_id) {
            json_response(['error' => 'job_id is required'], 400);
        }
        $stmt = $pdo->prepare("SELECT * FROM proposal_generation_jobs WHERE id = ?");
        $stmt->execute([$job_id]);
        $job = $stmt->fetch();
        json_response(['status' => 'ok', 'job' => $job ?: null]);

    } elseif ($action === 'feedback') {
        // ── Check feedback state ──────────────────────────────────────
        $emp = require_auth();
        $lead_key = $_GET['lead_key'] ?? '';

        if (!$lead_key) {
            json_response(['error' => 'lead_key is required'], 400);
        }

        $lead = get_lead($lead_key);
        if (!$lead) {
            json_response(['error' => 'Lead not found'], 404);
        }
        if (!lead_accessible_to($emp, $lead)) {
            json_response(['error' => 'Access denied'], 403);
        }

        $has_sample = lead_has_proposal($lead_key, 'sample_site');
        $has_deck = lead_has_proposal($lead_key, 'pitch_deck');
        $has_proposals = $has_sample || $has_deck;

        $stmt = $pdo->prepare("SELECT * FROM proposal_generation_jobs WHERE lead_key = ? ORDER BY created_at DESC LIMIT 1");
        $stmt->execute([$lead_key]);
        $latest_job = $stmt->fetch();

        json_response([
            'status' => 'ok',
            'has_proposals' => $has_proposals,
            'latest_job' => $latest_job ?: null,
        ]);

    } else {
        // ── Download / view ────────────────────────────────────────────
        $emp = require_auth();

        $lead_key = $_GET['lead_key'] ?? '';
        $type     = $_GET['type'] ?? '';

        if (!$lead_key || !$type) {
            http_response_code(400);
            echo "Missing lead_key or type";
            exit;
        }
        if (!in_array($type, PROPOSAL_TYPES, true)) {
            http_response_code(400);
            echo "Invalid proposal type";
            exit;
        }

        // Verify access
        $lead = get_lead($lead_key);
        if (!$lead) {
            http_response_code(404);
            echo "Lead not found";
            exit;
        }
        if (!lead_accessible_to($emp, $lead)) {
            http_response_code(403);
            echo "Access denied";
            exit;
        }

        $stmt = $pdo->prepare("SELECT * FROM proposals WHERE lead_key = ? AND type = ?");
        $stmt->execute([$lead_key, $type]);
        $proposal = $stmt->fetch();

        if (!$proposal) {
            http_response_code(404);
            echo "No proposal found for this lead";
            exit;
        }

        $html = $proposal['html'];
        $filename = $proposal['file_name'] ?: ($type === 'sample_site' ? "{$lead_key}-website.html" : "{$lead_key}-pitch-deck.html");

        $mode = $_GET['mode'] ?? 'view';
        if ($mode === 'download') {
            header('Content-Type: application/octet-stream');
            header('Content-Disposition: attachment; filename="' . $filename . '"');
            header('Content-Length: ' . strlen($html));
            echo $html;
        } else {
            header('Content-Type: text/html; charset=utf-8');
            echo $html;
        }
        exit;
    }
} else {
    http_response_code(405);
    echo "Method not allowed";
}
