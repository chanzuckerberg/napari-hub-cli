import sys
from pathlib import Path

import pytest
import requests
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
                    "jobs_url": f"{BRAINREG2}/joburl",
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
    requests_mock.get(
        f"{BRAINREG2}/joburl",
        json={
            "jobs": [
                {
                    "name": "Running tests",
                    "conclusion": "cancelled",
                    "status": "completed",
                    "labels": ["ubuntu"],
                    "steps":[
                        {
                            "name": "Test with tox",
                            "conclusion": "cancelled",
                            "status": "completed"
                        },
                        {
                            "name": "Install dependencies",
                            "conclusion": "success",
                            "status": "completed"
                        }
                    ]
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
                    "jobs_url": f"{BRAINREG5}/joburl",
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
    requests_mock.get(
        f"{BRAINREG5}/joburl",
        json={
            "jobs": [
                {
                    "name": "Running tests",
                    "conclusion": "success",
                    "status": "completed",
                    "labels": ["ubuntu"],
                    "steps":[
                        {
                            "name": "Test with tox",
                            "conclusion": "success",
                            "status": "completed"
                        },
                        {
                            "name": "Install dependencies",
                            "conclusion": "success",
                            "status": "completed"
                        }
                    ]
                }
            ]
        },
    )
    requests_mock.post(
        f"https://api.codecov.io/graphql/gh",
        json={
            "data": {
                "owner": {
                    "repository": {
                        "branch": {
                            "name": "master",
                            "head": {
                                "totals": {
                                    "percentCovered": 58.53,
                                    "lineCount": 258,
                                    "hitsCount": 151,
                                }
                            },
                        }
                    }
                }
            }
        },
    )
    requests_mock.post(
        f"https://failapi.codecov.io/graphql/gh",
        json={"data": {"owner": {"repository": {"branch": None}}}},
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


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Issue with request mocks on POST for Windows",
)
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
    coverage = ghwd.query_codecov_api()
    assert coverage and coverage == 58.53
    assert ghwd.has_codecove_more_80 is False

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

    # Test unexisting owner
    OLD_URL = GhActionWorkflowFolder.CODECOV_API
    NEW_URL = "https://failapi.codecov.io/graphql/gh"
    GhActionWorkflowFolder.CODECOV_API = NEW_URL

    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-small" / ".github" / "workflows",
        url="https://github.com/_foo/bar_baz",
    )
    coverage = ghwd.query_codecov_api()
    assert coverage is None
    assert ghwd.has_codecove_more_80 is False

    # Test unexisting repo
    ghwd = GhActionWorkflowFolder(
        resources / "CZI-29-small" / ".github" / "workflows",
        url="https://github.com/brainglobe/bar_baz",
    )
    coverage = ghwd.query_codecov_api()
    assert coverage is None
    assert ghwd.has_codecove_more_80 is False

    GhActionWorkflowFolder.CODECOV_API = OLD_URL


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Issue with request mocks on POST for Windows",
)
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
@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Issue with request mocks on POST for Windows",
)
def test_infos_GHWorkflowFolder_testresult_online(resources):
    try:
        ghwd = GhActionWorkflowFolder(
            resources / "conda-infos2" / ".github" / "workflows",
            url="https://github.com/brainglobe/brainreg-napari.git",
        )
        assert ghwd.has_successful_tests is True
        assert ghwd.has_codecove_more_80 is False

        ghwd = GhActionWorkflowFolder(
            resources / "CZI-29-small" / ".github" / "workflows",
            url="https://github.com/PolusAI/bfio",
        )
        assert ghwd.has_successful_tests is False
        assert ghwd.has_codecove_more_80 is False

        ghwd = GhActionWorkflowFolder(
            resources / "conda-infos2" / ".github" / "workflows",
            url="https://github.com/PolarizedLightFieldMicroscopy/napari-LF",
        )
        assert ghwd.has_successful_tests is True
        assert ghwd.has_codecove_more_80 is False

        ghwd = GhActionWorkflowFolder(
            resources / "conda-infos2" / ".github" / "workflows",
            url="https://gitlab.com/Polarizedscopy/napari-LF",
        )
        assert ghwd.has_successful_tests is False
        assert ghwd.has_codecove_more_80 is False
    except requests.exceptions.HTTPError:
        pytest.skip("We probably exceed the github API limit")


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Issue with request mocks on POST for Windows",
)
def test_details_failing_tests(resources, fake_github_api):
    ghwd = GhActionWorkflowFolder(
            resources / "CZI-29-small" / ".github" / "workflows",
            url="https://github.com/brainglobe/brainreg-napari2",
        )

    result = ghwd.details_failing_tests
    assert "ubuntu" in result
    assert "Running tests" in result
    assert "Test with tox" in result


    ghwd = GhActionWorkflowFolder(
            resources / "CZI-29-small" / ".github" / "workflows",
            url="https://github.com/brainglobe/brainreg-napari5",
        )

    result = ghwd.details_failing_tests
    assert result == "None"