from .githubInfo import *
from .htmlScraper import *
from rich import print
from rich.console import Console
from .patterns_doc_checklist import *

        
def napari_cfgfile_soup(path):
    """Get the scraped text from napari-hub/config.yml
    Parameters
    ----------
    path : str
        local path to the plugin
    
    Returns
    -------
    napari_cfg_scraped_text: str
        napari-hub/config.yml scraped text
    """
    console = Console()
    console.print('Checking napari-hub/config.yml file...')

    #get Git information from the local plugin path
    git_repo_username,git_repo_name, git_repo_link,git_base_branch = getGitInfo(path)
    #create URL for the napari-hub/config.yml file location
    NAPARI_CFG_LINK = git_repo_link + '/blob/%s/.napari-hub/config.yml'%(git_base_branch)
    #get the scraped text from the napari-hub/config.yml file
    napari_cfg_soup = get_html(NAPARI_CFG_LINK)
    napari_cfg_scraped_text = napari_cfg_soup.find_all("table", {'class': 'highlight tab-size js-file-line-container js-code-nav-container js-tagsearch-file'})
    napari_cfg_scraped_text = str(napari_cfg_scraped_text)
    #strip HTML tags from the scraped text
    napari_cfg_scraped_text = strip_tags(napari_cfg_scraped_text)

    return napari_cfg_scraped_text



def summary_metadata_naparicfg(scraped_text):
    """Checks for Summary Sentence data on the napari-hub/config.yml file
    Parameters
    ----------
    scraped_text : str
         napari-hub/config.yml scraped text
    
    Returns
    -------
    summary_sentence_check: bool
        True if Summary Sentence is found, False on the contrary
    """
    #finds summary sentence data in napari-hub/config.yml
    summary_sentence_data = re.findall(NAPARI_CFG_SUMMARY_SENTENCE_PATTERN, scraped_text, flags=re.DOTALL)
    #if there is data assign a value of True, to then be used in the documentation checklist
    summary_sentence_check = False
    if(bool(summary_sentence_data)):
        summary_sentence_check = True
    return summary_sentence_check


def sourcecode_metadata_naparicfg(scraped_text):
    """Checks for Source Code Link data on the napari-hub/config.yml file
    Parameters
    ----------
    scraped_text : str
         napari-hub/config.yml scraped text
    
    Returns
    -------
    source_code_check: bool
        True if Source Code Link is found, False on the contrary
    """
    #finds source code link in napari-hub/config.yml
    source_code_data = re.findall(NAPARI_CFG_SOURCE_CODE_PATTERN, scraped_text, flags=re.DOTALL)
    #if there is data assign a value of True, to then be used in the documentation checklist
    source_code_check = False
    if(bool(source_code_data)):
        source_code_check = True
    return source_code_check


def author_metadata_naparicfg(scraped_text):
    """Checks for Author data on the napari-hub/config.yml file
    Parameters
    ----------
    scraped_text : str
         napari-hub/config.yml scraped text
    
    Returns
    -------
    author_check: bool
        True if Author is found, False on the contrary
    """
    #finds author data in napari-hub/config.yml
    author_data = re.findall(NAPARI_CFG_AUTHOR_PATTERN, scraped_text, flags=re.DOTALL)
    #if there is data assign a value of True, to then be used in the documentation checklist
    author_check = False
    if(bool(author_data)):
        author_check = True
    return author_check


def usersupport_metadata_naparicfg(scraped_text):
    """Checks for User Support Link data on the napari-hub/config.yml file
    Parameters
    ----------
    scraped_text : str
         napari-hub/config.yml scraped text
    
    Returns
    -------
    user_support_check: bool
        True if User Support Link is found, False on the contrary
    """
    #finds user support link in napari-hub/config.yml
    user_support_data = re.findall(NAPARI_CFG_USER_SUPPORT_PATTERN, scraped_text, flags=re.DOTALL)
    #if there is data assign a value of True, to then be used in the documentation checklist
    user_support_check = False
    if(bool(user_support_data)):
        user_support_check = True
    return user_support_check


def bugtracker_metadata_naparicfg(scraped_text):
    """Checks for Bug Tracker Link data on the napari-hub/config.yml file
    Parameters
    ----------
    scraped_text : str
         napari-hub/config.yml scraped text
    
    Returns
    -------
    bug_tracker_check: bool
        True if Bug Tracker Link is found, False on the contrary
    """
    #finds bug tracker link data in napari-hub/config.yml
    if (bool(re.findall(NAPARI_CFG_BUG_TRACKER_PATTERN, scraped_text, flags=re.DOTALL))):
        bug_tracker_data = re.findall(NAPARI_CFG_BUG_TRACKER_PATTERN, scraped_text, flags=re.DOTALL)
    else:
        bug_tracker_data = re.findall(NAPARI_CFG_REPORT_ISSUES_PATTERN, scraped_text, flags=re.DOTALL)
    
    #if there is data assign a value of True, to then be used in the documentation checklist
    bug_tracker_check = False
    if(bool(bug_tracker_data)):
        bug_tracker_check = True    
    
    return bug_tracker_check

