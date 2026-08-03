<?php
header('X-Robots-Tag: noindex, nofollow');
/**
 * TKVibes CRM — Sync API endpoint
 * Called by the lead engine (Python) after each discovery run.
 * Protected by shared API key (config.local.php → api_key).
 */
require __DIR__ . '/../lib/db.php';
require __DIR__ . '/../lib/functions.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    json_response(['error' => 'POST required'], 405);
}

$cfg = require __DIR__ . '/../config.local.php';
$body = body_json();

// Validate API key
$key = $body['key'] ?? $_GET['key'] ?? '';
if (!$key || $key !== $cfg['api_key']) {
    json_response(['error' => 'Invalid API key'], 403);
}

$leads = $body['leads'] ?? [];
if (empty($leads)) {
    json_response(['status' => 'ok', 'added' => 0, 'updated' => 0]);
}

$pdo = get_db();
$added = 0;
$updated = 0;

$insert_sql = "
    INSERT INTO leads (
        lead_key, business_name, category, owner_name, phone_primary, phone_secondary,
        whatsapp, email, address, city, pincode, latitude, longitude, opening_hours,
        has_website, website_url, website_quality, rating, review_count, years_in_business,
        socials, source, source_url, place_id, lead_score, lead_tier, data_fetched_at,
        stale_after, outreach_status, opt_out, sample_site_url, pitch_deck_url, notes,
        contact_channel, wa_link, region, country, assigned_employee, pain_points,
        recommended_pitch, crm_status, created_at, updated_at
    ) VALUES (
        :lead_key, :business_name, :category, :owner_name, :phone_primary, :phone_secondary,
        :whatsapp, :email, :address, :city, :pincode, :latitude, :longitude, :opening_hours,
        :has_website, :website_url, :website_quality, :rating, :review_count, :years_in_business,
        :socials, :source, :source_url, :place_id, :lead_score, :lead_tier, :data_fetched_at,
        :stale_after, :outreach_status, :opt_out, :sample_site_url, :pitch_deck_url, :notes,
        :contact_channel, :wa_link, :region, :country, :assigned_employee, :pain_points,
        :recommended_pitch, 'new', datetime('now'), datetime('now')
    )
    ON CONFLICT(lead_key) DO UPDATE SET
        business_name     = :business_name,
        category          = :category,
        owner_name        = :owner_name,
        phone_primary     = :phone_primary,
        phone_secondary   = :phone_secondary,
        whatsapp          = :whatsapp,
        email             = :email,
        address           = :address,
        city              = :city,
        pincode           = :pincode,
        latitude          = :latitude,
        longitude         = :longitude,
        opening_hours     = :opening_hours,
        has_website       = :has_website,
        website_url       = :website_url,
        website_quality   = :website_quality,
        rating            = :rating,
        review_count      = :review_count,
        years_in_business = :years_in_business,
        socials           = :socials,
        source            = :source,
        source_url        = :source_url,
        place_id          = :place_id,
        lead_score        = :lead_score,
        lead_tier         = :lead_tier,
        data_fetched_at   = :data_fetched_at,
        stale_after       = :stale_after,
        outreach_status   = :outreach_status,
        opt_out           = :opt_out,
        sample_site_url   = :sample_site_url,
        pitch_deck_url    = :pitch_deck_url,
        notes             = :notes,
        contact_channel   = :contact_channel,
        wa_link           = :wa_link,
        region            = :region,
        country           = :country,
        assigned_employee = :assigned_employee,
        pain_points       = :pain_points,
        recommended_pitch = :recommended_pitch,
        updated_at        = datetime('now')
";

$stmt = $pdo->prepare($insert_sql);

foreach ($leads as $l) {
    $l['lead_key'] = $l['lead_key'] ?? ($l['business_name'] ?? uniqid('lead_'));
    $l['has_website'] = !empty($l['has_website']) ? 1 : 0;
    $l['opt_out'] = !empty($l['opt_out']) ? 1 : 0;
    $l['latitude'] = $l['latitude'] ?? null;
    $l['longitude'] = $l['longitude'] ?? null;
    $l['rating'] = $l['rating'] ?? null;
    $l['review_count'] = $l['review_count'] ?? null;

    // Map fields to params
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
        ':lead_score'        => $l['lead_score'] ?? 0,
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
    ];

    try {
        $stmt->execute($params);
        if ($stmt->rowCount() === 1) {
            $added++;
        } else {
            $updated++;
        }
    } catch (PDOException $e) {
        // Log error but continue
        error_log("CRM sync: lead {$l['lead_key']}: " . $e->getMessage());
    }
}

json_response([
    'status'  => 'ok',
    'added'   => $added,
    'updated' => $updated,
    'total'   => count($leads),
]);