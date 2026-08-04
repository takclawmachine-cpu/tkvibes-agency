<?php
/** Public API: list all proposals. No auth required. */
require __DIR__ . '/../lib/db.php';
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
$pdo = get_db();
$leads = $pdo->query("SELECT lead_key, business_name, sample_site_url, pitch_deck_url FROM leads WHERE (sample_site_url != '' OR pitch_deck_url != '') AND business_name != '' ORDER BY lead_tier, business_name")->fetchAll();
echo json_encode($leads, JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);