from pathlib import Path

import pytest

from napari_hub_cli.autofix import build_issue_message, create_commits
from napari_hub_cli.checklist import analyse_local_plugin, display_checklist
from napari_hub_cli.checklist.analysis import DEFAULT_SUITE
from napari_hub_cli.checklist.metadata import Feature, check_feature
from napari_hub_cli.checklist.projectmetadata import (
    DISPLAY_NAME,
    ENTRIES_DOC_URL,
    LABELS_DOC_URL,
    VIDEO_SCREENSHOT,
)
from napari_hub_cli.citation import create_cff_citation
from napari_hub_cli.fs import NapariPlugin


@pytest.fixture(scope="module")
def test_repo():
    current_path = Path(__file__).parent.absolute()
    return NapariPlugin(current_path / "resources" / "CZI-29-test")


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
    assert setup_cfg.has_summary is True
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


def test_check_feature_primary(test_repo):
    setup_cfg = test_repo.setup_cfg

    result = check_feature(DISPLAY_NAME, (setup_cfg,), ())

    assert isinstance(result, Feature)
    assert result.meta is DISPLAY_NAME
    assert result.found is True
    assert result.found_in == setup_cfg
    assert result.only_in_fallback is False
    assert result.has_fallback_files is False
    assert result.scanned_files == [setup_cfg]


def test_check_feature_secondary(test_repo):
    setup_cfg = test_repo.setup_cfg

    result = check_feature(DISPLAY_NAME, (), (setup_cfg,))

    assert isinstance(result, Feature)
    assert result.meta is DISPLAY_NAME
    assert result.found is True
    assert result.found_in == setup_cfg
    assert result.only_in_fallback is True
    assert result.has_fallback_files is True
    assert result.scanned_files == [setup_cfg]


def test_check_feature_missing(test_repo):
    setup_py = test_repo.setup_py
    result = check_feature(DISPLAY_NAME, (), (setup_py,))

    assert isinstance(result, Feature)
    assert result.meta is DISPLAY_NAME
    assert result.found is False
    assert result.found_in is None
    assert result.only_in_fallback is False
    assert result.has_fallback_files is True
    assert result.scanned_files == [setup_py]


def test_create_checkist(test_repo):
    result = analyse_local_plugin(test_repo.path, DEFAULT_SUITE)

    assert len(result.features) == 13

    disp_name = result.features[0]
    assert disp_name.meta is DISPLAY_NAME
    assert disp_name.found is True
    assert disp_name.found_in == test_repo.npe2_yaml
    assert disp_name.only_in_fallback is False
    assert disp_name.has_fallback_files is True

    description = result.features[6]
    assert description.meta is VIDEO_SCREENSHOT
    assert description.found is True
    assert description.found_in == test_repo.setup_cfg.long_description()
    assert description.only_in_fallback is True
    assert description.has_fallback_files is True


# smoke test
def test_display_checklist(test_repo):
    result = analyse_local_plugin(test_repo.path, DEFAULT_SUITE)
    display_checklist(result)


def test_has_citation_file(test_repo):
    assert test_repo.has_citation_file is False


def test_access_specific_result(test_repo):
    result = analyse_local_plugin(test_repo.path, DEFAULT_SUITE)

    specific = result[DISPLAY_NAME]
    assert specific is not None
    assert specific.meta is DISPLAY_NAME

    with pytest.raises(StopIteration):
        result[0]


def test_build_issue_message(test_repo):
    result = analyse_local_plugin(test_repo.path, DEFAULT_SUITE)
    features = result.features

    assert len(features) > 0

    message = build_issue_message("bar", 2, result)

    assert "I'm bar" in message
    assert "complement #2" in message
    assert "'Source Code'" in message
    assert "'Author Name'" in message
    assert "'Issue Submission Link'" in message
    assert "'Support Channel Link'" in message
    assert "'Installation'" in message
    assert "'Usage Overview'" in message
    assert "'Intro Paragraph'" in message

    assert LABELS_DOC_URL in message
    assert ENTRIES_DOC_URL in message


def test_create_citation(test_repo):
    assert test_repo.citation_file.exists is False

    created = create_cff_citation(test_repo.path, save=True, display_info=False)

    assert created is True

    citation = test_repo.citation_file
    assert citation.exists is True
    citation.file.unlink()


# def test_create_commits(test_repo):
#     result = create_checklist(test_repo.path)
#     create_commits(result)
