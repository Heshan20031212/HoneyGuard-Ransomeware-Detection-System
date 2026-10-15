"""
Unit Tests: Containment Logic and Process Safety Rules
"""

import os
from honeyguard.response.containment import ContainmentManager


def test_containment_allowlist():
    mgr = ContainmentManager()

    # Self PID must be allowlisted
    assert mgr.is_process_allowlisted(os.getpid(), "python.exe") is True

    # Critical OS processes must be allowlisted
    assert mgr.is_process_allowlisted(4, "System") is True
    assert mgr.is_process_allowlisted(99999, "explorer.exe") is True
    assert mgr.is_process_allowlisted(99998, "svchost.exe") is True


def test_unresolved_pid_safeguard():
    mgr = ContainmentManager()
    alert = {
        "alert_id": "ALT-TEST-001",
        "affected_file": "C:\\demo\\file.txt",
        "pid": None,
        "process_name": None,
        "risk_score": 90,
        "risk_level": "CRITICAL"
    }

    # Attempting termination on UNRESOLVED PID must be refused safely
    res = mgr.execute_containment(alert, action_type="TERMINATE_PROCESS")
    assert res["success"] is False
    assert res["status"] == "UNRESOLVED_PID"
