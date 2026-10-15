# HoneyGuard Requirements Traceability Matrix (RTM)
**Module:** IE3092 — Information Security Project  
**Institution:** Sri Lanka Institute of Information Technology (SLIIT)  
**Group:** Group 15  

---

## 1. Functional Requirements Traceability

| ID | Requirement Description | Implementation Module | Database Table | Verification Test | Genuine Evidence | Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-1.1** | Create synthetic PDF, DOCX, XLSX, and TXT decoys with context-appropriate names and non-sensitive content. | `honeyguard.decoy_generation.generator` | `decoys` | `test_decoys.py` | Validated files on disk in `demo_workspace/` | **PASS** |
| **FR-1.2** | Place decoys into selected high-value-looking directories to act as canaries for scanning and bulk encryption. | `honeyguard.decoy_generation.registry` | `protected_directories` | `create_demo_environment.py` | Canary files deployed in `Finance`, `HR`, `Legal`, `General` | **PASS** |
| **FR-1.3** | Register each deployed decoy's location, type, creation time, SHA-256 hash, and monitoring status. | `honeyguard.decoy_generation.registry` | `decoys` | `test_db_tc02_decoy_insert` | Decoy records visible in MySQL & phpMyAdmin | **PASS** |
| **FR-2.1** | Continuously monitor protected directories in the background using the Python watchdog library. | `honeyguard.file_monitoring.watcher` | `protected_directories` | `test_end_to_end_pipeline.py` | Non-blocking observer active; events logged | **PASS** |
| **FR-2.2** | Capture create, write, modify, rename, move, and delete events on protected paths. | `honeyguard.file_monitoring.watcher` | `file_events` | `TC01`, `TC02`, `TC05` | Intercepted operations recorded in `file_events` | **PASS** |
| **FR-2.3** | Associate each captured event with timestamp and process telemetry (PID, executable path where resolvable). | `honeyguard.file_monitoring.process_resolver` | `file_events` | `test_db_tc03_filesystem_event_insert` | PID and attribution status recorded in MySQL | **PASS** |
| **FR-3.1** | Evaluate behavioural indicators: high-frequency modification, repeated renaming/extension, entropy change. | `honeyguard.detection.indicators` | `file_events` | `TC04`, `TC05`, `test_detection.py` | Matched indicators generated and logged | **PASS** |
| **FR-3.2** | Compute weighted Risk Score = Honeytoken + Activity + Rename + Entropy for correlated events. | `honeyguard.detection.risk_engine` | `alerts` | `test_risk_score_calculation` | Composite score reaches 103 on full attack | **PASS** |
| **FR-3.3** | Generate high-risk alert once Risk Score exceeds configured threshold (Default: 70). | `honeyguard.detection.alert_manager` | `alerts` | `TC06`, `test_db_tc04_alert_insert` | Alerts raised in MySQL & UI | **PASS** |
| **FR-3.4** | Each alert shall include affected file, suspicious process info, event time, and matched indicators. | `honeyguard.detection.alert_manager` | `alerts` | `TC06`, `AlertsView` | Structured fields rendered in Alert Window | **PASS** |
| **FR-4.1** | Execute containment actions only after alert verification, never on a single unverified raw event. | `honeyguard.response.containment` | `response_actions` | `test_unresolved_pid_safeguard` | Single raw event rejected; requires score $\ge 70$ | **PASS** |
| **FR-4.2** | Terminate or isolate offending process using supported OS controls, restricted to authorized sandbox. | `honeyguard.response.containment` | `response_actions` | `test_containment_allowlist` | Process termination via psutil; allowlist verified | **PASS** |
| **FR-4.3** | Record offending executable path and full incident context for forensic analysis. | `honeyguard.response.forensics` | `incidents` | `test_end_to_end_pipeline.py` | CPU, RAM, cmdline logged in incident record | **PASS** |
| **FR-4.4** | Every response action shall be logged and auditable. | `honeyguard.response.containment` | `response_actions`, `audit_logs` | `test_db_tc05_incident_and_response_transaction` | Action records in MySQL & phpMyAdmin | **PASS** |
| **FR-5.1** | Persist decoy registrations, file events, alerts, and response actions in relational database (MySQL). | `honeyguard.database.repositories` | `honeyguard_db` (10 tables) | `test_database.py` (DB-TC01 to DB-TC10) | Verified in MySQL 8.0 & phpMyAdmin | **PASS** |
| **FR-5.2** | Maintain chronological, queryable timeline of all security-relevant activity. | `honeyguard.database.repositories` | `incidents`, `file_events` | `IncidentLogsView` | Reverse-chronological query confirmed | **PASS** |
| **FR-5.3** | Assign each confirmed incident a unique identifier (`INC-2026-XXXX`) and support exports. | `honeyguard.response.containment` | `incidents` | `test_sanitize_incident_id`, JSON/CSV Export | Generated IDs like `INC-2026-0001`; exports work | **PASS** |

---

## 2. Non-Functional Requirements Traceability

| ID | Category | Requirement Description | Measured Value | Target / Threshold | Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **NFR-P1** | Performance | Minimise indicator-to-alert detection time. | Mean: **457.2 ms** (TC06) / **147.7 ms** (TC04) | < 1000 ms | **PASS** |
| **NFR-P2** | Performance | Low CPU and RAM overhead on endpoint during monitoring. | CPU: **0.0% – 0.6%** \| RAM: **~84.8 MB** | CPU < 5%, RAM < 200 MB | **PASS** |
| **NFR-P3** | Performance | Process filesystem events with low latency. | Asynchronous EventBus queue buffer | Real-time / Non-blocking | **PASS** |
| **NFR-S1** | Safety | Scoped protected directories and non-sensitive decoys. | Strict path validation (`is_safe_sandbox_path`) | Confined to `demo_workspace/` | **PASS** |
| **NFR-S2** | Safety | Restrict containment actions to authorized sandbox; enforce allowlist. | Critical OS and HoneyGuard allowlist verified | Zero disruption to OS processes | **PASS** |
| **NFR-S3** | Safety | Handle service and database errors gracefully without crash. | Handled in `connection.py` and `schema.py` | Fail-safe exception handling | **PASS** |
| **NFR-R1** | Reliability | Continuous background monitoring without interruption. | Watchdog thread runs in background | Zero UI thread blocking | **PASS** |
| **NFR-R2** | Reliability | Measure and minimize false-positive rate. | FPR = **0.0%** across TC01, TC02, TC07 | < 5.0% | **PASS** |
| **NFR-R3** | Reliability | Remain resilient under normal benign workloads. | TC01, TC02, TC07 pass cleanly | 100% Benign pass rate | **PASS** |
| **NFR-U1** | Usability | Clear colour-coded protection status and KPI cards. | Implemented in `DashboardView` | Figure 4 Wireframe compliant | **PASS** |
| **NFR-U2** | Usability | Unified alert breakdown view with scores and indicators. | Implemented in `AlertsView` | Figure 6 Wireframe compliant | **PASS** |
| **NFR-U3** | Usability | Exportable and readable incident logs. | Implemented in `IncidentLogsView` | Valid JSON & CSV outputs generated | **PASS** |
