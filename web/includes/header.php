<?php
/**
 * HoneyGuard Web Portal - Shared Left Navigation Sidebar
 */
require_once __DIR__ . '/../auth_check.php';
requireAuth();
$currentUser = getCurrentUser();
$activePage = basename($_SERVER['PHP_SELF'], '.php');
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= $pageTitle ?? 'HoneyGuard SOC Portal' ?> — Ransomware Defense System</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
</head>
<body class="app-layout">
    <!-- Left Vertical Navigation Sidebar -->
    <aside class="sidebar">
        <!-- Brand / Logo Area -->
        <div class="sidebar-brand">
            <a href="dashboard.php" class="brand-link">
                <div class="brand-icon">
                    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                        <path d="M9 12l2 2 4-4"/>
                    </svg>
                </div>
                <div class="brand-info">
                    <span class="brand-title">HoneyGuard</span>
                    <span class="brand-tag">SOC CONSOLE</span>
                </div>
            </a>
            
            <div class="system-status-badge">
                <span class="pulse-dot"></span>
                <span>SHIELD ACTIVE (PORT 3306)</span>
            </div>
        </div>

        <!-- Navigation Menu Items -->
        <div class="sidebar-nav-container">
            <div class="nav-section-label">CORE DEFENSE</div>
            <nav class="sidebar-menu">
                <a href="dashboard.php" class="sidebar-item <?= $activePage === 'dashboard' ? 'active' : '' ?>">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
                    <span>Dashboard</span>
                </a>
                <a href="decoys.php" class="sidebar-item <?= $activePage === 'decoys' ? 'active' : '' ?>">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                    <span>Canary Decoys</span>
                </a>
                <a href="file_monitor.php" class="sidebar-item <?= $activePage === 'file_monitor' ? 'active' : '' ?>">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    <span>File Monitor</span>
                </a>
                <a href="alerts.php" class="sidebar-item <?= $activePage === 'alerts' ? 'active' : '' ?>">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                    <span>Alerts & Response</span>
                </a>
            </nav>

            <div class="nav-section-label" style="margin-top: 24px;">ANALYTICS & DATABASE</div>
            <nav class="sidebar-menu">
                <a href="benchmarks.php" class="sidebar-item <?= $activePage === 'benchmarks' ? 'active' : '' ?>">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
                    <span>Benchmarks</span>
                </a>
                <a href="http://localhost/phpmyadmin/" target="_blank" class="sidebar-item nav-ext">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
                    <span>phpMyAdmin ↗</span>
                </a>
            </nav>
        </div>

        <!-- User / Session Footer at bottom of sidebar -->
        <div class="sidebar-footer">
            <div class="user-card">
                <div class="user-avatar user-avatar-<?= htmlspecialchars($currentUser['role']) ?>">
                    <?= strtoupper(substr($currentUser['username'], 0, 1)) ?>
                </div>
                <div class="user-meta">
                    <div class="user-name-row">
                        <span class="user-name"><?= htmlspecialchars($currentUser['full_name']) ?></span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px; margin-top: 2px;">
                        <span class="role-pill role-<?= htmlspecialchars($currentUser['role']) ?>">
                            <?= strtoupper(htmlspecialchars($currentUser['role'])) ?>
                        </span>
                        <span class="user-handle">@<?= htmlspecialchars($currentUser['username']) ?></span>
                    </div>
                </div>
            </div>
            <a href="logout.php" class="btn-sidebar-logout" title="Sign Out">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
                </svg>
                <span>Logout</span>
            </a>
        </div>
    </aside>

    <!-- Main Content Container (positioned right next to sidebar) -->
    <div class="content-wrapper">
        <main class="main-content">
