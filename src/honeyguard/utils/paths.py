"""
HoneyGuard Path Utilities
Provides portable path resolution and workspace containment validation.
"""

from pathlib import Path
from typing import Union


def get_project_root() -> Path:
    """Return the absolute path to the HoneyGuard project root directory."""
    # From src/honeyguard/utils/paths.py -> 3 levels up to project root
    return Path(__file__).resolve().parent.parent.parent.parent


def get_config_dir() -> Path:
    """Return the configuration directory path."""
    return get_project_root() / "config"


def get_database_dir() -> Path:
    """Return the database scripts directory path."""
    return get_project_root() / "database"


def get_data_dir() -> Path:
    """Return the persistent runtime data directory path."""
    data_dir = get_project_root() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_logs_dir() -> Path:
    """Return the log output directory path."""
    logs_dir = get_data_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_benchmark_results_dir() -> Path:
    """Return the benchmark results directory path."""
    bench_dir = get_data_dir() / "benchmark_results"
    bench_dir.mkdir(parents=True, exist_ok=True)
    return bench_dir


def get_quarantine_dir() -> Path:
    """Return the quarantine directory path."""
    quar_dir = get_data_dir() / "quarantine"
    quar_dir.mkdir(parents=True, exist_ok=True)
    return quar_dir


def get_exports_dir() -> Path:
    """Return the exports directory path."""
    exp_dir = get_data_dir() / "exports"
    exp_dir.mkdir(parents=True, exist_ok=True)
    return exp_dir


def get_demo_workspace() -> Path:
    """Return the authorized demo workspace directory path."""
    demo_dir = get_project_root() / "demo_workspace"
    demo_dir.mkdir(parents=True, exist_ok=True)
    return demo_dir


def is_safe_sandbox_path(target_path: Union[str, Path]) -> bool:
    """
    Verify whether the target path is strictly contained within the authorized demo workspace.
    This prevents accidental modification outside the safe sandbox.
    """
    try:
        resolved_target = Path(target_path).resolve()
        resolved_workspace = get_demo_workspace().resolve()
        return resolved_workspace in resolved_target.parents or resolved_target == resolved_workspace
    except Exception:
        return False
