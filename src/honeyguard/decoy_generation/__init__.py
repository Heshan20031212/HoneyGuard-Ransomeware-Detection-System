"""HoneyGuard Decoy Generation Package"""
from honeyguard.decoy_generation.generator import generate_decoy_file
from honeyguard.decoy_generation.integrity import calculate_file_hash_and_size, verify_decoy_integrity
from honeyguard.decoy_generation.registry import DecoyRegistry
from honeyguard.decoy_generation.templates import get_available_templates

__all__ = [
    "generate_decoy_file",
    "calculate_file_hash_and_size",
    "verify_decoy_integrity",
    "DecoyRegistry",
    "get_available_templates"
]
