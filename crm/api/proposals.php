<?php
header('X-Robots-Tag: noindex, nofollow');
/**
 * TKVibes CRM — Proposals API
 * 
 * POST: Upload a proposal (sample site or pitch deck HTML).
 *   Protected by API key. 
 *   Body: lead_key, type (sample_site|pitch_deck), html (raw HTML content)
 * 
 * GET (action=generate): Create a proposal generation job.
 *   Params: lead_key, feedback (optional if no proposals exist)
 * 
 * GET (action=status): Get generation jobs for a lead.
 *   Params: lead_key
 * 
 * GET (action=feedback): Check if proposals exist and get latest job.
 *   Params: lead_key
 * 
 * GET (no action): Download/view a proposal.
 *   Params: lead_key, type, mode (view|download)
 */

require __DIR__ . '/../lib/db.php';
require __DIR__ . '/../lib/auth.php';
require __DIR__ . '/../lib/functions.php';

$pdo = get_db();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // ── Upload ─────────────────────────────────────────────────────────
    $cfg = require __DIR__ . '/../config.local.php';
    $body = body_json();

    $key = $body['key'] ?? $_GET['key'] ?? '';
    if (!$key || $key !== $cfg['api_key']) {
        json_response(['error' => 'Invalid API key'], 403);
    }

    $lead_key = $body['lead_key'] ?? '';
    $type     = $body['type'] ?? '';
    $html     = $body['html'] ?? '';
    $filename = $body['file_name'] ?? '';

    if (!$lead_key || !$type || !$html) {
        json_response(['error' => 'lead_key, type, and html are required'], 400);
    }
    if (!in_array($type, ['sample_site', 'pitch_deck'])) {
        json_response(['error' => 'type must be sample_site or pitch_deck'], 400);
    }

    // Verify lead exists
    $lead = get_lead($lead_key);
    if (!$lead) {
        // Auto-create a minimal lead entry so the proposal can link
        $stmt = $pdo->prepare("INSERT OR IGNORE INTO leads (lead_key, business_name, crm_status, created_at, updated_at) VALUES (?, ?, 'new', datetime('now'), datetime('now'))");
        // For MySQL compatibility
        try {
            $stmt->execute([$lead_key, $lead_key]);
        } catch (PDOException $e) {
            // MySQL: use INSERT IGNORE
            $pdo->exec("INSERT IGNORE INTO leads (lead_key, business_name, crm_status, created_at, updated_at) VALUES ('" . addslashes($lead_key) . "', '" . addslashes($lead_key) . "', 'new', NOW(), NOW())");
        }
    }

    // Upsert proposal
    if ($pdo->getAttribute(PDO::ATTR_DRIVER_NAME) === 'sqlite') {
        $stmt = $pdo->prepare("
            INSERT INTO proposals (lead_key, type, html, file_name, created_at, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
            ON CONFLICT(lead_key, type) DO UPDATE SET
                html = excluded.html,
                file_name = excluded.file_name,
                updated_at = datetime('now')
        ");
    } else {
        $stmt = $pdo->prepare("
            INSERT INTO proposals (lead_key, type, html, file_name, created_at, updated_at)
            VALUES (?, ?, ?, ?, NOW(), NOW())
            ON DUPLICATE KEY UPDATE
                html = VALUES(html),
                file_name = VALUES(file_name),
                updated_at = NOW()
        ");
    }
    $stmt->execute([$lead_key, $type, $html, $filename]);

    // Also update the lead's sample_site_url / pitch_deck_url field
    $slug = preg_replace('/[^a-z0-9\s-]/', '', strtolower(trim($lead_key)));
    $slug = preg_replace('/\s+/', '-', $slug);
    $slug = substr($slug, 0, 60);
    if ($type === 'sample_site') {
        $github_url = "https://raw.githubusercontent.com/takclawmachine-cpu/tkvibes-agency/main/Sample%20Webpages%20and%20pitch%20deck/sample%20website/{$slug}.html";
        $pdo->prepare("UPDATE leads SET sample_site_url = ?, updated_at = datetime('now') WHERE lead_key = ? AND (sample_site_url IS NULL OR sample_site_url = '')")
            ->execute([$github_url, $lead_key]);
    } elseif ($type === 'pitch_deck') {
        $github_url = "https://raw.githubusercontent.com/takclawmachine-cpu/tkvibes-agency/main/Sample%20Webpages%20and%20pitch%20deck/pitch%20deck/{$slug}.html";
        $pdo->prepare("UPDATE leads SET pitch_deck_url = ?, updated_at = datetime('now') WHERE lead_key = ? AND (pitch_deck_url IS NULL OR pitch_deck_url = '')")
            ->execute([$github_url, $lead_key]);
    }

    // Mark any pending/running generation jobs as completed when a proposal is uploaded
    $pdo->prepare("UPDATE proposal_generation_jobs SET status = 'completed', updated_at = " . ($pdo->getAttribute(PDO::ATTR_DRIVER_NAME) === 'sqlite' ? "datetime('now')" : "NOW()") . " WHERE lead_key = ? AND status IN ('pending', 'running')")
        ->execute([$lead_key]);

    json_response(['status' => 'ok', 'lead_key' => $lead_key, 'type' => $type]);

} elseif ($_SERVER['REQUEST_METHOD'] === 'GET') {
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

        // Check if proposals already exist
        $has_sample = lead_has_proposal($lead_key, 'sample_site');
        $has_deck = lead_has_proposal($lead_key, 'pitch_deck');

        // Check if a pending/running job already exists
        $stmt = $pdo->prepare("SELECT id FROM proposal_generation_jobs WHERE lead_key = ? AND status IN ('pending', 'running') LIMIT 1");
        $stmt->execute([$lead_key]);
        $existing = $stmt->fetch();

        if ($existing) {
            json_response(['error' => 'A generation job is already in progress'], 409);
        }

        // If proposals already exist, feedback is required
        if (($has_sample || $has_deck) && empty($feedback)) {
            json_response(['error' => 'Feedback is required when re-generating'], 400);
        }

        // Create the job
        if ($pdo->getAttribute(PDO::ATTR_DRIVER_NAME) === 'sqlite') {
            $stmt = $pdo->prepare("
                INSERT INTO proposal_generation_jobs (lead_key, feedback, status, created_at, updated_at)
                VALUES (?, ?, 'pending', datetime('now'), datetime('now'))
            ");
        } else {
            $stmt = $pdo->prepare("
                INSERT INTO proposal_generation_jobs (lead_key, feedback, status, created_at, updated_at)
                VALUES (?, ?, 'pending', NOW(), NOW())
            ");
        }
        $stmt->execute([$lead_key, $feedback]);
        $job_id = $pdo->lastInsertId();

        json_response(['status' => 'ok', 'job_id' => (int)$job_id]);

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

        $stmt = $pdo->prepare("SELECT * FROM proposal_generation_jobs WHERE lead_key = ? ORDER BY created_at DESC");
        $stmt->execute([$lead_key]);
        $jobs = $stmt->fetchAll();

        json_response(['status' => 'ok', 'jobs' => $jobs]);

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

        // Check if the user wants to download or view
        $mode = $_GET['mode'] ?? 'view';

        if ($mode === 'download') {
            header('Content-Type: application/octet-stream');
            header('Content-Disposition: attachment; filename="' . $filename . '"');
            header('Content-Length: ' . strlen($html));
            echo $html;
        } else {
            // View inline — serve as HTML
            header('Content-Type: text/html; charset=utf-8');
            echo $html;
        }
        exit;
    }

} else {
    http_response_code(405);
    echo "Method not allowed";
}