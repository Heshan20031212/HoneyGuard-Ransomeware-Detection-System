"""
HoneyGuard Synthetic Decoy Content Templates
Provides realistic business and administrative document templates containing zero sensitive data.
"""

from typing import Dict, List, Any

# Realistic document naming templates categorized by corporate department
TEMPLATE_CATALOG = {
    "Finance": [
        {
            "filename": "Employee_Salary_2026.xlsx",
            "type": "XLSX",
            "title": "Corporate Payroll Summary - FY2026",
            "sheet_name": "Payroll",
            "headers": ["Emp ID", "Department", "Role", "Gross Salary ($)", "Tax ($)", "Net Salary ($)"],
            "rows": [
                ["EMP-1042", "Finance", "Senior Financial Analyst", 6800.0, 1360.0, 5440.0],
                ["EMP-1088", "Marketing", "Campaign Specialist", 5200.0, 1040.0, 4160.0],
                ["EMP-1102", "Operations", "Logistics Coordinator", 4900.0, 980.0, 3920.0],
                ["EMP-1145", "Engineering", "Systems Architect", 8900.0, 1780.0, 7120.0],
                ["EMP-1201", "Human Resources", "Talent Acquisition Lead", 5800.0, 1160.0, 4640.0],
            ]
        },
        {
            "filename": "Financial_Forecast_2027.xlsx",
            "type": "XLSX",
            "title": "Annual Operating Budget & Revenue Projections 2027",
            "sheet_name": "Projections",
            "headers": ["Quarter", "Projected Revenue ($)", "OpEx ($)", "CapEx ($)", "Net Margin (%)"],
            "rows": [
                ["Q1 2027", 1250000.0, 780000.0, 120000.0, 28.0],
                ["Q2 2027", 1420000.0, 810000.0, 95000.0, 36.2],
                ["Q3 2027", 1550000.0, 840000.0, 110000.0, 38.7],
                ["Q4 2027", 1890000.0, 910000.0, 140000.0, 44.4],
            ]
        },
        {
            "filename": "Bank_Account_Summary.xlsx",
            "type": "XLSX",
            "title": "Treasury Account Balances & Liquidity Report",
            "sheet_name": "Treasury",
            "headers": ["Account Name", "Institution", "Currency", "Available Balance", "Status"],
            "rows": [
                ["Operating Reserve", "Metro Commercial Bank", "USD", 485020.50, "ACTIVE"],
                ["Capital Expenditure", "Standard Heritage Bank", "USD", 1250000.00, "RESTRICTED"],
                ["Disbursement Account", "Pacific Global Financial", "USD", 84500.00, "ACTIVE"],
            ]
        }
    ],
    "Legal": [
        {
            "filename": "Legal_Agreement_Draft.pdf",
            "type": "PDF",
            "title": "NON-DISCLOSURE AND MUTUAL CONFIDENTIALITY AGREEMENT",
            "sections": [
                ("1. Purpose", "This Agreement governs the disclosures made between Parties concerning commercial strategic partnerships, proprietary research, and technical specifications."),
                ("2. Confidential Information", "The Receiving Party agrees to retain all synthetic evaluation data in strict confidence and prevent unauthorized access or modification."),
                ("3. Term and Termination", "This commitment remains binding for a period of thirty-six (36) months from the execution timestamp recorded herein."),
                ("4. Governing Jurisdiction", "This synthetic agreement is executed in accordance with international commercial arbitration standards.")
            ]
        },
        {
            "filename": "Client_Contracts_Backup.docx",
            "type": "DOCX",
            "title": "Master Services Agreement - Enterprise Service Delivery",
            "paragraphs": [
                "This Master Services Agreement is entered into by and between Enterprise Solutions Corp and Client Organization.",
                "Scope of Services: Provider shall deliver cybersecurity early-warning infrastructure, canary deployment management, and real-time behavioral telemetry monitoring.",
                "Service Level Guarantees: Monitoring latency shall maintain a threshold under 50 milliseconds across continuous operations.",
                "Data Integrity Obligations: Neither party shall intentionally execute destructive payload modifications on protected production nodes."
            ]
        }
    ],
    "HR": [
        {
            "filename": "Confidential_HR_Report.docx",
            "type": "DOCX",
            "title": "Annual Executive Workforce Review & Retention Strategy",
            "paragraphs": [
                "Executive Summary: Organizational restructuring in FY2026 highlights expanded investments in digital infrastructure defense and cyber resilience capabilities.",
                "Staffing Metrics: Total technical headcount increased by 18.4% across systems engineering, incident handling, and threat containment teams.",
                "Policy Compliance: 99.4% of personnel have completed mandatory information security awareness and anti-phishing simulations.",
                "Recommendation: Continue proactive canary placement in high-tier administrative shared directories."
            ]
        },
        {
            "filename": "Payroll_September_2026.xlsx",
            "type": "XLSX",
            "title": "Staff Payroll Disbursement Schedule - September 2026",
            "sheet_name": "September",
            "headers": ["Employee Name", "Title", "Bank Code", "Net Pay ($)", "Verification"],
            "rows": [
                ["Alex J. Mercer", "Infrastructure Lead", "BK-9021", 6200.0, "VERIFIED"],
                ["Elena V. Rostova", "Security Operations Specialist", "BK-4412", 5900.0, "VERIFIED"],
                ["David K. Silva", "Database Administrator", "BK-8831", 5400.0, "VERIFIED"],
                ["Rachel S. Green", "Legal Counsel", "BK-1109", 7100.0, "VERIFIED"]
            ]
        }
    ],
    "General": [
        {
            "filename": "Management_Notes.txt",
            "type": "TXT",
            "title": "EXECUTIVE STRATEGY BRIEFING NOTES",
            "content": """================================================================================
EXECUTIVE STRATEGY BRIEFING NOTES - FY2026
CLASSIFICATION: INTERNAL CONFIDENTIAL (SYNTHETIC DECOY ASSET)
================================================================================

1. PROJECT STATUS:
   The early-warning ransomware containment program (HoneyGuard) is actively
   protecting shared business directories using randomized canary decoys.

2. OPERATIONAL TARGETS:
   - Early detection prior to mass encryption spread.
   - Low CPU and RAM overhead for continuous endpoint protection.
   - Auditable forensic containment records in relational database.

3. NOTICE:
   This file represents an authorized canary honeytoken. Any unauthorized
   access, modification, renaming, or deletion triggers security telemetry.
================================================================================
"""
        }
    ]
}


def get_available_templates() -> Dict[str, List[Dict[str, Any]]]:
    """Return catalog of synthetic decoy document definitions."""
    return TEMPLATE_CATALOG
