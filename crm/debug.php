<?php
/** Debug + Cleanup: check CRM database, remove duplicate empty leads */
require __DIR__ . '/lib/db.php';
header('Content-Type: application/json');

$pdo = get_db();

// Find duplicates with empty business_name
$dupes = $pdo->query("SELECT lead_key, COUNT(*) as cnt FROM leads GROUP BY lead_key HAVING cnt > 1")->fetchAll();
$removed = 0;
foreach ($dupes as $d) {
    $lk = $d['lead_key'];
    $stmt = $pdo->prepare("DELETE FROM leads WHERE lead_key = ? AND (business_name = '' OR business_name IS NULL)");
    $stmt->execute([$lk]);
    $removed += $stmt->rowCount();
}

// Also clean any remaining empties
$removed2 = $pdo->exec("DELETE FROM leads WHERE business_name = '' OR business_name IS NULL");

// Return remaining leads
$leads = $pdo->query("SELECT lead_key, business_name, category, city, phone_primary, region, country, assigned_employee, lead_tier, crm_status, sample_site_url, pitch_deck_url FROM leads ORDER BY created_at DESC")->fetchAll();

echo json_encode([
    'duplicates_removed' => $removed,
    'empties_removed' => $removed2,
    'remaining' => count($leads),
    'leads' => $leads,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);