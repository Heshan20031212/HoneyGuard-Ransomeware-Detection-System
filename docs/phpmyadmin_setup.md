# HoneyGuard — phpMyAdmin & MySQL Database Setup Guide
**Module:** IE3092 — Information Security Project  
**Institution:** Sri Lanka Institute of Information Technology (SLIIT)  
**Group:** Group 15  

---

## 1. Overview
HoneyGuard utilizes **MySQL 8.0+ / MariaDB** as its primary relational database (`honeyguard_db`). Web-based database administration, visual inspection, and verification are conducted using **phpMyAdmin** (via XAMPP or standalone phpMyAdmin).

This document explains step-by-step how to configure, import, and inspect the HoneyGuard database in phpMyAdmin, and details how to resolve common connectivity challenges.

---

## 2. Prerequisites
1. **MySQL Server:** Oracle MySQL 8.0+ or MariaDB 10.4+ (Default port: `3306` or `3307`).
2. **Web Server with phpMyAdmin:** Apache via XAMPP (`C:\xampp`).
3. **HoneyGuard Repository:** Located on the local host.

---

## 3. Step-by-Step Setup Procedure

### Step 1: Start Apache and MySQL in XAMPP
1. Open the **XAMPP Control Panel** (`C:\xampp\xampp-control.exe`).
2. Click **Start** next to **Apache**. Verify the status changes to green (Port 80/443).
3. If using XAMPP's internal MySQL, click **Start** next to **MySQL**. If using an existing Windows service (such as `MySQL80` on port 3306), ensure that service is running (`Get-Service MySQL80`).

### Step 2: Open phpMyAdmin
1. Open your web browser (Google Chrome, Microsoft Edge, or Firefox).
2. Navigate to:
   ```
   http://localhost/phpmyadmin/
   ```
3. You will be greeted by the phpMyAdmin administration interface.

### Step 3: Create the Database `honeyguard_db`
1. In the left navigation sidebar of phpMyAdmin, click **New**.
2. In the **Database name** input box, enter:
   ```
   honeyguard_db
   ```
3. In the collation dropdown, select:
   ```
   utf8mb4_unicode_ci
   ```
4. Click **Create**.

### Step 4: Import the Schema SQL File
1. Select the newly created `honeyguard_db` from the left sidebar.
2. In the top navigation menu, click the **Import** tab.
3. Under **File to import**, click **Choose File**.
4. Browse to the project repository and select:
   ```
   database/honeyguard_db.sql
   ```
5. Leave character set as `utf-8` and format as `SQL`.
6. Scroll to the bottom and click **Import** (or **Go**).
7. phpMyAdmin will execute the script and display a green success banner:
   *"Import has been successfully finished, queries executed."*

### Step 5: Verify the 10 Relational Tables
In the left sidebar under `honeyguard_db`, verify that all 10 normalized tables exist:
1. `protected_directories`
2. `decoys`
3. `file_events`
4. `alerts`
5. `incidents`
6. `response_actions`
7. `benchmark_runs`
8. `benchmark_measurements`
9. `application_settings`
10. `audit_logs`

### Step 6: Configure HoneyGuard `.env` Connection
Ensure the `.env` file in the HoneyGuard root directory matches your MySQL server:
```ini
DB_HOST=localhost
DB_PORT=3306
DB_NAME=honeyguard_db
DB_USER=root
DB_PASSWORD=root
```
*(If using default XAMPP MySQL with no root password, set `DB_PORT=3307` or `3306` and `DB_PASSWORD=` accordingly).*

### Step 7: Verify Connection from Terminal
Run the diagnostic script:
```powershell
python scripts/test_database_connection.py
```
Expected output:
```
[+] SUCCESS: Connected to MySQL server.
[+] SCHEMA STATUS: HEALTHY (All 10 required tables verified).
```

---

## 4. Live Inspection in phpMyAdmin During Lecturer Demonstration

When presenting HoneyGuard to academic supervisors or examiners:

1. **Decoys Inspection:**
   - In phpMyAdmin, click `decoys`.
   - Observe rows showing `filename`, `file_type`, `baseline_hash` (SHA-256), `baseline_size`, and `status` (`INTACT`).
2. **Real-Time Filesystem Events:**
   - Click `file_events`.
   - Observe live records populated by the watchdog watcher: `event_type` (`MODIFY`, `EXTENSION_CHANGE`), `source_path`, `is_decoy` (1 or 0), and `process_attribution_status`.
3. **Alerts & Risk Scores:**
   - Click `alerts`.
   - Observe `risk_score` (e.g. 103), `risk_level` (`HIGH`/`CRITICAL`), `configured_threshold` (70), and individual indicator weights.
4. **Incidents & Forensics:**
   - Click `incidents`.
   - Review confirmed incident IDs (`INC-2026-0001`), forensic CPU/RAM capture, and detection latency.
5. **Containment Response Actions:**
   - Click `response_actions`.
   - Verify auditable containment records: `action_type` (`TERMINATE_PROCESS`), `operator_confirmation` (1), `result`, and `success` status.
6. **Benchmark Runs:**
   - Click `benchmark_runs` and `benchmark_measurements`.
   - Review empirical data logged across TC01–TC07 trials.

---

## 5. Troubleshooting Common MySQL & phpMyAdmin Errors

| Error Symptom | Root Cause | Solution |
| :--- | :--- | :--- |
| **Access denied for user 'root'@'localhost'** | Password mismatch in `.env` or MySQL configuration. | Verify password in `.env`. On MySQL 8.0, check `DB_PASSWORD=root`. In XAMPP, root is often blank. |
| **MySQL Server Has Gone Away / Can't connect** | MySQL service is stopped or port is blocked. | Ensure `MySQL80` service or XAMPP MySQL is active. Check with `Get-Service MySQL80` or XAMPP Control Panel. |
| **Unknown database 'honeyguard_db'** | Database has not yet been created in phpMyAdmin. | In phpMyAdmin, click **New**, type `honeyguard_db`, and click **Create**, then import `database/honeyguard_db.sql`. |
| **Foreign key constraint fails** | Attempting to insert a child record referencing a non-existent parent. | Ensure parent directory exists before inserting decoy, or that alert exists before referencing in incident. |
| **Port Conflict (3306 vs 3307)** | Both Oracle MySQL 8.0 and XAMPP MySQL installed simultaneously. | Configure phpMyAdmin `config.inc.php` port to match the running database instance (e.g. `$cfg['Servers'][$i]['port'] = '3306';`). |
| **ModuleNotFoundError: PyMySQL** | Python connector library not installed in active environment. | Run `pip install pymysql cryptography`. |
