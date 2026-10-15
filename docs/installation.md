# HoneyGuard Installation & Execution Guide
**Module:** IE3092 — Information Security Project  
**Institution:** Sri Lanka Institute of Information Technology (SLIIT)  
**Group:** Group 15  

---

## 1. System Requirements
- **Operating System:** Windows 10 / 11 (64-bit)
- **Python Version:** Python 3.12 or 3.13
- **Database Server:** Oracle MySQL Server 8.0+ or XAMPP (Apache + MariaDB/MySQL)
- **Web Browser:** Google Chrome / Edge (for phpMyAdmin)

---

## 2. Quick-Start Setup (Windows PowerShell)

### Step 1: Clone or Navigate to the Project Root
```powershell
cd "C:\Users\LENOVO\OneDrive\Desktop\HoneyGuard project folder"
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
pip install -e .
```

### Step 4: Configure Database Settings
Copy the template configuration to `.env`:
```powershell
cp .env.example .env
```
Ensure your `.env` contains the correct MySQL credentials:
```ini
DB_HOST=localhost
DB_PORT=3306
DB_NAME=honeyguard_db
DB_USER=root
DB_PASSWORD=root
AUTO_CONTAINMENT=0
LOG_LEVEL=INFO
```

### Step 5: Initialize the MySQL Database
You can initialize the database using either phpMyAdmin or the MySQL command-line client:
```powershell
Get-Content database\honeyguard_db.sql | & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -proot
```
*(Alternatively, import `database/honeyguard_db.sql` via phpMyAdmin at `http://localhost/phpmyadmin/` as detailed in `docs/phpmyadmin_setup.md`).*

### Step 6: Test Database Connectivity
```powershell
python scripts/test_database_connection.py
```
Output:
```
[+] SUCCESS: Connected to MySQL server.
[+] SCHEMA STATUS: HEALTHY (All 10 required tables verified).
```

### Step 7: Populate Initial Demo Environment
```powershell
python scripts/create_demo_environment.py
```
This automatically initializes `demo_workspace/` (`Finance`, `HR`, `Legal`, `General`) and seeds realistic synthetic canary tokens.

---

## 3. Running HoneyGuard

### Launch the Desktop Application:
```powershell
python -m honeyguard.main
```
Or execute:
```powershell
honeyguard
```
The HoneyGuard SOC dashboard will open, showing:
- Active Protection status (● Green)
- Live Database status (● CONNECTED)
- KPI cards reflecting active canaries and events
- Real-time file activity feed

---

## 4. Running the Safe Ransomware-Like Simulator

To demonstrate early-warning detection and containment safely in the authorized demo sandbox:

### Run Safe Simulator:
```powershell
python -m honeyguard.analytics.simulator --mode encrypt --count 10
```
- Operates **exclusively** inside `demo_workspace/Finance/`.
- Replaces disposable synthetic document content with high-entropy bytes.
- Touches a canary decoy.
- In HoneyGuard, notice:
  - Real-time event feed displays `[CANARY TOUCHED]`
  - Risk score reaches **103** (Threshold: 70)
  - Alert banner turns **RED** with `RANSOMWARE-LIKE ACTIVITY DETECTED`
  - Action modal allows verified termination or quarantine!

---

## 5. Running Automated Verification & Benchmarks

### Execute Pytest Suite (30 Tests):
```powershell
pytest -v
```

### Execute 5-Trial Benchmark Suite (TC01–TC07):
```powershell
python scripts/run_benchmarks.py
```
This runs 35 empirical trials, captures CPU/RAM telemetry, computes statistics, and generates charts in `data/benchmark_results/`.
