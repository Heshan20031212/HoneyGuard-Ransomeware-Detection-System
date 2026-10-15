"""
HoneyGuard Shannon Entropy Calculator
Evaluates file content randomness to distinguish plaintext documents from encrypted payloads.
Theoretical limits: 0.0 (uniform bytes) to 8.0 (pure random/ciphertext).
"""

import math
from collections import Counter
from pathlib import Path
from typing import Optional

from honeyguard.utils.logger import get_logger

logger = get_logger("HoneyGuard.Entropy")


def calculate_bytes_entropy(data: bytes) -> float:
    """Calculate Shannon entropy of raw byte buffer in bits per byte (0.0 to 8.0)."""
    if not data:
        return 0.0

    length = len(data)
    counts = Counter(data)
    entropy = 0.0
    for count in counts.values():
        p_x = count / length
        entropy -= p_x * math.log2(p_x)

    return round(entropy, 4)


def calculate_file_entropy(file_path: Path, max_sample_bytes: int = 65536) -> Optional[float]:
    """
    Read up to max_sample_bytes from the file and calculate Shannon entropy.
    Safely handles file locks and missing files.
    """
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        return None

    try:
        with open(p, "rb") as f:
            data = f.read(max_sample_bytes)
        return calculate_bytes_entropy(data)
    except (PermissionError, OSError) as exc:
        logger.debug(f"Could not read {p} for entropy check: {exc}")
        return None
