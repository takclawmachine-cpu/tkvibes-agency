<?php
/** Clean duplicate leads, keep the one with most data */
require __DIR__ . '/lib/db.php';
header('Content-Type: text/plain');
$pdo = get_db();

// Find duplicates: keep the row with the most non-empty fields
$dupes = $pdo->query("SELECT lead_key, COUNT(*) as cnt FROM leads GROUP BY lead_key HAVING cnt > 1")->fetchAll();
echo "Found " . count($dupes) . " duplicate lead_keys\n";

foreach ($dupes as $d) {
    $lk = $d['lead_key'];
    $rows = $pdo->prepare("SELECT rowid, * FROM leads WHERE lead_key = ? ORDER BY LENGTH(business_name || category || city || phone_primary) DESC")->execute([$lk])->fetchAll();
    // Keep first (most data), delete rest
    $keep = true;
    foreach ($rows as $row) {
        if ($keep) { $keep = false; continue; }
        $pdo->prepare("DELETE FROM leads WHERE rowid = ?")->execute([$row['rowid']]);
        echo "  Deleted duplicate: $lk (rowid={$row['rowid']})\n";
    }
}

// Delete leads with empty business_name
$deleted = $pdo->exec("DELETE FROM leads WHERE business_name = '' OR business_name IS NULL");
echo "Deleted $deleted empty-name leads\n";

echo "Done. Remaining leads: " . $pdo->query("SELECT COUNT(*) FROM leads")->fetchColumn() . "\n";