"""
HoneyGuard Demo Environment Creator
Prepares demo workspace directories (Finance, HR, Legal, General),
seeds realistic synthetic business files, and deploys canary decoys.
"""

from pathlib import Path
from honeyguard.database.repositories import DirectoryRepository
from honeyguard.decoy_generation.registry import DecoyRegistry
from honeyguard.utils.paths import get_demo_workspace


def main():
    print("==================================================================")
    print("      HONEYGUARD DEMO ENVIRONMENT SETUP UTILITY")
    print("==================================================================")

    demo_root = get_demo_workspace()
    departments = [
        ("Finance", "Finance Department Workspace"),
        ("HR", "Human Resources Directory"),
        ("Legal", "Legal & Contracts Share"),
        ("General", "General Operations Archive")
    ]

    for dept, name in departments:
        dept_path = demo_root / dept
        dept_path.mkdir(parents=True, exist_ok=True)
        print(f"[+] Setting up workspace: {dept_path}")

        # Register in database
        dir_id = DirectoryRepository.add_directory(str(dept_path.resolve()), name, True)

        # Deploy realistic canary files
        deployed = DecoyRegistry.deploy_default_canary_pack(dir_id, dept)
        print(f"    Deployed {len(deployed)} canaries for {dept}:")
        for dec in deployed:
            print(f"      - {dec['filename']} ({dec['file_type']}) -> {dec['decoy_id']}")

    print("\n[+] DEMO ENVIRONMENT SETUP COMPLETE!")


if __name__ == "__main__":
    main()
