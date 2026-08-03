<?php
/**
 * Upload proposal files to server. POST with API key auth.
 * Body (JSON): {key, name, content}
 */
require __DIR__ . '/../lib/db.php';
$body = json_decode(file_get_contents('php://input'), true) ?: [];
$cfg = require __DIR__ . '/../config.local.php';
$key = $body['key'] ?? '';
if (!$key || $key !== $cfg['api_key']) {
    http_response_code(403); exit;
}
$name = $body['name'] ?? '';
$content = $body['content'] ?? '';
if (!$name || !$content) {
    http_response_code(400); exit;
}
// Security: only allow .html files, no path traversal
if (!preg_match('/^[a-zA-Z0-9_\-]+\.html$/', $name)) {
    http_response_code(400); exit;
}
$dir = __DIR__ . '/../../proposals';
@mkdir("$dir/sample-website", 0755, true);
@mkdir("$dir/pitch-deck", 0755, true);
file_put_contents("$dir/$name", $content);
echo json_encode(['status' => 'ok', 'name' => $name]);