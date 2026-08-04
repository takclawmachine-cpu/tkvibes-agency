<?php
/**
 * Deploy proposal HTML files from local repo to the proposals directory.
 * Run via cron after git pull or business_job generates new proposals.
 */
header('Content-Type: text/plain; charset=utf-8');
require __DIR__ . '/lib/db.php';
require __DIR__ . '/lib/functions.php';

$base_dir = __DIR__ . '/../proposals';
@mkdir("$base_dir/sample-website", 0755, true);
@mkdir("$base_dir/pitch-deck", 0755, true);

// Source files are in the git repo at the same level
$repo_root = __DIR__ . '/..';
$source_sample_dir = "$repo_root/Sample Webpages and pitch deck/sample website";
$source_pitch_dir = "$repo_root/Sample Webpages and pitch deck/pitch deck";

$pdo = get_db();
$leads = $pdo->query("SELECT lead_key, business_name, sample_site_url, pitch_deck_url FROM leads WHERE (sample_site_url != '' OR pitch_deck_url != '') AND business_name != '' AND business_name != 'Test Business' AND removed_at IS NULL")->fetchAll();

$ok = 0;
$fail = 0;
foreach ($leads as $l) {
    $name = $l['business_name'] ?: $l['lead_key'];
    echo "\n--- $name ---\n";

    if ($l['sample_site_url']) {
        $slug = basename(parse_url($l['sample_site_url'], PHP_URL_PATH), '.html');
        $src = "$source_sample_dir/$slug.html";
        $dst = "$base_dir/sample-website/$slug.html";
        if (file_exists($src) && copy($src, $dst)) {
            echo "  ✅ Sample site: $slug.html\n";
            $local_url = "/proposals/sample-website/$slug.html";
            $pdo->prepare("UPDATE leads SET sample_site_url = ? WHERE lead_key = ?")->execute([$local_url, $l['lead_key']]);
            $ok++;
        } else {
            echo "  ❌ Sample site: $slug.html (not found at $src)\n";
            $fail++;
        }
    }

    if ($l['pitch_deck_url']) {
        $slug = basename(parse_url($l['pitch_deck_url'], PHP_URL_PATH), '.html');
        $src = "$source_pitch_dir/$slug.html";
        $dst = "$base_dir/pitch-deck/$slug.html";
        if (file_exists($src) && copy($src, $dst)) {
            echo "  ✅ Pitch deck: $slug.html\n";
            $local_url = "/proposals/pitch-deck/$slug.html";
            $pdo->prepare("UPDATE leads SET pitch_deck_url = ? WHERE lead_key = ?")->execute([$local_url, $l['lead_key']]);
            $ok++;
        } else {
            echo "  ❌ Pitch deck: $slug.html (not found at $src)\n";
            $fail++;
        }
    }
}

echo "\nDone: $ok deployed, $fail failed\n";