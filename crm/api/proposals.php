<?php
header('X-Robots-Tag: noindex, nofollow');
/**
 * TKVibes CRM — Proposals API
 * 
 * POST: Upload a proposal (sample site or pitch deck HTML).
 *   Protected by API key. 
 *   Body: lead_key, type (sample_site|pitch_deck), html (raw HTML content)
 * 
 * GET: Download/view a proposal.
 *   ?lead_key=XXX&type=sample_site
 *   Returns the HTML for download or inline display.
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
    // for the GitHub raw URL (set by git_publish) or mark as uploaded
    // Build the expected GitHub raw URL for future reference
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

    json_response(['status' => 'ok', 'lead_key' => $lead_key, 'type' => $type]);

} elseif ($_SERVER['REQUEST_METHOD'] === 'GET') {
    // ── Download / view ────────────────────────────────────────────────
    $emp = require_auth();  // requires employee login

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

} else {
    http_response_code(405);
    echo "Method not allowed";
}