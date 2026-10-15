-- ==============================================================================
-- HONEYGUARD - SAMPLE / DEMO DATA (FOR DEMO AND PRESENTATION PURPOSES ONLY)
-- NOTICE: THIS FILE CONTAINS SYNTHETIC DEMONSTRATION DATA.
-- ALL BENCHMARK MEASUREMENTS AND TEST EVIDENCE IN THE RESEARCH EVALUATION MUST
-- ORIGINATE FROM GENUINE TEST EXECUTION, NOT FROM THIS DEMO SCRIPT.
-- ==============================================================================

USE `honeyguard_db`;

-- Demo Protected Directory
INSERT INTO `protected_directories` (`directory_id`, `directory_path`, `display_name`, `monitoring_enabled`)
VALUES (1, 'C:\\Users\\LENOVO\\OneDrive\\Desktop\\HoneyGuard project folder\\demo_workspace\\Finance', 'Finance Department Shared Workspace', 1)
ON DUPLICATE KEY UPDATE `display_name`=VALUES(`display_name`);

-- Demo Decoys
INSERT INTO `decoys` (`decoy_id`, `directory_id`, `filename`, `absolute_path`, `file_type`, `baseline_hash`, `baseline_size`, `status`, `monitoring_enabled`)
VALUES
('DEC-DEMO-001', 1, 'Employee_Salary_2026.xlsx', 'C:\\Users\\LENOVO\\OneDrive\\Desktop\\HoneyGuard project folder\\demo_workspace\\Finance\\Employee_Salary_2026.xlsx', 'XLSX', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 8420, 'INTACT', 1),
('DEC-DEMO-002', 1, 'Financial_Forecast_2027.xlsx', 'C:\\Users\\LENOVO\\OneDrive\\Desktop\\HoneyGuard project folder\\demo_workspace\\Finance\\Financial_Forecast_2027.xlsx', 'XLSX', 'ca978112ca1bbdcafac231b39a23dc4da786081cd1e14b5357a6e78117387182', 9150, 'INTACT', 1),
('DEC-DEMO-003', 1, 'Client_Contracts_Backup.docx', 'C:\\Users\\LENOVO\\OneDrive\\Desktop\\HoneyGuard project folder\\demo_workspace\\Finance\\Client_Contracts_Backup.docx', 'DOCX', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 12300, 'INTACT', 1)
ON DUPLICATE KEY UPDATE `status`=VALUES(`status`);

-- Demo Audit Log
INSERT INTO `audit_logs` (`timestamp`, `action`, `component`, `description`, `severity`, `success`)
VALUES
(NOW(3), 'DEMO_DATA_LOADED', 'Database', 'Synthetic demo data loaded for presentation inspection in phpMyAdmin', 'INFO', 1);
