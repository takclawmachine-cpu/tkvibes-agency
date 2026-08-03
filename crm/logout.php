<?php
/**
 * TKVibes CRM — Logout
 */
require __DIR__ . '/lib/auth.php';
start_session();
logout();
header('Location: index.php');
exit;