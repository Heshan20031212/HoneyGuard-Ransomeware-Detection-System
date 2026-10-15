<?php
/**
 * HoneyGuard Web Portal - Modern Animated Cybersecurity Login Portal
 * Matches the reference design with animated particle mesh & glassmorphism
 */

require_once __DIR__ . '/config/db.php';
require_once __DIR__ . '/auth_check.php';

// Redirect if already logged in
if (isLoggedIn()) {
    header("Location: dashboard.php");
    exit;
}

$error = '';
$success = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username'] ?? '');
    $password = trim($_POST['password'] ?? '');

    if (empty($username) || empty($password)) {
        $error = "Please enter both username and password.";
    } else {
        try {
            $pdo = getDB();
            $stmt = $pdo->prepare("SELECT id, username, password_hash, role, full_name, email, is_active FROM users WHERE username = :uname LIMIT 1");
            $stmt->execute([':uname' => $username]);
            $user = $stmt->fetch();

            if ($user && $user['is_active']) {
                // Verify password (bcrypt or fallback)
                if (password_verify($password, $user['password_hash']) || ($password === 'admin123' && $user['username'] === 'admin') || ($password === 'user123' && $user['username'] === 'user')) {
                    $_SESSION['user_id'] = $user['id'];
                    $_SESSION['username'] = $user['username'];
                    $_SESSION['role'] = $user['role'];
                    $_SESSION['full_name'] = $user['full_name'];
                    $_SESSION['email'] = $user['email'];

                    // Update last login
                    $upd = $pdo->prepare("UPDATE users SET last_login = NOW() WHERE id = :id");
                    $upd->execute([':id' => $user['id']]);

                    // Audit log
                    $audit = $pdo->prepare("INSERT INTO audit_logs (timestamp, action, component, description, severity, success) VALUES (NOW(3), 'USER_LOGIN', 'WEB_PORTAL', :details, 'INFO', 1)");
                    $audit->execute([':details' => "User {$user['username']} ({$user['role']}) logged into web portal from {$_SERVER['REMOTE_ADDR']}"]);

                    header("Location: dashboard.php");
                    exit;
                } else {
                    $error = "Invalid password. Please check your credentials.";
                }
            } else {
                $error = "User not found or account is deactivated.";
            }
        } catch (Exception $e) {
            $error = "Authentication system error: " . $e->getMessage();
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HoneyGuard — Web Portal Login</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body class="login-body">
    <!-- Interactive Background Cyber Constellation Mesh Canvas -->
    <canvas id="cyberCanvas" class="cyber-bg-canvas"></canvas>

    <div class="login-wrapper">
        <div class="login-card glass-morphism">
            <!-- 3D Glowing Shield Header -->
            <div class="login-header">
                <div class="logo-emblem-3d">
                    <div class="shield-aura"></div>
                    <svg viewBox="0 0 24 24" class="shield-svg" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                        <path d="M9 12l2 2 4-4" stroke-width="2.2"/>
                    </svg>
                </div>
                <h1 class="portal-title">HoneyGuard</h1>
                <p class="portal-subtitle">Honeytoken-Based Ransomware Detection & Prevention System</p>
                <div class="badge-container">
                    <span class="badge-cyan-glow">SLIIT IE3092 • CYBER SECURITY</span>
                </div>
            </div>

            <?php if (!empty($error)): ?>
                <div class="alert alert-danger">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                    </svg>
                    <span><?= htmlspecialchars($error) ?></span>
                </div>
            <?php endif; ?>

            <!-- Login Form -->
            <form method="POST" action="login.php" class="login-form" id="loginForm">
                <div class="form-group">
                    <label for="username">Username / ID</label>
                    <div class="input-with-icon">
                        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
                        </svg>
                        <input type="text" id="username" name="username" placeholder="Enter username (admin or user)" required autocomplete="username" autofocus>
                    </div>
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <div class="input-with-icon">
                        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                        </svg>
                        <input type="password" id="password" name="password" placeholder="Enter password" required autocomplete="current-password">
                    </div>
                </div>

                <button type="submit" class="btn btn-emerald-submit btn-block">
                    <span>Sign In to Dashboard</span>
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5">
                        <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
                    </svg>
                </button>
            </form>

            <!-- Quick Access Section -->
            <div class="divider">
                <span>DEMO QUICK ACCESS</span>
            </div>

            <div class="quick-access-grid">
                <!-- Admin Access Card -->
                <div class="quick-card quick-card-admin" onclick="quickFill('admin', 'admin123')">
                    <div class="quick-card-icons">
                        <div class="icon-bubble icon-terminal">
                            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>
                            </svg>
                        </div>
                        <div class="icon-bubble icon-key">
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>
                            </svg>
                        </div>
                    </div>
                    <div class="quick-card-content">
                        <strong>Admin Access</strong>
                        <div class="quick-creds">username: <span>admin</span> / password: <span>admin123</span></div>
                        <span class="quick-tag tag-admin">Full Control</span>
                    </div>
                </div>

                <!-- User Access Card -->
                <div class="quick-card quick-card-user" onclick="quickFill('user', 'user123')">
                    <div class="quick-card-icons">
                        <div class="icon-bubble icon-radar">
                            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"/><path d="M12 2a10 10 0 0 1 10 10"/><path d="M12 12l7-7"/>
                            </svg>
                        </div>
                        <div class="icon-bubble icon-shield">
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                            </svg>
                        </div>
                    </div>
                    <div class="quick-card-content">
                        <strong>User Access</strong>
                        <div class="quick-creds">username: <span>user</span> / password: <span>user123</span></div>
                        <span class="quick-tag tag-user">SOC Analyst</span>
                    </div>
                </div>
            </div>

            <!-- Footer Details -->
            <div class="login-footer">
                <div class="context-list">
                    <p class="context-item"><span class="context-lead text-cyan">Admin Context:</span> Canary Deployment, Process Termination & Containment, Full DB Control.</p>
                    <p class="context-item"><span class="context-lead text-cyan">User Context:</span> Threat Monitoring, Alert Analytics, Live Event Inspection.</p>
                </div>
                <div class="db-link-container">
                    <a href="http://localhost/phpmyadmin/" target="_blank" class="phpmyadmin-btn">
                        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                            <ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
                        </svg>
                        <span>Open phpMyAdmin Database</span>
                    </a>
                </div>
            </div>
        </div>
    </div>

    <script src="assets/js/particles.js"></script>
    <script>
        function quickFill(user, pass) {
            document.getElementById('username').value = user;
            document.getElementById('password').value = pass;
            document.getElementById('loginForm').submit();
        }
    </script>
</body>
</html>
