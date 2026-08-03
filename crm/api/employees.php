<?php
header('X-Robots-Tag: noindex, nofollow');
/**
 * TKVibes CRM — Employees API
 * Returns employee region and country coverage for the lead engine.
 * Protected by shared API key.
 */
require __DIR__ . '/../lib/db.php';
require __DIR__ . '/../lib/functions.php';

$cfg = require __DIR__ . '/../config.local.php';

$key = $_GET['key'] ?? '';
if (!$key || $key !== $cfg['api_key']) {
    json_response(['error' => 'Invalid API key'], 403);
}

$pdo = get_db();
$employees = $pdo->query("SELECT id, name, email, role FROM employees WHERE active = 1")->fetchAll();

$result = [];
foreach ($employees as $emp) {
    $stmt = $pdo->prepare("SELECT region, country FROM employee_regions WHERE employee_id = ?");
    $stmt->execute([$emp['id']]);
    $region_rows = $stmt->fetchAll();

    $regions = [];
    $countries = [];
    foreach ($region_rows as $r) {
        $regions[] = $r['region'];
        $countries[$r['country']] = true;
    }

    $result[] = [
        'id'        => (int)$emp['id'],
        'name'      => $emp['name'],
        'email'     => $emp['email'],
        'role'      => $emp['role'],
        'regions'   => array_values(array_unique($regions)),
        'countries' => array_keys($countries),
    ];
}

json_response($result);