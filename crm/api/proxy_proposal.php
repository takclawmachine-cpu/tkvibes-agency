<?php
header('X-Robots-Tag: noindex, nofollow');
/**
 * Proxy for proposal files hosted on private GitHub repo.
 * Employees can view/download sample sites and pitch decks via the CRM.
 *
 * GET /crm/api/proxy_proposal.php?lead_key=xxx&type=sample_site
 * GET /crm/api/proxy_proposal.php?lead_key=xxx&type=pitch_deck
 */
require __DIR__ . '/../lib/db.php';
require __DIR__ . '/../lib/auth.php';
require __DIR__ . '/../lib/functions.php';

$emp = require_auth();

$lead_key = $_GET['lead_key'] ?? '';
$type     = $_GET['type'] ?? '';

if (!$lead_key || !$type) {
    http_response_code(400);
    echo "Missing lead_key or type";
    exit;
}

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

$url = $lead[$type === 'sample_site' ? 'sample_site_url' : 'pitch_deck_url'] ?? '';
if (!$url) {
    http_response_code(404);
    echo "No proposal URL found for this lead";
    exit;
}

// Only allow github raw URLs
if (!str_starts_with($url, 'https://raw.githubusercontent.com/')) {
    http_response_code(403);
    echo "Invalid source URL";
    exit;
}

// Read GitHub token from config
$cfg = require __DIR__ . '/../config.local.php';
$token = $cfg['github_token'] ?? '';

$opts = ['http' => ['method' => 'GET', 'header' => '']];
if ($token) {
    $opts['http']['header'] = "Authorization: Bearer $token\r\n";
}
$html = @file_get_contents($url, false, stream_context_create($opts));

if ($html === false) {
    http_response_code(502);
    echo "Failed to fetch proposal from GitHub";
    exit;
}

$mode = $_GET['mode'] ?? 'view';
$filename = basename(parse_url($url, PHP_URL_PATH));

if ($mode === 'download') {
    header('Content-Type: application/octet-stream');
    header("Content-Disposition: attachment; filename=\"$filename\"");
    header('Content-Length: ' . strlen($html));
} else {
    header('Content-Type: text/html; charset=utf-8');
}

echo $html;