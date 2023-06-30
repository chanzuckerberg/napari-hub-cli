from pathlib import Path

import pytest
import requests_mock

from napari_hub_cli.checklist.analysis import (
    DEFAULT_SUITE,
    analyse_remote_plugin,
    analyze_remote_plugins,
    build_csv_dict,
    display_remote_analysis,
    write_csv,
)
from napari_hub_cli.checklist.metadata import (
    AnalysisStatus,
    PluginAnalysisResult,
    analyse_local_plugin,
)
from napari_hub_cli.constants import NAPARI_HUB_API_URL
from napari_hub_cli.utils import (
    NonExistingNapariPluginError,
    closest_plugin_name,
    get_repository_url,
)

_, DEFAULT_SUITE = DEFAULT_SUITE


@pytest.fixture
def napari_hub(requests_mock):
    requests_mock.get(
        NAPARI_HUB_API_URL,
        json={
            "avidaq": "0.0.5",
            "mikro-napari": "0.1.49",
            "napari-curtain": "0.1.1",
        },
    )
    return requests_mock


def test_closest_plugin_name(napari_hub):
    assert closest_plugin_name("avidaq") == "avidaq"
    assert closest_plugin_name("avida") == "avidaq"
    assert closest_plugin_name("foo") is None


def test_analysis_unexisting_plugin(napari_hub):
    napari_hub.get(
        f"{NAPARI_HUB_API_URL}/avida",
        json={},
    )

    with pytest.raises(NonExistingNapariPluginError) as e:
        get_repository_url("avida")

    assert e.value.plugin_name == "avida"
    assert e.value.closest == "avidaq"

    napari_hub.get(f"{NAPARI_HUB_API_URL}/avidal", json={}, status_code=404)

    with pytest.raises(NonExistingNapariPluginError) as e:
        get_repository_url("avidal")

    assert e.value.plugin_name == "avidal"
    assert e.value.closest == "avidaq"


def test_get_plugin_url(napari_hub):
    napari_hub.get(
        f"{NAPARI_HUB_API_URL}/avidaq",
        json={"code_repository": "my_repo_url"},
    )

    url = get_repository_url("avidaq")

    assert url == "my_repo_url"


def test_no_result_analysis():
    result = PluginAnalysisResult.with_status(
        AnalysisStatus.UNACCESSIBLE_REPOSITORY, title="my list"
    )

    assert result.features == []
    assert result.status is AnalysisStatus.UNACCESSIBLE_REPOSITORY
    assert result.url is None
    assert result.repository is None
    assert result.title == "my list"


def test_analyse_remote_plugin_bad_url(napari_hub):
    napari_hub.get(
        f"{NAPARI_HUB_API_URL}/avidaq",
        json={"code_repository": "http://my_repo_url"},
    )
    napari_hub.get(
        "http://my_repo_url",
        json={},
    )
    results = analyse_remote_plugin("avidaq", display_info=False)

    assert results.status is AnalysisStatus.BAD_URL


def test_analyse_remote_plugin_unaccessible(napari_hub):
    napari_hub.get(
        f"{NAPARI_HUB_API_URL}/avidaq",
        json={"code_repository": "http://my_repo_url"},
    )
    napari_hub.get("http://my_repo_url", json={}, status_code=404)
    results = analyse_remote_plugin("avidaq", display_info=False)

    assert results.status is AnalysisStatus.UNACCESSIBLE_REPOSITORY


# integration test
def test_display_remote_analysis(napari_hub):
    napari_hub.get(
        f"{NAPARI_HUB_API_URL}/avidaq",
        json={"code_repository": "http://my_repo_url"},
    )
    napari_hub.get("http://my_repo_url", json={}, status_code=404)
    results = display_remote_analysis("avidaq")

    assert results is False


# integration test
def test_analyze_all_remote_plugins(napari_hub):
    napari_hub.get(
        f"{NAPARI_HUB_API_URL}/avidaq",
        json={"code_repository": "http://my_repo_url"},
    )
    napari_hub.get(
        f"{NAPARI_HUB_API_URL}/mikro-napari",
        json={"code_repository": ""},
    )
    napari_hub.get(
        f"{NAPARI_HUB_API_URL}/napari-curtain",
        json={"code_repository": "http://my_repo_url"},
    )
    napari_hub.get(
        "http://my_repo_url",
        json={},
    )
    results = analyze_remote_plugins(all_plugins=True)

    assert list(results.keys()) == ["avidaq", "mikro-napari", "napari-curtain"]

    results = analyze_remote_plugins(all_plugins=True, display_info=True)

    assert list(results.keys()) == ["avidaq", "mikro-napari", "napari-curtain"]

    results = analyze_remote_plugins(plugins_name=["avidaq"], display_info=True)

    assert list(results.keys()) == ["avidaq"]

    results = analyze_remote_plugins(plugins_name=[], display_info=True)

    assert list(results.keys()) == []


def test_build_csv_empty():
    assert build_csv_dict({}) == []
    assert build_csv_dict(None) == []


def test_build_csv():
    current_path = Path(__file__).parent.absolute()
    checklist = analyse_local_plugin(
        current_path / "resources/CZI-29-test", DEFAULT_SUITE
    )
    rows = build_csv_dict({"CZI-29-test": checklist})

    assert rows != []


def test_write_csv_empty(tmp_path):
    output = tmp_path / "output.csv"

    write_csv([], output)

    assert output.exists() is False


def test_write_csv(tmp_path):
    output = tmp_path / "output.csv"
    current_path = Path(__file__).parent.absolute()
    checklist = analyse_local_plugin(
        current_path / "resources/CZI-29-test", DEFAULT_SUITE
    )
    rows = build_csv_dict({"CZI-29-test": checklist})

    write_csv(rows, output)

    assert output.exists() is True


def test_analysis_local_directory(napari_hub, tmp_path):
    napari_hub.get(
        f"{NAPARI_HUB_API_URL}/avidaq",
        json={"code_repository": "http://my_repo_url"},
    )
    napari_hub.get(
        "http://my_repo_url",
        json={},
    )

    p = tmp_path / "inside"
    p.mkdir()
    analyse_remote_plugin("avidaq", display_info=False, directory=p)

    assert p.exists() is False

    analyse_remote_plugin("avidaq", display_info=False, directory=p, cleanup=False)
    assert p.exists() is True


@pytest.mark.online
def test_closest_plugin_name__online():
    assert closest_plugin_name("avidaq") == "avidaq"
    assert closest_plugin_name("avida") == "avidaq"
    assert closest_plugin_name("foo") is None


@pytest.mark.online
def test_analysis_unexisting_plugin__online():
    with pytest.raises(NonExistingNapariPluginError) as e:
        get_repository_url("avida")

    assert e.value.plugin_name == "avida"
    assert e.value.closest == "avidaq"


@pytest.mark.online
def test_get_plugin_url__online():
    url = get_repository_url("PartSeg")

    assert url == "https://github.com/4DNucleome/PartSeg"


@pytest.mark.parametrize(
    "name, status",
    [
        ("avidaq", AnalysisStatus.MISSING_URL),
        ("mikro-napari", AnalysisStatus.SUCCESS),
        ("foo", AnalysisStatus.NON_EXISTING_PLUGIN),
    ],
)
@pytest.mark.online
def test_analyse_remote_plugin__online(name, status):
    results = analyse_remote_plugin(name, display_info=False)

    assert results.status is status
