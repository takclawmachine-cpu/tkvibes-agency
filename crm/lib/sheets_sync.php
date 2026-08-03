<?php
header('X-Robots-Tag: noindex, nofollow');
/**
 * TKVibes CRM — Sheets Sync Cron
 * Provides a single function to get a configured GoogleSheetsClient instance,
 * plus write-back helpers for lead updates.
 */

/**
 * Get a configured GoogleSheetsClient, or null if sheets not configured.
 * @return GoogleSheetsClient|null
 */
function get_sheets_client(): ?GoogleSheetsClient
{
    static $client = null;
    if ($client !== null) {
        return $client;
    }

    $cfg = require __DIR__ . '/../config.local.php';
    if (empty($cfg['google_service_account']) || empty($cfg['google_sheet_id'])) {
        return null;
    }

    try {
        require_once __DIR__ . '/GoogleSheetsClient.php';
        $client = new GoogleSheetsClient($cfg['google_service_account'], $cfg['google_sheet_id']);
        return $client;
    } catch (RuntimeException $e) {
        error_log("Sheets sync: init failed: " . $e->getMessage());
        return null;
    }
}

/**
 * Write back CRM state changes to Google Sheets.
 * Fire-and-forget — wrapped in try/catch so CRM never breaks if sheets is down.
 *
 * @param string $lead_key  The lead identifier
 * @param array  $fields    Associative array of {column_name: value}
 */
function sheets_writeback(string $lead_key, array $fields): void
{
    try {
        $client = get_sheets_client();
        if ($client === null) {
            return; // sheets not configured
        }
        $client->update_lead_fields($lead_key, $fields);
    } catch (Throwable $e) {
        error_log("Sheets write-back failed for $lead_key: " . $e->getMessage());
    }
}