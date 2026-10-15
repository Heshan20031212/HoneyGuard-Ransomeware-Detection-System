<?php
/**
 * HoneyGuard Web Portal - Main Security Dashboard
 */

$pageTitle = "SOC Overview";
require_once __DIR__ . '/config/db.php';
require_once __DIR__ . '/includes/header.php';

$pdo = getDB();

// 1. Fetch Aggregated Metrics
$stmtDecoys = $pdo->query("SELECT COUNT(*) AS total, SUM(CASE WHEN status = 'INTACT' THEN 1 ELSE 0 END) AS active FROM decoys");
$decoyCounts = $stmtDecoys->fetch();

$stmtEvents = $pdo->query("SELECT COUNT(*) AS total, SUM(CASE WHEN risk_contribution > 0 OR is_decoy = 1 THEN 1 ELSE 0 END) AS suspicious FROM file_events");
$eventCounts = $stmtEvents->fetch();

$stmtAlerts = $pdo->query("SELECT COUNT(*) AS total, 
    SUM(CASE WHEN risk_level = 'CRITICAL' THEN 1 ELSE 0 END) AS crit,
    SUM(CASE WHEN risk_level = 'HIGH' THEN 1 ELSE 0 END) AS high,
    SUM(CASE WHEN risk_level = 'MEDIUM' THEN 1 ELSE 0 END) AS med,
    SUM(CASE WHEN risk_level = 'LOW' THEN 1 ELSE 0 END) AS low
    FROM alerts");
$alertCounts = $stmtAlerts->fetch();

$stmtActions = $pdo->query("SELECT COUNT(*) AS total FROM response_actions WHERE success = 1");
$actionCounts = $stmtActions->fetch();

// 2. Fetch Recent Alerts
$stmtRecentAlerts = $pdo->query("SELECT alert_id, risk_level, risk_score, process_name, pid, affected_file, alert_status, timestamp 
                                  FROM alerts ORDER BY timestamp DESC LIMIT 6");
$recentAlerts = $stmtRecentAlerts->fetchAll();

// 3. Fetch Recent Decoys
$stmtRecentDecoys = $pdo->query("SELECT decoy_id, filename, absolute_path, file_type, baseline_hash, status, creation_timestamp 
                                  FROM decoys ORDER BY creation_timestamp DESC LIMIT 5");
$recentDecoys = $stmtRecentDecoys->fetchAll();
?>

<div class="page-header">
    <div class="page-title-box">
        <h1>Security Operations Center (SOC) Dashboard</h1>
        <p>Real-time ransomware threat telemetry, honeytoken sensor mesh, and behavioural correlation</p>
    </div>
    <div class="page-actions">
        <?php if (isAdmin()): ?>
            <a href="decoys.php" class="btn btn-primary">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                <span>Deploy New Canary</span>
            </a>
        <?php endif; ?>
    </div>
</div>

<!-- 4 Key Telemetry Metric Cards -->
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-icon stat-icon-emerald">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
        </div>
        <div class="stat-content">
            <div class="stat-label">Active Canaries</div>
            <div class="stat-value"><?= number_format($decoyCounts['active'] ?? 0) ?></div>
            <div class="stat-sub">Total Deployed: <?= number_format($decoyCounts['total'] ?? 0) ?> files</div>
        </div>
    </div>

    <div class="stat-card">
        <div class="stat-icon stat-icon-cyan">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
        </div>
        <div class="stat-content">
            <div class="stat-label">File Events Logged</div>
            <div class="stat-value"><?= number_format($eventCounts['total'] ?? 0) ?></div>
            <div class="stat-sub text-amber"><?= number_format($eventCounts['suspicious'] ?? 0) ?> suspicious triggers</div>
        </div>
    </div>

    <div class="stat-card">
        <div class="stat-icon stat-icon-red">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        </div>
        <div class="stat-content">
            <div class="stat-label">Ransomware Alerts</div>
            <div class="stat-value"><?= number_format($alertCounts['total'] ?? 0) ?></div>
            <div class="stat-sub text-red"><?= number_format($alertCounts['crit'] ?? 0) ?> Critical / <?= number_format($alertCounts['high'] ?? 0) ?> High</div>
        </div>
    </div>

    <div class="stat-card">
        <div class="stat-icon stat-icon-amber">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        </div>
        <div class="stat-content">
            <div class="stat-label">Containment Actions</div>
            <div class="stat-value"><?= number_format($actionCounts['total'] ?? 0) ?></div>
            <div class="stat-sub text-emerald">100% Process Neutralization</div>
        </div>
    </div>
</div>

<!-- Charts Section -->
<div class="charts-grid">
    <div class="card">
        <div class="card-header">
            <span class="card-title">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                Filesystem Activity & Event Velocity
            </span>
            <span class="card-subtitle">Real-time Watchdog Telemetry</span>
        </div>
        <div style="height: 240px; position: relative;">
            <canvas id="velocityChart"></canvas>
        </div>
    </div>

    <div class="card">
        <div class="card-header">
            <span class="card-title">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
                Alert Severity Distribution
            </span>
            <span class="card-subtitle">Risk Engine Classification</span>
        </div>
        <div style="height: 240px; position: relative;">
            <canvas id="severityChart" 
                data-crit="<?= (int)($alertCounts['crit'] ?? 0) ?>" 
                data-high="<?= (int)($alertCounts['high'] ?? 0) ?>" 
                data-med="<?= (int)($alertCounts['med'] ?? 0) ?>" 
                data-low="<?= (int)($alertCounts['low'] ?? 0) ?>"></canvas>
        </div>
    </div>
</div>

<!-- Live Incidents Table -->
<div class="card">
    <div class="card-header">
        <span class="card-title">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            Recent High-Risk Security Alerts
        </span>
        <a href="alerts.php" class="phpmyadmin-link">View All Alerts &rarr;</a>
    </div>

    <div class="table-responsive">
        <table class="data-table">
            <thead>
                <tr>
                    <th style="min-width: 160px;">Alert ID</th>
                    <th style="min-width: 110px;">Risk Level</th>
                    <th style="min-width: 105px;">Risk Score</th>
                    <th style="min-width: 200px;">Process & PID</th>
                    <th style="min-width: 240px;">Affected Path / Canary</th>
                    <th style="min-width: 110px;">Status</th>
                    <th style="min-width: 170px;">Timestamp</th>
                </tr>
            </thead>
            <tbody>
                <?php if (!empty($recentAlerts)): ?>
                    <?php foreach ($recentAlerts as $a): ?>
                        <tr>
                            <td class="col-id"><?= htmlspecialchars($a['alert_id']) ?></td>
                            <td class="col-nowrap">
                                <span class="badge badge-<?= strtolower($a['risk_level'] ?? 'medium') ?>">
                                    <?= htmlspecialchars($a['risk_level'] ?? 'MEDIUM') ?>
                                </span>
                            </td>
                            <td class="col-nowrap">
                                <?php 
                                    $score = (int)($a['risk_score'] ?? 0);
                                    $scoreClass = $score >= 70 ? 'score-high' : ($score >= 40 ? 'score-med' : 'score-low');
                                ?>
                                <span class="score-badge <?= $scoreClass ?>">
                                    <span class="score-val"><?= $score ?></span>
                                    <span class="score-den">/100</span>
                                </span>
                            </td>
                            <td class="col-nowrap">
                                <div class="process-cell">
                                    <span class="process-name"><?= htmlspecialchars($a['process_name'] ?? 'Unknown') ?></span>
                                    <?php if ($a['pid']): ?>
                                        <span class="pid-pill">PID: <?= (int)$a['pid'] ?></span>
                                    <?php endif; ?>
                                </div>
                            </td>
                            <td class="col-path" title="<?= htmlspecialchars($a['affected_file']) ?>">
                                <?= htmlspecialchars($a['affected_file'] ?? 'N/A') ?>
                            </td>
                            <td class="col-nowrap">
                                <?php 
                                    $st = strtoupper($a['alert_status'] ?? 'ACTIVE');
                                    if ($st === 'RESOLVED' || $st === 'MITIGATED') {
                                        echo '<span class="badge badge-mitigated">✓ RESOLVED</span>';
                                    } else {
                                        echo '<span class="badge badge-threat">⚠ ACTIVE</span>';
                                    }
                                ?>
                            </td>
                            <td class="col-time"><?= htmlspecialchars($a['timestamp']) ?></td>
                        </tr>
                    <?php endforeach; ?>
                <?php else: ?>
                    <tr>
                        <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 30px;">
                            No active ransomware alerts logged in database.
                        </td>
                    </tr>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
</div>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
