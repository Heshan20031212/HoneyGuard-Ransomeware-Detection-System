"""
HoneyGuard Safe Ransomware-Like Simulator
AUTHORIZED FOR ACADEMIC TESTING IN DEMO WORKSPACE ONLY.
Strict Safeguards:
- Refuses to operate outside demo_workspace/
- Modifies ONLY disposable synthetic test files
- Contains ZERO malicious payloads, persistence, or network activity
- Provides Dry-Run mode
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any

from honeyguard.utils.logger import get_logger
from honeyguard.utils.paths import get_demo_workspace, is_safe_sandbox_path

logger = get_logger("HoneyGuard.Simulator")


class SafeSimulator:
    """Safe, sandboxed ransomware behavioural simulation utility."""

    def __init__(self, target_directory: Path = None, dry_run: bool = False):
        self.target_dir = target_directory or (get_demo_workspace() / "Finance")
        self.dry_run = dry_run

        # Strict validation
        if not is_safe_sandbox_path(self.target_dir):
            raise PermissionError(
                f"SAFETY VIOLATION: Simulator target '{self.target_dir}' is OUTSIDE the authorized demo_workspace! Execution refused."
            )

    def prepare_synthetic_files(self, count: int = 15) -> List[Path]:
        """Create disposable synthetic test files for simulation."""
        self.target_dir.mkdir(parents=True, exist_ok=True)
        created_files = []
        for i in range(1, count + 1):
            file_path = self.target_dir / f"synthetic_document_{i:02d}.txt"
            if not self.dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"Standard synthetic corporate document record #{i}\n" * 10)
            created_files.append(file_path)

        logger.info(f"Prepared {len(created_files)} synthetic files in {self.target_dir}")
        return created_files

    def run_mass_modification(self, count: int = 12, delay_between_files: float = 0.05) -> Dict[str, Any]:
        """Simulate rapid modification across multiple synthetic files."""
        files = self.prepare_synthetic_files(count)
        start_time = time.time()
        modified = 0

        logger.info(f"Starting Safe Mass Modification simulation (Dry Run: {self.dry_run})...")
        for f in files:
            if not self.dry_run:
                with open(f, "a", encoding="utf-8") as fh:
                    fh.write(f"\n[SIMULATED MODIFICATION TIMESTAMP: {time.time()}]\n")
            modified += 1
            if delay_between_files > 0:
                time.sleep(delay_between_files)

        duration = time.time() - start_time
        return {
            "simulation": "MASS_MODIFICATION",
            "files_modified": modified,
            "duration_seconds": round(duration, 3),
            "dry_run": self.dry_run
        }

    def run_rename_extension_simulation(self, count: int = 10, new_extension: str = ".locked") -> Dict[str, Any]:
        """Simulate ransomware-style extension change across synthetic files."""
        files = self.prepare_synthetic_files(count)
        renamed = 0
        start_time = time.time()

        logger.info(f"Starting Safe Extension Change simulation ({new_extension})...")
        for f in files:
            target_renamed = f.with_suffix(new_extension)
            if not self.dry_run:
                if f.exists():
                    if target_renamed.exists():
                        target_renamed.unlink()
                    f.rename(target_renamed)
            renamed += 1
            time.sleep(0.05)

        duration = time.time() - start_time
        return {
            "simulation": "RENAME_EXTENSION",
            "files_renamed": renamed,
            "duration_seconds": round(duration, 3),
            "dry_run": self.dry_run
        }

    def run_encryption_simulation(self, count: int = 10, target_decoy: Path = None) -> Dict[str, Any]:
        """
        Simulate encryption by replacing content with high-entropy bytes (os.urandom).
        Optionally touches a decoy file to trigger composite risk scoring.
        """
        files = self.prepare_synthetic_files(count)
        encrypted_count = 0
        start_time = time.time()

        # If a decoy is targeted, include it
        if target_decoy and target_decoy.exists():
            files.insert(0, target_decoy)

        logger.info("Starting Safe Encryption Simulation (High-Entropy Synthetic Payload)...")
        for f in files:
            if not self.dry_run:
                # High entropy random bytes (approaching 8.0 bits/byte)
                synthetic_ciphertext = os.urandom(2048)
                with open(f, "wb") as fh:
                    fh.write(synthetic_ciphertext)
            encrypted_count += 1
            time.sleep(0.04)

        duration = time.time() - start_time
        return {
            "simulation": "ENCRYPTION_SIMULATION",
            "files_encrypted": encrypted_count,
            "duration_seconds": round(duration, 3),
            "dry_run": self.dry_run
        }


def main():
    parser = argparse.ArgumentParser(description="HoneyGuard Safe Ransomware Simulator (Sandbox Only)")
    parser.add_argument("--mode", choices=["modify", "rename", "encrypt"], default="encrypt")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without writing to disk")
    parser.add_argument("--count", type=int, default=12, help="Number of files to process")
    args = parser.parse_args()

    print("=================================================================")
    print("  HONEYGUARD AUTHORIZED SAFE RANSOMWARE-LIKE SIMULATOR")
    print("  NOTICE: FOR ISOLATED TESTING ONLY IN demo_workspace/")
    print(f"  MODE: {args.mode.upper()} | DRY RUN: {args.dry_run} | COUNT: {args.count}")
    print("=================================================================")

    sim = SafeSimulator(dry_run=args.dry_run)
    if args.mode == "modify":
        res = sim.run_mass_modification(count=args.count)
    elif args.mode == "rename":
        res = sim.run_rename_extension_simulation(count=args.count)
    elif args.mode == "encrypt":
        res = sim.run_encryption_simulation(count=args.count)

    print("SIMULATION COMPLETED SUCCESSFULLY:")
    for k, v in res.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
