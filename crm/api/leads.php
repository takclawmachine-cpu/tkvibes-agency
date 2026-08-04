<?php
header('X-Robots-Tag: noindex, nofollow');
/**
 * TKVibes CRM — Leads API
 * Handles: tag, note, call log, field update
 * 
 * Auth modes:
 * 1. API key — allowed for sample_site_url / pitch_deck_url fields only
 * 2. Session — all other actions require employee login
 */
require __DIR__ . '/../lib/db.php';
require __DIR__ . '/../lib/auth.php';
require __DIR__ . '/../lib/functions.php';
require_once __DIR__ . '/../lib/constants.php';
require_once __DIR__ . '/../lib/sheets_sync.php';

$pdo = get_db();

// ── Auth ────────────────────────────────────────────────────────────────
// Read body ONCE — used for both API key detection and parameter extraction
$body = body_json();

$api_key_mode = false;
$emp = null;

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
    // CSRF check for session-authenticated requests
    if (!verify_csrf()) {
        json_response(['error' => 'Invalid or missing CSRF token'], 403);
    }
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    json_response(['error' => 'Method not allowed'], 405);
}

// ── Read parameters from JSON body with $_POST fallback ─────────────────
$action   = $body['action'] ?? $_POST['action'] ?? '';
$lead_key = $body['lead_key'] ?? $_POST['lead_key'] ?? '';

if (!$lead_key) {
    json_response(['error' => 'lead_key is required'], 400);
}

// Verify lead exists and is accessible
$lead = get_lead($lead_key);
if (!$lead) {
    json_response(['error' => 'Lead not found'], 404);
}
if (!$api_key_mode && !lead_accessible_to($emp, $lead)) {
    json_response(['error' => 'Access denied to this lead'], 403);
}

/**
 * Validate a SQL column/field name.
 * Only allows lowercase letters, numbers, and underscores.
 * Prevents SQL injection through field names even when whitelisted.
 */
function validate_field_name(string $name): bool
{
    return preg_match('/^[a-z][a-z0-9_]*$/', $name) === 1;
}

switch ($action) {

    case 'update':
        $field = $body['field'] ?? $_POST['field'] ?? '';
        $value = $body['value'] ?? $_POST['value'] ?? '';

        if (!$field) {
            json_response(['error' => 'field is required'], 400);
        }

        // Validate field name safety (defense-in-depth beyond whitelist)
        if (!validate_field_name($field)) {
            json_response(['error' => 'Invalid field name'], 400);
        }

        // Whitelist editable fields (from centralized constants)
        if (!in_array($field, EDITABLE_FIELDS, true)) {
            json_response(['error' => 'Field not editable: ' . $field], 400);
        }

        $old_value = (string)($lead[$field] ?? '');

        // Sanitize value by type
        if (in_array($field, ['rating', 'review_count', 'lead_score', 'has_website'], true)) {
            $value = $value === '' ? null : (float)$value;
            if ($field === 'review_count' || $field === 'lead_score' || $field === 'has_website') {
                $value = $value === null ? null : (int)$value;
            }
            // Use quoted identifier for the field name — validated above
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
        sheets_writeback($lead_key, [$field => (string)$value]);

        json_response(['status' => 'ok', 'field' => $field, 'old_value' => $old_value, 'new_value' => (string)$value]);
        break;

    case 'tag':
        $new_status = $body['status'] ?? $_POST['status'] ?? '';
        if (!in_array($new_status, ['qualified', 'callback', 'not_qualified'])) {
            json_response(['error' => 'Invalid status'], 400);
        }
        $old_status = $lead['crm_status'] ?? 'new';

        $stmt = $pdo->prepare("UPDATE leads SET crm_status = ?, updated_at = datetime('now') WHERE lead_key = ?");
        $stmt->execute([$new_status, $lead_key]);

        log_activity($emp['id'], $lead_key, 'tagged', $old_status, $new_status,
            "Changed status from $old_status to $new_status");

        sheets_writeback($lead_key, ['crm_status' => $new_status]);

        json_response(['status' => 'ok', 'new_status' => $new_status]);
        break;

    case 'note':
        $note = trim($body['note'] ?? $_POST['note'] ?? '');
        if (!$note) {
            json_response(['error' => 'Note is required'], 400);
        }
        $existing = $lead['crm_notes'] ?? '';
        $updated = $existing
            ? $existing . "\n---\n" . date('Y-m-d H:i') . " (" . $emp['name'] . "):\n" . $note
            : date('Y-m-d H:i') . " (" . $emp['name'] . "):\n" . $note;

        $stmt = $pdo->prepare("UPDATE leads SET crm_notes = ?, updated_at = datetime('now') WHERE lead_key = ?");
        $stmt->execute([$updated, $lead_key]);

        log_activity($emp['id'], $lead_key, 'note', null, null, $note);
        sheets_writeback($lead_key, ['crm_notes' => $updated]);

        json_response(['status' => 'ok', 'note' => $note]);
        break;

    case 'called':
        $stmt = $pdo->prepare("UPDATE leads SET last_contacted_at = datetime('now'), updated_at = datetime('now') WHERE lead_key = ?");
        $stmt->execute([$lead_key]);

        log_activity($emp['id'], $lead_key, 'called', null, null, 'Marked as contacted');
        sheets_writeback($lead_key, ['last_contacted_at' => date('Y-m-d H:i:s')]);

        json_response(['status' => 'ok']);
        break;

    default:
        json_response(['error' => 'Unknown action: ' . $action], 400);
}