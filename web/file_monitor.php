<?php
/**
 * HoneyGuard Web Portal - Real-Time Filesystem Event Monitor
 */

$pageTitle = "File Monitor";
require_once __DIR__ . '/config/db.php';
require_once __DIR__ . '/includes/header.php';

$pdo = getDB();

$filter = $_GET['filter'] ?? 'all';
$sql = "SELECT event_id, event_type, source_path, destination_path, is_decoy, pid, process_name, executable_path, process_attribution_status, risk_contribution, timestamp 
        FROM file_events ";

if ($filter === 'suspicious') {
    $sql .= "WHERE risk_contribution > 0 OR is_decoy = 1 ";
} elseif ($filter === 'decoys') {
    $sql .= "WHERE is_decoy = 1 ";
}
$sql .= "ORDER BY timestamp DESC LIMIT 50";

$stmt = $pdo->query($sql);
$events = $stmt->fetchAll();
?>

<div class="page-header">
    <div class="page-title-box">
        <h1>Filesystem Monitoring Sensor Stream</h1>
        <p>Continuous kernel-level and watchdog file activity telemetry, process attribution, and entropy audits</p>
    </div>
    <div class="page-actions" style="display: flex; align-items: center; gap: 14px;">
        <label style="display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-secondary); cursor: pointer;">
            <input type="checkbox" id="liveAutoRefresh">
            <span>Auto-Refresh (5s)</span>
        </label>
        <a href="file_monitor.php" class="btn" style="background: var(--bg-card); border: 1px solid var(--border-color); color: #fff;">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
            <span>Refresh Now</span>
        </a>
    </div>
</div>

<div class="card" style="margin-bottom: 16px; padding: 14px 20px;">
    <div style="display: flex; align-items: center; gap: 10px; font-size: 13px;">
        <strong style="color: var(--text-secondary);">Event Filter:</strong>
        <a href="file_monitor.php?filter=all" class="badge <?= $filter === 'all' ? 'badge-active' : 'badge-medium' ?>" style="text-decoration: none;">All Events</a>
        <a href="file_monitor.php?filter=suspicious" class="badge <?= $filter === 'suspicious' ? 'badge-critical' : 'badge-medium' ?>" style="text-decoration: none;">Suspicious Only</a>
        <a href="file_monitor.php?filter=decoys" class="badge <?= $filter === 'decoys' ? 'badge-high' : 'badge-medium' ?>" style="text-decoration: none;">Canary Hits Only</a>
    </div>
</div>

<div class="card">
    <div class="card-header">
        <span class="card-title">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            Latest File Activity Stream (Displaying <?= count($events) ?> records)
        </span>
        <span class="card-subtitle">Real-time Watchdog + psutil Capture</span>
    </div>

    <div class="table-responsive">
        <table class="data-table">
            <thead>
                <tr>
                    <th style="min-width: 140px;">Event ID</th>
                    <th style="min-width: 110px;">Type</th>
                    <th style="min-width: 250px;">Source Path</th>
                    <th style="min-width: 190px;">Associated Process</th>
                    <th style="min-width: 85px;">PID</th>
                    <th style="min-width: 130px;">Attribution</th>
                    <th style="min-width: 130px;">Canary Hit</th>
                    <th style="min-width: 105px;">Risk Weight</th>
                    <th style="min-width: 165px;">Timestamp</th>
                </tr>
            </thead>
            <tbody>
                <?php if (!empty($events)): ?>
                    <?php foreach ($events as $ev): ?>
                        <tr>
                            <td class="col-id">#EV-<?= str_pad($ev['event_id'], 5, '0', STR_PAD_LEFT) ?></td>
                            <td class="col-nowrap">
                                <?php 
                                    $t = strtoupper($ev['event_type'] ?? 'MODIFY');
                                    $badgeStyle = 'badge-medium';
                                    if ($ev['is_decoy']) $badgeStyle = 'badge-critical';
                                    elseif (strpos($t, 'DELETE') !== false) $badgeStyle = 'badge-high';
                                    elseif (strpos($t, 'CREATE') !== false) $badgeStyle = 'badge-low';
                                ?>
                                <span class="badge <?= $badgeStyle ?>"><?= htmlspecialchars($t) ?></span>
                            </td>
                            <td class="col-path" title="<?= htmlspecialchars($ev['source_path']) ?>">
                                <?= htmlspecialchars($ev['source_path']) ?>
                            </td>
                            <td class="col-nowrap">
                                <span class="process-name"><?= htmlspecialchars($ev['process_name'] ?? 'System/Unknown') ?></span>
                            </td>
                            <td class="col-nowrap">
                                <?php if ($ev['pid']): ?>
                                    <span class="pid-pill"><?= (int)$ev['pid'] ?></span>
                                <?php else: ?>
                                    <span class="text-muted">-</span>
                                <?php endif; ?>
                            </td>
                            <td class="col-nowrap">
                                <span class="badge badge-medium"><?= htmlspecialchars($ev['process_attribution_status'] ?? 'UNRESOLVED') ?></span>
                            </td>
                            <td class="col-nowrap">
                                <?php if ($ev['is_decoy']): ?>
                                    <span class="badge badge-threat">🎯 CANARY HIT</span>
                                <?php else: ?>
                                    <span class="text-muted" style="font-size: 12px;">Standard</span>
                                <?php endif; ?>
                            </td>
                            <td class="col-nowrap font-mono">
                                <?php 
                                    $rw = (int)($ev['risk_contribution'] ?? 0);
                                    $rwColor = $rw >= 40 ? 'text-red' : ($rw > 0 ? 'text-amber' : 'text-emerald');
                                ?>
                                <strong class="<?= $rwColor ?>">+<?= $rw ?></strong>
                            </td>
                            <td class="col-time"><?= htmlspecialchars($ev['timestamp']) ?></td>
                        </tr>
                    <?php endforeach; ?>
                <?php else: ?>
                    <tr>
                        <td colspan="9" style="text-align: center; color: var(--text-muted); padding: 30px;">
                            No file events recorded yet. Filesystem activity will appear here in real-time.
                        </td>
                    </tr>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
</div>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
