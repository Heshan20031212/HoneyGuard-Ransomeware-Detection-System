# HoneyGuard Testing & Validation Specification
**Module:** IE3092 — Information Security Project  
**Institution:** Sri Lanka Institute of Information Technology (SLIIT)  
**Group:** Group 15  

---

## 1. Testing Methodology Overview
HoneyGuard employs a multi-tiered testing strategy comprising:
1. **Unit Testing:** Individual verification of decoy generators, SHA-256 baselines, Shannon entropy calculations, weighted risk scoring formulas, and containment allowlists.
2. **Database Integration Testing (DB-TC01 to DB-TC10):** Validation of MySQL ACID transactions, foreign-key constraints, parameterized query injection resistance, and relational integrity.
3. **End-to-End Pipeline Testing:** Verification of the complete closed loop from filesystem event to containment execution and incident logging.
4. **Empirical Scenario Testing (TC01 to TC07):** Reproducible scenario tests evaluated across 5 repeated trials to measure detection time, accuracy, resource usage, and false-positive rates.

---

## 2. Test Execution Summary

**Execution Command:**
```powershell
pytest -v
```

**Results:**
- **Total Tests Collected:** 30
- **Total Passed:** 30 (100% Pass Rate)
- **Execution Time:** ~7.1 seconds
- **Failures / Errors:** 0

---

## 3. Detailed Scenario Test Matrix (TC01–TC07)

| Test ID | Scenario Name | Workload Description | Expected Result | Actual Result | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC01** | Normal Document Editing | Legitimate user modifies normal files at standard desktop typing cadence. | No high-risk alert triggered; FPR = 0.0%. | Zero false alerts triggered. Risk score remained at 0. | **PASS** |
| **TC02** | Normal Bulk Copying | User copies 8 business files into protected directory simultaneously. | High write rate accepted without false ransomware classification. | 8 files copied; no decoy touched; zero false alerts. | **PASS** |
| **TC03** | Single Decoy Access | User or benign program opens/edits a single canary honeytoken file. | Suspicious event logged; Score = 40 (remains below alert threshold 70). | Event logged in MySQL with Score = 40. No false containment. | **PASS** |
| **TC04** | Rapid Mass Modification | Automated script modifies 12 synthetic files within 2 seconds. | High-frequency modification indicator triggers; latency recorded. | High-frequency indicator fired (12 files in window). Latency: 147.7 ms. | **PASS** |
| **TC05** | Repeated Rename / Extension Changes | Script renames 10 synthetic files with `.locked` extension. | Suspicious extension change detected; risk elevated. | Extension indicator fired on all 10 renames. Latency: 184.7 ms. | **PASS** |
| **TC06** | Controlled Encryption Simulation | Safe simulator replaces file bytes with random high-entropy ciphertext and touches canary. | Composite score $\ge 70$, verified alert raised, process contained. | Composite score reached 103 (HIGH RISK). Containment executed. Damage reduction: 81.8%. | **PASS** |
| **TC07** | Benign High-I/O Workload | Heavy read/write cache operations on temporary non-decoy files. | Measure false-positive rate under stress. | Zero false alerts generated; false-positive rate = 0.0%. | **PASS** |

---

## 4. Database Integration Tests (DB-TC01 to DB-TC10)

| Test ID | Description | Tested Component | Result |
| :--- | :--- | :--- | :--- |
| **DB-TC01** | MySQL connection and schema verification. | `DatabaseManager`, `honeyguard_db` | **PASS** |
| **DB-TC02** | Decoy insertion and retrieval with SHA-256 baseline. | `DecoyRepository` | **PASS** |
| **DB-TC03** | Filesystem event insertion with process attribution status. | `EventRepository` | **PASS** |
| **DB-TC04** | Structured alert insertion with weight breakdown. | `AlertRepository` | **PASS** |
| **DB-TC05** | ACID transaction integrity across incident and response actions. | `IncidentRepository`, `ResponseActionRepository` | **PASS** |
| **DB-TC06** | Foreign-key constraints preventing orphan child records. | MySQL Foreign Keys | **PASS** |
| **DB-TC07** | JSON & CSV export integrity matching database records. | `IncidentLogsView` Export Engine | **PASS** |
| **DB-TC08** | Graceful degradation and fallback upon database timeout. | `DatabaseManager.is_connected()` | **PASS** |
| **DB-TC09** | Parameterized query resistance against SQL injection strings. | `DirectoryRepository.get_by_path()` | **PASS** |
| **DB-TC10** | phpMyAdmin relational visual verification. | phpMyAdmin UI Inspection | **PASS** |

---

## 5. Unit Test Suite

- `test_generate_txt_decoy`: Verifies creation and readability of plain text canary.
- `test_generate_pdf_decoy`: Verifies valid `%PDF-1.4` binary header and page objects.
- `test_generate_docx_decoy`: Verifies formatted paragraphs and headers via `python-docx`.
- `test_generate_xlsx_decoy`: Verifies spreadsheet styling and cells via `xlsxwriter`.
- `test_integrity_hash_and_tamper`: Verifies baseline hash and detection of `INTACT`, `MODIFIED`, and `DELETED` states.
- `test_entropy_plain_text`: Asserts plaintext entropy falls within $3.0 - 5.5$ bits/byte.
- `test_entropy_random_ciphertext`: Asserts encrypted/random data exceeds $7.8$ bits/byte.
- `test_risk_score_calculation`: Verifies composite score addition ($40 + 25 + 20 + 18 = 103$).
- `test_containment_allowlist`: Asserts self PID, Python, and system processes cannot be terminated.
- `test_unresolved_pid_safeguard`: Enforces refusal to kill arbitrary processes when attribution is unresolved.
- `test_sandbox_path_validation`: Guarantees simulator operations are strictly rejected outside `demo_workspace/`.
