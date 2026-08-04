<?php
header('X-Robots-Tag: noindex, nofollow');
/**
 * TKVibes CRM — Authentication & CSRF Protection
 * Session-based auth with password_hash and token-based CSRF.
 */

function start_session(): void
{
    if (session_status() === PHP_SESSION_NONE) {
        $cfg = require __DIR__ . '/../config.local.php';
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
        // Regenerate session ID on login to prevent session fixation
        session_regenerate_id(true);
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

/**
 * Generate or retrieve the CSRF token for the current session.
 * Tokens expire after 2 hours.
 */
function csrf_token(): string
{
    start_session();
    $now = time();
    $token_data = $_SESSION['csrf_token'] ?? null;
    
    // Generate new token if none exists or expired (>2h)
    if (!$token_data || ($token_data['expires'] ?? 0) < $now) {
        $token = bin2hex(random_bytes(32));
        $_SESSION['csrf_token'] = [
            'token'   => $token,
            'expires' => $now + 7200,  // 2 hours
        ];
        return $token;
    }
    
    return $token_data['token'];
}

/**
 * Verify a CSRF token from request data.
 * Checks POST param `_csrf_token` and `X-CSRF-Token` header.
 * 
 * @param string|null $token  Optional explicit token (for API clients)
 * @return bool True if token is valid
 */
function verify_csrf(?string $token = null): bool
{
    start_session();
    $token_data = $_SESSION['csrf_token'] ?? null;
    if (!$token_data) {
        return false;
    }
    
    // Check token hasn't expired
    if (time() > ($token_data['expires'] ?? 0)) {
        return false;
    }
    
    // Resolve token from parameter, POST data, or header
    if ($token === null) {
        $body = body_json();
        $token = $body['_csrf_token'] ?? $_POST['_csrf_token'] ?? '';
    }
    if (!$token) {
        // Check X-CSRF-Token header
        $headers = function_exists('getallheaders') ? getallheaders() : [];
        $token = $headers['X-CSRF-Token'] ?? $headers['x-csrf-token'] ?? '';
    }
    
    return hash_equals($token_data['token'], $token);
}