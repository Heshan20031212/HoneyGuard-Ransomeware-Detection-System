# HoneyGuard Desktop Application User Guide
**Module:** IE3092 — Information Security Project  
**Institution:** Sri Lanka Institute of Information Technology (SLIIT)  
**Group:** Group 15  

---

## 1. Introduction
The **HoneyGuard Desktop Management Console** is a specialized Security Operations Center (SOC) graphical user interface built to monitor protected workspaces, manage canary honeytokens, inspect real-time behavioural telemetry, and execute controlled containment against ransomware-like operations.

---

## 2. Navigating the Interface

### 2.1 The Left Navigation Rail
The persistent navigation rail on the left gives access to all seven functional modules:
- **📊 Dashboard:** High-level early-warning KPI cards and recent security events.
- **🍯 Decoy Manager:** Manage, plant, and verify canary files.
- **👁 File Monitor:** Stream live filesystem operations and process attribution.
- **🚨 Alerts:** Detailed breakdown of high-risk detection incidents.
- **📜 Incident Logs:** Historical audit records, forensic snapshots, and data exports.
- **⚡ Benchmarking:** Live 5-trial performance evaluation and empirical metrics.
- **⚙ Settings:** Configure directories, detection weights, thresholds, and database connection.

### 2.2 Persistent Status Box
Located under the shield logo on the left rail:
- **● PROTECTION ACTIVE:** Indicates that the background watchdog thread is actively observing filesystem events.
- **● DB: CONNECTED:** Confirms active connection to the MySQL `honeyguard_db` database.

---

## 3. Screen Walkthroughs

### 3.1 Dashboard (Figure 4)
- **KPI Cards:**
  - **Decoys Deployed:** Total active canary tokens currently registered in MySQL.
  - **Files Monitored:** Approximate count of monitored entities and recent activities.
  - **Active Alerts:** Unresolved high-risk alerts awaiting operator triage.
  - **Processes Contained:** Hostile processes successfully neutralized.
- **Recent Security Events Feed:**
  - Live reverse-chronological event stream.
  - Colour-coded badges:
    - `CRITICAL` (Red): Canary touched, extension change, or high risk.
    - `RESPONSE` (Blue): Containment action executed.
    - `WARNING` (Yellow): Single decoy access below threshold.
    - `INFO` (White): Standard file creation/modification.

### 3.2 Decoy Manager (Figure 5)
- **Deploying a New Decoy:**
  1. Click **+ Deploy New Decoy**.
  2. Select department template pack (e.g. *Finance*, *HR*, *Legal*, *General*).
  3. Select the target protected directory.
  4. Click **Deploy Decoys**. HoneyGuard will generate synthetic PDF/DOCX/XLSX/TXT files on disk and register their SHA-256 baseline in MySQL.
- **Verifying Decoy Integrity:**
  - Click **Verify All Decoys**. HoneyGuard hashes every canary on disk and verifies if any have been accessed, modified, or deleted.

### 3.3 File Monitor
- Displays real-time intercepted filesystem operations:
  - Timestamp, Event Type (`CREATE`, `MODIFY`, `RENAME`, `EXTENSION_CHANGE`, `DELETE`), Path, Canary status (`YES`/`NO`), Process Name/PID, and Risk Contribution.
- Controls:
  - **⏸ Pause Feed:** Temporarily pause stream rendering to inspect a specific line.
  - **Clear View:** Clear local view buffer.

### 3.4 Alerts Screen (Figure 6)
When composite risk score exceeds the configured threshold (default: 70):
1. **Red Banner:** `⚠ RANSOMWARE-LIKE ACTIVITY DETECTED`.
2. **Incident Details:** Affected Canary File, Directory, Suspicious Process, PID, and Timestamp.
3. **Risk Score Breakdown Table:**
   - Honeytoken Interaction Weight: 40
   - High-Frequency Activity Weight: 25
   - Rename / Extension Change Weight: 20
   - Content / Entropy Indicator Weight: 18
   - **Total Risk Score:** e.g. 103 (HIGH/CRITICAL RISK).
4. **Indicators Matched Checklist:** Shows plain-language confirmation of matched indicators.
5. **Mitigation Actions:**
   - **🚨 Isolate & Terminate Process:** Prompts confirmation modal before terminating the hostile PID.
   - **📦 Quarantine File:** Moves target file into `data/quarantine/`.
   - **Log Only (Ignore):** Acknowledges alert without terminating processes.

### 3.5 Security & Incident Logs (Figure 7)
- Review complete history of confirmed incidents and forensic telemetry.
- **Exporting Records:**
  - Click **Export JSON** to save all MySQL incident records to `data/exports/incidents_export_*.json`.
  - Click **Export CSV** to generate a tabular spreadsheet export for report preparation.

### 3.6 Testing & Benchmarking
- Click **▶ Execute 5-Trial Evaluation Suite**.
- HoneyGuard will run all 7 scenarios across 5 trials in the background, logging 140+ telemetry samples and generating performance charts in `data/benchmark_results/`.

### 3.7 Settings
- **Protected Directories:** Add or remove directories watched by HoneyGuard.
- **Detection Formulas:** Adjust weights for honeytokens, frequency, renaming, and entropy.
- **Database Test:** Click **Test Connection** to verify live connection to MySQL 8.0.
