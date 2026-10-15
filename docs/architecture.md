# HoneyGuard System Architecture Document
**Module:** IE3092 — Information Security Project  
**Institution:** Sri Lanka Institute of Information Technology (SLIIT)  
**Group:** Group 15  

---

## 1. Closed-Loop Cyber Defence Lifecycle

HoneyGuard implements an active, closed detection-and-response loop rather than a passive alert-only pipeline. Every confirmed incident updates forensic records, adjusts risk posture, and reinforces decoy canaries:

```
[Decoy Generation] 
        ↓
[Protected Directories] 
        ↓
[Real-Time File Monitoring (watchdog)] 
        ↓
[Context Enrichment & Process Attribution (psutil)] 
        ↓
[Behavioural Analysis & Shannon Entropy] 
        ↓
[Weighted Risk Scoring Engine] 
        ↓
[Detection & Alert Dispatch] 
        ↓
[Controlled Response & Process Containment] 
        ↓
[Incident Logging & MySQL Persistence (honeyguard_db)] 
        ↓
[Feedback Loop / Threshold & Decoy Registry Improvement]
```

---

## 2. Five-Stage Technical Execution Pipeline

The processing pipeline traces an OS-level filesystem modification through to auditable process containment across five modular stages:

### Stage 1 — Capture (OS-Level Event Interception)
- **Module:** `src/honeyguard/file_monitoring/watcher.py`
- Utilizes the cross-platform `watchdog` library subscribing directly to Windows `ReadDirectoryChangesW` kernel notifications.
- Intercepts raw file operations: `CREATE`, `MODIFY`, `WRITE`, `RENAME`, `MOVE`, `DELETE`.
- Completely non-blocking: dispatches immediately onto an in-memory thread-safe `EventBus`.

### Stage 2 — Enrichment (Context & Process Association)
- **Module:** `src/honeyguard/file_monitoring/event_bus.py` & `process_resolver.py`
- Appends high-resolution timestamps.
- Performs real-time lookup against `decoys` in MySQL to tag canary interactions (`is_decoy = True`).
- Interrogates `psutil` telemetry to correlate originating process ID (PID), executable name, and binary path.
- **Academic Integrity Guard:** If PID cannot be definitively verified, `process_attribution_status` is explicitly recorded as `UNRESOLVED` to prevent arbitrary process disruption.

### Stage 3 — Scoring (Behavioural Correlation & Risk Calculation)
- **Module:** `src/honeyguard/detection/indicators.py` & `risk_engine.py`
- Evaluates four independent behavioural indicator families:
  1. **Honeytoken Interaction:** Touched canary file (Default weight: 40).
  2. **High-Frequency Modification:** Sliding time window tracking file modifications (Default weight: 25).
  3. **Rename / Extension Change:** Rapid renaming or matching known ransomware extensions like `.locked`, `.crypto`, `.crypted` (Default weight: 20).
  4. **Content / Entropy Change:** Sudden jump in Shannon entropy toward 8.0 bits/byte (Default weight: 18).
- Formula:
  $$\text{Risk Score} = W_{\text{honeytoken}} + W_{\text{activity}} + W_{\text{rename}} + W_{\text{entropy}}$$
  *Example maximum composite score:* $40 + 25 + 20 + 18 = 103$.

### Stage 4 — Alerting (Threshold Evaluation)
- **Module:** `src/honeyguard/detection/alert_manager.py`
- Compares composite Risk Score against configured threshold (Default: 70).
- If score $\ge 70$, raises a verified alert classified as `HIGH` (70–89) or `CRITICAL` (90+).
- Persists structured alert into MySQL `alerts` table and notifies UI subscribers.

### Stage 5 — Containment (Controlled Response & Forensics)
- **Module:** `src/honeyguard/response/containment.py` & `forensics.py`
- **Safeguard Check:** Evaluates target PID against critical process allowlist (protecting HoneyGuard, Python, Windows Explorer, Svchost).
- **Attribution Enforcement:** If PID is `UNRESOLVED`, refuses arbitrary termination and defaults safely to `LOG_ONLY` or quarantine.
- If verified hostile process, issues graceful `terminate()` followed by `kill()` if necessary.
- Captures forensic snapshot (CPU, memory, command line) and commits atomic incident record to MySQL.

---

## 3. Data Flow Diagram (DFD Level 1)

```
                       ┌─────────────────────────┐
                       │   Ransomware Process    │
                       └────────────┬────────────┘
                                    │
                         (1) File Modification / Rename
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │             P2: Capture File-System Events             │
       └────────────────────────────┬───────────────────────────┘
                                    │ Raw Event
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │             P3: Compute Risk Score & Alert             │
       │    (Indicators: Decoy, Frequency, Extension, Entropy)   │
       └────────────────────────────┬───────────────────────────┘
                                    │ Verified Alert (Score >= 70)
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │         P4: Contain Process & Record Forensics         │
       └──────┬─────────────────────┬────────────────────┬──────┘
              │                     │                    │
              ▼ (Terminate PID)     ▼ (Incident Log)     ▼ (Audit Log)
   ┌──────────────────────┐   ┌───────────────┐   ┌────────────────┐
   │ Hostile Process Node │   │ D3: Incidents │   │ D4: Audit Logs │
   │   (demo_workspace)   │   │  (MySQL 8.0)  │   │  (MySQL 8.0)   │
   └──────────────────────┘   └───────────────┘   └────────────────┘
```

---

## 4. CIA Triad Contribution Matrix

| Principle | Technical Problem Solved | HoneyGuard Mechanism |
| :--- | :--- | :--- |
| **Confidentiality** | Adversary attempts unauthorized reconnaissance or file discovery across shared corporate storage. | Deliberately planted synthetic honeytokens (`Employee_Salary_2026.xlsx`, `Legal_Agreement_Draft.pdf`) act as tripwires. Unauthorized access is detected immediately before mass exfiltration or tampering occurs. |
| **Integrity** | Ransomware executes bulk encryption, unauthorized renaming, or malicious file overwriting. | Real-time watchdog observation and Shannon entropy analysis detect high-entropy ciphertext generation, triggering instant alerts. |
| **Availability** | Ransomware permanently locks access to critical business documents. | Controlled process termination halts the hostile encryption loop at the earliest canary interaction, saving 80%+ of protected files and preventing complete operational outage. |
