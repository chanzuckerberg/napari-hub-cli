from pathlib import Path
from napari_hub_cli.fs import NapariPlugin
from napari_hub_cli.fs.condainfo import CondaInfo

import pytest
import requests_mock as req


URL = CondaInfo.URL


@pytest.fixture
def npe2api(requests_mock):
    requests_mock.get(
        f"{URL}/brainreg-napari",
        json={"conda_platforms": ["noarch"]},
    )
    requests_mock.get(
        f"{URL}/btrack",
        json={"conda_platforms": ["win-32"]},
    )
    requests_mock.get(
        f"{URL}/anchor-droplet-chip",
        json={"conda_platforms": ["osx-64", "linux-64"]},
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