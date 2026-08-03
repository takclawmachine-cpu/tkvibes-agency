<?php
error_reporting(E_ALL); ini_set('display_errors','1');
require __DIR__ . '/lib/db.php';
require __DIR__ . '/lib/functions.php';
$cfg = require __DIR__ . '/config.local.php';
echo "sa set: " . (!empty($cfg['google_service_account']) ? 'yes' : 'no') . "\n";
echo "sa file exists: " . (file_exists($cfg['google_service_account']) ? 'yes' : 'NO') . "\n";
echo "sheet_id: " . ($cfg['google_sheet_id'] ?? 'NONE') . "\n";
try {
    require __DIR__ . '/lib/GoogleSheetsClient.php';
    $client = new GoogleSheetsClient($cfg['google_service_account'], $cfg['google_sheet_id']);
    [$header, $rows] = $client->read_sheet();
    echo "header cols: " . count($header) . "\n";
    echo "data rows: " . count($rows) . "\n";
    if (!empty($header)) echo "first header: " . implode(',', array_slice($header,0,5)) . "\n";
} catch (Throwable $e) {
    echo "ERR: " . $e->getMessage() . "\n";
}
