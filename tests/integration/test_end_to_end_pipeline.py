"""
Integration Test: End-to-End Closed-Loop Pipeline
Tests: Decoy Generation -> Event -> Indicators -> Risk Engine -> Alert -> Containment -> MySQL.
"""

from datetime import datetime
from pathlib import Path
from honeyguard.database.repositories import DirectoryRepository, DecoyRepository, IncidentRepository
from honeyguard.decoy_generation.registry import DecoyRegistry
from honeyguard.detection.alert_manager import AlertManager
from honeyguard.response.containment import ContainmentManager
from honeyguard.utils.paths import get_demo_workspace


def test_full_detection_and_containment_pipeline():
    workspace = get_demo_workspace() / "Finance"
    workspace.mkdir(parents=True, exist_ok=True)

    # 1. Register Directory
    dir_id = DirectoryRepository.add_directory(str(workspace), "Finance Test", True)

    # 2. Deploy Decoy
    decoy = DecoyRegistry.deploy_decoy(dir_id, "Pipeline_Canary.xlsx", "XLSX")
    assert decoy is not None

    # 3. Simulate Event
    alert_mgr = AlertManager()
    containment_mgr = ContainmentManager()

    # Composite ransomware-like event
    event = {
        "timestamp": datetime.now(),
        "event_type": "MODIFY",
        "source_path": decoy["absolute_path"],
        "destination_path": decoy["absolute_path"] + ".locked",
        "directory_id": dir_id,
        "decoy_id": decoy["decoy_id"],
        "is_decoy": True,
        "pid": 99999,  # Mock PID
        "process_name": "simulated_ransomware.exe"
    }

    # Force composite indicators
    indicators = {
        "honeytoken_interaction": True,
        "high_frequency_file_activity": True,
        "rename_extension_change": True,
        "content_entropy_change": True,
        "details": {"file_entropy": 7.8, "target_extension": ".locked"}
    }
    risk_res = alert_mgr.risk_engine.evaluate_risk(indicators)
    assert risk_res["risk_score"] == 103
    assert risk_res["is_alert"] is True

    # Build alert
    alert = {
        "alert_id": f"ALT-PIPE-{datetime.now().strftime('%H%M%S')}",
        "timestamp": datetime.now(),
        "affected_file": decoy["absolute_path"],
        "decoy_id": decoy["decoy_id"],
        "risk_score": risk_res["risk_score"],
        "risk_level": risk_res["risk_level"],
        "configured_threshold": 70,
        "honeytoken_weight": 40,
        "file_activity_weight": 25,
        "rename_extension_weight": 20,
        "entropy_weight": 18,
        "matched_indicators": risk_res["matched_indicators"],
        "pid": 99999,
        "process_name": "simulated_ransomware.exe"
    }

    # 4. Containment Execution (LOG_ONLY for non-existent mock PID)
    res = containment_mgr.execute_containment(alert, action_type="LOG_ONLY", operator_confirmed=True)
    assert res["incident_id"].startswith("INC-")
    assert res["status"] == "LOG_ONLY"

    # 5. Verify MySQL Persistence
    inc = IncidentRepository.get_by_id(res["incident_id"])
    assert inc is not None
    assert inc["risk_score"] == 103
