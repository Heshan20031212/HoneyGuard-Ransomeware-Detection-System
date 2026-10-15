-- ==============================================================================
-- HONEYGUARD - HONEYTOKEN-BASED RANSOMWARE DETECTION AND PREVENTION SYSTEM
-- Database Schema Definition (MySQL 8.0+ / MariaDB / phpMyAdmin Compatible)
-- Module: IE3092 - Information Security Project | Group 15
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS `honeyguard_db`
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE `honeyguard_db`;

-- Disable foreign key checks during setup
SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------------------------
-- Table 1: protected_directories
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS `protected_directories`;
CREATE TABLE `protected_directories` (
    `directory_id` INT AUTO_INCREMENT PRIMARY KEY,
    `directory_path` VARCHAR(500) NOT NULL UNIQUE,
    `display_name` VARCHAR(150) NOT NULL,
    `monitoring_enabled` TINYINT(1) NOT NULL DEFAULT 1,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_dir_status` (`monitoring_enabled`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- Table 2: decoys
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS `decoys`;
CREATE TABLE `decoys` (
    `decoy_id` VARCHAR(64) PRIMARY KEY,
    `directory_id` INT NOT NULL,
    `filename` VARCHAR(255) NOT NULL,
    `absolute_path` VARCHAR(500) NOT NULL UNIQUE,
    `file_type` VARCHAR(10) NOT NULL, -- PDF, DOCX, XLSX, TXT
    `baseline_hash` VARCHAR(64) NOT NULL, -- SHA-256
    `baseline_size` BIGINT NOT NULL,
    `status` ENUM('INTACT', 'ACCESSED', 'MODIFIED', 'RENAMED', 'DELETED') NOT NULL DEFAULT 'INTACT',
    `monitoring_enabled` TINYINT(1) NOT NULL DEFAULT 1,
    `creation_timestamp` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `last_verified_timestamp` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_decoy_directory` FOREIGN KEY (`directory_id`)
        REFERENCES `protected_directories` (`directory_id`) ON DELETE CASCADE,
    INDEX `idx_decoy_status` (`status`),
    INDEX `idx_decoy_dir` (`directory_id`),
    INDEX `idx_decoy_file` (`filename`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- Table 3: file_events
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS `file_events`;
CREATE TABLE `file_events` (
    `event_id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `directory_id` INT NULL,
    `decoy_id` VARCHAR(64) NULL,
    `timestamp` DATETIME(3) NOT NULL,
    `event_type` VARCHAR(30) NOT NULL, -- CREATE, MODIFY, WRITE, MOVE, RENAME, DELETE, EXTENSION_CHANGE
    `source_path` VARCHAR(500) NOT NULL,
    `destination_path` VARCHAR(500) NULL,
    `is_decoy` TINYINT(1) NOT NULL DEFAULT 0,
    `pid` INT NULL,
    `process_name` VARCHAR(255) NULL,
    `executable_path` VARCHAR(500) NULL,
    `process_attribution_status` VARCHAR(50) NOT NULL DEFAULT 'UNRESOLVED', -- CONFIRMED, INFERRED, UNRESOLVED
    `risk_contribution` INT NOT NULL DEFAULT 0,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_event_directory` FOREIGN KEY (`directory_id`)
        REFERENCES `protected_directories` (`directory_id`) ON DELETE SET NULL,
    CONSTRAINT `fk_event_decoy` FOREIGN KEY (`decoy_id`)
        REFERENCES `decoys` (`decoy_id`) ON DELETE SET NULL,
    INDEX `idx_event_time` (`timestamp`),
    INDEX `idx_event_type` (`event_type`),
    INDEX `idx_event_is_decoy` (`is_decoy`),
    INDEX `idx_event_pid` (`pid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- Table 4: alerts
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS `alerts`;
CREATE TABLE `alerts` (
    `alert_id` VARCHAR(64) PRIMARY KEY,
    `event_id` BIGINT NULL,
    `timestamp` DATETIME(3) NOT NULL,
    `affected_file` VARCHAR(500) NOT NULL,
    `decoy_id` VARCHAR(64) NULL,
    `risk_score` INT NOT NULL,
    `risk_level` VARCHAR(20) NOT NULL, -- LOW, MEDIUM, HIGH, CRITICAL
    `configured_threshold` INT NOT NULL,
    `honeytoken_weight` INT NOT NULL DEFAULT 0,
    `file_activity_weight` INT NOT NULL DEFAULT 0,
    `rename_extension_weight` INT NOT NULL DEFAULT 0,
    `entropy_weight` INT NOT NULL DEFAULT 0,
    `matched_indicators` TEXT NOT NULL,
    `pid` INT NULL,
    `process_name` VARCHAR(255) NULL,
    `executable_path` VARCHAR(500) NULL,
    `alert_status` VARCHAR(30) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, ACKNOWLEDGED, RESOLVED, DISMISSED
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_alert_event` FOREIGN KEY (`event_id`)
        REFERENCES `file_events` (`event_id`) ON DELETE SET NULL,
    CONSTRAINT `fk_alert_decoy` FOREIGN KEY (`decoy_id`)
        REFERENCES `decoys` (`decoy_id`) ON DELETE SET NULL,
    INDEX `idx_alert_time` (`timestamp`),
    INDEX `idx_alert_level` (`risk_level`),
    INDEX `idx_alert_status` (`alert_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- Table 5: incidents
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS `incidents`;
CREATE TABLE `incidents` (
    `internal_id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `incident_id` VARCHAR(64) NOT NULL UNIQUE, -- e.g. INC-2026-0001
    `alert_id` VARCHAR(64) NULL,
    `detected_at` DATETIME(3) NOT NULL,
    `affected_file` VARCHAR(500) NOT NULL,
    `decoy_id` VARCHAR(64) NULL,
    `risk_score` INT NOT NULL,
    `risk_level` VARCHAR(20) NOT NULL,
    `matched_indicators` TEXT NOT NULL,
    `pid` INT NULL,
    `process_name` VARCHAR(255) NULL,
    `executable_path` VARCHAR(500) NULL,
    `containment_status` VARCHAR(50) NOT NULL DEFAULT 'PENDING', -- CONTAINED, ISOLATED, FAILED, PENDING, LOG_ONLY
    `files_modified_before_response` INT NOT NULL DEFAULT 0,
    `files_modified_after_response` INT NOT NULL DEFAULT 0,
    `detection_latency_ms` DOUBLE NOT NULL DEFAULT 0.0,
    `cpu_usage` DOUBLE NOT NULL DEFAULT 0.0,
    `ram_usage` DOUBLE NOT NULL DEFAULT 0.0,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_incident_alert` FOREIGN KEY (`alert_id`)
        REFERENCES `alerts` (`alert_id`) ON DELETE SET NULL,
    CONSTRAINT `fk_incident_decoy` FOREIGN KEY (`decoy_id`)
        REFERENCES `decoys` (`decoy_id`) ON DELETE SET NULL,
    INDEX `idx_incident_id` (`incident_id`),
    INDEX `idx_incident_time` (`detected_at`),
    INDEX `idx_incident_level` (`risk_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- Table 6: response_actions
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS `response_actions`;
CREATE TABLE `response_actions` (
    `response_id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `incident_id` VARCHAR(64) NOT NULL,
    `action_type` VARCHAR(50) NOT NULL, -- LOG_ONLY, QUARANTINE, TERMINATE_PROCESS, ISOLATE_PROCESS
    `requested_at` DATETIME(3) NOT NULL,
    `executed_at` DATETIME(3) NULL,
    `target_pid` INT NULL,
    `target_path` VARCHAR(500) NULL,
    `operator_confirmation` TINYINT(1) NOT NULL DEFAULT 0,
    `result` VARCHAR(100) NOT NULL,
    `success` TINYINT(1) NOT NULL DEFAULT 0,
    `error_message` TEXT NULL,
    CONSTRAINT `fk_response_incident` FOREIGN KEY (`incident_id`)
        REFERENCES `incidents` (`incident_id`) ON DELETE CASCADE,
    INDEX `idx_resp_incident` (`incident_id`),
    INDEX `idx_resp_action` (`action_type`),
    INDEX `idx_resp_success` (`success`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- Table 7: benchmark_runs
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS `benchmark_runs`;
CREATE TABLE `benchmark_runs` (
    `benchmark_run_id` VARCHAR(64) PRIMARY KEY,
    `test_case` VARCHAR(50) NOT NULL, -- TC01, TC02, ..., TC07
    `trial_number` INT NOT NULL,
    `started_at` DATETIME(3) NOT NULL,
    `completed_at` DATETIME(3) NULL,
    `result` VARCHAR(50) NOT NULL, -- PASS, FAIL
    `environment_info` TEXT NOT NULL,
    `notes` TEXT NULL,
    INDEX `idx_bench_tc` (`test_case`),
    INDEX `idx_bench_trial` (`trial_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- Table 8: benchmark_measurements
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS `benchmark_measurements`;
CREATE TABLE `benchmark_measurements` (
    `measurement_id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `benchmark_run_id` VARCHAR(64) NOT NULL,
    `metric_name` VARCHAR(100) NOT NULL, -- DETECTION_TIME_MS, CPU_PERCENT, RAM_MB, FILES_MODIFIED, etc.
    `metric_value` DOUBLE NOT NULL,
    `metric_unit` VARCHAR(20) NOT NULL,
    `sample_timestamp` DATETIME(3) NOT NULL,
    CONSTRAINT `fk_measurement_run` FOREIGN KEY (`benchmark_run_id`)
        REFERENCES `benchmark_runs` (`benchmark_run_id`) ON DELETE CASCADE,
    INDEX `idx_meas_run` (`benchmark_run_id`),
    INDEX `idx_meas_metric` (`metric_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- Table 9: application_settings
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS `application_settings`;
CREATE TABLE `application_settings` (
    `setting_key` VARCHAR(100) PRIMARY KEY,
    `setting_value` TEXT NOT NULL,
    `description` VARCHAR(255) NULL,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- Table 10: audit_logs
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS `audit_logs`;
CREATE TABLE `audit_logs` (
    `audit_id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `timestamp` DATETIME(3) NOT NULL,
    `action` VARCHAR(100) NOT NULL,
    `component` VARCHAR(100) NOT NULL,
    `description` TEXT NOT NULL,
    `severity` VARCHAR(20) NOT NULL DEFAULT 'INFO',
    `incident_id` VARCHAR(64) NULL,
    `success` TINYINT(1) NOT NULL DEFAULT 1,
    INDEX `idx_audit_time` (`timestamp`),
    INDEX `idx_audit_comp` (`component`),
    INDEX `idx_audit_sev` (`severity`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Enable foreign keys
SET FOREIGN_KEY_CHECKS = 1;

-- ------------------------------------------------------------------------------
-- Seed Default Configurable Settings
-- ------------------------------------------------------------------------------
INSERT INTO `application_settings` (`setting_key`, `setting_value`, `description`) VALUES
('risk_threshold', '70', 'Threshold score to classify an event sequence as high-risk ransomware'),
('honeytoken_weight', '40', 'Weight assigned when a monitored canary/decoy file is touched'),
('file_activity_weight', '25', 'Weight assigned when rapid mass modification threshold is exceeded'),
('rename_extension_weight', '20', 'Weight assigned for suspicious rename or ransomware extension change'),
('entropy_weight', '18', 'Weight assigned for sudden high Shannon entropy / encryption-like modification'),
('frequency_window_seconds', '3.0', 'Sliding evaluation window in seconds for rapid file activity'),
('frequency_threshold', '10', 'Number of file modifications within the window to trigger frequency indicator'),
('entropy_threshold', '7.2', 'Shannon entropy threshold (0-8 bits/byte) indicating potential encryption'),
('auto_containment_enabled', '0', 'Whether automatic process termination is enabled in authorized test mode')
ON DUPLICATE KEY UPDATE `setting_value`=VALUES(`setting_value`);
