"""
HoneyGuard Event Bus
Provides asynchronous event routing, enrichment, and background database logging.
"""

import queue
import threading
from datetime import datetime
from typing import Callable, List, Dict, Any, Optional

from honeyguard.database.repositories import EventRepository, DecoyRepository
from honeyguard.file_monitoring.process_resolver import resolve_process_for_event
from honeyguard.utils.logger import get_logger

logger = get_logger("HoneyGuard.EventBus")


class EventBus:
    """Thread-safe event bus that buffers, enriches, and dispatches file events."""

    _instance: Optional["EventBus"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._queue = queue.Queue(maxsize=10000)
            cls._instance._subscribers = []
            cls._instance._running = False
            cls._instance._worker_thread = None
        return cls._instance

    def subscribe(self, callback: Callable[[Dict[str, Any]], None]):
        """Register a callback subscriber to receive enriched file events."""
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[Dict[str, Any]], None]):
        """Unregister a callback subscriber."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def publish_raw_event(
        self,
        event_type: str,
        source_path: str,
        destination_path: Optional[str] = None,
        directory_id: Optional[int] = None,
        hint_pid: Optional[int] = None
    ):
        """Put raw watchdog event onto queue for non-blocking asynchronous processing."""
        raw = {
            "timestamp": datetime.now(),
            "event_type": event_type,
            "source_path": source_path,
            "destination_path": destination_path,
            "directory_id": directory_id,
            "hint_pid": hint_pid
        }
        try:
            self._queue.put_nowait(raw)
        except queue.Full:
            logger.warning("Event bus queue full, dropping event to prevent memory exhaust.")

    def start(self):
        """Start the background enrichment and dispatch worker thread."""
        if self._running:
            return
        self._running = True
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True, name="EventBusWorker")
        self._worker_thread.start()
        logger.info("EventBus background dispatcher started.")

    def stop(self):
        """Stop event processing cleanly."""
        self._running = False
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2.0)
        logger.info("EventBus stopped.")

    def _process_queue(self):
        """Worker loop that enriches events, logs to MySQL, and notifies subscribers."""
        while self._running:
            try:
                raw_event = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                enriched = self._enrich_event(raw_event)

                # Persist to MySQL
                try:
                    event_id = EventRepository.log_event(
                        timestamp=enriched["timestamp"],
                        event_type=enriched["event_type"],
                        source_path=enriched["source_path"],
                        destination_path=enriched.get("destination_path"),
                        directory_id=enriched.get("directory_id"),
                        decoy_id=enriched.get("decoy_id"),
                        is_decoy=enriched["is_decoy"],
                        pid=enriched.get("pid"),
                        process_name=enriched.get("process_name"),
                        executable_path=enriched.get("executable_path"),
                        process_attribution_status=enriched.get("process_attribution_status", "UNRESOLVED"),
                        risk_contribution=enriched.get("risk_contribution", 0)
                    )
                    enriched["event_id"] = event_id
                except Exception as db_exc:
                    logger.warning(f"Failed to persist event to MySQL: {db_exc}")

                # Notify subscribers (Detection Engine, GUI, etc.)
                for callback in list(self._subscribers):
                    try:
                        callback(enriched)
                    except Exception as sub_exc:
                        logger.error(f"Error in event subscriber callback: {sub_exc}")

                self._queue.task_done()
            except Exception as exc:
                logger.error(f"Error processing event from queue: {exc}")

    def _enrich_event(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Check against decoy registry and resolve process attribution."""
        source = raw["source_path"]

        # Check if touched file is a registered decoy
        decoy_record = DecoyRepository.get_by_path(source)
        is_decoy = decoy_record is not None
        decoy_id = decoy_record["decoy_id"] if decoy_record else None

        # Resolve process info
        proc_info = resolve_process_for_event(source, hint_pid=raw.get("hint_pid"))

        enriched = {
            "timestamp": raw["timestamp"],
            "event_type": raw["event_type"],
            "source_path": source,
            "destination_path": raw.get("destination_path"),
            "directory_id": raw.get("directory_id") or (decoy_record["directory_id"] if decoy_record else None),
            "is_decoy": is_decoy,
            "decoy_id": decoy_id,
            "pid": proc_info.get("pid"),
            "process_name": proc_info.get("process_name"),
            "executable_path": proc_info.get("executable_path"),
            "process_attribution_status": proc_info.get("status", "UNRESOLVED"),
            "risk_contribution": 40 if is_decoy else 0
        }
        return enriched


def get_event_bus() -> EventBus:
    """Return singleton instance of EventBus."""
    return EventBus()
