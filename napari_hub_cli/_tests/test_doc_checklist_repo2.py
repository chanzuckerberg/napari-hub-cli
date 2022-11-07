from pathlib import Path
import pytest

from napari_hub_cli.documentation_checklist.filesaccess import NapariPlugin


@pytest.fixture(scope="module")
def test_repo():
    current_path = Path(__file__).parent.absolute()
    return NapariPlugin(current_path / "resources/CZI-29-test2")


def test_check_napari_config(test_repo):
    napari_config_yaml = test_repo.config_yml

    assert napari_config_yaml.has_summary is False
    assert napari_config_yaml.has_projectsite is False
    assert napari_config_yaml.has_author is False
    assert napari_config_yaml.has_bugtracker is False
    assert napari_config_yaml.has_usersupport is False


def test_check_napari_description(test_repo):
    description = test_repo.description

    assert description.exists is True

    assert description.has_videos is True
    assert description.has_screenshots is True
    assert description.has_videos_or_screenshots is True
    assert description.has_usage is True
    assert description.has_intro is True


def test_check_npe2(test_repo):
    np2e_file = test_repo.npe2_yaml

    assert np2e_file.exists is True
    assert np2e_file.has_name is True


def test_check_pysetup(test_repo):
    setup_py = test_repo.setup_py

    description = setup_py.long_description()

    assert setup_py.exists is True
    assert description.exists is True

    assert setup_py.has_name is False
    assert setup_py.has_summary is False
    assert setup_py.has_sourcecode is False
    assert setup_py.has_author is False
    assert setup_py.has_bugtracker is False
    assert setup_py.has_usersupport is False

    assert description.has_usage is False
    assert description.has_intro is False
    assert description.has_videos is False
    assert description.has_screenshots is False


def test_check_setupcfg(test_repo):
    setup_cfg = test_repo.setup_cfg
    description = setup_cfg.long_description()

    assert setup_cfg.exists is True
    assert description.exists is True

    assert setup_cfg.has_name is True
    assert setup_cfg.has_summary is False
    assert setup_cfg.has_sourcecode is False
    assert setup_cfg.has_author is False
    assert setup_cfg.has_bugtracker is False
    assert setup_cfg.has_usersupport is False

    assert description.has_videos is False
    assert description.has_screenshots is True
    assert description.has_usage is False
    assert description.has_intro is False


def test_check_citation(test_repo):
    citation = test_repo.citation_file

    assert citation.exists is False
