"""
Unit Tests: Path Containment and Setting Validators
"""

from pathlib import Path
from honeyguard.utils.paths import get_demo_workspace, is_safe_sandbox_path
from honeyguard.utils.validators import validate_thresholds, sanitize_incident_id


def test_sandbox_path_validation():
    demo = get_demo_workspace()
    safe_target = demo / "Finance" / "sample.docx"
    assert is_safe_sandbox_path(safe_target) is True

    unsafe_target = Path("C:/Windows/System32/calc.exe")
    assert is_safe_sandbox_path(unsafe_target) is False


def test_validate_thresholds():
    valid = {
        "risk_threshold": 70,
        "weights": {
            "honeytoken_interaction": 40,
            "high_frequency_file_activity": 25,
            "rename_extension_change": 20,
            "content_entropy_change": 18
        }
    }
    assert validate_thresholds(valid) is True

    invalid = {"risk_threshold": -10}
    assert validate_thresholds(invalid) is False


def test_sanitize_incident_id():
    assert sanitize_incident_id("INC-2026-0001") is True
    assert sanitize_incident_id("INVALID-ID-XYZ") is False
