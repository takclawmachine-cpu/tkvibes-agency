<?php
/**
 * TKVibes CRM — Install Wizard
 * Handles first-run setup: DB creation, employee creation, config writing.
 */

require __DIR__ . '/lib/functions.php';

$step = $_GET['step'] ?? $_POST['step'] ?? 'welcome';

// If config.local.php already exists, check if DB is set up
$config_exists = file_exists(__DIR__ . '/config.local.php');

if ($config_exists && $step !== 'done' && $step !== 'config') {
    try {
        require __DIR__ . '/lib/db.php';
        $pdo = get_db();
        $pdo->query("SELECT COUNT(*) FROM employees");
        // Already set up — redirect to login
        header('Location: index.php');
        exit;
    } catch (Throwable $e) {
        // DB setup needed — fall through to the wizard
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $error = null;

    if ($step === 'config') {
        $db_type = $_POST['db_type'] ?? 'sqlite';
        $db_host = $_POST['db_host'] ?? 'localhost';
        $db_name = $_POST['db_name'] ?? 'tkvibes_crm';
        $db_user = $_POST['db_user'] ?? '';
        $db_pass = $_POST['db_pass'] ?? '';
        $secret  = $_POST['secret'] ?? '';
        $api_key = $_POST['api_key'] ?? '';
        $sheet_id = $_POST['sheet_id'] ?? '';
        if (!$secret) $secret = bin2hex(random_bytes(16));
        if (!$api_key) $api_key = bin2hex(random_bytes(16));

        if ($db_type === 'sqlite') {
            $dsn = 'sqlite:' . __DIR__ . '/data/crm.db';
            $username = null;
            $password = null;
        } else {
            $dsn = "mysql:host=$db_host;dbname=$db_name;charset=utf8mb4";
            $username = $db_user;
            $password = $db_pass;
        }

        $u = $username === null ? 'null' : var_export($username, true);
        $p = $password === null ? 'null' : var_export($password, true);
        $config = '<?php' . PHP_EOL . 'return [' . PHP_EOL
            . "    'db' => [" . PHP_EOL
            . "        'dsn'      => " . var_export($dsn, true) . "," . PHP_EOL
            . "        'username' => $u," . PHP_EOL
            . "        'password' => $p," . PHP_EOL
            . "    ]," . PHP_EOL
            . "    'secret' => " . var_export($secret, true) . "," . PHP_EOL
            . "    'google_service_account' => null," . PHP_EOL
            . "    'google_sheet_id' => " . var_export($sheet_id, true) . "," . PHP_EOL
            . "    'api_key' => " . var_export($api_key, true) . "," . PHP_EOL
            . '];' . PHP_EOL;

        file_put_contents(__DIR__ . '/config.local.php', $config);
        header('Location: install.php?step=admin');
        exit;
    }

    if ($step === 'admin') {
        require __DIR__ . '/lib/db.php';
        require __DIR__ . '/lib/auth.php';

        $name     = $_POST['name'] ?? '';
        $email    = $_POST['email'] ?? '';
        $password = $_POST['password'] ?? '';

        if (!$name || !$email || !$password) {
            $error = 'All fields are required.';
        } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $error = 'Invalid email address.';
        } elseif (strlen($password) < 6) {
            $error = 'Password must be at least 6 characters.';
        } else {
            try {
                init_schema();
                $pdo = get_db();
                $hash = password_hash($password, PASSWORD_BCRYPT);
                $stmt = $pdo->prepare("INSERT INTO employees (name, email, password, role) VALUES (?, ?, ?, 'admin')");
                $stmt->execute([$name, $email, $hash]);
                header('Location: install.php?step=done');
                exit;
            } catch (Throwable $e) {
                $error = $e->getMessage();
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TKVibes CRM — Setup</title>
<link rel="stylesheet" href="assets/css/crm.css?v=1">
</head>
<body class="install-page">
<div class="install-container">
    <div class="install-header">
        <img src="../tk-vibes-mark.svg" alt="TKVibes" height="48">
        <h1>TKVibes CRM Setup</h1>
        <p>Configure your CRM database and admin account</p>
    </div>

    <?php if (isset($error)): ?>
        <div class="alert alert-error"><?= e($error) ?></div>
    <?php endif; ?>

    <?php
    // Capture PHP errors during install and show them inline
    $last_error = error_get_last();
    if ($last_error && strpos($last_error['file'] ?? '', 'install.php') !== false):
    ?>
        <div class="alert alert-error">
            PHP: <?= e($last_error['message']) ?><br>
            <small><?= e($last_error['file']) ?>:<?= $last_error['line'] ?></small>
        </div>
    <?php endif; ?>

    <?php if ($step === 'welcome'): ?>
        <div class="install-card">
            <p>This wizard will:</p>
            <ol>
                <li>Create the CRM database</li>
                <li>Set up the database schema</li>
                <li>Create your admin account</li>
            </ol>
            <p class="text-muted">You'll need: database credentials (or use SQLite), and your admin email/password.</p>
            <form method="get" action="install.php">
                <input type="hidden" name="step" value="config">
                <button type="submit" class="btn btn-primary">Start Setup</button>
            </form>
        </div>

    <?php elseif ($step === 'config'): ?>
        <?php
        // Generate keys once, before HTML output — with fallback
        try {
            $auto_secret = bin2hex(random_bytes(16));
            $auto_api_key = bin2hex(random_bytes(16));
        } catch (Exception $e) {
            $auto_secret = md5(uniqid(mt_rand(), true));
            $auto_api_key = md5(uniqid(mt_rand(), true) . microtime());
        }
        ?>
        <div class="install-card">
            <h2>Database Configuration</h2>
            <form method="post">
                <input type="hidden" name="step" value="config">
                <input type="hidden" name="secret" value="<?= e($auto_secret) ?>">
                <input type="hidden" name="api_key" value="<?= e($auto_api_key) ?>">

                <div class="form-group">
                    <label>Database Type</label>
                    <select name="db_type" class="form-control" onchange="toggleDbFields(this.value)">
                        <option value="sqlite" selected>SQLite (recommended — zero-config)</option>
                        <option value="mysql">MySQL (requires database setup)</option>
                    </select>
                </div>

                <div id="mysql-fields" style="display:none">
                    <div class="form-group">
                        <label>MySQL Host</label>
                        <input type="text" name="db_host" class="form-control" value="localhost" placeholder="localhost">
                    </div>
                    <div class="form-group">
                        <label>Database Name</label>
                        <input type="text" name="db_name" class="form-control" placeholder="tkvibes_crm">
                    </div>
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" name="db_user" class="form-control" placeholder="root">
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="db_pass" class="form-control" placeholder="(leave blank if none)">
                    </div>
                </div>

                <div class="form-group">
                    <label>CRM API Key</label>
                    <div style="display:flex;gap:0.5rem;align-items:center">
                        <input type="text" class="form-control" value="<?= e($auto_api_key) ?>" readonly style="font-family:monospace;font-size:0.8rem;background:var(--bg-primary)" onclick="this.select()">
                        <span class="text-muted" style="flex-shrink:0;font-size:0.75rem">📋 click to copy</span>
                    </div>
                    <small class="text-muted">Put this in config.yaml → crm.api_key</small>
                </div>

                <div class="form-group">
                    <label>Google Sheet ID (optional)</label>
                    <input type="text" name="sheet_id" class="form-control" placeholder="1cZ7w4HlN...">
                    <small class="text-muted">For "Import from Sheet" feature. Leave blank if unsure.</small>
                </div>

                <button type="submit" class="btn btn-primary btn-block" style="margin-top:0.75rem">Continue →</button>
            </form>
        </div>

    <?php elseif ($step === 'admin'): ?>
        <div class="install-card">
            <h2>Create Admin Account</h2>
            <form method="post">
                <input type="hidden" name="step" value="admin">
                <div class="form-group">
                    <label>Full Name</label>
                    <input type="text" name="name" class="form-control" required placeholder="Admin Name">
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" class="form-control" required placeholder="admin@tkvibes.in">
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" class="form-control" required minlength="6" placeholder="Min 6 characters">
                </div>
                <button type="submit" class="btn btn-primary">Create Admin & Finish</button>
            </form>
        </div>

    <?php elseif ($step === 'done'): ?>
        <div class="install-card install-success">
            <h2>✅ Setup Complete!</h2>
            <p>Your CRM is ready. You can now log in with your admin credentials.</p>
            <p class="text-muted mt-1">Important next steps:</p>
            <ul class="text-muted">
                <li>Copy your <strong>CRM API Key</strong> from config.local.php into <code>config.yaml → crm.api_key</code></li>
                <li>Set <code>crm.api_url</code> in config.yaml to your CRM URL (e.g. https://tkvibes.in/crm)</li>
                <li>Add employees via the Admin Dashboard</li>
                <li>Assign regions to each employee</li>
            </ul>
            <a href="index.php" class="btn btn-primary mt-2">Go to Login</a>
        </div>
    <?php endif; ?>
</div>

<script>
function toggleDbFields(val) {
    document.getElementById('mysql-fields').style.display = val === 'mysql' ? 'block' : 'none';
}
</script>
</body>
</html>