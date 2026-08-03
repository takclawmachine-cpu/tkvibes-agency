<?php
error_reporting(E_ALL); ini_set('display_errors','1');
$cfg = require __DIR__ . '/config.local.php';
echo "config loaded OK\n";
echo "google_service_account: " . ($cfg['google_service_account'] ?? 'NONE') . "\n";
echo "sa file exists: " . (file_exists($cfg['google_service_account'] ?? 'x') ? 'yes' : 'NO') . "\n";
echo "sheet_id: " . ($cfg['google_sheet_id'] ?? 'NONE') . "\n";
echo "api_key set: " . (!empty($cfg['api_key']) ? 'yes' : 'no') . "\n";
echo "secret set: " . (!empty($cfg['secret']) ? 'yes' : 'no') . "\n";
echo "db dsn: " . ($cfg['db']['dsn'] ?? 'NONE') . "\n";
