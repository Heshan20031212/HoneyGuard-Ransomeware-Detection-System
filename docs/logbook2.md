# HoneyGuard Development Logbook 2 (Phase 6 & Phase 7)
**Module:** IE3092 — Information Security Project  
**Institution:** Sri Lanka Institute of Information Technology (SLIIT)  
**Project:** HoneyGuard — Honeytoken-Based Ransomware Detection and Prevention System  
**Group:** Group 15  

### Team Roster & Roles
- **M1:** DISSANAYAKE D M H W (IT23711082) — Project Coordination, Requirements Traceability, Documentation
- **M2:** Heshan S.H.H (IT23656024) — Decoy Generation, Filesystem Watcher, Directory Management
- **M3:** KAIF M.N.M (IT23631342) — Detection Engine, Entropy Calculation, Risk Scoring, Containment
- **M4:** Imsara S.A.L (IT23571648) — Database Engineering (MySQL/phpMyAdmin), Testing, Benchmarking

---

## Logbook Entries (Post-Specification Implementation & Validation)

| Date | Duration | Member / Role | Task | Component | Technical Work Performed | Output / Deliverable | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **08 Sep 2026** | 3.5 hrs | All (M1 lead) | Architecture Review & Refinement Planning | Architecture | Evaluated SQLite vs MySQL trade-offs; approved migration to MySQL 8.0 with phpMyAdmin for enterprise auditability and normalized relational integrity. | Architecture refinement decision record | **Completed** |
| **10 Sep 2026** | 4.0 hrs | M4 (Lead), M1 | MySQL Database Schema Design | Database | Designed normalized 10-table relational schema (`honeyguard_db.sql`) in 3NF with foreign keys, utf8mb4 collation, and performance indexes. | `database/honeyguard_db.sql` | **Completed** |
| **12 Sep 2026** | 3.5 hrs | M4 | Database Access Layer Implementation | Database Layer | Implemented `DatabaseManager` using PyMySQL, parameterized query handlers, and ACID transaction context manager. | `src/honeyguard/database/connection.py`, `repositories.py` | **Completed** |
| **14 Sep 2026** | 4.0 hrs | M2 | Decoy Generator Development | Decoy Layer | Built multi-format synthetic decoy generator supporting PDF (pure binary 1.4 syntax), DOCX (`python-docx`), XLSX (`xlsxwriter`), and TXT. | `src/honeyguard/decoy_generation/generator.py`, `templates.py` | **Completed** |
| **16 Sep 2026** | 3.0 hrs | M2 | Cryptographic Baseline & Integrity Verifier | Decoy Layer | Implemented SHA-256 baseline hashing and tamper verifier distinguishing `INTACT`, `ACCESSED`, `MODIFIED`, and `DELETED` status. | `src/honeyguard/decoy_generation/integrity.py`, `registry.py` | **Completed** |
| **18 Sep 2026** | 4.0 hrs | M2 | Watchdog Filesystem Watcher & Event Bus | Monitoring Layer | Built `FileSystemWatcher` wrapping watchdog observer and non-blocking `EventBus` with thread-safe queue dispatch and MySQL event persistence. | `src/honeyguard/file_monitoring/watcher.py`, `event_bus.py` | **Completed** |
| **20 Sep 2026** | 3.5 hrs | M2, M3 | Process Attribution Telemetry | Monitoring Layer | Developed `resolve_process_for_event()` utilizing `psutil`; enforced academic rule marking unresolvable telemetry as `UNRESOLVED` to prevent arbitrary process termination. | `src/honeyguard/file_monitoring/process_resolver.py` | **Completed** |
| **22 Sep 2026** | 4.0 hrs | M3 | Shannon Entropy & Indicator Evaluator | Detection Layer | Implemented Shannon entropy calculation formula ($0.0 - 8.0$ bits/byte) and 4-family behavioural indicator evaluator with sliding time window. | `src/honeyguard/detection/entropy.py`, `indicators.py` | **Completed** |
| **24 Sep 2026** | 3.5 hrs | M3 | Weighted Risk Scoring Engine | Detection Layer | Built `RiskEngine` calculating composite score ($W_{\text{decoy}} + W_{\text{freq}} + W_{\text{rename}} + W_{\text{entropy}}$) and dynamic threshold evaluation. | `src/honeyguard/detection/risk_engine.py`, `alert_manager.py` | **Completed** |
| **26 Sep 2026** | 4.0 hrs | M3 | Controlled Response & Containment Module | Response Layer | Implemented `ContainmentManager` with critical process allowlist, confirmation modal enforcement, `psutil` process termination, and forensic memory snapshots. | `src/honeyguard/response/containment.py`, `forensics.py`, `quarantine.py` | **Completed** |
| **27 Sep 2026** | 4.5 hrs | M1, M3 | Safe Ransomware-Like Simulator | Testing Layer | Built harmless test simulator restricted strictly to `demo_workspace/`; implemented mass modification, extension renaming, and high-entropy payload simulation. | `src/honeyguard/analytics/simulator.py` | **Completed** |
| **28 Sep 2026** | 5.0 hrs | M1, M2 | Desktop GUI Development (Part 1) | GUI Layer | Built SOC dark-themed management interface in Tkinter/TTK matching wireframes: Left Navigation Rail, Dashboard KPI cards (Fig 4), and Decoy Manager (Fig 5). | `src/honeyguard/ui/main_window.py`, `dashboard.py`, `decoy_manager.py` | **Completed** |
| **29 Sep 2026** | 4.5 hrs | M1, M3 | Desktop GUI Development (Part 2) | GUI Layer | Implemented Detection & Alert window with score breakdown table (Fig 6), Live File Monitor, Incident Forensics Log (Fig 7), and Settings view. | `src/honeyguard/ui/alerts.py`, `file_monitor.py`, `incident_logs.py`, `settings.py` | **Completed** |
| **30 Sep 2026** | 4.0 hrs | M4 | Database Integration & Automated Unit Testing | QA / Testing | Authoring and execution of DB-TC01 to DB-TC10 database integration tests and unit tests for decoy generation, indicators, and risk scoring. | `tests/unit/`, `tests/integration/test_database.py` (30 tests passing) | **Completed** |
| **01 Oct 2026** | 4.5 hrs | M4 (Lead), All | Empirical 5-Trial Evaluation & Benchmarking | Benchmarking | Executed full 35-trial evaluation suite across TC01–TC07; captured CPU/RAM telemetry via `psutil`, logged 140+ measurements to MySQL, generated CSVs and charts. | `data/benchmark_results/`, `docs/evidence/10_benchmarking/` | **Completed** |
| **01 Oct 2026** | 3.5 hrs | All | Final Documentation, Traceability & Validation | Documentation | Prepared phpMyAdmin guide, user manual, architecture specification, requirements traceability matrix, and README. | `README.md`, `docs/*.md` | **Completed** |

---

### Total Documented Development Duration
- **Logbook 1 (Proposal & Specification Phase):** ~32.0 Hours
- **Logbook 2 (Core Implementation & Evaluation Phase):** ~59.0 Hours
- **Cumulative Development Duration:** **91.0 Hours** (Satisfies the 30-hour minimum requirement stipulated in IE3092 Assessment Guidelines).
