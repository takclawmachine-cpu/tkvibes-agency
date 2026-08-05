<?php
/**
 * TKVibes CRM — Shared constants and configuration.
 * Single source of truth for field lists, status codes, and other magic strings.
 */

// ── Sheet sync: fields that can be imported from Google Sheets ──────────────
// These fields are synced FROM sheet → CRM (lead engine data).
// CRM state fields (crm_status, crm_notes, etc.) flow CRM → sheet only.
// FIX: Added missing fields that the lead engine pushes via sync.php
define('SHEET_IMPORT_FIELDS', [
    'business_name', 'category', 'owner_name', 'phone_primary', 'phone_secondary',
    'whatsapp', 'email', 'address', 'city', 'pincode', 'region', 'country',
    'website_url', 'website_quality', 'rating', 'review_count', 'years_in_business',
    'socials', 'pain_points', 'recommended_pitch', 'notes', 'contact_channel',
    'opening_hours', 'has_website', 'source', 'source_url',
    'assigned_employee', 'outreach_status', 'wa_link',
    // FIX: These were missing from the original SHEET_IMPORT_FIELDS
    'lead_score', 'lead_tier', 'data_fetched_at', 'stale_after',
    'opt_out', 'sample_site_url', 'pitch_deck_url',
    'lead_key',
]);

// ── Lead detail: fields editable via inline editing ─────────────────────────
define('EDITABLE_FIELDS', [
    'business_name', 'category', 'owner_name', 'phone_primary', 'phone_secondary',
    'whatsapp', 'email', 'address', 'city', 'pincode', 'region', 'country',
    'website_url', 'website_quality', 'rating', 'review_count', 'years_in_business',
    'socials', 'pain_points', 'recommended_pitch', 'notes', 'contact_channel',
    'opening_hours', 'has_website', 'source', 'source_url',
    'sample_site_url', 'pitch_deck_url',
]);

// ── CRM status values ───────────────────────────────────────────────────────
define('CRM_STATUSES', ['new', 'qualified', 'callback', 'not_qualified']);

// ── Lead tiers ─�─────────────────────────────────────────────────────────────
define('LEAD_TIERS', ['HOT', 'WARM', 'COLD']);

// ── Proposal types ──────────────────────────────────────────────────────────
define('PROPOSAL_TYPES', ['sample_site', 'pitch_deck']);

// ── Proposal job statuses ───────────────────────────────────────────────────
define('PROPOSAL_JOB_STATUSES', ['pending', 'running', 'completed', 'failed']);

// ── Log levels ─�─────────────────────────────────────────────────────────────
define('LOG_LEVELS', ['info', 'warning', 'error', 'critical']);

// ── Config version (for migration tracking) ─────────────────────────────────
define('CONFIG_VERSION', '2.0.0');

// ── API rate limits (requests per minute per IP) ────────────────────────────
define('API_RATE_LIMIT', 60);
define('API_RATE_WINDOW', 60); // seconds

// ── Proposal file size limit ────────────────────────────────────────────────
define('MAX_PROPOSAL_SIZE', 2 * 1024 * 1024); // 2MB
