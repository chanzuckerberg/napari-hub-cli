import pytest
import requests_mock

from napari_hub_cli.constants import NAPARI_HUB_API_LINK
from napari_hub_cli.documentation_checklist.metadata_checklist import (
    AnalysisStatus,
    PluginAnalysisResult,
)
from napari_hub_cli.utils import (
    NonExistingNapariPluginError,
    closest_plugin_name,
    get_repository_url,
)


@pytest.fixture
def napari_hub(requests_mock):
    requests_mock.get(
        NAPARI_HUB_API_LINK,
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


@pytest.mark.online
def test_closest_plugin_name__online():

    assert closest_plugin_name("avidaq") == "avidaq"
    assert closest_plugin_name("avida") == "avidaq"
    assert closest_plugin_name("foo") is None


def test_analysis_unexisting_plugin(napari_hub):
    napari_hub.get(
        f"{NAPARI_HUB_API_LINK}/avida",
        json={},
    )

    with pytest.raises(NonExistingNapariPluginError) as e:
        get_repository_url("avida")

    assert e.value.plugin_name == "avida"
    assert e.value.closest == "avidaq"

    napari_hub.get(f"{NAPARI_HUB_API_LINK}/avidal", json={}, status_code=404)

    with pytest.raises(NonExistingNapariPluginError) as e:
        get_repository_url("avidal")

    assert e.value.plugin_name == "avidal"
    assert e.value.closest == "avidaq"


@pytest.mark.online
def test_analysis_unexisting_plugin__online():
    with pytest.raises(NonExistingNapariPluginError) as e:
        get_repository_url("avida")

    assert e.value.plugin_name == "avida"
    assert e.value.closest == "avidaq"


def test_get_plugin_url(napari_hub):
    napari_hub.get(
        f"{NAPARI_HUB_API_LINK}/avidaq",
        json={"code_repository": "my_repo_url"},
    )

    url = get_repository_url("avidaq")

    assert url == "my_repo_url"


@pytest.mark.online
def test_get_plugin_url__online():
    url = get_repository_url("PartSeg")

    assert url == "https://github.com/4DNucleome/PartSeg"


def test_no_result_analysis():
    result = PluginAnalysisResult.with_status(AnalysisStatus.UNACCESSIBLE_REPOSITORY)

    assert result.features == []
    assert result.status is AnalysisStatus.UNACCESSIBLE_REPOSITORY
    assert result.url is None
    assert result.repository is None
