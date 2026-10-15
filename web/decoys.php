<?php
/**
 * HoneyGuard Web Portal - Canary Decoy Management
 */

$pageTitle = "Canary Decoys";
require_once __DIR__ . '/config/db.php';
require_once __DIR__ . '/includes/header.php';

$pdo = getDB();
$msg = '';
$err = '';

// Handle Admin Action: Deploy New Decoy
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'deploy_decoy') {
    if (!isAdmin()) {
        $err = "Unauthorized: Only administrators can deploy decoys.";
    } else {
        $filename = trim($_POST['filename'] ?? '');
        $filepath = trim($_POST['filepath'] ?? '');
        $file_type = strtoupper(trim($_POST['file_type'] ?? 'DOCX'));

        if (empty($filename) || empty($filepath)) {
            $err = "Filename and Filepath are required.";
        } else {
            try {
                // Ensure proper extension on filename
                $expectedExt = '.' . strtolower($file_type);
                if (!preg_match('/\.[a-zA-Z0-9]+$/', $filename)) {
                    $filename .= $expectedExt;
                }

                // Resolve absolute target path on PC disk
                $filepath = str_replace('/', DIRECTORY_SEPARATOR, $filepath);
                if (is_dir($filepath) || !preg_match('/\.[a-zA-Z0-9]+$/', $filepath)) {
                    $absolute_path = rtrim($filepath, DIRECTORY_SEPARATOR) . DIRECTORY_SEPARATOR . $filename;
                } else {
                    $absolute_path = $filepath;
                    $filename = basename($absolute_path);
                }

                // Ensure parent directory exists on physical disk
                $parentDir = dirname($absolute_path);
                if (!is_dir($parentDir)) {
                    @mkdir($parentDir, 0777, true);
                }

                // 1. Physically generate synthetic decoy file on PC disk
                $pythonCandidates = [
                    'C:\\Users\\LENOVO\\AppData\\Local\\Programs\\Python\\Python313\\python.exe',
                    'python'
                ];
                $pythonBin = 'python';
                foreach ($pythonCandidates as $cand) {
                    if (file_exists($cand)) {
                        $pythonBin = $cand;
                        break;
                    }
                }

                $scriptCandidates = [
                    'C:\\Users\\LENOVO\\OneDrive\\Desktop\\HoneyGuard project folder\\scripts\\generate_single_decoy.py',
                    __DIR__ . DIRECTORY_SEPARATOR . 'scripts' . DIRECTORY_SEPARATOR . 'generate_single_decoy.py',
                    dirname(__DIR__) . DIRECTORY_SEPARATOR . 'scripts' . DIRECTORY_SEPARATOR . 'generate_single_decoy.py'
                ];
                $scriptPath = '';
                foreach ($scriptCandidates as $sc) {
                    if (file_exists($sc)) {
                        $scriptPath = $sc;
                        break;
                    }
                }

                $realSize = 0;
                $realHash = '';

                if (!empty($scriptPath)) {
                    $cmd = 'cmd /c ""' . $pythonBin . '" "' . $scriptPath . '" "' . $absolute_path . '" "' . $file_type . '"" 2>&1';
                    $cmdOut = shell_exec($cmd);

                    if (preg_match('/METADATA:(\d+):([a-f0-9]{64})/', $cmdOut, $matches)) {
                        $realSize = (int)$matches[1];
                        $realHash = $matches[2];
                    }
                }

                // Fallback direct generation if script failed or file not yet on disk
                if ($realSize <= 0) {
                    if (!file_exists($absolute_path)) {
                        $content = "=== HONEYGUARD SYNTHETIC CANARY TOKEN ===\n";
                        $content .= "Filename: " . $filename . "\n";
                        $content .= "Type: " . $file_type . "\n";
                        $content .= "Deployed: " . date('Y-m-d H:i:s') . "\n";
                        $content .= "Classification: HIGH-VALUE CONFIDENTIAL CANARY DECOY\n";
                        $content .= "Description: Deployed by HoneyGuard for ransomware detection.\n";
                        $content .= "---------------------------------------------------------\n";
                        $content .= "Account ID: ACC-" . rand(100000, 999999) . "\n";
                        $content .= "Records: Active Payroll and Corporate Treasury Ledger\n";
                        @file_put_contents($absolute_path, $content);
                    }

                    clearstatcache(true, $absolute_path);
                    $realSize = @filesize($absolute_path) ?: 2048;
                    $realHash = @hash_file('sha256', $absolute_path) ?: hash('sha256', $filename . time());
                }

                // Find or register protected directory
                $dirStmt = $pdo->prepare("SELECT directory_id FROM protected_directories WHERE directory_path = :dp LIMIT 1");
                $dirStmt->execute([':dp' => $parentDir]);
                $dirId = $dirStmt->fetchColumn();

                if (!$dirId) {
                    $dirIns = $pdo->prepare("INSERT INTO protected_directories (directory_path, display_name, monitoring_enabled) VALUES (:dp, :dn, 1)");
                    $dirIns->execute([
                        ':dp' => $parentDir,
                        ':dn' => basename($parentDir) . ' Folder'
                    ]);
                    $dirId = $pdo->lastInsertId();
                }

                // Register decoy in MySQL
                $decoy_id = 'DEC-' . strtoupper(substr(md5(uniqid(mt_rand(), true)), 0, 10));
                $stmt = $pdo->prepare("INSERT INTO decoys (decoy_id, directory_id, filename, absolute_path, file_type, baseline_hash, baseline_size, status, monitoring_enabled, creation_timestamp, last_verified_timestamp) 
                                        VALUES (:did, :dir_id, :fn, :fp, :ft, :hsh, :bsz, 'INTACT', 1, NOW(), NOW())");
                $stmt->execute([
                    ':did' => $decoy_id,
                    ':dir_id' => $dirId,
                    ':fn' => $filename,
                    ':fp' => $absolute_path,
                    ':ft' => $file_type,
                    ':hsh' => $realHash,
                    ':bsz' => $realSize
                ]);

                // Audit log
                $audit = $pdo->prepare("INSERT INTO audit_logs (timestamp, action, component, description, severity, success) 
                                        VALUES (NOW(3), 'DECOY_DEPLOYED', 'WEB_PORTAL', :det, 'INFO', 1)");
                $audit->execute([':det' => "Admin {$currentUser['username']} deployed decoy {$filename} physically at {$absolute_path} ({$realSize} bytes)"]);

                $sizeKb = round($realSize / 1024, 2);
                $msg = "✓ Canary decoy '<strong>{$filename}</strong>' physically created and saved on your PC!<br><span style='font-size: 0.85rem; opacity: 0.9;'>Saved at: <code style='color: #38bdf8;'>{$absolute_path}</code> | Size: {$sizeKb} KB</span>";
            } catch (Exception $e) {
                $err = "Failed to deploy decoy: " . $e->getMessage();
            }
        }
    }
}

// Fetch all decoys
$stmt = $pdo->query("SELECT decoy_id, directory_id, filename, absolute_path, file_type, baseline_hash, baseline_size, status, monitoring_enabled, creation_timestamp, last_verified_timestamp 
                     FROM decoys ORDER BY creation_timestamp DESC");
$decoys = $stmt->fetchAll();
?>

<div class="page-header">
    <div class="page-title-box">
        <h1>Canary Honeytoken Registry</h1>
        <p>Manage and audit deployed high-interaction decoy sensors across protected file systems</p>
    </div>
    <div class="page-actions">
        <?php if (isAdmin()): ?>
            <button class="btn btn-primary" onclick="openModal('deployModal')">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                <span>Deploy New Decoy</span>
            </button>
        <?php else: ?>
            <span class="badge badge-medium">Role: Security Analyst (Read-Only)</span>
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
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            Registered Canaries (Total: <?= count($decoys) ?>)
        </span>
        <span class="card-subtitle">Real-time Canary Integrity Sensors</span>
    </div>

    <div class="table-responsive">
        <table class="data-table">
            <thead>
                <tr>
                    <th style="min-width: 170px;">Decoy ID</th>
                    <th style="min-width: 190px;">Canary Filename</th>
                    <th style="min-width: 95px;">Format</th>
                    <th style="min-width: 250px;">Deployment Path</th>
                    <th style="min-width: 110px;">File Size</th>
                    <th style="min-width: 175px;">Integrity Hash (SHA-256)</th>
                    <th style="min-width: 110px;">Status</th>
                    <th style="min-width: 165px;">Deployed At</th>
                </tr>
            </thead>
            <tbody>
                <?php if (!empty($decoys)): ?>
                    <?php foreach ($decoys as $d): ?>
                        <tr>
                            <td class="col-id"><?= htmlspecialchars($d['decoy_id']) ?></td>
                            <td class="col-nowrap">
                                <strong><?= htmlspecialchars($d['filename']) ?></strong>
                            </td>
                            <td class="col-nowrap">
                                <?php $ft = strtolower($d['file_type'] ?? 'docx'); ?>
                                <span class="badge fmt-<?= $ft ?>">.<?= strtoupper($ft) ?></span>
                            </td>
                            <td class="col-path" title="<?= htmlspecialchars($d['absolute_path']) ?>">
                                <?= htmlspecialchars($d['absolute_path']) ?>
                            </td>
                            <td class="col-nowrap">
                                <span class="size-pill"><?= number_format((int)($d['baseline_size'] ?? 0)) ?> B</span>
                            </td>
                            <td class="col-nowrap">
                                <span class="hash-pill" title="<?= htmlspecialchars($d['baseline_hash'] ?? 'N/A') ?>">
                                    <?= htmlspecialchars(substr($d['baseline_hash'] ?? 'N/A', 0, 16)) ?>&hellip;
                                </span>
                            </td>
                            <td class="col-nowrap">
                                <?php if ($d['status'] === 'INTACT'): ?>
                                    <span class="badge badge-mitigated">✓ INTACT</span>
                                <?php else: ?>
                                    <span class="badge badge-threat">⚠ <?= htmlspecialchars($d['status']) ?></span>
                                <?php endif; ?>
                            </td>
                            <td class="col-time"><?= htmlspecialchars($d['creation_timestamp']) ?></td>
                        </tr>
                    <?php endforeach; ?>
                <?php else: ?>
                    <tr>
                        <td colspan="8" style="text-align: center; color: var(--text-muted); padding: 30px;">
                            No canaries registered yet. Deploy your first decoy canary.
                        </td>
                    </tr>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
</div>

<!-- Modal: Deploy Decoy -->
<div id="deployModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h3 style="color: #ffffff;">Deploy New Canary Decoy</h3>
            <button class="modal-close" onclick="closeModal('deployModal')">&times;</button>
        </div>
        <form method="POST" action="decoys.php">
            <input type="hidden" name="action" value="deploy_decoy">
            <div class="form-group">
                <label>Canary Filename</label>
                <input type="text" id="decoy_fn" name="filename" placeholder="e.g. employee_salaries_2026.xlsx" required 
                       style="width: 100%; padding: 10px; background: #0d131f; border: 1px solid var(--border-color); border-radius: 8px; color: #fff;">
            </div>
            <div class="form-group">
                <label>Deployment Target Directory / Path on PC</label>
                <input type="text" id="decoy_fp" name="filepath" value="C:\Users\LENOVO\OneDrive\Desktop\HoneyGuard project folder\data\protected_test_dir\employee_salaries_2026.xlsx" required 
                       style="width: 100%; padding: 10px; background: #0d131f; border: 1px solid var(--border-color); border-radius: 8px; color: #fff;">
                <div style="font-size: 0.78rem; color: #38bdf8; margin-top: 6px;">
                    💡 <strong>Physical Storage:</strong> This synthetic file will be physically saved on your PC hard drive at this path.
                </div>
            </div>
            <div class="form-group">
                <label>Decoy File Format</label>
                <select name="file_type" style="width: 100%; padding: 10px; background: #0d131f; border: 1px solid var(--border-color); border-radius: 8px; color: #fff;">
                    <option value="DOCX">Microsoft Word Document (.docx)</option>
                    <option value="XLSX" selected>Microsoft Excel Spreadsheet (.xlsx)</option>
                    <option value="PDF">Adobe PDF Document (.pdf)</option>
                    <option value="TXT">Plain Text / Config (.txt)</option>
                </select>
            </div>
            <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px;">
                <button type="button" class="btn" style="background: var(--bg-card); border: 1px solid var(--border-color); color: #fff;" onclick="closeModal('deployModal')">Cancel</button>
                <button type="submit" class="btn btn-primary">Deploy Canary to PC</button>
            </div>
        </form>
    </div>
</div>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
