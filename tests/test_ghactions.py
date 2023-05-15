from pathlib import Path

import pytest
import requests_mock as req

from napari_hub_cli.fs.ghactions import GhActionWorkflow, GhActionWorkflowFolder


@pytest.fixture(scope="module")
def resources():
    return Path(__file__).parent.absolute() / "resources"


BRAINREG = "https://api.github.com/repos/brainglobe/brainreg-napari"
BRAINREG2 = "https://api.github.com/repos/brainglobe/brainreg-napari2"
BRAINREG3 = "https://api.github.com/repos/brainglobe/brainreg-napari3"
BRAINREG4 = "https://api.github.com/repos/brainglobe/brainreg-napari4"
BRAINREG5 = "https://api.github.com/repos/brainglobe/brainreg-napari5"


@pytest.fixture
def fake_github_api(requests_mock):
    requests_mock.get(
        f"{BRAINREG}/actions/runs",
        json={
            "workflow_runs": [
                {
                    "head_branch": "develop",
                    "head_sha": "0b9479313ba94f8733648b7d0af5f4f1fc993807",
                    "path": ".github/workflows/test_main.yml",
                    "status": "running",
                    "conclusion": "success",
                },
                {
                    "head_branch": "main",
                    "head_sha": "d65a2a972f439413ea1f5229b501c38036e66b36",
                    "path": ".github/workflows/test_main.yml",
                    "status": "completed",
                    "conclusion": "success",
                },
            ]
        },
    )
    requests_mock.get(
        f"{BRAINREG}/commits/d65a2a972f439413ea1f5229b501c38036e66b36/status",
        json={
            "statuses": [
                {
                    "description": "97.82% (+0.00%) compared to d65a2a9",
                    "context": "codecov/project",
                }
            ]
        },
    )
    # Second URL
    requests_mock.get(
        f"{BRAINREG2}/actions/runs",
        json={
            "workflow_runs": [
                {
                    "head_branch": "develop",
                    "head_sha": "0b9479313ba94f8733648b7d0af5f4f1fc993807",
                    "path": ".github/workflows/test_main.yml",
                    "status": "completed",
                    "conclusion": "success",
                },
                {
                    "head_branch": "master",
                    "head_sha": "MYCOMMIT",
                    "path": ".github/workflows/test_main.yml",
                    "status": "completed",
                    "conclusion": "failed",
                },
            ]
        },
    )
    requests_mock.get(
        f"{BRAINREG2}/commits/MYCOMMIT/status",
        json={
            "statuses": [
                {
                    "description": "55.04%",
                    "context": "codecov/project",
                }
            ]
        },
    )
    # Third URL
    requests_mock.get(
        f"{BRAINREG3}/actions/runs",
        json={
            "workflow_runs": [
                {
                    "head_branch": "develop",
                    "head_sha": "0b9479313ba94f8733648b7d0af5f4f1fc993807",
                    "path": ".github/workflows/test_main.yml",
                    "status": "completed",
                    "conclusion": "success",
                },
                {
                    "head_branch": "develop",
                    "head_sha": "d65a2a972f439413ea1f5229b501c38036e66b36",
                    "path": ".github/workflows/test_main.yml",
                    "status": "completed",
                    "conclusion": "success",
                },
            ]
        },
    )
    # Fourth URL
    requests_mock.get(
        f"{BRAINREG4}/actions/runs",
        json={
            "workflow_runs": [
                {
                    "head_branch": "develop",
                    "head_sha": "MYCOMMIT2",
                    "path": ".github/workflows/test_main.yml",
                    "status": "completed",
                    "conclusion": "success",
                },
                {
                    "head_branch": "main",
                    "head_sha": "MYCOMMIT",
                    "path": ".github/workflows/test_main.yml",
                    "status": "completed",
                    "conclusion": "fail",
                },
            ]
        },
    )
    requests_mock.get(
        f"{BRAINREG4}/commits/MYCOMMIT/status",
        json={
            "statuses": [
                {
                    "description": "55.04%",
                    "context": "othercoveragetool/project",
                }
            ]
        },
    )
    # Fifth URL
    requests_mock.get(
        f"{BRAINREG5}/actions/runs",
        json={
            "workflow_runs": [
                {
                    "head_branch": "develop",
                    "head_sha": "MYCOMMIT2",
                    "path": ".github/workflows/test_main.yml",
                    "status": "completed",
                    "conclusion": "success",
                },
                {
                    "head_branch": "main",
                    "head_sha": "MYCOMMIT",
                    "path": ".github/workflows/test_main.yml",
                    "status": "completed",
                    "conclusion": "success",
                },
            ]
        },
    )
    requests_mock.get(
        f"{BRAINREG5}/commits/MYCOMMIT/status",
        json={
            "statuses": [
                {
                    "description": "no value",
                    "context": "codecov/project",
                }
            ]
        },
    )
    return requests_mock


def test_infos_GHWorkflowFolder(resources):
    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-small" / ".github" / "workflows", url=None
    )

    assert ghwd.exists is True
    assert len(ghwd.workflows) == 1
    assert ghwd.workflows[0].file.name == "test_main.yml"
    assert ghwd.gh_test_config
    assert ghwd.gh_test_config.file.name == "test_main.yml"
    assert ghwd.gh_codecov_config
    assert ghwd.gh_codecov_config.file.name == "test_main.yml"

    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-faulty" / ".github" / "workflows", url=None
    )

    assert ghwd.exists is True
    assert len(ghwd.workflows) == 1
    assert ghwd.workflows[0].file.name == "config_random.yml"
    assert ghwd.gh_test_config is None
    assert ghwd.gh_codecov_config
    assert ghwd.gh_codecov_config.file.name == "config_random.yml"

    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-test" / ".github" / "workflows", url=None
    )

    assert ghwd.exists is False
    assert ghwd.workflows == []
    assert ghwd.gh_codecov_config is None
    assert ghwd.gh_test_config is None


def test_infos_GHTests(resources):
    ghw = GhActionWorkflow(
        resources / "CZI-29-small" / ".github" / "workflows" / "test_main.yml"
    )

    assert ghw.defines_test is True
    assert ghw.supported_python_version == [(3, 7), (3, 8), (3, 9), (3, 10)]
    assert ghw.defines_codecov_coverage is True


def test_infos_GHTests2(resources):
    ghw = GhActionWorkflow(
        resources / "CZI-29-faulty" / ".github" / "workflows" / "config_random.yml"
    )

    assert ghw.defines_test is False
    assert ghw.supported_python_version == []
    assert ghw.defines_codecov_coverage is True


def test_infos_GHTests3(resources):
    ghw = GhActionWorkflow(
        resources / "conda-infos1" / ".github" / "workflows" / "test.yml"
    )

    assert ghw.defines_test is True
    assert ghw.supported_python_version == [(3, 9)]
    assert ghw.defines_codecov_coverage is False


def test_infos_GHTests4(resources):
    ghw = GhActionWorkflow(
        resources / "conda-infos2" / ".github" / "workflows" / "test_and_deploy.yml"
    )

    assert ghw.defines_test is True
    assert ghw.supported_python_version == [(3, 8), (3, 9), (3, 10)]
    assert ghw.defines_codecov_coverage is False


def test_infos_GHWorkflowFolder_codecov(resources, fake_github_api):
    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-small" / ".github" / "workflows",
        url="https://gitlab.com/brainglobe/brainreg-napari.git",
    )
    coverage = ghwd.query_codecov_result()
    assert coverage is None
    assert ghwd.has_codecove_more_80 is False

    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-small" / ".github" / "workflows",
        url="https://github.com/brainglobe/brainreg-napari.git",
    )
    coverage = ghwd.query_codecov_result()
    assert coverage and coverage == 97.82
    assert ghwd.has_codecove_more_80 is True

    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-small" / ".github" / "workflows",
        url="https://github.com/brainglobe/brainreg-napari2",
    )
    coverage = ghwd.query_codecov_result()
    assert coverage and coverage == 55.04
    assert ghwd.has_codecove_more_80 is False

    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-small" / ".github" / "workflows",
        url="https://github.com/brainglobe/brainreg-napari3",
    )
    coverage = ghwd.query_codecov_result()
    assert coverage is None
    assert ghwd.has_codecove_more_80 is False

    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-small" / ".github" / "workflows",
        url="https://github.com/brainglobe/brainreg-napari4",
    )
    coverage = ghwd.query_codecov_result()
    assert coverage is None
    assert ghwd.has_codecove_more_80 is False

    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-small" / ".github" / "workflows",
        url="https://github.com/brainglobe/brainreg-napari5",
    )
    coverage = ghwd.query_codecov_result()
    assert coverage is None
    assert ghwd.has_codecove_more_80 is False


def test_infos_GHWorkflowFolder_testresult(resources, fake_github_api):
    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-small" / ".github" / "workflows",
        url="https://gitlab.com/brainglobe/brainreg-napari.git",
    )
    assert ghwd.has_successful_tests is False

    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-small" / ".github" / "workflows",
        url="https://github.com/brainglobe/brainreg-napari.git",
    )
    assert ghwd.has_successful_tests is True

    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-small" / ".github" / "workflows",
        url="https://github.com/brainglobe/brainreg-napari2",
    )
    assert ghwd.has_successful_tests is False

    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-small" / ".github" / "workflows",
        url="https://github.com/brainglobe/brainreg-napari3",
    )
    assert ghwd.has_successful_tests is False

    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-small" / ".github" / "workflows",
        url="https://github.com/brainglobe/brainreg-napari4",
    )
    assert ghwd.has_successful_tests is False

    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-small" / ".github" / "workflows",
        url="https://github.com/brainglobe/brainreg-napari5",
    )
    assert ghwd.has_successful_tests is True


@pytest.mark.online
def test_infos_GHWorkflowFolder_testresult_online(resources):
    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-small" / ".github" / "workflows",
        url="https://github.com/brainglobe/brainreg-napari.git",
    )
    assert ghwd.has_successful_tests is True
    assert ghwd.has_codecove_more_80 is False

    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-small" / ".github" / "workflows",
        url="https://github.com/PolusAI/bfio",
    )
    assert ghwd.has_successful_tests is True
    assert ghwd.has_codecove_more_80 is False
