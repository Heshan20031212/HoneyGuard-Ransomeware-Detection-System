"""
HoneyGuard Database Diagnostic Script
Tests MySQL connection, authenticates credentials, inspects tables, and reports health.
"""

import sys
from honeyguard.database.connection import get_db_connection, is_db_connected
from honeyguard.database.schema import check_tables_exist, verify_schema


def main():
    print("==================================================================")
    print("      HONEYGUARD MYSQL DATABASE DIAGNOSTIC UTILITY")
    print("==================================================================")

    if not is_db_connected():
        print("[-] CONNECTION FAILED: Unable to establish connection to MySQL.")
        print("    Troubleshooting steps:")
        print("    1. Verify MySQL / MariaDB service is running (Port 3306 or 3307).")
        print("    2. Verify credentials in .env file (DB_HOST, DB_USER, DB_PASSWORD, DB_PORT).")
        print("    3. Ensure database 'honeyguard_db' has been created.")
        sys.exit(1)

    print("[+] SUCCESS: Connected to MySQL server.")
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT VERSION(), CURRENT_USER(), DATABASE();")
        ver, user, db = cursor.fetchone().values()
        print(f"    • Server Version: {ver}")
        print(f"    • Active User:    {user}")
        print(f"    • Database Name:  {db}")

    tables = check_tables_exist()
    print(f"\n[+] Total Tables Found ({len(tables)}/10):")
    for t in tables:
        print(f"    - {t}")

    if verify_schema():
        print("\n[+] SCHEMA STATUS: HEALTHY (All 10 required tables verified).")
        sys.exit(0)
    else:
        print("\n[!] SCHEMA STATUS: WARNING (Some tables missing).")
        sys.exit(1)


if __name__ == "__main__":
    main()
