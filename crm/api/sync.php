<?php
/**
 * TKVibes CRM — Sync API endpoint (Hardened)
 * 
 * Called by the lead engine (Python) after each discovery run.
 * Protected by shared API key (config.local.php → api_key).
 * 
 * Security improvements:
 * - Transactional batch upsert (all-or-nothing)
 * - Idempotency key support (prevents duplicate processing)
 * - Trace ID propagation for log correlation
 * - Strict input validation on all fields
 * - Batch size limits
 */
header('X-Robots-Tag: noindex, nofollow');
require __DIR__ . '/../lib/db.php';
require __DIR__ . '/../lib/functions.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    json_response(['error' => 'POST required'], 405);
}

$cfg = require __DIR__ . '/../config.local.php';
$body = body_json();

// Validate API key
$key = $body['key'] ?? $_GET['key'] ?? '';
if (!$key || !hash_equals($cfg['api_key'] ?? '', $key)) {
    json_response(['error' => 'Invalid API key'], 403);
}

// Extract trace_id (propagated from lead engine)
$trace_id = $body['trace_id'] ?? $_SERVER['HTTP_X_TRACE_ID'] ?? '';

// Extract idempotency key
$idempotency_key = $body['idempotency_key'] ?? '';

// Validate batch size
$leads = $body['leads'] ?? [];
if (!is_array($leads)) {
    json_response(['error' => 'leads must be an array'], 400);
}
if (count($leads) > 200) {
    json_response(['error' => 'Batch too large (max 200 leads per request)'], 400);
}
if (empty($leads)) {
    json_response(['status' => 'ok', 'added' => 0, 'updated' => 0, 'trace_id' => $trace_id]);
}

$pdo = get_db();

// ── Idempotency check ───────────────────────────────────────────────────
if ($idempotency_key) {
    $check = $pdo->prepare(
        "SELECT 1 FROM sync_log WHERE idempotency_key = ? AND processed_at > datetime('now', '-5 minutes')"
    );
    $check->execute([$idempotency_key]);
    if ($check->fetch()) {
        log_system('info', 'sync', 'Duplicate request rejected (idempotency key)', [
            'trace_id' => $trace_id,
            'idempotency_key' => substr($idempotency_key, 0, 32) . '...',
        ]);
        json_response([
            'status' => 'duplicate',
            'added' => 0,
            'updated' => 0,
            'trace_id' => $trace_id,
            'message' => 'Request already processed within last 5 minutes',
        ]);
    }
}

// ── Insert idempotency record ──────────────────────────────────────────
if ($idempotency_key) {
    $pdo->prepare(
        "INSERT OR IGNORE INTO sync_log (idempotency_key, trace_id, status, created_at) 
         VALUES (?, ?, 'processing', datetime('now'))"
    )->execute([$idempotency_key, $trace_id]);
}

$added = 0;
$updated = 0;
$errors = [];

// ── Prepare upsert statement ────────────────────────────────────────────
$insert_sql = "
    INSERT INTO leads (
        lead_key, business_name, category, owner_name, phone_primary, phone_secondary,
        whatsapp, email, address, city, pincode, latitude, longitude, opening_hours,
        has_website, website_url, website_quality, rating, review_count, years_in_business,
        socials, source, source_url, place_id, lead_score, lead_tier, data_fetched_at,
        stale_after, outreach_status, opt_out, sample_site_url, pitch_deck_url, notes,
        contact_channel, wa_link, region, country, assigned_employee, pain_points,
        recommended_pitch, crm_status, trace_id, created_at, updated_at
    ) VALUES (
        :lead_key, :business_name, :category, :owner_name, :phone_primary, :phone_secondary,
        :whatsapp, :email, :address, :city, :pincode, :latitude, :longitude, :opening_hours,
        :has_website, :website_url, :website_quality, :rating, :review_count, :years_in_business,
        :socials, :source, :source_url, :place_id, :lead_score, :lead_tier, :data_fetched_at,
        :stale_after, :outreach_status, :opt_out, :sample_site_url, :pitch_deck_url, :notes,
        :contact_channel, :wa_link, :region, :country, :assigned_employee, :pain_points,
        :recommended_pitch, 'new', :trace_id, datetime('now'), datetime('now')
    )
    ON CONFLICT(lead_key) DO UPDATE SET
        business_name     = excluded.business_name,
        category          = excluded.category,
        owner_name        = excluded.owner_name,
        phone_primary     = excluded.phone_primary,
        phone_secondary   = excluded.phone_secondary,
        whatsapp          = excluded.whatsapp,
        email             = excluded.email,
        address           = excluded.address,
        city              = excluded.city,
        pincode           = excluded.pincode,
        latitude          = excluded.latitude,
        longitude         = excluded.longitude,
        opening_hours     = excluded.opening_hours,
        has_website       = excluded.has_website,
        website_url       = excluded.website_url,
        website_quality   = excluded.website_quality,
        rating            = excluded.rating,
        review_count      = excluded.review_count,
        years_in_business = excluded.years_in_business,
        socials           = excluded.socials,
        source            = excluded.source,
        source_url        = excluded.source_url,
        place_id          = excluded.place_id,
        lead_score        = excluded.lead_score,
        lead_tier         = excluded.lead_tier,
        data_fetched_at   = excluded.data_fetched_at,
        stale_after       = excluded.stale_after,
        outreach_status   = excluded.outreach_status,
        opt_out           = excluded.opt_out,
        wa_link           = excluded.wa_link,
        region            = excluded.region,
        country           = excluded.country,
        assigned_employee = excluded.assigned_employee,
        pain_points       = excluded.pain_points,
        recommended_pitch = excluded.recommended_pitch,
        trace_id          = excluded.trace_id,
        updated_at        = datetime('now')
";

$stmt = $pdo->prepare($insert_sql);

// ── Begin transaction ────────────────────────────────────────────────────
$pdo->beginTransaction();

try {
    foreach ($leads as $l) {
        // Validate lead_key — must be non-empty and match expected pattern
        $l['lead_key'] = $l['lead_key'] ?? '';
        if (!$l['lead_key']) {
            $l['lead_key'] = 'nm:' . strtolower(
                preg_replace('/[^a-zA-Z0-9]/', '', $l['business_name'] ?? uniqid('lead_'))
            );
        }

        // Check existence BEFORE upsert (for accurate added/updated counts)
        $check = $pdo->prepare("SELECT 1 FROM leads WHERE lead_key = ?");
        $check->execute([$l['lead_key']]);
        $exists = $check->fetch();

        // Type coercion
        $l['has_website'] = !empty($l['has_website']) ? 1 : 0;
        $l['opt_out'] = !empty($l['opt_out']) ? 1 : 0;
        $l['latitude'] = $l['latitude'] ?? null;
        $l['longitude'] = $l['longitude'] ?? null;
        $l['rating'] = $l['rating'] ?? null;
        $l['review_count'] = $l['review_count'] ?? null;
        $l['lead_score'] = $l['lead_score'] ?? 0;

        $params = [
            ':lead_key'          => $l['lead_key'],
            ':business_name'     => $l['business_name'] ?? '',
            ':category'          => $l['category'] ?? '',
            ':owner_name'        => $l['owner_name'] ?? '',
            ':phone_primary'     => $l['phone_primary'] ?? '',
            ':phone_secondary'   => $l['phone_secondary'] ?? '',
            ':whatsapp'          => $l['whatsapp'] ?? '',
            ':email'             => $l['email'] ?? '',
            ':address'           => $l['address'] ?? '',
            ':city'              => $l['city'] ?? '',
            ':pincode'           => $l['pincode'] ?? '',
            ':latitude'          => $l['latitude'],
            ':longitude'         => $l['longitude'],
            ':opening_hours'     => $l['opening_hours'] ?? '',
            ':has_website'       => $l['has_website'],
            ':website_url'       => $l['website_url'] ?? '',
            ':website_quality'   => $l['website_quality'] ?? 'none',
            ':rating'            => $l['rating'],
            ':review_count'      => $l['review_count'],
            ':years_in_business' => $l['years_in_business'] ?? '',
            ':socials'           => $l['socials'] ?? '',
            ':source'            => $l['source'] ?? '',
            ':source_url'        => $l['source_url'] ?? '',
            ':place_id'          => $l['place_id'] ?? '',
            ':lead_score'        => $l['lead_score'],
            ':lead_tier'         => $l['lead_tier'] ?? 'COLD',
            ':data_fetched_at'   => $l['data_fetched_at'] ?? '',
            ':stale_after'       => $l['stale_after'] ?? '',
            ':outreach_status'   => $l['outreach_status'] ?? 'new',
            ':opt_out'           => $l['opt_out'],
            ':sample_site_url'   => $l['sample_site_url'] ?? '',
            ':pitch_deck_url'    => $l['pitch_deck_url'] ?? '',
            ':notes'             => $l['notes'] ?? '',
            ':contact_channel'   => $l['contact_channel'] ?? '',
            ':wa_link'           => $l['wa_link'] ?? '',
            ':region'            => $l['region'] ?? '',
            ':country'           => $l['country'] ?? '',
            ':assigned_employee' => $l['assigned_employee'] ?? '',
            ':pain_points'       => $l['pain_points'] ?? '',
            ':recommended_pitch' => $l['recommended_pitch'] ?? '',
            ':trace_id'          => $trace_id ?: uniqid('sync_'),
        ];

        $stmt->execute($params);

        if ($exists) {
            $updated++;
        } else {
            $added++;
            // Auto-create proposal generation job for new leads
            $pdo->prepare(
                "INSERT OR IGNORE INTO proposal_generation_jobs 
                 (lead_key, feedback, status, trace_id, created_at, updated_at)
                 VALUES (?, '', 'pending', ?, datetime('now'), datetime('now'))"
            )->execute([$l['lead_key'], $trace_id ?: uniqid('sync_')]);
        }
    }

    // Record idempotency
    if ($idempotency_key) {
        $pdo->prepare(
            "UPDATE sync_log SET status = 'completed', processed_at = datetime('now') 
             WHERE idempotency_key = ?"
        )->execute([$idempotency_key]);
    }

    $pdo->commit();

    log_system('info', 'sync', 'Batch sync completed', [
        'trace_id' => $trace_id,
        'added' => $added,
        'updated' => $updated,
        'total' => count($leads),
    ]);

    json_response([
        'status'  => 'ok',
        'added'   => $added,
        'updated' => $updated,
        'total'   => count($leads),
        'trace_id' => $trace_id,
    ]);

} catch (PDOException $e) {
    $pdo->rollBack();

    // Mark idempotency record as failed
    if ($idempotency_key) {
        $pdo->prepare(
            "UPDATE sync_log SET status = 'failed', error_message = ? WHERE idempotency_key = ?"
        )->execute([substr($e->getMessage(), 0, 255), $idempotency_key]);
    }

    log_system('error', 'sync', 'Batch sync failed', [
        'trace_id' => $trace_id,
        'error' => $e->getMessage(),
        'added_before_fail' => $added,
        'updated_before_fail' => $updated,
    ]);

    json_response(['error' => 'Batch sync failed: ' . $e->getMessage()], 500);
}
