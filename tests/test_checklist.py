
from pathlib import Path
import pytest
from napari_hub_cli.checklist.projectquality import suite_generator, NUMBER_DEPENDENCIES, INSTALLABLE_LINUX
from napari_hub_cli.fs import NapariPlugin


@pytest.fixture(scope="module")
def test_repo():
    current_path = Path(__file__).parent.absolute()
    return NapariPlugin(current_path / "resources" / "CZI-29-faulty")


def test_project_quality_nodeps(test_repo):

    suite = suite_generator(test_repo)

    requirement = next((r for r in suite.requirements if INSTALLABLE_LINUX in r.features), None)
    additional = next((r for r in suite.additionals if NUMBER_DEPENDENCIES in r.features), None)

    assert requirement
    assert requirement.main_files != []
    assert additional
    assert additional.main_files != []


    suite = suite_generator(test_repo, disable_pip_based_requirements=True)

    requirement = next((r for r in suite.requirements if INSTALLABLE_LINUX in r.features), None)
    additional = next((r for r in suite.additionals if NUMBER_DEPENDENCIES in r.features), None)

    assert requirement
    assert requirement.main_files == []
    assert additional
    assert additional.main_files == []




