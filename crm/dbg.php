<?php
error_reporting(E_ALL);
ini_set('display_errors', '1');
try {
    require __DIR__ . '/lib/functions.php';
    require __DIR__ . '/lib/db.php';
    require __DIR__ . '/lib/auth.php';
    $pdo = get_db();
    echo "DB OK driver=" . $pdo->getAttribute(PDO::ATTR_DRIVER_NAME) . "\n";
    init_schema();
    echo "schema OK\n";
    $hash = password_hash('Tkadmin2026', PASSWORD_BCRYPT);
    $stmt = $pdo->prepare("INSERT INTO employees (name, email, password, role) VALUES (?, ?, ?, 'admin')");
    $stmt->execute(['Admin', 'admin@tkvibes.in', $hash]);
    echo "admin inserted id=" . $pdo->lastInsertId() . "\n";
    echo "employees=" . $pdo->query("SELECT COUNT(*) FROM employees")->fetchColumn() . "\n";
} catch (Throwable $e) {
    echo "ERR: " . $e->getMessage() . "\n";
    echo "FILE: " . $e->getFile() . ":" . $e->getLine() . "\n";
}
