# HoneyGuard Database Design Specification
**Module:** IE3092 — Information Security Project  
**Institution:** Sri Lanka Institute of Information Technology (SLIIT)  
**Database Name:** `honeyguard_db`  
**Collation:** `utf8mb4_unicode_ci`  
**Group:** Group 15  

---

## 1. Academic Integrity Statement: Database Architecture Evolution

In the initial proposal and software stack specification submitted during preliminary academic milestones, lightweight local persistence using SQLite and flat JSON files was initially scoped to facilitate rapid single-host prototyping.

As part of the **Final Implementation Refinement**, the development team transitioned the primary persistence engine to **MySQL 8.0+**, managed through **phpMyAdmin**. 

This transition represents an intentional engineering refinement justified by:
1. **Relational Integrity & ACID Transactions:** Enforcement of foreign key constraints (`ON DELETE CASCADE`, `ON DELETE SET NULL`) ensuring that decoys, events, alerts, and incidents remain strictly synchronized without orphan records.
2. **Centralized Enterprise Auditability:** MySQL provides an enterprise-grade tabular structure suitable for multi-endpoint expansion and SIEM telemetry aggregation.
3. **Interactive Inspection via phpMyAdmin:** Facilitates transparent, web-based verification of security telemetry for examiners, lecturers, and SOC operators.
4. **Separation of Operational Data from Analytical Exports:** High-speed SQL queries handle live events, while JSON/CSV formats are reserved for portable forensic exports and benchmarking charts.

---

## 2. Entity-Relationship Overview

```
[protected_directories]
         │ (1:N)
         ├─────────────────────────────┐
         ▼                             ▼
     [decoys]                     [file_events]
         │ (1:N)                       │ (1:1 optional)
         ├─────────────┐               ▼
         ▼             ▼            [alerts]
    [file_events]   [alerts]           │ (1:1 optional)
                       │               ▼
                       └──────────> [incidents]
                                       │ (1:N)
                                       ▼
                               [response_actions]

[benchmark_runs]
         │ (1:N)
         ▼
[benchmark_measurements]

[application_settings] (Key-Value Store)
[audit_logs] (Append-Only Event Store)
```

---

## 3. Data Dictionary & Table Schemas

### 3.1 `protected_directories`
Stores directory paths actively monitored by the real-time watchdog watcher.

| Column | Data Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `directory_id` | INT | AUTO_INCREMENT, PK | Unique directory identifier |
| `directory_path` | VARCHAR(500) | NOT NULL, UNIQUE | Absolute filesystem path |
| `display_name` | VARCHAR(150) | NOT NULL | Friendly departmental label |
| `monitoring_enabled` | TINYINT(1) | DEFAULT 1 | Whether watcher actively observes this path |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Registration timestamp |
| `updated_at` | DATETIME | ON UPDATE CURRENT_TIMESTAMP | Last modification timestamp |

### 3.2 `decoys`
Maintains cryptographic baseline records of planted honeytoken canary files.

| Column | Data Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `decoy_id` | VARCHAR(64) | PRIMARY KEY | Unique canary ID (e.g. `DEC-3D40890A`) |
| `directory_id` | INT | FK -> `protected_directories` | Associated parent directory |
| `filename` | VARCHAR(255) | NOT NULL | Filename (e.g. `Employee_Salary_2026.xlsx`) |
| `absolute_path` | VARCHAR(500) | NOT NULL, UNIQUE | Full filesystem location |
| `file_type` | VARCHAR(10) | NOT NULL | Format: `PDF`, `DOCX`, `XLSX`, `TXT` |
| `baseline_hash` | VARCHAR(64) | NOT NULL | Initial SHA-256 cryptographic hash |
| `baseline_size` | BIGINT | NOT NULL | Initial file byte size |
| `status` | ENUM | NOT NULL, DEFAULT 'INTACT' | `INTACT`, `ACCESSED`, `MODIFIED`, `RENAMED`, `DELETED` |
| `monitoring_enabled`| TINYINT(1) | DEFAULT 1 | Active decoy monitoring flag |
| `creation_timestamp`| DATETIME | DEFAULT CURRENT_TIMESTAMP | Generation timestamp |
| `last_verified_timestamp`| DATETIME | DEFAULT CURRENT_TIMESTAMP | Most recent integrity check timestamp |

### 3.3 `file_events`
Logs real-time filesystem operations intercepted by watchdog.

| Column | Data Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `event_id` | BIGINT | AUTO_INCREMENT, PK | Global event sequence number |
| `directory_id` | INT | FK -> `protected_directories` (NULLABLE) | Protected directory reference |
| `decoy_id` | VARCHAR(64) | FK -> `decoys` (NULLABLE) | Decoy reference if canary file |
| `timestamp` | DATETIME(3) | NOT NULL | High-precision event timestamp |
| `event_type` | VARCHAR(30) | NOT NULL | `CREATE`, `MODIFY`, `RENAME`, `DELETE`, `EXTENSION_CHANGE` |
| `source_path` | VARCHAR(500) | NOT NULL | Original path |
| `destination_path` | VARCHAR(500) | NULLABLE | Destination path if moved/renamed |
| `is_decoy` | TINYINT(1) | DEFAULT 0 | 1 if event touched a canary |
| `pid` | INT | NULLABLE | Originating process ID (if resolvable) |
| `process_name` | VARCHAR(255) | NULLABLE | Executable name (e.g. `python.exe`) |
| `executable_path` | VARCHAR(500) | NULLABLE | Absolute path to binary |
| `process_attribution_status` | VARCHAR(50) | DEFAULT 'UNRESOLVED' | `CONFIRMED`, `INFERRED`, `UNRESOLVED` |
| `risk_contribution` | INT | DEFAULT 0 | Immediate risk points awarded |

### 3.4 `alerts`
Stores structured alerts generated when composite risk exceeds the configured threshold.

| Column | Data Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `alert_id` | VARCHAR(64) | PRIMARY KEY | Unique alert identifier (e.g. `ALT-2026-0001`) |
| `event_id` | BIGINT | FK -> `file_events` (NULLABLE) | Triggering event reference |
| `timestamp` | DATETIME(3) | NOT NULL | Alert generation timestamp |
| `affected_file` | VARCHAR(500) | NOT NULL | Primary target path |
| `decoy_id` | VARCHAR(64) | FK -> `decoys` (NULLABLE) | Touched canary reference |
| `risk_score` | INT | NOT NULL | Calculated composite score (e.g. 103) |
| `risk_level` | VARCHAR(20) | NOT NULL | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `configured_threshold`| INT | NOT NULL | Threshold at detection time (e.g. 70) |
| `honeytoken_weight` | INT | NOT NULL | Points from decoy hit (40) |
| `file_activity_weight` | INT | NOT NULL | Points from rapid modification (25) |
| `rename_extension_weight` | INT | NOT NULL | Points from extension change (20) |
| `entropy_weight` | INT | NOT NULL | Points from high Shannon entropy (18) |
| `matched_indicators` | TEXT | NOT NULL | JSON array of human-readable matched indicators |
| `pid` | INT | NULLABLE | Attributed process ID |
| `process_name` | VARCHAR(255) | NULLABLE | Attributed process name |
| `executable_path` | VARCHAR(500) | NULLABLE | Executable location |
| `alert_status` | VARCHAR(30) | DEFAULT 'ACTIVE' | `ACTIVE`, `ACKNOWLEDGED`, `RESOLVED`, `DISMISSED` |

### 3.5 `incidents`
Maintains verified security incidents and containment status.

| Column | Data Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `internal_id` | BIGINT | AUTO_INCREMENT, PK | Internal database surrogate key |
| `incident_id` | VARCHAR(64) | NOT NULL, UNIQUE | Canonical incident identifier (e.g. `INC-2026-0001`) |
| `alert_id` | VARCHAR(64) | FK -> `alerts` (NULLABLE) | Associated alert ID |
| `detected_at` | DATETIME(3) | NOT NULL | Detection timestamp |
| `affected_file` | VARCHAR(500) | NOT NULL | Primary file targeted |
| `decoy_id` | VARCHAR(64) | FK -> `decoys` (NULLABLE) | Associated decoy token |
| `risk_score` | INT | NOT NULL | Evaluated risk score |
| `risk_level` | VARCHAR(20) | NOT NULL | Assigned severity |
| `matched_indicators` | TEXT | NOT NULL | Detailed indicator summary |
| `containment_status` | VARCHAR(50) | DEFAULT 'PENDING' | `CONTAINED`, `ISOLATED`, `FAILED`, `LOG_ONLY` |
| `files_modified_before_response` | INT | DEFAULT 0 | Count of files modified prior to containment |
| `files_modified_after_response` | INT | DEFAULT 0 | Count of files modified post-containment (0 if successful) |
| `detection_latency_ms` | DOUBLE | DEFAULT 0.0 | Indicator-to-alert latency in milliseconds |
| `cpu_usage` | DOUBLE | DEFAULT 0.0 | Host CPU percentage at incident time |
| `ram_usage` | DOUBLE | DEFAULT 0.0 | Memory footprint in MB |

### 3.6 `response_actions`
Provides an immutable audit record of every containment attempt.

| Column | Data Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `response_id` | BIGINT | AUTO_INCREMENT, PK | Unique response sequence ID |
| `incident_id` | VARCHAR(64) | FK -> `incidents` | Target incident reference |
| `action_type` | VARCHAR(50) | NOT NULL | `TERMINATE_PROCESS`, `ISOLATE_PROCESS`, `QUARANTINE`, `LOG_ONLY` |
| `requested_at` | DATETIME(3) | NOT NULL | Containment request timestamp |
| `executed_at` | DATETIME(3) | NULLABLE | Execution completion timestamp |
| `target_pid` | INT | NULLABLE | Process ID targeted for termination |
| `operator_confirmation` | TINYINT(1) | DEFAULT 0 | Whether human operator confirmed action |
| `result` | VARCHAR(100) | NOT NULL | Plain-text outcome description |
| `success` | TINYINT(1) | DEFAULT 0 | 1 if containment achieved |
| `error_message` | TEXT | NULLABLE | Error description if operation failed |

### 3.7 `benchmark_runs` & `benchmark_measurements`
Captures empirical evaluation data across multiple trials of test cases TC01–TC07.

---

## 4. Security & SQL Injection Prevention
All database queries within HoneyGuard are executed strictly through **parameterized queries** via PyMySQL. Raw SQL string concatenation is strictly prohibited across the entire codebase.

Example from `DirectoryRepository`:
```python
query = """
    INSERT INTO protected_directories (directory_path, display_name, monitoring_enabled)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE display_name = VALUES(display_name);
"""
cursor.execute(query, (path, display_name, int(monitoring_enabled)))
```
This guarantees that malicious paths containing single quotes, semicolons, or SQL injection payloads (e.g. `' OR '1'='1`) are safely treated as literal string values.
