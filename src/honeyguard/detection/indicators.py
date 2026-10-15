"""
HoneyGuard Behavioural Indicators
Evaluates four core indicator families:
1. Honeytoken Interaction
2. High-Frequency File Activity (sliding window)
3. Rename / Extension Change
4. Content / Entropy Anomaly
"""

import time
from collections import deque
from pathlib import Path
from typing import Dict, Any, List

from honeyguard.detection.entropy import calculate_file_entropy
from honeyguard.utils.logger import get_logger

logger = get_logger("HoneyGuard.Indicators")

SUSPICIOUS_EXTENSIONS = {
    ".locked", ".crypto", ".crypted", ".enc", ".ransom",
    ".wnry", ".wcry", ".lockbit", ".blackcat", ".phobos", ".makop"
}


class IndicatorEvaluator:
    """Evaluates enriched filesystem events against behavioural indicator families."""

    def __init__(self, window_seconds: float = 3.0, frequency_threshold: int = 10, entropy_threshold: float = 7.2):
        self.window_seconds = window_seconds
        self.frequency_threshold = frequency_threshold
        self.entropy_threshold = entropy_threshold

        # Sliding window buffer: deque of (timestamp_epoch, file_path)
        self._recent_modifications = deque()

    def evaluate(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate an incoming enriched event.
        Returns:
            {
                "honeytoken_interaction": bool,
                "high_frequency_file_activity": bool,
                "rename_extension_change": bool,
                "content_entropy_change": bool,
                "details": Dict[str, Any]
            }
        """
        now = time.time()
        source_path = event.get("source_path", "")
        dest_path = event.get("destination_path")
        event_type = event.get("event_type", "")
        is_decoy = event.get("is_decoy", False)

        # 1. Honeytoken Interaction
        honeytoken_hit = bool(is_decoy)

        # 2. High-Frequency File Activity Tracking
        if event_type in ("CREATE", "MODIFY", "WRITE", "RENAME", "EXTENSION_CHANGE"):
            self._recent_modifications.append((now, source_path))

        # Evict old events outside window
        while self._recent_modifications and (now - self._recent_modifications[0][0]) > self.window_seconds:
            self._recent_modifications.popleft()

        unique_files_in_window = len(set(fp for _, fp in self._recent_modifications))
        high_frequency_hit = unique_files_in_window >= self.frequency_threshold

        # 3. Rename / Extension Change Detection
        rename_ext_hit = False
        target_ext = ""
        if event_type == "EXTENSION_CHANGE" or (dest_path and dest_path != source_path):
            check_path = dest_path if dest_path else source_path
            ext = Path(check_path).suffix.lower()
            target_ext = ext
            if ext in SUSPICIOUS_EXTENSIONS or ".locked" in check_path.lower():
                rename_ext_hit = True
        elif event_type == "RENAME" and dest_path:
            ext = Path(dest_path).suffix.lower()
            if ext in SUSPICIOUS_EXTENSIONS:
                rename_ext_hit = True

        # 4. Content / Entropy Change Detection
        entropy_hit = False
        file_entropy = None
        if event_type in ("MODIFY", "CREATE", "WRITE") and source_path:
            file_entropy = calculate_file_entropy(Path(source_path))
            if file_entropy is not None and file_entropy >= self.entropy_threshold:
                entropy_hit = True

        matched = {
            "honeytoken_interaction": honeytoken_hit,
            "high_frequency_file_activity": high_frequency_hit,
            "rename_extension_change": rename_ext_hit,
            "content_entropy_change": entropy_hit,
            "details": {
                "unique_files_in_window": unique_files_in_window,
                "window_seconds": self.window_seconds,
                "file_entropy": file_entropy,
                "target_extension": target_ext,
                "is_decoy": is_decoy,
                "event_type": event_type
            }
        }

        return matched
