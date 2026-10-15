"""
HoneyGuard Weighted Risk Engine
Calculates composite ransomware risk score using configurable weights and thresholds.
Formula:
    Risk Score = Honeytoken Weight + File Activity Weight + Rename/Extension Weight + Content/Entropy Weight
"""

from typing import Dict, Any, List

from honeyguard.database.repositories import SettingsRepository
from honeyguard.utils.logger import get_logger

logger = get_logger("HoneyGuard.RiskEngine")


class RiskEngine:
    """Computes weighted risk scores from behavioural indicators."""

    def __init__(
        self,
        honeytoken_weight: int = 40,
        file_activity_weight: int = 25,
        rename_extension_weight: int = 20,
        entropy_weight: int = 18,
        threshold: int = 70
    ):
        self.honeytoken_weight = honeytoken_weight
        self.file_activity_weight = file_activity_weight
        self.rename_extension_weight = rename_extension_weight
        self.entropy_weight = entropy_weight
        self.threshold = threshold

    def reload_from_settings(self):
        """Synchronize weights and thresholds from MySQL application_settings table."""
        try:
            settings = SettingsRepository.get_all()
            if "honeytoken_weight" in settings:
                self.honeytoken_weight = int(settings["honeytoken_weight"])
            if "file_activity_weight" in settings:
                self.file_activity_weight = int(settings["file_activity_weight"])
            if "rename_extension_weight" in settings:
                self.rename_extension_weight = int(settings["rename_extension_weight"])
            if "entropy_weight" in settings:
                self.entropy_weight = int(settings["entropy_weight"])
            if "risk_threshold" in settings:
                self.threshold = int(settings["risk_threshold"])
        except Exception as exc:
            logger.debug(f"Could not reload settings from DB, keeping defaults: {exc}")

    def evaluate_risk(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate total weighted risk score and classify severity.
        """
        score = 0
        matched_list: List[str] = []
        breakdown = {
            "honeytoken": 0,
            "file_activity": 0,
            "rename_extension": 0,
            "entropy": 0
        }

        if indicators.get("honeytoken_interaction"):
            score += self.honeytoken_weight
            breakdown["honeytoken"] = self.honeytoken_weight
            matched_list.append("Decoy file accessed and modified outside baseline behaviour")

        if indicators.get("high_frequency_file_activity"):
            score += self.file_activity_weight
            breakdown["file_activity"] = self.file_activity_weight
            count = indicators.get("details", {}).get("unique_files_in_window", 0)
            matched_list.append(f"{count} files modified within 3 seconds (rapid mass modification)")

        if indicators.get("rename_extension_change"):
            score += self.rename_extension_weight
            breakdown["rename_extension"] = self.rename_extension_weight
            ext = indicators.get("details", {}).get("target_extension", "")
            matched_list.append(f"Suspicious extension change detected ({ext})")

        if indicators.get("content_entropy_change"):
            score += self.entropy_weight
            breakdown["entropy"] = self.entropy_weight
            ent = indicators.get("details", {}).get("file_entropy", 0.0)
            matched_list.append(f"High-entropy content consistent with encryption (Entropy: {ent:.2f}/8.0)")

        # Determine risk level
        if score >= 90:
            level = "CRITICAL"
        elif score >= self.threshold:
            level = "HIGH"
        elif score >= 40:
            level = "MEDIUM"
        else:
            level = "LOW"

        is_alert = score >= self.threshold

        return {
            "risk_score": score,
            "risk_level": level,
            "threshold": self.threshold,
            "is_alert": is_alert,
            "breakdown": breakdown,
            "matched_indicators": matched_list,
            "details": indicators.get("details", {})
        }
