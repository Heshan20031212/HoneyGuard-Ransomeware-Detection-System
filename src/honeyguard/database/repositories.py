"""
HoneyGuard Database Repositories
Parameterized data access layer for all HoneyGuard entities.
Zero raw string SQL formatting — 100% parameterized against SQL injection.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from honeyguard.database.connection import get_db_connection, db_transaction
from honeyguard.utils.logger import get_logger

logger = get_logger("HoneyGuard.Repositories")


class DirectoryRepository:
    """Repository for managing monitored and protected directories."""

    @staticmethod
    def add_directory(path: str, display_name: str, monitoring_enabled: bool = True) -> int:
        conn = get_db_connection()
        query = """
            INSERT INTO protected_directories (directory_path, display_name, monitoring_enabled)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE display_name = VALUES(display_name), monitoring_enabled = VALUES(monitoring_enabled);
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (path, display_name, int(monitoring_enabled)))
            conn.commit()
            if cursor.lastrowid:
                return cursor.lastrowid

        existing = DirectoryRepository.get_by_path(path)
        return existing["directory_id"] if existing else 0

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM protected_directories ORDER BY directory_id ASC;")
            return cursor.fetchall()

    @staticmethod
    def get_by_path(path: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM protected_directories WHERE directory_path = %s LIMIT 1;", (path,))
            return cursor.fetchone()

    @staticmethod
    def set_monitoring_enabled(directory_id: int, enabled: bool):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE protected_directories SET monitoring_enabled = %s WHERE directory_id = %s;",
                (int(enabled), directory_id)
            )
            conn.commit()

    @staticmethod
    def remove(directory_id: int):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM protected_directories WHERE directory_id = %s;", (directory_id,))
            conn.commit()


class DecoyRepository:
    """Repository for managing canary / honeytoken files."""

    @staticmethod
    def add_decoy(
        decoy_id: str,
        directory_id: int,
        filename: str,
        absolute_path: str,
        file_type: str,
        baseline_hash: str,
        baseline_size: int,
        status: str = "INTACT"
    ) -> str:
        conn = get_db_connection()
        existing = DecoyRepository.get_by_path(absolute_path)
        if existing:
            decoy_id = existing["decoy_id"]

        query = """
            INSERT INTO decoys (
                decoy_id, directory_id, filename, absolute_path,
                file_type, baseline_hash, baseline_size, status, monitoring_enabled
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
            ON DUPLICATE KEY UPDATE
                baseline_hash = VALUES(baseline_hash),
                baseline_size = VALUES(baseline_size),
                status = VALUES(status),
                last_verified_timestamp = CURRENT_TIMESTAMP;
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (
                decoy_id, directory_id, filename, absolute_path,
                file_type, baseline_hash, baseline_size, status
            ))
            conn.commit()
            return decoy_id

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT d.*, pd.directory_path as base_directory, pd.display_name as directory_name
                FROM decoys d
                LEFT JOIN protected_directories pd ON d.directory_id = pd.directory_id
                ORDER BY d.creation_timestamp DESC;
            """)
            return cursor.fetchall()

    @staticmethod
    def get_by_path(absolute_path: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM decoys WHERE absolute_path = %s LIMIT 1;", (absolute_path,))
            return cursor.fetchone()

    @staticmethod
    def get_by_id(decoy_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM decoys WHERE decoy_id = %s LIMIT 1;", (decoy_id,))
            return cursor.fetchone()

    @staticmethod
    def update_status(decoy_id: str, status: str, last_verified: Optional[datetime] = None):
        conn = get_db_connection()
        query = """
            UPDATE decoys
            SET status = %s, last_verified_timestamp = COALESCE(%s, CURRENT_TIMESTAMP)
            WHERE decoy_id = %s;
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (status, last_verified, decoy_id))
            conn.commit()

    @staticmethod
    def remove(decoy_id: str):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM decoys WHERE decoy_id = %s;", (decoy_id,))
            conn.commit()

    @staticmethod
    def count_active() -> int:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as cnt FROM decoys WHERE monitoring_enabled = 1;")
            row = cursor.fetchone()
            return row["cnt"] if row else 0


class EventRepository:
    """Repository for auditing filesystem events and process telemetry."""

    @staticmethod
    def log_event(
        timestamp: datetime,
        event_type: str,
        source_path: str,
        destination_path: Optional[str] = None,
        directory_id: Optional[int] = None,
        decoy_id: Optional[str] = None,
        is_decoy: bool = False,
        pid: Optional[int] = None,
        process_name: Optional[str] = None,
        executable_path: Optional[str] = None,
        process_attribution_status: str = "UNRESOLVED",
        risk_contribution: int = 0
    ) -> int:
        conn = get_db_connection()
        query = """
            INSERT INTO file_events (
                directory_id, decoy_id, timestamp, event_type, source_path, destination_path,
                is_decoy, pid, process_name, executable_path, process_attribution_status, risk_contribution
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (
                directory_id, decoy_id, timestamp, event_type, source_path, destination_path,
                int(is_decoy), pid, process_name, executable_path, process_attribution_status, risk_contribution
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_recent(limit: int = 50) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM file_events ORDER BY timestamp DESC LIMIT %s;", (limit,))
            return cursor.fetchall()

    @staticmethod
    def count_total() -> int:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as cnt FROM file_events;")
            row = cursor.fetchone()
            return row["cnt"] if row else 0


class AlertRepository:
    """Repository for managing high-risk detection alerts."""

    @staticmethod
    def create_alert(
        alert_id: str,
        timestamp: datetime,
        affected_file: str,
        risk_score: int,
        risk_level: str,
        configured_threshold: int,
        honeytoken_weight: int,
        file_activity_weight: int,
        rename_extension_weight: int,
        entropy_weight: int,
        matched_indicators: Any,
        event_id: Optional[int] = None,
        decoy_id: Optional[str] = None,
        pid: Optional[int] = None,
        process_name: Optional[str] = None,
        executable_path: Optional[str] = None,
        alert_status: str = "ACTIVE"
    ) -> str:
        conn = get_db_connection()
        ind_str = json.dumps(matched_indicators) if isinstance(matched_indicators, (list, dict)) else str(matched_indicators)

        query = """
            INSERT INTO alerts (
                alert_id, event_id, timestamp, affected_file, decoy_id,
                risk_score, risk_level, configured_threshold,
                honeytoken_weight, file_activity_weight, rename_extension_weight, entropy_weight,
                matched_indicators, pid, process_name, executable_path, alert_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (
                alert_id, event_id, timestamp, affected_file, decoy_id,
                risk_score, risk_level, configured_threshold,
                honeytoken_weight, file_activity_weight, rename_extension_weight, entropy_weight,
                ind_str, pid, process_name, executable_path, alert_status
            ))
            conn.commit()
            return alert_id

    @staticmethod
    def get_recent(limit: int = 50) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT %s;", (limit,))
            return cursor.fetchall()

    @staticmethod
    def get_active() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM alerts WHERE alert_status = 'ACTIVE' ORDER BY timestamp DESC;")
            return cursor.fetchall()

    @staticmethod
    def update_status(alert_id: str, new_status: str):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE alerts SET alert_status = %s WHERE alert_id = %s;", (new_status, alert_id))
            conn.commit()

    @staticmethod
    def count_active() -> int:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as cnt FROM alerts WHERE alert_status = 'ACTIVE';")
            row = cursor.fetchone()
            return row["cnt"] if row else 0


class IncidentRepository:
    """Repository for confirmed ransomware incidents and forensics records."""

    @staticmethod
    def create_incident(
        incident_id: str,
        detected_at: datetime,
        affected_file: str,
        risk_score: int,
        risk_level: str,
        matched_indicators: Any,
        alert_id: Optional[str] = None,
        decoy_id: Optional[str] = None,
        pid: Optional[int] = None,
        process_name: Optional[str] = None,
        executable_path: Optional[str] = None,
        containment_status: str = "PENDING",
        files_modified_before: int = 0,
        files_modified_after: int = 0,
        detection_latency_ms: float = 0.0,
        cpu_usage: float = 0.0,
        ram_usage: float = 0.0
    ) -> str:
        conn = get_db_connection()
        ind_str = json.dumps(matched_indicators) if isinstance(matched_indicators, (list, dict)) else str(matched_indicators)

        query = """
            INSERT INTO incidents (
                incident_id, alert_id, detected_at, affected_file, decoy_id,
                risk_score, risk_level, matched_indicators, pid, process_name, executable_path,
                containment_status, files_modified_before_response, files_modified_after_response,
                detection_latency_ms, cpu_usage, ram_usage
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (
                incident_id, alert_id, detected_at, affected_file, decoy_id,
                risk_score, risk_level, ind_str, pid, process_name, executable_path,
                containment_status, files_modified_before, files_modified_after,
                detection_latency_ms, cpu_usage, ram_usage
            ))
            conn.commit()
            return incident_id

    @staticmethod
    def update_containment(
        incident_id: str,
        containment_status: str,
        files_modified_after: Optional[int] = None
    ):
        conn = get_db_connection()
        if files_modified_after is not None:
            query = """
                UPDATE incidents
                SET containment_status = %s, files_modified_after_response = %s
                WHERE incident_id = %s;
            """
            params = (containment_status, files_modified_after, incident_id)
        else:
            query = "UPDATE incidents SET containment_status = %s WHERE incident_id = %s;"
            params = (containment_status, incident_id)

        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()

    @staticmethod
    def get_all(limit: int = 100) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM incidents ORDER BY detected_at DESC LIMIT %s;", (limit,))
            return cursor.fetchall()

    @staticmethod
    def get_by_id(incident_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM incidents WHERE incident_id = %s LIMIT 1;", (incident_id,))
            return cursor.fetchone()

    @staticmethod
    def count_contained() -> int:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as cnt FROM incidents WHERE containment_status IN ('CONTAINED', 'ISOLATED');")
            row = cursor.fetchone()
            return row["cnt"] if row else 0


class ResponseActionRepository:
    """Repository for auditable containment response actions."""

    @staticmethod
    def record_action(
        incident_id: str,
        action_type: str,
        requested_at: datetime,
        result: str,
        success: bool,
        executed_at: Optional[datetime] = None,
        target_pid: Optional[int] = None,
        target_path: Optional[str] = None,
        operator_confirmation: bool = False,
        error_message: Optional[str] = None
    ) -> int:
        conn = get_db_connection()
        query = """
            INSERT INTO response_actions (
                incident_id, action_type, requested_at, executed_at,
                target_pid, target_path, operator_confirmation, result, success, error_message
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (
                incident_id, action_type, requested_at, executed_at,
                target_pid, target_path, int(operator_confirmation), result, int(success), error_message
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_for_incident(incident_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM response_actions WHERE incident_id = %s ORDER BY requested_at ASC;", (incident_id,))
            return cursor.fetchall()


class BenchmarkRepository:
    """Repository for benchmark experimental runs and telemetry samples."""

    @staticmethod
    def create_run(
        run_id: str,
        test_case: str,
        trial_number: int,
        started_at: datetime,
        completed_at: Optional[datetime],
        result: str,
        environment_info: str,
        notes: Optional[str] = None
    ) -> str:
        conn = get_db_connection()
        query = """
            INSERT INTO benchmark_runs (
                benchmark_run_id, test_case, trial_number, started_at,
                completed_at, result, environment_info, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE completed_at = VALUES(completed_at), result = VALUES(result);
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (
                run_id, test_case, trial_number, started_at,
                completed_at, result, environment_info, notes
            ))
            conn.commit()
            return run_id

    @staticmethod
    def record_measurement(
        run_id: str,
        metric_name: str,
        metric_value: float,
        metric_unit: str,
        sample_timestamp: datetime
    ):
        conn = get_db_connection()
        query = """
            INSERT INTO benchmark_measurements (
                benchmark_run_id, metric_name, metric_value, metric_unit, sample_timestamp
            ) VALUES (%s, %s, %s, %s, %s);
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (run_id, metric_name, metric_value, metric_unit, sample_timestamp))
            conn.commit()

    @staticmethod
    def get_runs_by_test_case(test_case: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM benchmark_runs WHERE test_case = %s ORDER BY trial_number ASC;", (test_case,))
            return cursor.fetchall()

    @staticmethod
    def get_measurements_for_run(run_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM benchmark_measurements WHERE benchmark_run_id = %s;", (run_id,))
            return cursor.fetchall()


class SettingsRepository:
    """Repository for dynamically tunable configuration settings in MySQL."""

    @staticmethod
    def get_all() -> Dict[str, str]:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT setting_key, setting_value FROM application_settings;")
            rows = cursor.fetchall()
            return {r["setting_key"]: r["setting_value"] for r in rows}

    @staticmethod
    def get(key: str, default: Optional[str] = None) -> Optional[str]:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT setting_value FROM application_settings WHERE setting_key = %s LIMIT 1;", (key,))
            row = cursor.fetchone()
            return row["setting_value"] if row else default

    @staticmethod
    def set(key: str, value: str, description: Optional[str] = None):
        conn = get_db_connection()
        query = """
            INSERT INTO application_settings (setting_key, setting_value, description)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value), description = COALESCE(VALUES(description), description);
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (key, str(value), description))
            conn.commit()


class AuditLogRepository:
    """Repository for security and operational audit trails."""

    @staticmethod
    def log(
        action: str,
        component: str,
        description: str,
        severity: str = "INFO",
        incident_id: Optional[str] = None,
        success: bool = True
    ) -> int:
        conn = get_db_connection()
        query = """
            INSERT INTO audit_logs (
                timestamp, action, component, description, severity, incident_id, success
            ) VALUES (NOW(3), %s, %s, %s, %s, %s, %s);
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (action, component, description, severity, incident_id, int(success)))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_recent(limit: int = 100) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT %s;", (limit,))
            return cursor.fetchall()
