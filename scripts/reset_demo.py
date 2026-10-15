"""
HoneyGuard Demo Reset Script
Cleans up temporary simulated files in demo_workspace/ while preserving original directory layout.
"""

import shutil
from pathlib import Path
from honeyguard.utils.paths import get_demo_workspace


def main():
    print("==================================================================")
    print("      HONEYGUARD DEMO WORKSPACE RESET UTILITY")
    print("==================================================================")

    demo_root = get_demo_workspace()
    for item in demo_root.glob("*/*"):
        if item.is_file() and not item.name.startswith("DEC_"):
            # Check if it was a simulated file
            if "synthetic_document" in item.name or ".locked" in item.name or ".tmp" in item.name:
                try:
                    item.unlink()
                    print(f"[-] Removed simulation artifact: {item.name}")
                except Exception as exc:
                    print(f"[!] Could not remove {item.name}: {exc}")

    print("[+] Workspace reset complete.")


if __name__ == "__main__":
    main()
