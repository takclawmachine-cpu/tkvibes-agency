<?php
header('X-Robots-Tag: noindex, nofollow');
/**
 * TKVibes CRM — Leads API
 * Handles: tag, note, call log, sync
 */
require __DIR__ . '/../lib/db.php';
require __DIR__ . '/../lib/auth.php';
require __DIR__ . '/../lib/functions.php';
require_once __DIR__ . '/../lib/sheets_sync.php';

$pdo = get_db();

// Allow API key-based updates for specific fields (sample_site_url, pitch_deck_url)
// Must check BEFORE require_auth() since API clients have no session.
$body = body_json();
$api_key_mode = false;
if (is_file(__DIR__ . '/../config.local.php')) {
    $cfg = require __DIR__ . '/../config.local.php';
    $is_api_key = ($body['key'] ?? '') === ($cfg['api_key'] ?? '');
    if ($is_api_key && in_array($body['field'] ?? '', ['sample_site_url', 'pitch_deck_url'], true)) {
        $api_key_mode = true;
        $emp = ['id' => 0, 'name' => 'System', 'role' => 'admin'];
    }
}
if (!$api_key_mode) {
    $emp = require_auth();
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    json_response(['error' => 'Method not allowed'], 405);
}

$action   = $body['action'] ?? $_POST['action'] ?? '';
$lead_key = $body['lead_key'] ?? $_POST['lead_key'] ?? '';

if (!$lead_key) {
    json_response(['error' => 'lead_key is required'], 400);
}

// Verify lead exists and is accessible to this employee
$lead = get_lead($lead_key);
if (!$lead) {
    json_response(['error' => 'Lead not found'], 404);
}
if (!$api_key_mode && !lead_accessible_to($emp, $lead)) {
    json_response(['error' => 'Access denied to this lead'], 403);
}

switch ($action) {

    case 'update':
        // Accept JSON body for field updates
        $field = $body['field'] ?? $_POST['field'] ?? '';
        $value  = $body['value'] ?? $_POST['value'] ?? '';

        if (!$field) {
            json_response(['error' => 'field is required'], 400);
        }

        // Whitelist editable fields
        $editable = [
            'business_name', 'category', 'owner_name', 'phone_primary', 'phone_secondary',
            'whatsapp', 'email', 'address', 'city', 'pincode', 'region', 'country',
            'website_url', 'website_quality', 'rating', 'review_count', 'years_in_business',
            'socials', 'pain_points', 'recommended_pitch', 'notes', 'contact_channel',
            'opening_hours', 'has_website', 'source', 'source_url',
            'sample_site_url', 'pitch_deck_url',
        ];
        if (!in_array($field, $editable, true)) {
            json_response(['error' => 'Field not editable: ' . $field], 400);
        }

        $old_value = (string)($lead[$field] ?? '');

        // Sanitize value
        if (in_array($field, ['rating', 'review_count', 'lead_score', 'has_website'], true)) {
            $value = $value === '' ? null : (float)$value;
            if ($field === 'review_count' || $field === 'lead_score' || $field === 'has_website') {
                $value = $value === null ? null : (int)$value;
            }
            $stmt = $pdo->prepare("UPDATE leads SET \"$field\" = ?, updated_at = datetime('now') WHERE lead_key = ?");
            $stmt->execute([$value, $lead_key]);
        } else {
            $value = (string)$value;
            $stmt = $pdo->prepare("UPDATE leads SET \"$field\" = ?, updated_at = datetime('now') WHERE lead_key = ?");
            $stmt->execute([$value, $lead_key]);
        }

        $desc = "Updated $field";
        if ($old_value !== (string)$value) {
            $desc = "Updated $field: '" . mb_substr($old_value, 0, 80) . "' → '" . mb_substr((string)$value, 0, 80) . "'";
        }

        log_activity($emp['id'], $lead_key, 'updated', $old_value, (string)$value, $desc);

        // Real-time sync back to Google Sheets
        sheets_writeback($lead_key, [$field => (string)$value]);

        json_response(['status' => 'ok', 'field' => $field, 'old_value' => $old_value, 'new_value' => (string)$value]);
        break;

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

        // Real-time sync back to Google Sheets
        sheets_writeback($lead_key, ['crm_status' => $new_status]);

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

        // Real-time sync back to Google Sheets
        sheets_writeback($lead_key, ['crm_notes' => $updated]);

        json_response(['status' => 'ok', 'note' => $note]);
        break;

    case 'called':
        $stmt = $pdo->prepare("UPDATE leads SET last_contacted_at = datetime('now'), updated_at = datetime('now') WHERE lead_key = ?");
        $stmt->execute([$lead_key]);

        log_activity($emp['id'], $lead_key, 'called', null, null, 'Marked as contacted');

        // Real-time sync back to Google Sheets
        sheets_writeback($lead_key, ['last_contacted_at' => date('Y-m-d H:i:s')]);

        json_response(['status' => 'ok']);
        break;

    default:
        json_response(['error' => 'Unknown action: ' . $action], 400);
}