
import pathlib
import git
from git import Repo, rmtree
from napari_hub_cli.documentation_checklist.check_metadata.check_meta_data_from_setupcfg import *
from napari_hub_cli.documentation_checklist.check_metadata.check_meta_data_from_pysetup import *
from napari_hub_cli.documentation_checklist.check_metadata.check_meta_data_from_napari_config_yml import *
from napari_hub_cli.documentation_checklist.check_metadata.check_meta_data_from_napari_descriptionmd import *
from napari_hub_cli.documentation_checklist.check_metadata.check_meta_data_from_npe2config import *
from napari_hub_cli.documentation_checklist.check_metadata.check_citation import *
import pytest


git.Git(str(pathlib.Path().resolve())).clone('https://github.com/SimaoBolota-MetaCell/CZI-29-test')

TEST_REPO_LINK = (str(pathlib.Path().resolve())) + '/CZI-29-test'

def test_check_napari_config():
    napari_cfg_scraped_text = napari_cfgfile_soup(TEST_REPO_LINK)

    assert(summary_metadata_naparicfg(napari_cfg_scraped_text) ) == False
    assert(sourcecode_metadata_naparicfg(napari_cfg_scraped_text)) == False
    assert(author_metadata_naparicfg(napari_cfg_scraped_text)) == False
    assert(bugtracker_metadata_naparicfg(napari_cfg_scraped_text)) == False
    assert(usersupport_metadata_naparicfg(napari_cfg_scraped_text)) == False


def test_check_napari_description():
    description_scraped_text = description_soup(TEST_REPO_LINK)

    assert(video_metadata_descriptionfile(description_scraped_text)) == False
    assert(screenshot_metadata_descriptionfile(description_scraped_text)) == False
    assert(usage_metadata_descriptionfile(description_scraped_text)) == False
    assert(intro_metadata_descriptionfile(description_scraped_text)) == False


def test_check_npe2():
   npe2_napari_file = npe2_file_location(TEST_REPO_LINK)
   assert( name_metadata_npe2file(TEST_REPO_LINK,npe2_napari_file)) == True


def test_check_pysetup():
    setupy_scraped_text, git_link = setuppy_soup(TEST_REPO_LINK)
    longdescription_pysetup_scraped_text = long_description_pysetupfile(setupy_scraped_text, git_link)

    assert(name_metadata_pysetupfile(setupy_scraped_text)) == False
    assert(summary_metadata_pysetupfile(setupy_scraped_text)) == False
    assert(sourcecode_metadata_pysetupfile(setupy_scraped_text)) == False
    assert(author_metadata_pysetupfile(setupy_scraped_text)) == False
    assert(bug_metadata_pysetupfile(setupy_scraped_text)) == False
    assert(usersupport_metadata_pysetupfile(setupy_scraped_text)) == False

    assert(usage_metadata_pysetupfile(longdescription_pysetup_scraped_text)) == False
    assert(intro_metadata_pysetupfile(longdescription_pysetup_scraped_text)) == False
    assert(video_metadata_pysetupfile(longdescription_pysetup_scraped_text)) == False
    assert(screenshot_metadata_pysetupfile(longdescription_pysetup_scraped_text)) == False


def test_check_setupcfg():
    cfg_scraped_text, git_link = cfg_soup(TEST_REPO_LINK)
    longdescription_scraped_text = long_description_file(cfg_scraped_text,git_link )

    assert(name_metadata_cfgfile(cfg_scraped_text))  == True
    assert(summary_metadata_cfgfile(cfg_scraped_text))  == False
    assert(sourcecode_metadata_cfgfile(cfg_scraped_text)) == False
    assert(author_metadata_cfgfile(cfg_scraped_text)) == False
    assert(bug_metadata_cfgfile(cfg_scraped_text)) == False
    assert(usersupport_metadata_cfgfile(cfg_scraped_text)) == False

    assert(video_metadata_cfgfile(longdescription_scraped_text)) == False
    assert(screenshot_metadata_cfgfile(longdescription_scraped_text)) == True
    assert(usage_metadata_cfgfile(longdescription_scraped_text)) == False
    assert(intro_metadata_cfgfile(longdescription_scraped_text)) == False
    

@pytest.mark.usefixtures("delete_test_repo")
def test_check_citation():

    assert(check_for_citation(TEST_REPO_LINK , 'CITATION.CFF')) == False

