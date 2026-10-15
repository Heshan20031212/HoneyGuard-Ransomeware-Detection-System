<?php
/**
 * HoneyGuard Web Portal - Authentication & Session Guard
 */

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

function isLoggedIn() {
    return isset($_SESSION['user_id']) && !empty($_SESSION['username']);
}

function requireAuth() {
    if (!isLoggedIn()) {
        header("Location: login.php");
        exit;
    }
}

function requireAdmin() {
    requireAuth();
    if ($_SESSION['role'] !== 'admin') {
        header("Location: dashboard.php?error=unauthorized");
        exit;
    }
}

function isAdmin() {
    return isset($_SESSION['role']) && $_SESSION['role'] === 'admin';
}

function getCurrentUser() {
    return [
        'id' => $_SESSION['user_id'] ?? null,
        'username' => $_SESSION['username'] ?? 'Guest',
        'full_name' => $_SESSION['full_name'] ?? 'Guest User',
        'role' => $_SESSION['role'] ?? 'guest',
        'email' => $_SESSION['email'] ?? ''
    ];
}
?>
