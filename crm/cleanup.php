<?php
header('X-Robots-Tag: noindex, nofollow');
require __DIR__ . '/lib/db.php';
require __DIR__ . '/lib/functions.php';
$pdo = get_db();
$pdo->exec("DELETE FROM lead_activities");
$pdo->exec("DELETE FROM proposals");
$pdo->exec("DELETE FROM proposal_generation_jobs");
$pdo->exec("DELETE FROM leads");
echo "DB cleaned\n";
$cfg = require __DIR__ . '/config.local.php';
if (!empty($cfg['google_service_account']) && !empty($cfg['google_sheet_id'])) {
    require_once __DIR__ . '/lib/sheets_sync.php';
    $client = get_sheets_client();
    if ($client) {
        $resp = $client->read_sheet();
        $num_rows = count($resp[1] ?? []);
        if ($num_rows > 0) {
            $cols = count($resp[0]);
            $range = "A2:" . chr(64+max(26, $cols)) . ($num_rows+1);
            $client->api_call("PUT", "values/$range", ["values" => [[]], "majorDimension" => "ROWS"]);
        }
        echo "Sheet cleaned\n";
    }
}
echo "DONE\n";