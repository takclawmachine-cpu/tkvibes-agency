<?php
header('X-Robots-Tag: noindex, nofollow');
/**
 * TKVibes CRM — Authentication
 * Session-based auth with password_hash.
 */

function start_session(): void
{
    $cfg = require __DIR__ . '/../config.local.php';
    if (session_status() === PHP_SESSION_NONE) {
        session_name('TKCRM');
        session_start();
    }
}

function login(string $email, string $password): array|false
{
    $pdo = get_db();
    $stmt = $pdo->prepare("SELECT * FROM employees WHERE email = ? AND active = 1");
    $stmt->execute([$email]);
    $emp = $stmt->fetch();

    if ($emp && password_verify($password, $emp['password'])) {
        $_SESSION['employee_id'] = (int)$emp['id'];
        $_SESSION['employee_name'] = $emp['name'];
        $_SESSION['employee_role'] = $emp['role'];
        $_SESSION['employee_email'] = $emp['email'];
        return $emp;
    }
    return false;
}

function logout(): void
{
    $_SESSION = [];
    if (ini_get("session.use_cookies")) {
        $params = session_get_cookie_params();
        setcookie(session_name(), '', time() - 42000,
            $params["path"], $params["domain"],
            $params["secure"], $params["httponly"]
        );
    }
    session_destroy();
}

function require_auth(): array
{
    start_session();
    if (empty($_SESSION['employee_id'])) {
        header('Location: index.php?r=' . urlencode($_SERVER['REQUEST_URI']));
        exit;
    }
    return [
        'id'    => (int)$_SESSION['employee_id'],
        'name'  => $_SESSION['employee_name'],
        'role'  => $_SESSION['employee_role'],
        'email' => $_SESSION['employee_email'],
    ];
}

function require_admin(): array
{
    $emp = require_auth();
    if ($emp['role'] !== 'admin') {
        http_response_code(403);
        die('Access denied. Admin privileges required.');
    }
    return $emp;
}

function is_logged_in(): bool
{
    start_session();
    return !empty($_SESSION['employee_id']);
}

function current_employee(): ?array
{
    start_session();
    if (empty($_SESSION['employee_id'])) return null;
    return [
        'id'    => (int)$_SESSION['employee_id'],
        'name'  => $_SESSION['employee_name'],
        'role'  => $_SESSION['employee_role'],
        'email' => $_SESSION['employee_email'],
    ];
}