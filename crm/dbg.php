<?php
echo "=== config.local.php raw (no require) ===\n";
echo file_get_contents(__DIR__ . '/config.local.php');
echo "\n=== end ===\n";
