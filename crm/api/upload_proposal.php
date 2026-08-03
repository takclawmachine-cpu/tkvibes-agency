<?php
/** Upload proposal files. POST JSON: {"name":"sample-website/fn.html","content":"..."} */
$b = json_decode(file_get_contents('php://input'), true) ?: [];
$n = $b['name'] ?? ''; $c = $b['content'] ?? '';
if (!$n || !$c) { http_response_code(400); exit; }
// Security: only .html files, no path traversal
if (preg_match('/\.\./', $n) || !preg_match('/\.html$/', $n)) { http_response_code(400); exit; }
$base = dirname(__DIR__) . '/proposals';
$path = "$base/$n";
$dir = dirname($path);
if (!is_dir($dir)) mkdir($dir, 0755, true);
file_put_contents($path, $c);
echo 'OK';