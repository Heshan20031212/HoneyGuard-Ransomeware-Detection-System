"""
HoneyGuard Input and Configuration Validators
"""

import os
import re
from pathlib import Path
from typing import Dict, Any


def validate_directory_path(path: str) -> bool:
    """Check if directory path exists and is readable."""
    if not path or not isinstance(path, (str, Path)):
        return False
    p = Path(path)
    return p.exists() and p.is_dir()


def validate_thresholds(thresholds: Dict[str, Any]) -> bool:
    """Validate threshold dictionary structure and ranges."""
    required_keys = ["risk_threshold", "weights"]
    for k in required_keys:
        if k not in thresholds:
            return False

    weights = thresholds.get("weights", {})
    req_weights = [
        "honeytoken_interaction",
        "high_frequency_file_activity",
        "rename_extension_change",
        "content_entropy_change"
    ]
    for rw in req_weights:
        if rw not in weights:
            return False
        val = weights[rw]
        if not isinstance(val, (int, float)) or val < 0 or val > 100:
            return False

    rt = thresholds.get("risk_threshold", 0)
    if not isinstance(rt, (int, float)) or rt < 1 or rt > 500:
        return False

    return True


def sanitize_incident_id(incident_id: str) -> bool:
    """Ensure incident ID conforms to standard format INC-YYYY-NNNN."""
    if not incident_id or not isinstance(incident_id, str):
        return False
    return bool(re.match(r"^INC-\d{4}-\d{4,8}$", incident_id))
