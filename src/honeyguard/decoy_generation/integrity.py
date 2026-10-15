"""
HoneyGuard Decoy Integrity Verifier
Calculates SHA-256 baseline hashes and verifies tamper status of planted honeytokens.
"""

import hashlib
from pathlib import Path
from typing import Tuple, Dict, Any

from honeyguard.utils.logger import get_logger

logger = get_logger("HoneyGuard.Integrity")


def calculate_file_hash_and_size(file_path: Path) -> Tuple[str, int]:
    """Calculate SHA-256 hash and byte size of a file."""
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"Target file does not exist: {file_path}")

    hasher = hashlib.sha256()
    size = 0
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
            size += len(chunk)

    return hasher.hexdigest(), size


def verify_decoy_integrity(decoy_record: Dict[str, Any]) -> str:
    """
    Verify the physical state of a decoy against its database baseline.
    Returns: 'INTACT', 'MODIFIED', 'DELETED', or 'ACCESSED'
    """
    target_path = Path(decoy_record["absolute_path"])
    if not target_path.exists():
        logger.warning(f"Decoy file missing on disk (DELETED): {target_path}")
        return "DELETED"

    try:
        current_hash, current_size = calculate_file_hash_and_size(target_path)
        if current_hash != decoy_record["baseline_hash"] or current_size != decoy_record["baseline_size"]:
            logger.warning(f"Decoy file altered on disk (MODIFIED): {target_path}")
            return "MODIFIED"

        return "INTACT"
    except Exception as exc:
        logger.error(f"Error checking integrity for {target_path}: {exc}")
        return "MODIFIED"
