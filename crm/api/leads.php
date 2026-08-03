<?php
/**
 * TKVibes CRM — API endpoints
 * Handles: tag, note, call log, sync
 */
require __DIR__ . '/../lib/db.php';
require __DIR__ . '/../lib/auth.php';
require __DIR__ . '/../lib/functions.php';

$emp = require_auth();
$pdo = get_db();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    json_response(['error' => 'Method not allowed'], 405);
}

$action   = $_POST['action'] ?? '';
$lead_key = $_POST['lead_key'] ?? '';

if (!$lead_key) {
    json_response(['error' => 'lead_key is required'], 400);
}

// Verify lead exists and is accessible to this employee
$lead = get_lead($lead_key);
if (!$lead) {
    json_response(['error' => 'Lead not found'], 404);
}
if (!lead_accessible_to($emp, $lead)) {
    json_response(['error' => 'Access denied to this lead'], 403);
}

switch ($action) {

    case 'tag':
        $new_status = $_POST['status'] ?? '';
        if (!in_array($new_status, ['qualified', 'callback', 'not_qualified'])) {
            json_response(['error' => 'Invalid status'], 400);
        }
        $old_status = $lead['crm_status'] ?? 'new';

        $stmt = $pdo->prepare("UPDATE leads SET crm_status = ?, updated_at = datetime('now') WHERE lead_key = ?");
        $stmt->execute([$new_status, $lead_key]);

        log_activity($emp['id'], $lead_key, 'tagged', $old_status, $new_status,
            "Changed status from $old_status to $new_status");

        json_response(['status' => 'ok', 'new_status' => $new_status]);
        break;

    case 'note':
        $note = trim($_POST['note'] ?? '');
        if (!$note) {
            json_response(['error' => 'Note is required'], 400);
        }
        $existing = $lead['crm_notes'] ?? '';
        $updated = $existing ? $existing . "\n---\n" . date('Y-m-d H:i') . " (" . $emp['name'] . "):\n" . $note
                             : date('Y-m-d H:i') . " (" . $emp['name'] . "):\n" . $note;

        $stmt = $pdo->prepare("UPDATE leads SET crm_notes = ?, updated_at = datetime('now') WHERE lead_key = ?");
        $stmt->execute([$updated, $lead_key]);

        log_activity($emp['id'], $lead_key, 'note', null, null, $note);

        json_response(['status' => 'ok', 'note' => $note]);
        break;

    case 'called':
        $stmt = $pdo->prepare("UPDATE leads SET last_contacted_at = datetime('now'), updated_at = datetime('now') WHERE lead_key = ?");
        $stmt->execute([$lead_key]);

        log_activity($emp['id'], $lead_key, 'called', null, null, 'Marked as contacted');

        json_response(['status' => 'ok']);
        break;

    default:
        json_response(['error' => 'Unknown action: ' . $action], 400);
}