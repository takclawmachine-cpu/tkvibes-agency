<?php
// TEMP debug probe — removed after diagnosis.
error_reporting(E_ALL);
ini_set('display_errors', '1');
try {
    require __DIR__ . '/lib/functions.php';
    require __DIR__ . '/lib/db.php';
    $pdo = get_db();
    echo "DB OK driver=" . $pdo->getAttribute(PDO::ATTR_DRIVER_NAME) . "\n";
    echo "employees=" . $pdo->query("SELECT COUNT(*) FROM employees")->fetchColumn() . "\n";
} catch (Throwable $e) {
    echo "ERR: " . $e->getMessage() . "\n";
    echo "FILE: " . $e->getFile() . ":" . $e->getLine() . "\n";
}
echo "config exists: " . (file_exists(__DIR__ . '/config.local.php') ? 'yes' : 'no') . "\n";
$cfg = @require __DIR__ . '/config.local.php';
echo "dsn=" . ($cfg['db']['dsn'] ?? 'NONE') . "\n";
echo "data dir writable: " . (is_writable(__DIR__ . '/data') ? 'yes' : 'no') . "\n";
echo "sqlite ext: " . (extension_loaded('pdo_sqlite') ? 'loaded' : 'MISSING') . "\n";
