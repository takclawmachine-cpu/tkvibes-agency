<?php
/** Debug: check CRM database leads */
require __DIR__ . '/lib/db.php';
header('Content-Type: application/json');
$pdo = get_db();
$stmt = $pdo->query("SELECT lead_key, business_name, category, city, phone_primary, region, country, assigned_employee, lead_tier, crm_status, sample_site_url, pitch_deck_url FROM leads ORDER BY created_at DESC LIMIT 10");
echo json_encode($stmt->fetchAll(), JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);