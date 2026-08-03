<?php
/**
 * One-time setup script: configures Google Sheets in config.local.php.
 * Requires the CRM API key to run.
 * Delete this file after successful setup.
 * 
 * Usage:
 *   curl -X POST https://tkvibes.in/crm/setup-sheets.php \
 *     -d "key=CRM_API_KEY"
 * 
 * Or with service account path:
 *   curl ... -d "key=CRM_API_KEY&sa_path=/home/u1234567/crm/credentials/google-service-account.json&sheet_id=SHEET_ID"
 */

// Config
$DEFAULT_SA_PATH = __DIR__ . '/credentials/google-service-account.json';
$DEFAULT_SHEET_ID = '1cZ7w4HlN5aGaSAY-m-9EPexqEaCVC52kRELPk1OGiX';

$cfg_path = __DIR__ . '/config.local.php';

// Check if config exists
if (!file_exists($cfg_path)) {
    http_response_code(400);
    die('config.local.php not found. Run install.php first.');
}

// Verify API key
$key = $_POST['key'] ?? '';
$cfg = require $cfg_path;
if (!$key || $key !== ($cfg['api_key'] ?? '')) {
    http_response_code(403);
    die('Invalid API key');
}

$sa_path = $_POST['sa_path'] ?? $DEFAULT_SA_PATH;
$sheet_id = $_POST['sheet_id'] ?? $DEFAULT_SHEET_ID;

// Verify service account file exists
if (!file_exists($sa_path)) {
    http_response_code(400);
    die("Service account file not found at: $sa_path");
}

// Read existing config
$existing = file_get_contents($cfg_path);

// Build new config with Google Sheets settings
$new_config = '<?php' . PHP_EOL
    . 'return [' . PHP_EOL
    . "    'db' => [" . PHP_EOL
    . "        'dsn'      => " . var_export($cfg['db']['dsn'], true) . "," . PHP_EOL
    . "        'username' => " . var_export($cfg['db']['username'], true) . "," . PHP_EOL
    . "        'password' => " . var_export($cfg['db']['password'], true) . "," . PHP_EOL
    . "    ]," . PHP_EOL
    . "    'secret' => " . var_export($cfg['secret'], true) . "," . PHP_EOL
    . "    'google_service_account' => " . var_export($sa_path, true) . "," . PHP_EOL
    . "    'google_sheet_id' => " . var_export($sheet_id, true) . "," . PHP_EOL
    . "    'api_key' => " . var_export($cfg['api_key'], true) . "," . PHP_EOL
    . '];' . PHP_EOL;

if (file_put_contents($cfg_path, $new_config) === false) {
    http_response_code(500);
    die('Failed to write config.local.php');
}

// Verify it parses
$verify = require $cfg_path;
if (empty($verify['google_service_account']) || empty($verify['google_sheet_id'])) {
    http_response_code(500);
    die('Config write appeared to succeed but verification failed');
}

// Test the connection
try {
    require_once __DIR__ . '/lib/GoogleSheetsClient.php';
    $client = new GoogleSheetsClient($verify['google_service_account'], $verify['google_sheet_id']);
    [$header, ] = $client->read_sheet();
    echo "SUCCESS\n";
    echo "Sheet ID: $sheet_id\n";
    echo "Service Account: $sa_path\n";
    echo "Sheet header columns: " . implode(', ', $header) . "\n";
    echo "(Rows: " . count($rows ?? []) . " data rows)\n";
} catch (Throwable $e) {
    echo "WARNING: Config written but connection test failed: " . $e->getMessage() . "\n";
    echo "The sheet may be empty or the service account may not have access.\n";
}

echo "\n--- Delete this file for security: rm -f " . __FILE__ . " ---\n";