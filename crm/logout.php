<?php
/**
 * TKVibes CRM — Logout
 */
require __DIR__ . '/lib/auth.php';
logout();
header('Location: index.php');
exit;