<?php
/**
 * TKVibes CRM — Configuration (Sample)
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
    // DO NOT use the default — generate one with: php -r "echo bin2hex(random_bytes(32));"
    'secret' => 'CHANGE_ME_TO_A_RANDOM_STRING',
    // CRM API key — shared secret that the lead engine uses to push leads.
    // Generate a random string and put the same value in .env as CRM_API_KEY.
    // DO NOT commit the real key — use env var in production.
    'api_key' => 'CHANGE_ME_TO_A_RANDOM_API_KEY',
    // GitHub repo for proposal URLs (used by proposals.php)
    // Format: "owner/repo-name" (without .git)
    'github_repo' => 'takclawmachine-cpu/tkvibes-agency',
    'github_branch' => 'main',
    // Google Sheets sync (optional — needed only for read-only reporting)
    // Set enable_sheet_sync to true to allow CRM to import from Google Sheets.
    // With MySQL as source of truth, this is DISABLED by default.
    'google_service_account' => null,  // e.g. '/home/u1234567/crm/credentials.json'
    'google_sheet_id' => null,         // e.g. '1cZ7w4HlN5aGaSAY...'
    'enable_sheet_sync' => false,      // Keep false — MySQL is source of truth
    // Force HTTPS (session cookies + HSTS)
    'force_https' => true,
    // Proposal webhook URL — called by cron when a generation job is ready
    'proposal_webhook_url' => null,
];