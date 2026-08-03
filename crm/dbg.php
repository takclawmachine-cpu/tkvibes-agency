<?php
error_reporting(E_ALL);
ini_set('display_errors', '1');
require __DIR__ . '/lib/db.php';
require __DIR__ . '/lib/functions.php';
$pdo = get_db();
$rows = $pdo->query("SELECT id, name, email, role, active, length(password) AS pwlen, substr(password,1,12) AS pwsample FROM employees ORDER BY id")->fetchAll(PDO::FETCH_ASSOC);
echo "=== employees ===\n";
foreach ($rows as $r) {
    echo "id={$r['id']} name={$r['name']} email={$r['email']} role={$r['role']} active={$r['active']} pwlen={$r['pwlen']} sample={$r['pwsample']}\n";
}
// Find jashmit
$j = $pdo->prepare("SELECT * FROM employees WHERE name LIKE ? OR email LIKE ?");
$j->execute(['%jashmit%', '%jashmit%']);
$row = $j->fetch(PDO::FETCH_ASSOC);
if ($row) {
    echo "=== jashmit found id={$row['id']} ===\n";
    echo "password column length: " . strlen($row['password']) . "\n";
    echo "password starts with \$2y\$: " . (strpos($row['password'], '$2y$') === 0 ? 'yes' : 'NO -> not a bcrypt hash') . "\n";
    // Test the admin-set new password candidate if provided
    if (!empty($_GET['test'])) {
        $ok = password_verify($_GET['test'], $row['password']);
        echo "password_verify('{$_GET['test']}') => " . ($ok ? 'MATCH' : 'no match') . "\n";
    }
} else {
    echo "jashmit NOT found by name/email search\n";
}
// Also dump table schema for password column
$col = $pdo->query("PRAGMA table_info(employees)")->fetchAll(PDO::FETCH_ASSOC);
foreach ($col as $c) {
    if ($c['name'] === 'password') echo "password column type: {$c['type']}\n";
}
