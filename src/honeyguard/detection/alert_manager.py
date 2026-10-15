"""
HoneyGuard Alert Manager
Coordinates indicator evaluation, risk calculation, MySQL persistence, and alert notifications.
"""

import time
import uuid
from datetime import datetime
from typing import Callable, List, Dict, Any, Optional

from honeyguard.database.repositories import AlertRepository, AuditLogRepository
from honeyguard.detection.indicators import IndicatorEvaluator
from honeyguard.detection.risk_engine import RiskEngine
from honeyguard.utils.logger import get_logger

logger = get_logger("HoneyGuard.AlertManager")


class AlertManager:
    """Evaluates incoming filesystem events and triggers structured alerts."""

    def __init__(self):
        self.evaluator = IndicatorEvaluator()
        self.risk_engine = RiskEngine()
        self._alert_subscribers: List[Callable[[Dict[str, Any]], None]] = []

    def subscribe(self, callback: Callable[[Dict[str, Any]], None]):
        """Register subscriber to receive verified alerts."""
        if callback not in self._alert_subscribers:
            self._alert_subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[Dict[str, Any]], None]):
        """Unregister alert subscriber."""
        if callback in self._alert_subscribers:
            self._alert_subscribers.remove(callback)

    def process_event(self, enriched_event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process an enriched event through indicators and risk engine.
        If threshold is breached, creates, persists, and broadcasts a verified alert.
        """
        self.risk_engine.reload_from_settings()

        # Step 1: Evaluate indicators
        indicators = self.evaluator.evaluate(enriched_event)

        # Step 2: Calculate risk score
        risk_result = self.risk_engine.evaluate_risk(indicators)

        # Update event's risk contribution
        enriched_event["risk_contribution"] = risk_result["risk_score"]

        # Step 3: Check if threshold exceeded
        if not risk_result["is_alert"]:
            return None

        # Build Alert Object
        alert_id = f"ALT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        affected_file = enriched_event.get("destination_path") or enriched_event.get("source_path", "UNKNOWN")

        alert = {
            "alert_id": alert_id,
            "event_id": enriched_event.get("event_id"),
            "timestamp": enriched_event.get("timestamp", datetime.now()),
            "affected_file": affected_file,
            "decoy_id": enriched_event.get("decoy_id"),
            "risk_score": risk_result["risk_score"],
            "risk_level": risk_result["risk_level"],
            "configured_threshold": risk_result["threshold"],
            "honeytoken_weight": risk_result["breakdown"]["honeytoken"],
            "file_activity_weight": risk_result["breakdown"]["file_activity"],
            "rename_extension_weight": risk_result["breakdown"]["rename_extension"],
            "entropy_weight": risk_result["breakdown"]["entropy"],
            "matched_indicators": risk_result["matched_indicators"],
            "pid": enriched_event.get("pid"),
            "process_name": enriched_event.get("process_name"),
            "executable_path": enriched_event.get("executable_path"),
            "alert_status": "ACTIVE"
        }

        # Persist Alert to MySQL
        try:
            AlertRepository.create_alert(
                alert_id=alert["alert_id"],
                timestamp=alert["timestamp"],
                affected_file=alert["affected_file"],
                risk_score=alert["risk_score"],
                risk_level=alert["risk_level"],
                configured_threshold=alert["configured_threshold"],
                honeytoken_weight=alert["honeytoken_weight"],
                file_activity_weight=alert["file_activity_weight"],
                rename_extension_weight=alert["rename_extension_weight"],
                entropy_weight=alert["entropy_weight"],
                matched_indicators=alert["matched_indicators"],
                event_id=alert.get("event_id"),
                decoy_id=alert.get("decoy_id"),
                pid=alert.get("pid"),
                process_name=alert.get("process_name"),
                executable_path=alert.get("executable_path"),
                alert_status="ACTIVE"
            )

            AuditLogRepository.log(
                action="ALERT_RAISED",
                component="AlertManager",
                description=f"Raised {alert['risk_level']} alert ({alert['alert_id']}) with Risk Score {alert['risk_score']}",
                severity="CRITICAL",
                success=True
            )
            logger.warning(f"HIGH-RISK ALERT RAISED: {alert['alert_id']} (Score: {alert['risk_score']}) for {alert['affected_file']}")
        except Exception as exc:
            logger.error(f"Failed to persist alert in MySQL: {exc}")

        # Broadcast to alert subscribers
        for sub in list(self._alert_subscribers):
            try:
                sub(alert)
            except Exception as exc:
                logger.error(f"Error in alert callback: {exc}")

        return alert
