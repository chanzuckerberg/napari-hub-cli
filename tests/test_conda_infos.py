from pathlib import Path

import pytest
import requests_mock as req

from napari_hub_cli.fs import NapariPlugin
from napari_hub_cli.fs.condainfo import CondaInfo

CONDA_URL = CondaInfo.CONDA_URL


@pytest.fixture
def npe2api(requests_mock):
    requests_mock.get(
        f"{CONDA_URL}/brainreg-napari",
        json={"conda_platforms": ["noarch"]},
    )
    requests_mock.get(
        f"{CONDA_URL}/btrack",
        json={"conda_platforms": ["win-32"]},
    )
    requests_mock.get(
        f"{CONDA_URL}/anchor-droplet-chip",
        json={"conda_platforms": ["osx-64", "linux-64"]},
    )
    requests_mock.get(
        f"{CondaInfo.ERRORS_URL}",
        json={
            "allencell-ml-segmenter": {
                "version": "0.0.7",
                "error": "manifest 'napari.yaml' does not exist in distribution for allencell-ml-segmenter",
            },
            "ilastik-napari": {
                "version": "0.2.1",
                "error": "manifest 'plugin.toml' does not exist in distribution for ilastik-napari",
            },
        },
    )
    return requests_mock


@pytest.fixture(scope="module")
def resources():
    current_path = Path(__file__).parent.absolute()
    return current_path / "resources"


@pytest.mark.online
def test_conda_info1(resources):
    repo = NapariPlugin(resources / "conda-infos1")
    infos: CondaInfo = repo.condainfo

    assert infos.is_on_conda is True
    assert infos.is_linux_supported is True
    assert infos.is_windows_supported is True
    assert infos.is_macos_supported is True


@pytest.mark.online
def test_conda_info2(resources):
    repo = NapariPlugin(resources / "conda-infos2")
    infos: CondaInfo = repo.condainfo

    assert infos.is_on_conda is True
    assert infos.is_linux_supported is True
    assert infos.is_windows_supported is False
    assert infos.is_macos_supported is True


@pytest.mark.online
def test_conda_info3(resources):
    repo = NapariPlugin(resources / "conda-infos3")
    infos: CondaInfo = repo.condainfo

    assert infos.is_on_conda is False
    assert infos.is_linux_supported is False
    assert infos.is_windows_supported is False
    assert infos.is_macos_supported is False


def test_conda_info1_offline(resources, npe2api):
    repo = NapariPlugin(resources / "conda-infos1")
    infos: CondaInfo = repo.condainfo

    assert infos.is_on_conda is True
    assert infos.is_linux_supported is True
    assert infos.is_windows_supported is True
    assert infos.is_macos_supported is True


def test_conda_info2_offline(resources, npe2api):
    repo = NapariPlugin(resources / "conda-infos2")
    infos: CondaInfo = repo.condainfo

    assert infos.is_on_conda is True
    assert infos.is_linux_supported is False
    assert infos.is_windows_supported is True
    assert infos.is_macos_supported is False


def test_conda_info3_offline(resources, npe2api):
    repo = NapariPlugin(resources / "conda-infos3")
    infos: CondaInfo = repo.condainfo

    assert infos.is_on_conda is True
    assert infos.is_linux_supported is True
    assert infos.is_windows_supported is False
    assert infos.is_macos_supported is True


def test_conda_info1_errors_offline(resources, npe2api):
    repo = NapariPlugin(resources / "conda-infos1")
    infos: CondaInfo = repo.condainfo

    assert infos.has_npe_parse_errors is False


def test_conda_info4_errors_offline(resources, npe2api):
    repo = NapariPlugin(resources / "conda-infos4")
    infos: CondaInfo = repo.condainfo

    assert infos.has_npe_parse_errors is True


@pytest.mark.online
def test_conda_info1_errors(resources, npe2api):
    repo = NapariPlugin(resources / "conda-infos1")
    infos: CondaInfo = repo.condainfo

    assert infos.has_npe_parse_errors is False


@pytest.mark.online
def test_conda_info4_errors(resources, npe2api):
    repo = NapariPlugin(resources / "conda-infos4")
    infos: CondaInfo = repo.condainfo

    assert infos.has_npe_parse_errors is True
