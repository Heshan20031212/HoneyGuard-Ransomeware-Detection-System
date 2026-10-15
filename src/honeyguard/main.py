"""
HoneyGuard Application Entrypoint
Module: IE3092 — Information Security Project | Group 15
Sri Lanka Institute of Information Technology (SLIIT)
"""

import sys
import argparse
from pathlib import Path

from honeyguard.database.connection import is_db_connected
from honeyguard.database.schema import initialize_schema_if_needed, verify_schema
from honeyguard.database.repositories import DirectoryRepository
from honeyguard.decoy_generation.registry import DecoyRegistry
from honeyguard.ui.main_window import HoneyGuardMainWindow
from honeyguard.utils.logger import setup_logger
from honeyguard.utils.paths import get_demo_workspace, get_project_root

logger = setup_logger("HoneyGuard.Main")


def initialize_environment():
    """Ensure required database schema and demo directories are prepared."""
    logger.info("Initializing HoneyGuard environment...")

    # Initialize demo directories
    demo_base = get_demo_workspace()
    for dept in ("Finance", "HR", "Legal", "General"):
        dept_path = demo_base / dept
        dept_path.mkdir(parents=True, exist_ok=True)

    # Check and initialize MySQL database schema
    if is_db_connected():
        logger.info("MySQL connection verified. Verifying schema...")
        initialize_schema_if_needed()

        # Seed initial protected directory if none registered
        dirs = DirectoryRepository.get_all()
        if not dirs:
            finance_dir = str(demo_base / "Finance")
            dir_id = DirectoryRepository.add_directory(finance_dir, "Finance Department (Demo Workspace)", True)
            logger.info(f"Registered initial protected directory: {finance_dir}")

            # Deploy initial canaries
            try:
                deployed = DecoyRegistry.deploy_default_canary_pack(dir_id, "Finance")
                logger.info(f"Deployed {len(deployed)} initial canary files into Finance directory.")
            except Exception as d_exc:
                logger.warning(f"Notice on initial canary deployment: {d_exc}")
    else:
        logger.warning(
            "DATABASE WARNING: MySQL is currently not reachable on configured port.\n"
            "HoneyGuard will launch in limited mode. Please ensure MySQL/XAMPP is running "
            "and database 'honeyguard_db' is created as documented in docs/phpmyadmin_setup.md"
        )


def main():
    parser = argparse.ArgumentParser(description="HoneyGuard - Honeytoken-Based Ransomware Detection & Prevention System")
    parser.add_argument("--benchmark", action="store_true", help="Execute 5-trial benchmark suite in CLI mode")
    parser.add_argument("--test-db", action="store_true", help="Test MySQL database connectivity and exit")
    parser.add_argument("--reset-demo", action="store_true", help="Reset demo workspace and seed fresh canaries")
    args = parser.parse_args()

    # DB Connection Test Mode
    if args.test_db:
        connected = is_db_connected()
        if connected:
            print("SUCCESS: Connected to MySQL database 'honeyguard_db'.")
            schema_ok = verify_schema()
            print(f"SCHEMA STATUS: {'ALL 10 TABLES VERIFIED' if schema_ok else 'SOME TABLES MISSING'}")
            sys.exit(0)
        else:
            print("ERROR: Cannot connect to MySQL database. Please verify credentials in .env and ensure MySQL is running.")
            sys.exit(1)

    # CLI Benchmark Mode
    if args.benchmark:
        initialize_environment()
        from honeyguard.analytics.benchmark import BenchmarkSuite
        print("Starting HoneyGuard 5-Trial Evaluation Suite across TC01–TC07...")
        suite = BenchmarkSuite(trials_per_scenario=5)
        res = suite.execute_full_suite()
        print(f"BENCHMARK COMPLETED: {res}")
        sys.exit(0)

    # Demo Reset Mode
    if args.reset_demo:
        initialize_environment()
        print("Demo workspace initialized and canaries seeded.")
        sys.exit(0)

    # Standard Desktop GUI Launch
    initialize_environment()
    app = HoneyGuardMainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
