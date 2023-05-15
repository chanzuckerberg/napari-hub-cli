from pathlib import Path
import pytest

from napari_hub_cli.fs.ghactions import GhActionWorkflow, GhActionWorkflowFolder


@pytest.fixture(scope="module")
def resources():
    return Path(__file__).parent.absolute() / "resources"


def test_infos_GHWorkflowFolder(resources):
    ghwd = GhActionWorkflowFolder(resources  / 'CZI-29-small' / '.github' / 'workflows')

    assert ghwd.exists is True
    assert len(ghwd.workflows) == 1
    assert ghwd.workflows[0].file.name == 'test_main.yml'


    ghwd = GhActionWorkflowFolder(resources  / 'CZI-29-faulty' / '.github' / 'workflows')

    assert ghwd.exists is True
    assert len(ghwd.workflows) == 1
    assert ghwd.workflows[0].file.name == 'config_random.yml'


    ghwd = GhActionWorkflowFolder(resources  / 'CZI-29-test' / '.github' / 'workflows')

    assert ghwd.exists is False
    assert ghwd.workflows == []


def test_infos_GHTests(resources):
    ghw = GhActionWorkflow(resources / 'CZI-29-small' / '.github' / 'workflows' / 'test_main.yml')

    assert ghw.defines_test is True
    assert ghw.supported_python_version == [(3,  7), (3,  8), (3,  9), (3,  10)]
    assert ghw.defines_codecov_coverage is True


def test_infos_GHTests2(resources):
    ghw = GhActionWorkflow(resources / 'CZI-29-faulty' / '.github' / 'workflows' / 'config_random.yml')

    assert ghw.defines_test is False
    assert ghw.supported_python_version == []
    assert ghw.defines_codecov_coverage is True