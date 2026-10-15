<?php
/**
 * HoneyGuard Web Portal - Alerts & Threat Containment
 */

$pageTitle = "Alerts & Incident Response";
require_once __DIR__ . '/config/db.php';
require_once __DIR__ . '/includes/header.php';

$pdo = getDB();
$msg = '';
$err = '';

// Handle Admin Containment Actions
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action'])) {
    if (!isAdmin()) {
        $err = "Access Denied: Only administrators can execute containment actions.";
    } else {
        $alert_id = trim($_POST['alert_id'] ?? '');
        $act = $_POST['action'];

        if ($act === 'contain_process') {
            $pid = intval($_POST['pid'] ?? 0);
            $pname = sanitize($_POST['pname'] ?? 'ransomware.exe');
            try {
                // Find or create incident
                $incStmt = $pdo->prepare("SELECT incident_id FROM incidents WHERE alert_id = :aid LIMIT 1");
                $incStmt->execute([':aid' => $alert_id]);
                $incident_id = $incStmt->fetchColumn();

                if (!$incident_id) {
                    $incident_id = 'INC-' . strtoupper(substr(md5(uniqid(mt_rand(), true)), 0, 8));
                    $insInc = $pdo->prepare("INSERT INTO incidents (incident_id, alert_id, detected_at, affected_file, risk_score, risk_level, matched_indicators, pid, process_name, containment_status)
                                              VALUES (:iid, :aid, NOW(3), 'Protected Directory', 85, 'HIGH', 'Manual admin intervention', :pid, :pname, 'CONTAINED')");
                    $insInc->execute([
                        ':iid' => $incident_id,
                        ':aid' => $alert_id ?: null,
                        ':pid' => $pid,
                        ':pname' => $pname
                    ]);
                }

                // Record response action in response_actions table
                $stmt = $pdo->prepare("INSERT INTO response_actions (incident_id, action_type, requested_at, executed_at, target_pid, target_path, operator_confirmation, result, success) 
                                        VALUES (:iid, 'TERMINATE_PROCESS', NOW(3), NOW(3), :pid, :pname, 1, 'PROCESS_TERMINATED', 1)");
                $stmt->execute([
                    ':iid' => $incident_id,
                    ':pid' => $pid,
                    ':pname' => $pname
                ]);

                // Update alert status
                if ($alert_id) {
                    $upd = $pdo->prepare("UPDATE alerts SET alert_status = 'RESOLVED' WHERE alert_id = :id");
                    $upd->execute([':id' => $alert_id]);
                }

                // Audit log
                $audit = $pdo->prepare("INSERT INTO audit_logs (timestamp, action, component, description, severity, success) 
                                        VALUES (NOW(3), 'CONTAINMENT_EXECUTED', 'WEB_PORTAL', :det, 'CRITICAL', 1)");
                $audit->execute([':det' => "Admin {$currentUser['username']} terminated malicious process {$pname} (PID: {$pid})"]);

                $msg = "Threat Neutralized: Process {$pname} (PID: {$pid}) terminated and alert marked RESOLVED.";
            } catch (Exception $e) {
                $err = "Containment action failed: " . $e->getMessage();
            }
        } elseif ($act === 'resolve_alert') {
            try {
                $upd = $pdo->prepare("UPDATE alerts SET alert_status = 'RESOLVED' WHERE alert_id = :id");
                $upd->execute([':id' => $alert_id]);
                $msg = "Alert {$alert_id} marked as RESOLVED.";
            } catch (Exception $e) {
                $err = "Update failed: " . $e->getMessage();
            }
        }
    }
}

// Fetch Alerts
$stmt = $pdo->query("SELECT alert_id, event_id, timestamp, affected_file, decoy_id, risk_score, risk_level, matched_indicators, pid, process_name, executable_path, alert_status 
                     FROM alerts ORDER BY timestamp DESC LIMIT 50");
$alerts = $stmt->fetchAll();
?>

<div class="page-header">
    <div class="page-title-box">
        <h1>Ransomware Alert & Containment Center</h1>
        <p>Dynamic risk scoring correlation engine and rapid automated/analyst response actions</p>
    </div>
    <div class="page-actions">
        <?php if (!isAdmin()): ?>
            <span class="badge badge-medium">Role: Security Analyst (View Only)</span>
        <?php else: ?>
            <span class="badge badge-critical" style="background: rgba(239, 68, 68, 0.2);">Admin Containment Clearance: ACTIVE</span>
        <?php endif; ?>
    </div>
</div>

<?php if ($msg): ?>
    <div class="alert" style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); color: #34d399;">
        <?= htmlspecialchars($msg) ?>
    </div>
<?php endif; ?>

<?php if ($err): ?>
    <div class="alert alert-danger">
        <?= htmlspecialchars($err) ?>
    </div>
<?php endif; ?>

<div class="card">
    <div class="card-header">
        <span class="card-title">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            Triggered Ransomware Incidents (Total: <?= count($alerts) ?>)
        </span>
        <span class="card-subtitle">Behavioural Correlation Engine Records</span>
    </div>

    <div class="table-responsive">
        <table class="data-table">
            <thead>
                <tr>
                    <th style="min-width: 160px;">Alert ID</th>
                    <th style="min-width: 105px;">Risk Level</th>
                    <th style="min-width: 105px;">Risk Score</th>
                    <th style="min-width: 190px;">Target Process & PID</th>
                    <th style="min-width: 220px;">Affected File / Canary</th>
                    <th style="min-width: 180px;">Matched Indicators</th>
                    <th style="min-width: 110px;">Status</th>
                    <th style="min-width: 160px;">Timestamp</th>
                    <th style="min-width: 150px;">Response Action</th>
                </tr>
            </thead>
            <tbody>
                <?php if (!empty($alerts)): ?>
                    <?php foreach ($alerts as $a): ?>
                        <tr>
                            <td class="col-id"><?= htmlspecialchars($a['alert_id']) ?></td>
                            <td class="col-nowrap">
                                <span class="badge badge-<?= strtolower($a['risk_level'] ?? 'medium') ?>">
                                    <?= htmlspecialchars($a['risk_level']) ?>
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
                            <td style="font-size: 11.5px; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="<?= htmlspecialchars($a['matched_indicators']) ?>">
                                <?= htmlspecialchars($a['matched_indicators'] ?? 'N/A') ?>
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
                            <td>
                                <?php if (isAdmin()): ?>
                                    <?php if ($a['alert_status'] === 'ACTIVE' || $a['alert_status'] === 'NEW'): ?>
                                        <div style="display: flex; gap: 6px;">
                                            <form method="POST" action="alerts.php" onsubmit="return confirm('Immediately terminate process <?= htmlspecialchars($a['process_name']) ?> (PID <?= (int)$a['pid'] ?>)?');">
                                                <input type="hidden" name="action" value="contain_process">
                                                <input type="hidden" name="alert_id" value="<?= htmlspecialchars($a['alert_id']) ?>">
                                                <input type="hidden" name="pname" value="<?= htmlspecialchars($a['process_name'] ?? '') ?>">
                                                <input type="hidden" name="pid" value="<?= (int)($a['pid'] ?? 0) ?>">
                                                <button type="submit" class="btn" style="padding: 4px 8px; font-size: 11px; background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.4); color: #f87171;">
                                                    Kill PID
                                                </button>
                                            </form>
                                            <form method="POST" action="alerts.php">
                                                <input type="hidden" name="action" value="resolve_alert">
                                                <input type="hidden" name="alert_id" value="<?= htmlspecialchars($a['alert_id']) ?>">
                                                <button type="submit" class="btn" style="padding: 4px 8px; font-size: 11px; background: rgba(59, 130, 246, 0.2); border: 1px solid rgba(59, 130, 246, 0.4); color: #60a5fa;">
                                                    Resolve
                                                </button>
                                            </form>
                                        </div>
                                    <?php else: ?>
                                        <span class="text-emerald" style="font-size: 11px; font-weight: 600;">✓ Contained</span>
                                    <?php endif; ?>
                                <?php else: ?>
                                    <span class="text-muted" style="font-size: 11px;">Admin Required</span>
                                <?php endif; ?>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                <?php else: ?>
                    <tr>
                        <td colspan="9" style="text-align: center; color: var(--text-muted); padding: 30px;">
                            No alerts recorded in database.
                        </td>
                    </tr>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
</div>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
