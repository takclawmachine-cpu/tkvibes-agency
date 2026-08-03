<?php
/**
 * TKVibes CRM — Configuration
 * Copy this file to config.local.php and fill in your values.
 * NEVER commit config.local.php to the repository.
 */
return [
    'db' => [
        // SQLite (default — zero-config, works on most PHP hosting)
        'dsn'  => 'sqlite:' . __DIR__ . '/data/crm.db',
        // MySQL (preferred for production — uncomment and fill in)
        // 'dsn'      => 'mysql:host=localhost;dbname=tkvibes_crm;charset=utf8mb4',
        // 'username' => 'root',
        // 'password' => '',
        'username' => null,
        'password' => null,
    ],
    // Secret key for session encryption — generate a random 32+ char string
    'secret' => 'CHANGE_ME_TO_A_RANDOM_STRING',
    // Google Sheets sync (optional — needed for "Import from Sheet" feature)
    // Path to the service account JSON file on the server
    'google_service_account' => null,  // e.g. '/home/u1234567/crm/credentials.json'
    // Google Sheet ID (same as in .env of the lead engine)
    'google_sheet_id' => null,  // e.g. '1cZ7w4HlN5aGaSAY...'
    // CRM API key — shared secret that the lead engine uses to push leads
    // Generate a random string and put the same value in config.yaml → crm.api_key
    'api_key' => 'CHANGE_ME_TO_A_RANDOM_API_KEY',
    // Proposal webhook URL — called by cron when a generation job is ready for processing
    'proposal_webhook_url' => null,
];