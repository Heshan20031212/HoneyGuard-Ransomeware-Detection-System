"""
Unit Tests: Decoy File Generation & Integrity Verification
Covers: PDF, DOCX, XLSX, TXT generation, SHA-256 calculation, and tamper detection.
"""

from pathlib import Path
from honeyguard.decoy_generation.generator import generate_decoy_file
from honeyguard.decoy_generation.integrity import calculate_file_hash_and_size, verify_decoy_integrity


def test_generate_txt_decoy(tmp_path):
    target = tmp_path / "test_notes.txt"
    p = generate_decoy_file(target, "TXT", {"content": "Canary token content"})
    assert p.exists()
    assert p.stat().st_size > 0


def test_generate_pdf_decoy(tmp_path):
    target = tmp_path / "test_agreement.pdf"
    p = generate_decoy_file(target, "PDF", {"title": "Test Agreement"})
    assert p.exists()
    with open(p, "rb") as f:
        header = f.read(8)
    assert header.startswith(b"%PDF-1.4")


def test_generate_docx_decoy(tmp_path):
    target = tmp_path / "test_memo.docx"
    p = generate_decoy_file(target, "DOCX", {"title": "Test Memo"})
    assert p.exists()
    assert p.stat().st_size > 1000


def test_generate_xlsx_decoy(tmp_path):
    target = tmp_path / "test_sheet.xlsx"
    p = generate_decoy_file(target, "XLSX", {"sheet_name": "TestSheet"})
    assert p.exists()
    assert p.stat().st_size > 1000


def test_integrity_hash_and_tamper(tmp_path):
    target = tmp_path / "canary.txt"
    generate_decoy_file(target, "TXT", {"content": "Baseline Content"})
    h1, s1 = calculate_file_hash_and_size(target)
    assert len(h1) == 64  # SHA-256 length

    record = {
        "absolute_path": str(target),
        "baseline_hash": h1,
        "baseline_size": s1
    }
    assert verify_decoy_integrity(record) == "INTACT"

    # Modify file
    with open(target, "a") as f:
        f.write("Tampered byte stream")

    assert verify_decoy_integrity(record) == "MODIFIED"

    # Delete file
    target.unlink()
    assert verify_decoy_integrity(record) == "DELETED"
