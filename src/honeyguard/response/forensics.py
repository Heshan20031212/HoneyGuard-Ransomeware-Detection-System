"""
HoneyGuard Forensics Collector
Collects process and system telemetry context when an alert or incident is declared.
"""

import os
from typing import Dict, Any, Optional
import psutil

from honeyguard.utils.logger import get_logger

logger = get_logger("HoneyGuard.Forensics")


def collect_process_forensics(pid: Optional[int]) -> Dict[str, Any]:
    """Capture snapshot of process telemetry if PID is available and running."""
    if not pid or not psutil.pid_exists(pid):
        return {
            "pid": None,
            "status": "PROCESS_NOT_FOUND_OR_TERMINATED",
            "cpu_percent": 0.0,
            "memory_mb": 0.0,
            "cmdline": [],
            "open_files_count": 0
        }

    try:
        proc = psutil.Process(pid)
        mem = proc.memory_info().rss / (1024 * 1024)
        cpu = proc.cpu_percent(interval=None)
        cmdline = proc.cmdline() if hasattr(proc, "cmdline") else []
        try:
            open_count = len(proc.open_files())
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            open_count = 0

        return {
            "pid": proc.pid,
            "name": proc.name(),
            "executable_path": proc.exe() if hasattr(proc, "exe") else None,
            "cpu_percent": cpu,
            "memory_mb": round(mem, 2),
            "cmdline": cmdline,
            "open_files_count": open_count,
            "status": "CAPTURED"
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied) as exc:
        return {
            "pid": pid,
            "status": f"UNAVAILABLE ({exc})",
            "cpu_percent": 0.0,
            "memory_mb": 0.0,
            "cmdline": [],
            "open_files_count": 0
        }
