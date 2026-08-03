<?php
error_reporting(E_ALL);
ini_set('display_errors', '1');
require __DIR__ . '/lib/db.php';
require __DIR__ . '/lib/auth.php';
require __DIR__ . '/lib/functions.php';
$pdo = get_db();

$newpw = 'Tkvibes@123';
$hash = password_hash($newpw, PASSWORD_BCRYPT);
$upd = $pdo->prepare("UPDATE employees SET password=?, active=1, updated_at=datetime('now') WHERE id=3");
$upd->execute([$hash]);
echo "reset jashmit(id=3) password, rows=" . $upd->rowCount() . "\n";

// Verify via the REAL login() function
$emp = login('jashmit@tkvibes.in', $newpw);
echo "login('jashmit@tkvibes.in','Tkvibes@123') => " . ($emp ? "SUCCESS role={$emp['role']}" : 'FAILED') . "\n";

// Also confirm old-wrong behavior: a bad password is rejected
$bad = login('jashmit@tkvibes.in', 'wrongpass');
echo "login bad password => " . ($bad ? 'UNEXPECTED SUCCESS' : 'correctly rejected') . "\n";

// Confirm the edit_employee re-hash path produces a verify-able hash (simulate)
$testhash = password_hash('newpass99', PASSWORD_BCRYPT);
echo "verify('newpass99') against fresh hash => " . (password_verify('newpass99', $testhash) ? 'ok' : 'FAIL') . "\n";
