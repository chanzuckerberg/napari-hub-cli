from pathlib import Path

import pytest

from napari_hub_cli.documentation_checklist.filesaccess import NapariPlugin
from napari_hub_cli.documentation_checklist.metadata_checklist import (
    DISPLAY_NAME,
    VIDEO_SCREENSHOT,
    create_checklist,
    display_checklist,
)


@pytest.fixture(scope="module")
def test_repo():
    current_path = Path(__file__).parent.absolute()
    return NapariPlugin(current_path / "resources/CZI-29-faulty")


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

    assert description.has_videos is False
    assert description.has_screenshots is False
    assert description.has_videos_or_screenshots is False
    assert description.has_usage is False
    assert description.has_intro is False


def test_check_npe2(test_repo):
    np2e_file = test_repo.npe2_yaml

    assert np2e_file.exists is False


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
    assert description.has_screenshots is False
    assert description.has_usage is False
    assert description.has_intro is False


def test_check_citation(test_repo):
    citation = test_repo.citation_file

    assert citation.exists is False


def test_create_checkist(test_repo):
    result = create_checklist(test_repo.path)

    assert len(result.features) == 12

    disp_name = result.features[0]
    assert disp_name.meta is DISPLAY_NAME
    assert disp_name.found is True
    assert disp_name.found_in == test_repo.setup_cfg.file
    assert disp_name.only_in_fallback is True
    assert disp_name.has_fallback_files is True

    description = result.features[6]
    assert description.meta is VIDEO_SCREENSHOT
    assert description.found is False
    assert description.found_in is None
    assert description.only_in_fallback is False
    assert description.has_fallback_files is True


def test_display_checklist(test_repo):
    result = create_checklist(test_repo.path)
    display_checklist(result)