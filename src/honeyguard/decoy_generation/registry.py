"""
HoneyGuard Decoy Registry
Manages lifecycle of decoy canary tokens: deployment, hashing, DB persistence, and verification.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from honeyguard.database.repositories import DecoyRepository, DirectoryRepository, AuditLogRepository
from honeyguard.decoy_generation.generator import generate_decoy_file
from honeyguard.decoy_generation.integrity import calculate_file_hash_and_size, verify_decoy_integrity
from honeyguard.decoy_generation.templates import get_available_templates
from honeyguard.utils.logger import get_logger

logger = get_logger("HoneyGuard.DecoyRegistry")


class DecoyRegistry:
    """Central registry and lifecycle manager for honeytoken canary files."""

    @staticmethod
    def deploy_decoy(
        directory_id: int,
        filename: str,
        file_type: str,
        template: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a synthetic decoy file, compute its cryptographic baseline, and register in MySQL.
        """
        dir_record = None
        for d in DirectoryRepository.get_all():
            if d["directory_id"] == directory_id:
                dir_record = d
                break

        if not dir_record:
            raise ValueError(f"Protected directory with ID {directory_id} does not exist in database.")

        target_dir = Path(dir_record["directory_path"])
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / filename

        # Select or generate template
        if not template:
            template = {"title": filename.replace("_", " ").split(".")[0]}

        # Generate on disk
        generate_decoy_file(file_path, file_type, template)

        # Baseline hash and size
        baseline_hash, baseline_size = calculate_file_hash_and_size(file_path)

        # Unique Decoy ID
        decoy_id = f"DEC-{uuid.uuid4().hex[:8].upper()}"

        # Persist to MySQL
        actual_id = DecoyRepository.add_decoy(
            decoy_id=decoy_id,
            directory_id=directory_id,
            filename=filename,
            absolute_path=str(file_path.resolve()),
            file_type=file_type.upper(),
            baseline_hash=baseline_hash,
            baseline_size=baseline_size,
            status="INTACT"
        )

        AuditLogRepository.log(
            action="DECOY_DEPLOYED",
            component="DecoyRegistry",
            description=f"Planted canary {filename} ({file_type}) in {target_dir}",
            severity="INFO",
            success=True
        )

        logger.info(f"Deployed decoy {actual_id} ({filename}) to {target_dir}")
        return DecoyRepository.get_by_id(actual_id)

    @staticmethod
    def deploy_default_canary_pack(directory_id: int, category: str = "Finance") -> List[Dict[str, Any]]:
        """Deploy standard template pack for a given category into a protected directory."""
        templates = get_available_templates().get(category, [])
        deployed = []
        for tmpl in templates:
            dec = DecoyRegistry.deploy_decoy(
                directory_id=directory_id,
                filename=tmpl["filename"],
                file_type=tmpl["type"],
                template=tmpl
            )
            deployed.append(dec)
        return deployed

    @staticmethod
    def verify_decoy(decoy_id: str) -> Dict[str, Any]:
        """Verify the integrity of a specific decoy and update its status in MySQL."""
        decoy = DecoyRepository.get_by_id(decoy_id)
        if not decoy:
            raise ValueError(f"Decoy {decoy_id} not found.")

        current_status = verify_decoy_integrity(decoy)
        DecoyRepository.update_status(decoy_id, current_status, datetime.now())

        if current_status != "INTACT":
            AuditLogRepository.log(
                action="DECOY_INTEGRITY_TAMPERED",
                component="DecoyRegistry",
                description=f"Canary {decoy['filename']} status changed to {current_status}",
                severity="WARNING" if current_status == "ACCESSED" else "CRITICAL",
                success=True
            )

        decoy["status"] = current_status
        return decoy

    @staticmethod
    def verify_all_decoys() -> List[Dict[str, Any]]:
        """Verify the integrity of all registered decoys across all protected directories."""
        all_decoys = DecoyRepository.get_all()
        results = []
        for d in all_decoys:
            res = DecoyRegistry.verify_decoy(d["decoy_id"])
            results.append(res)
        logger.info(f"Verified {len(results)} decoys. Status updated in database.")
        return results

    @staticmethod
    def remove_decoy(decoy_id: str, delete_from_disk: bool = True) -> bool:
        """Remove decoy registration from MySQL and optionally delete physical file."""
        decoy = DecoyRepository.get_by_id(decoy_id)
        if not decoy:
            return False

        if delete_from_disk:
            try:
                p = Path(decoy["absolute_path"])
                if p.exists():
                    p.unlink()
                    logger.info(f"Deleted physical decoy file: {p}")
            except Exception as exc:
                logger.warning(f"Could not delete physical file: {exc}")

        DecoyRepository.remove(decoy_id)
        AuditLogRepository.log(
            action="DECOY_REMOVED",
            component="DecoyRegistry",
            description=f"Removed canary {decoy['filename']} ({decoy_id})",
            severity="INFO",
            success=True
        )
        return True

    @staticmethod
    def list_decoys() -> List[Dict[str, Any]]:
        """Return list of all registered decoys."""
        return DecoyRepository.get_all()
