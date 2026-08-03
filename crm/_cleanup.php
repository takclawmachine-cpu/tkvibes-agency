<?php
error_reporting(E_ALL); ini_set('display_errors','1');
$files = ['dbg.php','cfg_set.php','cfg_dump.php','cfg_sync_test.php','_cleanup.php'];
foreach ($files as $f) {
    $p = __DIR__ . '/' . $f;
    if (file_exists($p)) { echo "$f: " . (unlink($p) ? "deleted" : "FAILED") . "\n"; }
    else echo "$f: absent\n";
}
// also remove credentials dir if present (key already embedded in config.local.php path)
echo "done\n";
