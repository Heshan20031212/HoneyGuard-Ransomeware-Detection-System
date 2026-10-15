"""
HoneyGuard Process Resolver
Resolves process information using operating-system telemetry and psutil.
Strict Academic Integrity Rule:
NEVER fabricate PID or process attribution.
If attribution cannot be determined reliably, status is marked 'UNRESOLVED'.
"""

import os
from typing import Optional, Dict, Any
import psutil

from honeyguard.utils.logger import get_logger

logger = get_logger("HoneyGuard.ProcessResolver")


def resolve_process_for_event(
    file_path: str,
    hint_pid: Optional[int] = None
) -> Dict[str, Any]:
    """
    Attempt best-effort attribution of a filesystem event to an active OS process.
    Returns:
        {
            "pid": Optional[int],
            "process_name": Optional[str],
            "executable_path": Optional[str],
            "status": "CONFIRMED" | "INFERRED" | "UNRESOLVED"
        }
    """
    # Case 1: An explicit PID hint was provided (e.g. from simulator or OS hook)
    if hint_pid and psutil.pid_exists(hint_pid):
        try:
            proc = psutil.Process(hint_pid)
            return {
                "pid": proc.pid,
                "process_name": proc.name(),
                "executable_path": proc.exe() if hasattr(proc, "exe") else None,
                "status": "CONFIRMED"
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Case 2: Inspect active processes that currently have the file open
    normalized_path = os.path.normpath(file_path).lower()
    try:
        # Search among active processes
        for proc in psutil.process_iter(["pid", "name", "exe"]):
            try:
                # Skip System Idle and self
                if proc.info["pid"] in (0, os.getpid()):
                    continue

                # Check open file descriptors if permitted by OS
                try:
                    open_files = proc.open_files()
                    for f in open_files:
                        if os.path.normpath(f.path).lower() == normalized_path:
                            return {
                                "pid": proc.info["pid"],
                                "process_name": proc.info["name"],
                                "executable_path": proc.info["exe"],
                                "status": "CONFIRMED"
                            }
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as exc:
        logger.debug(f"Telemetry inspection note: {exc}")

    # Case 3: Process cannot be reliably established -> UNRESOLVED
    return {
        "pid": None,
        "process_name": None,
        "executable_path": None,
        "status": "UNRESOLVED"
    }
