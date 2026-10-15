# HoneyGuard Academic Final Report Guidance & Evidence Dossier
**Module:** IE3092 — Information Security Project  
**Target Word Count:** ~7,500 words  
**Institution:** Sri Lanka Institute of Information Technology (SLIIT)  
**Group:** Group 15  

---

## 1. Executive Summary & Research Gap Alignment
HoneyGuard addresses the structural vulnerability of signature-based endpoint antivirus solutions against zero-day and polymorphic ransomware families. By planting realistic, context-appropriate canary decoys (`PDF`, `DOCX`, `XLSX`, `TXT`) in high-value shared directories and combining real-time filesystem observation (`watchdog`) with behavioral correlation (Shannon entropy, sliding-window frequency, extension renaming) and controlled process mitigation (`psutil`), HoneyGuard establishes a lightweight, closed-loop cyber defense layer.

---

## 2. Answers to Approved Research Questions Grounded in Empirical Evidence

### RQ1: How effectively can honeytokens identify ransomware-like file activity at an early stage?
- **Finding:** In all controlled simulations (TC03, TC06), interaction with canary honeytokens reliably generated high-confidence detection signals at the very outset of filesystem traversals.
- **Evidence:** Mean detection latency was measured at **457.23 ms** in composite encryption simulations (TC06) and **147.68 ms** during rapid mass modifications (TC04). Because canaries have zero legitimate operational purpose, they provide near-zero false-positive early tripwires before deeper directory structures are encrypted.

### RQ2: How accurately can HoneyGuard distinguish ransomware-like behaviour from legitimate file activity?
- **Finding:** HoneyGuard achieved a **100% detection rate** on attack simulations while maintaining a **0.0% False Positive Rate (FPR)** across benign scenarios (TC01 Normal Document Editing, TC02 Bulk File Copying, and TC07 Benign High-I/O Caching).
- **Evidence:** Benign high-volume file operations did not touch honeytokens, did not introduce suspicious ransomware extensions (`.locked`), and maintained low Shannon entropy ($\sim 4.2$ bits/byte), keeping composite risk scores comfortably below the alert threshold (70).

### RQ3: What detection time and resource overhead are produced by the proposed approach?
- **Finding:** The system operates with minimal endpoint footprint.
- **Evidence:**
  - **Detection Time:** $147.7\text{ ms}$ (Mass Modification) to $457.2\text{ ms}$ (High-Entropy Encryption).
  - **CPU Utilization:** Ranged between **0.0%** (idle/monitoring) and **0.62%** peak across benign and attack workloads.
  - **RAM Overhead:** Constant resident memory footprint of **~84.8 MB**, comfortably satisfying endpoint constraints.

### RQ4: How effectively can the response mechanism reduce further file modification during controlled simulations?
- **Finding:** Controlled process termination successfully halted the encryption loop immediately upon alert verification.
- **Evidence:** In multi-file encryption benchmarks (TC06), the simulator compromised only 2 files before process containment was executed, saving 9 of 11 files at risk and yielding a **81.82% damage reduction / containment effectiveness**.

---

## 3. Empirical Summary Statistics Table (For Chapter 5: Evaluation)

| Test Case | Scenario Description | Trials | Mean Latency (ms) | Mean CPU (%) | Mean RAM (MB) | False Positive Rate | Damage Reduction (%) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **TC01** | Normal Document Editing | 5 | 0.0 | 0.00 | 84.79 | 0.0% | N/A | **PASS** |
| **TC02** | Normal Bulk Copying | 5 | N/A | 0.62 | 84.79 | 0.0% | N/A | **PASS** |
| **TC03** | Single Decoy Access | 5 | N/A | 0.00 | 84.79 | 0.0% | N/A | **PASS** |
| **TC04** | Rapid Mass Modification | 5 | 147.68 | 0.00 | 84.80 | 0.0% | N/A | **PASS** |
| **TC05** | Repeated Extension Changes | 5 | 184.73 | 0.00 | 84.80 | 0.0% | N/A | **PASS** |
| **TC06** | Encryption Simulation + Canary | 5 | 457.23 | 0.00 | 84.92 | 0.0% | **81.82%** | **PASS** |
| **TC07** | Benign High-I/O Workload | 5 | N/A | 0.00 | 84.92 | 0.0% | N/A | **PASS** |

---

## 4. Cybersecurity Standards Alignment

### 4.1 NIST SP 800-61 Rev. 2 Mapping
- **Preparation:** Deployment of decoy assets and registration of cryptographic SHA-256 baselines in `decoys`.
- **Detection & Analysis:** Real-time event monitoring, Shannon entropy calculation, and weighted risk evaluation.
- **Containment & Recovery:** Controlled process termination, directory isolation, and forensic memory capture.
- **Post-Incident Activity:** Persistent incident logging in MySQL, timeline queryability, and JSON/CSV forensic reporting.

### 4.2 MITRE ATT&CK Mapping
- **T1486 (Data Encrypted for Impact):** Targeted by Shannon entropy thresholding and extension modification tracking.
- **T1083 (File and Directory Discovery):** Detected when adversarial discovery routines first access canary files.
- **T1490 (Inhibit System Recovery):** Mitigated by high-frequency modification alarms and automated containment.

---

## 5. Report Figures & Artifact References
When compiling the final report document, embed the genuine generated figures from `docs/evidence/10_benchmarking/`:
1. `detection_time_by_scenario.png`: Compares indicator-to-alert latency across test scenarios.
2. `resource_usage_overhead.png`: Illustrates endpoint CPU (%) and RAM (MB) footprint.
3. `containment_effectiveness.png`: Illustrates 81.8% damage reduction achieved by early process mitigation.
