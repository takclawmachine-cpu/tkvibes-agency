<?php
/** Upload to crm/ dir. POST JSON: {"path":"api/sync.php","content":"base64..."} */
$b = json_decode(file_get_contents('php://input'), true) ?: [];
$p = $b['path'] ?? ''; $c = $b['content'] ?? '';
if (!$p || !$c) { http_response_code(400); exit; }
if (preg_match('/\.\./', $p)) { http_response_code(400); exit; }
$abs = __DIR__ . "/$p";
$dir = dirname($abs);
if (!is_dir($dir)) mkdir($dir, 0755, true);
file_put_contents($abs, base64_decode($c));
echo 'OK';