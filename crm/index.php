<?php
/**
 * TKVibes CRM — Login
 */
require __DIR__ . '/lib/db.php';
require __DIR__ . '/lib/auth.php';
require __DIR__ . '/lib/functions.php';

// Already logged in → redirect
if (is_logged_in()) {
    $emp = current_employee();
    if ($emp['role'] === 'admin') {
        header('Location: admin.php');
    } else {
        header('Location: dashboard.php');
    }
    exit;
}

$error = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email    = $_POST['email'] ?? '';
    $password = $_POST['password'] ?? '';
    if (login($email, $password)) {
        $emp = current_employee();
        $redirect = $_GET['r'] ?? ($emp['role'] === 'admin' ? 'admin.php' : 'dashboard.php');
        header("Location: $redirect");
        exit;
    }
    $error = 'Invalid email or password.';
}

// Check if config exists and DB is set up
$config_exists = file_exists(__DIR__ . '/config.local.php');
$needs_setup = false;
if ($config_exists) {
    try {
        $pdo = get_db();
        $pdo->query("SELECT 1 FROM employees LIMIT 1");
    } catch (Exception $e) {
        $needs_setup = true;
    }
} else {
    $needs_setup = true;
}
?>
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TKVibes CRM — Login</title>
<link rel="stylesheet" href="assets/css/crm.css?v=1">
</head>
<body class="login-page">
<div class="login-container">
    <div class="login-header">
        <img src="../tk-vibes-mark.svg" alt="TKVibes" height="48">
        <h1>CRM</h1>
        <p>Employee Dashboard</p>
    </div>

    <?php if ($needs_setup): ?>
        <div class="install-card">
            <p>CRM is not configured yet.</p>
            <a href="install.php" class="btn btn-primary">Run Setup Wizard</a>
        </div>
    <?php else: ?>
        <?php if ($error): ?>
            <div class="alert alert-error"><?= e($error) ?></div>
        <?php endif; ?>

        <form method="post" class="login-form">
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" class="form-control" required autofocus
                       placeholder="you@tkvibes.com">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" class="form-control" required
                       placeholder="Enter your password">
            </div>
            <button type="submit" class="btn btn-primary btn-block">Sign In</button>
        </form>
    <?php endif; ?>
</div>
</body>
</html>