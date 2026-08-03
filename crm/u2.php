<?php
/** Upload any file. POST JSON: {"path":"proposals/sample-website/f.html","content":"..."} */
$b = json_decode(file_get_contents('php://input'), true) ?: [];
$p = $b['path'] ?? ''; $c = $b['content'] ?? '';
if (!$p || !$c) { http_response_code(400); exit; }
if (preg_match('/\.\./', $p)) { http_response_code(400); exit; }
$base = dirname(__DIR__) . '/proposals';
$abs = "$base/$p";
$dir = dirname($abs);
if (!is_dir($dir)) mkdir($dir, 0755, true);
file_put_contents($abs, $c);
echo 'OK';