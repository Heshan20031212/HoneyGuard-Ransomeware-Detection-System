"""
Database Integration Tests (DB-TC01 to DB-TC10)
Verifies MySQL connectivity, transactions, foreign keys, parameterized queries, and persistence.
"""

import uuid
from datetime import datetime
import pytest

from honeyguard.database.connection import get_db_connection, is_db_connected, db_transaction
from honeyguard.database.schema import verify_schema
from honeyguard.database.repositories import (
    DirectoryRepository,
    DecoyRepository,
    EventRepository,
    AlertRepository,
    IncidentRepository,
    ResponseActionRepository,
    BenchmarkRepository
)


def test_db_tc01_mysql_connection():
    """DB-TC01: Verify active MySQL connection succeeds."""
    assert is_db_connected() is True
    assert verify_schema() is True


def test_db_tc02_decoy_insert():
    """DB-TC02: Decoy inserts and queries correctly."""
    dir_id = DirectoryRepository.add_directory("C:\\test\\dir1", "Test Dir", True)
    decoy_id = f"DEC-TEST-{uuid.uuid4().hex[:6]}"
    DecoyRepository.add_decoy(
        decoy_id=decoy_id,
        directory_id=dir_id,
        filename="test_decoy.xlsx",
        absolute_path=f"C:\\test\\dir1\\{decoy_id}.xlsx",
        file_type="XLSX",
        baseline_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        baseline_size=1024,
        status="INTACT"
    )

    retrieved = DecoyRepository.get_by_id(decoy_id)
    assert retrieved is not None
    assert retrieved["filename"] == "test_decoy.xlsx"
    assert retrieved["status"] == "INTACT"


def test_db_tc03_filesystem_event_insert():
    """DB-TC03: Filesystem event inserts correctly."""
    ev_id = EventRepository.log_event(
        timestamp=datetime.now(),
        event_type="MODIFY",
        source_path="C:\\test\\file.txt",
        is_decoy=False,
        pid=1234,
        process_name="test_proc.exe",
        process_attribution_status="CONFIRMED",
        risk_contribution=0
    )
    assert ev_id > 0
    recent = EventRepository.get_recent(limit=5)
    assert any(e["event_id"] == ev_id for e in recent)


def test_db_tc04_alert_insert():
    """DB-TC04: Alert inserts correctly with breakdown."""
    alert_id = f"ALT-TEST-{uuid.uuid4().hex[:6]}"
    AlertRepository.create_alert(
        alert_id=alert_id,
        timestamp=datetime.now(),
        affected_file="C:\\test\\canary.docx",
        risk_score=85,
        risk_level="HIGH",
        configured_threshold=70,
        honeytoken_weight=40,
        file_activity_weight=25,
        rename_extension_weight=20,
        entropy_weight=0,
        matched_indicators=["Honeytoken Interaction", "High-Frequency Modification"],
        pid=4567,
        process_name="test_ransom.exe",
        alert_status="ACTIVE"
    )

    active = AlertRepository.get_active()
    assert any(a["alert_id"] == alert_id for a in active)


def test_db_tc05_incident_and_response_transaction():
    """DB-TC05: Incident and response action insert with transaction integrity."""
    inc_id = f"INC-2026-TEST-{uuid.uuid4().hex[:4]}"

    with db_transaction():
        IncidentRepository.create_incident(
            incident_id=inc_id,
            detected_at=datetime.now(),
            affected_file="C:\\test\\victim.docx",
            risk_score=90,
            risk_level="CRITICAL",
            matched_indicators=["Canary Touched", "Entropy Jump"],
            containment_status="CONTAINED"
        )
        ResponseActionRepository.record_action(
            incident_id=inc_id,
            action_type="TERMINATE_PROCESS",
            requested_at=datetime.now(),
            executed_at=datetime.now(),
            result="Terminated hostile PID 9999",
            success=True
        )

    retrieved = IncidentRepository.get_by_id(inc_id)
    assert retrieved is not None
    assert retrieved["containment_status"] == "CONTAINED"

    actions = ResponseActionRepository.get_for_incident(inc_id)
    assert len(actions) == 1
    assert actions[0]["action_type"] == "TERMINATE_PROCESS"


def test_db_tc06_foreign_key_constraints():
    """DB-TC06: Foreign key constraints prevent invalid parent references."""
    conn = get_db_connection()
    with conn.cursor() as cursor:
        with pytest.raises(Exception):
            # Attempt to insert decoy for non-existent directory_id 999999
            cursor.execute("""
                INSERT INTO decoys (decoy_id, directory_id, filename, absolute_path, file_type, baseline_hash, baseline_size)
                VALUES ('DEC-INVALID', 999999, 'orphan.xlsx', 'C:\\orphan.xlsx', 'XLSX', 'hash', 100);
            """)
            conn.commit()


def test_db_tc09_parameterized_query_sql_injection_defense():
    """DB-TC09: Parameterized queries safely neutralize SQL injection payload."""
    malicious_path = "C:\\legit\\' OR '1'='1"
    # Should safely query without syntax error or table dumping
    record = DirectoryRepository.get_by_path(malicious_path)
    assert record is None
