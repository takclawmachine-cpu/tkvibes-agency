<?php
/**
 * Deploy proposal HTML files from GitHub to the server.
 * Run via cron after business_job generates new proposals.
 *
 * Fetches sample sites and pitch decks from private GitHub repo
 * and saves them to /proposals/ directory on the server.
 */
header('Content-Type: text/plain; charset=utf-8');
require __DIR__ . '/lib/db.php';
require __DIR__ . '/lib/functions.php';

$cfg = require __DIR__ . '/config.local.php';
$token = $cfg['github_token'] ?? '';
if (!$token) {
    $token = 'ghp_ykHyIJ8w2NQz8jYd2PmYF6lg4Aq5sq';
}
if (!$token) {
    die("ERROR: github_token not configured\n");
}

$base_dir = __DIR__ . '/../proposals';
@mkdir("$base_dir/sample-website", 0755, true);
@mkdir("$base_dir/pitch-deck", 0755, true);

$pdo = get_db();
$leads = $pdo->query("SELECT lead_key, business_name, sample_site_url, pitch_deck_url FROM leads WHERE sample_site_url != '' OR pitch_deck_url != ''")->fetchAll();

$ok = 0;
$fail = 0;
foreach ($leads as $l) {
    $name = $l['business_name'] ?: $l['lead_key'];
    echo "\n--- $name ---\n";

    if ($l['sample_site_url']) {
        $slug = basename(parse_url($l['sample_site_url'], PHP_URL_PATH), '.html');
        $path = "$base_dir/sample-website/$slug.html";
        $html = fetch_github($l['sample_site_url'], $token);
        if ($html && file_put_contents($path, $html)) {
            echo "  ✅ Sample site: $slug.html\n";
            // Update to local URL
            $local_url = "/proposals/sample-website/$slug.html";
            $pdo->prepare("UPDATE leads SET sample_site_url = ? WHERE lead_key = ?")->execute([$local_url, $l['lead_key']]);
            $ok++;
        } else {
            echo "  ❌ Sample site failed\n";
            $fail++;
        }
    }

    if ($l['pitch_deck_url']) {
        $slug = basename(parse_url($l['pitch_deck_url'], PHP_URL_PATH), '.html');
        $path = "$base_dir/pitch-deck/$slug.html";
        $html = fetch_github($l['pitch_deck_url'], $token);
        if ($html && file_put_contents($path, $html)) {
            echo "  ✅ Pitch deck: $slug.html\n";
            $local_url = "/proposals/pitch-deck/$slug.html";
            $pdo->prepare("UPDATE leads SET pitch_deck_url = ? WHERE lead_key = ?")->execute([$local_url, $l['lead_key']]);
            $ok++;
        } else {
            echo "  ❌ Pitch deck failed\n";
            $fail++;
        }
    }
}

echo "\nDone: $ok deployed, $fail failed\n";

function fetch_github(string $url, string $token): ?string {
    $opts = ['http' => [
        'method' => 'GET',
        'header' => "Authorization: Bearer $token\r\n",
        'timeout' => 15,
    ]];
    $html = @file_get_contents($url, false, stream_context_create($opts));
    return $html !== false ? $html : null;
}