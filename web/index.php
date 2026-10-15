<?php
/**
 * HoneyGuard Web Portal - Root router
 */
require_once __DIR__ . '/auth_check.php';

if (isLoggedIn()) {
    header("Location: dashboard.php");
} else {
    header("Location: login.php");
}
exit;
?>
