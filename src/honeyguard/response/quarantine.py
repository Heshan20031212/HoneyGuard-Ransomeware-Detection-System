"""
HoneyGuard Quarantine Manager
Safely isolates suspicious files into the encrypted/restricted data/quarantine repository.
"""

import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from honeyguard.utils.logger import get_logger
from honeyguard.utils.paths import get_quarantine_dir

logger = get_logger("HoneyGuard.Quarantine")


def quarantine_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Safely move a suspicious file into the quarantine directory with isolation metadata.
    """
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        logger.warning(f"File to quarantine not found: {p}")
        return None

    try:
        quarantine_dir = get_quarantine_dir()
        quarantine_id = f"QUAR-{uuid.uuid4().hex[:8].upper()}"
        target_name = f"{quarantine_id}_{p.name}"
        dest_path = quarantine_dir / target_name

        shutil.move(str(p), str(dest_path))

        record = {
            "quarantine_id": quarantine_id,
            "original_path": str(p.resolve()),
            "quarantine_path": str(dest_path.resolve()),
            "isolated_at": datetime.now().isoformat(),
            "status": "ISOLATED"
        }
        logger.info(f"Quarantined {p} -> {dest_path}")
        return record
    except Exception as exc:
        logger.error(f"Failed to quarantine {p}: {exc}")
        return None
