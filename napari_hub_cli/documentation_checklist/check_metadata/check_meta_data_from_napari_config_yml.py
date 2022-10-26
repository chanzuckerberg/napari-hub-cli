from .githubInfo import *
from .htmlScraper import *
from rich import print
from rich.console import Console


# repo_path = '/Users/simaosa/Desktop/MetaCell/Projects/CZI/CLI_29/CZI-29-test'



NAPARI_CFG_SUMMARY_SENTENCE_PATTERN = '(?:summary\:\s)(.*?)(?=\s\n)'
NAPARI_CFG_SOURCE_CODE_PATTERN = '(?:Project\sSite\:\s)(.*?)(?=\s)'
NAPARI_CFG_AUTHOR_PATTERN = '(?:\-\sname\:\s)(.*?)(?=\s\n)'
NAPARI_CFG_BUG_TRACKER_PATTERN = '(?:Bug\sTracker\:\s)(.*?)(?=\s)'
NAPARI_CFG_REPORT_ISSUES_PATTERN = '(?:Report\sIssues\:\s)(.*?)(?=\s)'
NAPARI_CFG_USER_SUPPORT_PATTERN = '(?:User\sSupport\:\s)(.*?)(?=\s)'


        
def napari_cfgfile_soup(path):
    console = Console()
    console.print('Checking napari-hub/config.yml file...')
    
    git_repo_username,git_repo_name, git_repo_link,git_base_branch = getGitInfo(path)

    NAPARI_CFG_LINK = git_repo_link + '/blob/%s/.napari-hub/config.yml'%(git_base_branch)

    napari_cfg_soup = get_html(NAPARI_CFG_LINK)

    napari_cfg_scraped_text = napari_cfg_soup.find_all("table", {'class': 'highlight tab-size js-file-line-container js-code-nav-container js-tagsearch-file'})
    napari_cfg_scraped_text = str(napari_cfg_scraped_text)
    napari_cfg_scraped_text = strip_tags(napari_cfg_scraped_text)

    return napari_cfg_scraped_text

# p = napari_cfgfile_soup(repo_path)



def summary_metadata_naparicfg(scraped_text):
    summary_sentence_data = re.findall(NAPARI_CFG_SUMMARY_SENTENCE_PATTERN, scraped_text, flags=re.DOTALL)

    summary_sentence_check = False
    if(bool(summary_sentence_data)):
        summary_sentence_check = True
    return summary_sentence_check
# print('Summary Sentence found?')
# print(summary_metadata_naparicfg(p))
# print('\n')


def sourcecode_metadata_naparicfg(scraped_text):
    source_code_data = re.findall(NAPARI_CFG_SOURCE_CODE_PATTERN, scraped_text, flags=re.DOTALL)

    source_code_check = False
    if(bool(source_code_data)):
        source_code_check = True
    return source_code_check

# print('Source Code link found?')
# print(sourcecode_metadata_naparicfg(p))
# print('\n')

def author_metadata_naparicfg(scraped_text):
    author_data = re.findall(NAPARI_CFG_AUTHOR_PATTERN, scraped_text, flags=re.DOTALL)

    author_check = False
    if(bool(author_data)):
        author_check = True
    return author_check

# print('Author found?')
# print(author_metadata_naparicfg(p))
# print('\n')

def usersupport_metadata_naparicfg(scraped_text):
    user_support_data = re.findall(NAPARI_CFG_USER_SUPPORT_PATTERN, scraped_text, flags=re.DOTALL)

    user_support_check = False
    if(bool(user_support_data)):
        user_support_check = True
    return user_support_check

# print('User Support link found?')
# print(usersupport_metadata_naparicfg(p))
# print('\n')

def bugtracker_metadata_naparicfg(scraped_text):

    if (bool(re.findall(NAPARI_CFG_BUG_TRACKER_PATTERN, scraped_text, flags=re.DOTALL))):
        bug_tracker_data = re.findall(NAPARI_CFG_BUG_TRACKER_PATTERN, scraped_text, flags=re.DOTALL)
    else:
        bug_tracker_data = re.findall(NAPARI_CFG_REPORT_ISSUES_PATTERN, scraped_text, flags=re.DOTALL)

    bug_tracker_check = False
    if(bool(bug_tracker_data)):
        bug_tracker_check = True    
    return bug_tracker_check
# print('Bug Tracker link found?')
# print(bugtracker_metadata_naparicfg(p))
# print('\n')

