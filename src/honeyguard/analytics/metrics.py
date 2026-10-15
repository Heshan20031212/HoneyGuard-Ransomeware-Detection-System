"""
HoneyGuard Evaluation Metrics Calculator
Implements standard formulas for detection latency, accuracy, false-positive rate, and containment effectiveness.
"""

from datetime import datetime
from typing import Dict, Any


def calculate_detection_time_ms(indicator_time: datetime, alert_time: datetime) -> float:
    """
    Calculate detection latency in milliseconds:
    Detection Time = (Alert Timestamp - Indicator Timestamp) in ms
    """
    delta = (alert_time - indicator_time).total_seconds() * 1000.0
    return max(0.0, round(delta, 2))


def calculate_detection_rate(correct_detections: int, total_attack_scenarios: int) -> float:
    """
    Calculate detection accuracy percentage:
    Detection Rate = (Correct Detections / Total Attack Tests) * 100
    """
    if total_attack_scenarios == 0:
        return 0.0
    return round((correct_detections / total_attack_scenarios) * 100.0, 2)


def calculate_false_positive_rate(false_alerts: int, total_benign_runs: int) -> float:
    """
    Calculate false-positive rate percentage:
    FPR = (False Alerts / Total Benign Executions) * 100
    """
    if total_benign_runs == 0:
        return 0.0
    return round((false_alerts / total_benign_runs) * 100.0, 2)


def calculate_containment_effectiveness(
    files_modified_before: int,
    files_modified_after: int,
    total_files_at_risk: int
) -> float:
    """
    Measure damage mitigation percentage:
    Effectiveness = ((Total At Risk - Total Modified) / Total At Risk) * 100
    """
    if total_files_at_risk <= 0:
        return 100.0
    total_modified = files_modified_before + files_modified_after
    protected = max(0, total_files_at_risk - total_modified)
    return round((protected / total_files_at_risk) * 100.0, 2)
