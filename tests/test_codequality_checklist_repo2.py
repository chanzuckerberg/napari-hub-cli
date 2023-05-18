from pathlib import Path

import pytest

from napari_hub_cli.autofix import build_issue_message
from napari_hub_cli.checklist import analyse_local_plugin, display_checklist
from napari_hub_cli.checklist.projectquality import project_quality_suite
from napari_hub_cli.fs import NapariPlugin

_, SUITE = project_quality_suite


@pytest.fixture(scope="module")
def test_repo():
    current_path = Path(__file__).parent.absolute()
    return NapariPlugin(current_path / "resources" / "CZI-29-faulty")


# smoke test
def test_display_checklist(test_repo):
    result = analyse_local_plugin(test_repo.path, SUITE)
    display_checklist(result)
