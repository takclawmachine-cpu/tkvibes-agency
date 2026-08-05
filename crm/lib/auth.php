<?php
/**
 * TKVibes CRM — Authentication & CSRF Protection
 * Session-based auth with password_hash and token-based CSRF.
 * 
 * Security improvements:
 * - Session cookie flags: Secure, HttpOnly, SameSite=Strict
 * - Session timeout: 30 min idle timeout
 * - Session fixation prevention: regenerate on login
 * - Session activity tracking for idle timeout
 */
header('X-Robots-Tag: noindex, nofollow');

function start_session(): void
{
    if (session_status() === PHP_SESSION_NONE) {
        $cfg = require __DIR__ . '/../config.local.php';
        
        // Set secure cookie parameters BEFORE session_start
        $secure = isset($cfg['force_https']) ? (bool)$cfg['force_https'] : true;
        session_set_cookie_params([
            'lifetime' => 0,
            'path' => '/',
            'secure' => $secure,
            'httponly' => true,
            'samesite' => 'Strict',
        ]);
        
        session_name('TKCRM');
        
        // Configure session timeout
        ini_set('session.gc_maxlifetime', 1800); // 30 minutes
        ini_set('session.cookie_lifetime', 0);
        
        session_start();
        
        // Check for idle timeout
        if (isset($_SESSION['last_activity']) && time() - $_SESSION['last_activity'] > 1800) {
            session_unset();
            session_destroy();
            // Redirect to login with timeout flag
            if (!headers_sent()) {
                header('Location: index.php?timeout=1');
                exit;
            }
        }
        
        // Update last activity
        $_SESSION['last_activity'] = time();
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
        $_SESSION['login_time'] = time();
        $_SESSION['last_activity'] = time();
        // Regenerate session ID on login to prevent session fixation
        session_regenerate_id(true);
        
        log_system('info', 'auth', 'Login successful', [
            'employee_id' => (int)$emp['id'],
            'email' => $emp['email'],
            'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
        ]);
        
        return $emp;
    }
    
    log_system('warning', 'auth', 'Login failed', [
        'email' => $email,
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
        'user_agent' => substr($_SERVER['HTTP_USER_AGENT'] ?? '', 0, 255),
    ]);
    
    return false;
}

function logout(): void
{
    if (isset($_SESSION['employee_id'])) {
        log_system('info', 'auth', 'Logout', [
            'employee_id' => $_SESSION['employee_id'],
            'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
        ]);
    }
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
        $redirect = urlencode($_SERVER['REQUEST_URI']);
        header("Location: index.php?r=$redirect");
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
