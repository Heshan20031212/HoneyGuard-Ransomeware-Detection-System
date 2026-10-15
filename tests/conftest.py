"""
HoneyGuard Pytest Configuration and Global Fixtures
"""

import pytest
from pathlib import Path
from honeyguard.utils.paths import get_demo_workspace, get_data_dir


@pytest.fixture(scope="session")
def test_workspace(tmp_path_factory):
    """Temporary workspace isolated for testing."""
    test_dir = tmp_path_factory.mktemp("hg_test_workspace")
    return test_dir


@pytest.fixture(scope="session")
def demo_workspace_dir():
    """Returns the official demo workspace path."""
    return get_demo_workspace()
