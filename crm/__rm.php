<?php
error_reporting(E_ALL); ini_set('display_errors','1');
foreach (['dbg.php','cfg_set.php','__rm.php'] as $f) {
    $p = __DIR__ . '/' . $f;
    if (file_exists($p)) echo "$f: " . (unlink($p) ? "deleted\n" : "FAILED\n");
    else echo "$f: absent\n";
}
