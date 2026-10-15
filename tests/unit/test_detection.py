"""
Unit Tests: Detection Indicators & Shannon Entropy
"""

import os
from pathlib import Path
from honeyguard.detection.entropy import calculate_bytes_entropy, calculate_file_entropy
from honeyguard.detection.indicators import IndicatorEvaluator


def test_entropy_plain_text():
    # Plain text has moderate entropy (typically 3.0 to 5.0)
    plain_bytes = b"Hello world! This is normal plaintext sentence repeated." * 10
    ent = calculate_bytes_entropy(plain_bytes)
    assert 3.0 <= ent <= 5.5


def test_entropy_random_ciphertext():
    # Encrypted random bytes has high entropy (approaching 8.0)
    random_bytes = os.urandom(4096)
    ent = calculate_bytes_entropy(random_bytes)
    assert ent >= 7.8


def test_honeytoken_indicator_trigger():
    evaluator = IndicatorEvaluator()
    # Decoy event
    event = {
        "event_type": "MODIFY",
        "source_path": "/fake/path/decoy.xlsx",
        "is_decoy": True
    }
    res = evaluator.evaluate(event)
    assert res["honeytoken_interaction"] is True


def test_suspicious_extension_trigger():
    evaluator = IndicatorEvaluator()
    event = {
        "event_type": "EXTENSION_CHANGE",
        "source_path": "/fake/path/document.docx",
        "destination_path": "/fake/path/document.docx.locked",
        "is_decoy": False
    }
    res = evaluator.evaluate(event)
    assert res["rename_extension_change"] is True
