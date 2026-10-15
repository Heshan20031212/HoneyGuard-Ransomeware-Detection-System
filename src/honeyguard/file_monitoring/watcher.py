"""
HoneyGuard Real-Time File System Watcher
Leverages the Python watchdog library to monitor protected directories non-blockingly.
"""

from pathlib import Path
from typing import Dict, List, Optional
from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    FileCreatedEvent,
    FileModifiedEvent,
    FileMovedEvent,
    FileDeletedEvent
)

from honeyguard.file_monitoring.event_bus import get_event_bus
from honeyguard.utils.logger import get_logger

logger = get_logger("HoneyGuard.Watcher")


class HoneyGuardEventHandler(FileSystemEventHandler):
    """Event handler that maps watchdog events to normalized HoneyGuard events."""

    def __init__(self, directory_id: int):
        super().__init__()
        self.directory_id = directory_id
        self.event_bus = get_event_bus()

    def on_created(self, event):
        if event.is_directory:
            return
        self.event_bus.publish_raw_event(
            event_type="CREATE",
            source_path=event.src_path,
            directory_id=self.directory_id
        )

    def on_modified(self, event):
        if event.is_directory:
            return
        self.event_bus.publish_raw_event(
            event_type="MODIFY",
            source_path=event.src_path,
            directory_id=self.directory_id
        )

    def on_moved(self, event):
        if event.is_directory:
            return
        src = Path(event.src_path)
        dest = Path(event.dest_path)

        # Detect extension change
        event_type = "EXTENSION_CHANGE" if src.suffix.lower() != dest.suffix.lower() else "RENAME"

        self.event_bus.publish_raw_event(
            event_type=event_type,
            source_path=event.src_path,
            destination_path=event.dest_path,
            directory_id=self.directory_id
        )

    def on_deleted(self, event):
        if event.is_directory:
            return
        self.event_bus.publish_raw_event(
            event_type="DELETE",
            source_path=event.src_path,
            directory_id=self.directory_id
        )


class FileSystemWatcher:
    """Manages active watchdog observers for configured protected directories."""

    def __init__(self):
        self.observer: Optional[Observer] = None
        self._watch_schedules: Dict[int, Any] = {}
        self.is_running: bool = False

    def start(self, directories: List[Dict]):
        """
        Start monitoring the given list of protected directories.
        directories is a list of dicts with keys 'directory_id', 'directory_path', 'monitoring_enabled'.
        """
        if self.is_running:
            logger.info("Watcher is already running.")
            return

        get_event_bus().start()
        self.observer = Observer()

        monitored_count = 0
        for d in directories:
            if not d.get("monitoring_enabled", True):
                continue
            path_str = d["directory_path"]
            p = Path(path_str)
            if not p.exists():
                try:
                    p.mkdir(parents=True, exist_ok=True)
                except Exception as exc:
                    logger.warning(f"Could not create missing watch directory {path_str}: {exc}")
                    continue

            handler = HoneyGuardEventHandler(directory_id=d["directory_id"])
            watch = self.observer.schedule(handler, str(p), recursive=True)
            self._watch_schedules[d["directory_id"]] = watch
            monitored_count += 1
            logger.info(f"Scheduled watcher for: {path_str}")

        if monitored_count > 0:
            self.observer.start()
            self.is_running = True
            logger.info(f"FileSystemWatcher active across {monitored_count} directories.")
        else:
            logger.warning("No valid directories to monitor.")

    def stop(self):
        """Stop all file system watching cleanly."""
        if not self.is_running:
            return

        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=2.0)
            self.observer = None

        get_event_bus().stop()
        self._watch_schedules.clear()
        self.is_running = False
        logger.info("FileSystemWatcher stopped.")
