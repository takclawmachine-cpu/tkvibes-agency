<?php
error_reporting(E_ALL);
ini_set('display_errors', '1');
echo "=== config.local.php raw ===\n";
echo file_get_contents(__DIR__ . '/config.local.php');
echo "\n=== end ===\n";
