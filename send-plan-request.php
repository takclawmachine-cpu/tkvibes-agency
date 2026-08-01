<?php
/* ── send-plan-request.php ──────────────────────
   Receives JSON POST from plan-builder.js
   Sends email to services@tkvibes.in
   ───────────────────────────────────────────── */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['status' => 'error', 'message' => 'POST required']);
    exit;
}

$raw = file_get_contents('php://input');
$data = json_decode($raw, true);

if (!$data || empty($data['name']) || empty($data['email']) || empty($data['phone']) || empty($data['services'])) {
    http_response_code(400);
    echo json_encode(['status' => 'error', 'message' => 'Missing required fields']);
    exit;
}

$to = 'services@tkvibes.in';
$subject = 'Custom Plan Request from ' . $data['name'];

$lines = [];
$lines[] = 'New Custom Plan Request — TKVibes';
$lines[] = '';
$lines[] = 'Name:     ' . $data['name'];
$lines[] = 'Business: ' . ($data['business'] ?: '—');
$lines[] = 'Email:    ' . $data['email'];
$lines[] = 'Phone:    ' . $data['phone'];
$lines[] = '';
$lines[] = 'Selected Services:';

foreach ($data['services'] as $svc) {
    $price = 'Rs ' . number_format(intval($svc['price']), 0, '.', ',');
    $lines[] = '  - ' . $svc['name'] . ' (' . $price . ')';
}

$lines[] = '';
$lines[] = 'Total: Rs ' . number_format(intval($data['total']), 0, '.', ',');

if (!empty($data['notes'])) {
    $lines[] = '';
    $lines[] = 'Notes: ' . $data['notes'];
}

$body = implode("\r\n", $lines);

$headers = "From: TKVibes Website <no-reply@tkvibes.com>\r\n";
$headers .= "Reply-To: " . $data['email'] . "\r\n";
$headers .= "X-Mailer: PHP/" . phpversion();

$sent = mail($to, $subject, $body, $headers);

if ($sent) {
    echo json_encode(['status' => 'ok', 'message' => 'Email sent']);
} else {
    http_response_code(500);
    echo json_encode(['status' => 'error', 'message' => 'Mail delivery failed']);
}