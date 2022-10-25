from .githubInfo import *
from .htmlScraper import *
from rich import print
from rich.console import Console

repo_path = '/Users/simaosa/Desktop/MetaCell/Projects/CZI/CLI_29/CZI-29-test'

PYCFG_DISPLAY_NAME_PATTERN = '(?:name\s\=\s)(.*?)(?=\s\n)'
PYCFG_SUMMARY_SENTENCE_PATTERN = '(?:\sdescription\s\=\s)(.*?)(?=\s\n)'
PYCFG_LONG_DESCRIPTION_PATTERN = '(?:long_description\s\=\s)(.*?)(?=\s\n)'
PYCFG_SOURCE_CODE_PATTERN = '(?:Source\sCode\s\=\s)(.*?)(?=\s)'
PYCFG_AUTHOR_PATTERN = '(?:author\s\=\s)(.*?)(?=\s\n)'
PYCFG_BUG_TRACKER_PATTERN = '(?:Bug\sTracker\s\=\s)(.*?)(?=\s)'
PYCFG_USER_SUPPORT_PATTERN = '(?:User\sSupport\s\=\s)(.*?)(?=\s)'


FILE_IN_LONG_DESCRIPTION_PATTERN = '(?:file\:\s)(.*?)(?=\s)'

IMAGE_STYLE_PATTERN = '(?:max-width\:\s)(.*?)(?=\%)'
IMAGE_WIDTH_PATTERN ='(?:width\=\")(.*?)(?=\")'

SHIELDS_IO_PATTERN = '(?:img.shields.io)'




        
def cfg_soup(path):
    console = Console()
    console.print('Checking setup.cfg file...')
    git_repo_username,git_repo_name, git_repo_link,git_base_branch = getGitInfo(path)
    SET_UP_CFG_LINK = git_repo_link + '/blob/%s/setup.cfg'%(git_base_branch)

    soup = get_html(SET_UP_CFG_LINK)

    setup_cfg_scraped_text = soup.find_all("table", {'class': 'highlight tab-size js-file-line-container js-code-nav-container js-tagsearch-file'})
    setup_cfg_scraped_text = str(setup_cfg_scraped_text)
    setup_cfg_scraped_text = strip_tags(setup_cfg_scraped_text)

    return setup_cfg_scraped_text, git_repo_link

def name_metadata_cfgfile(scraped_text):
    display_name_data = re.findall(PYCFG_DISPLAY_NAME_PATTERN, scraped_text, flags=re.DOTALL)
    display_name_value = False
    if(bool(display_name_data)):
        display_name_value = True
   
    return display_name_value

# p, l = cfg_soup(repo_path)
# print(name_metadata_cfgfile(p))

def summary_metadata_cfgfile(scraped_text):
    summary_sentence_data = re.findall(PYCFG_SUMMARY_SENTENCE_PATTERN, scraped_text, flags=re.DOTALL)
    summary_sentence_check = False
    if(bool(summary_sentence_data)):
        summary_sentence_check = True
        
    return summary_sentence_check

# print(summary_metadata_cfgfile(p))

def sourcecode_metadata_cfgfile(scraped_text):
    source_code_check = False
    source_code_data = re.findall(PYCFG_SOURCE_CODE_PATTERN, scraped_text, flags=re.DOTALL)
    if(bool(source_code_data)):
        source_code_check = True
        
    return source_code_check

# print(sourcecode_metadata_cfgfile(p))

def author_metadata_cfgfile(scraped_text):
    author_check = False
    author_data = re.findall(PYCFG_AUTHOR_PATTERN, scraped_text, flags=re.DOTALL)
    # print('\n Author')
    if(bool(author_data)):
        author_check = True

    return author_check

# print(author_metadata_cfgfile(p))

def bug_metadata_cfgfile(scraped_text):
    bug_tracker_data = re.findall(PYCFG_BUG_TRACKER_PATTERN, scraped_text, flags=re.DOTALL)

    bug_tracker_check = False
    if(bool(bug_tracker_data)):
        bug_tracker_check = True
 
    return bug_tracker_check

# print(bug_metadata_cfgfile(p))


def usersupport_metadata_cfgfile(scraped_text):
    user_support_data = re.findall(PYCFG_USER_SUPPORT_PATTERN, scraped_text, flags=re.DOTALL)

    user_support_check = False
    if(bool(user_support_data)):
        user_support_check = True
    

    return user_support_check

# print(usersupport_metadata_cfgfile(p))


def long_description_file(scraped_text, repo_link):
    console = Console()
    console.print('Checking setup.cfg long_description associated file....')

    long_description_data = re.findall(PYCFG_LONG_DESCRIPTION_PATTERN, scraped_text, flags=re.DOTALL)

    for data in long_description_data:
        long_description_file = re.findall(FILE_IN_LONG_DESCRIPTION_PATTERN, data, flags=re.DOTALL)
    
    if bool(long_description_file):
       
        long_description_file = ''.join(long_description_file)
        LONG_DESCRIPTION_LINK = repo_link + '#%s'%(long_description_file)
        long_description_soup = get_html(LONG_DESCRIPTION_LINK)
        link_data_soup = long_description_soup.find_all("article",{'class': 'markdown-body entry-content container-lg'})
        link_data_soup = link_data_soup[0]

    return link_data_soup

# s = long_description_file(p,l)

def video_metadata_cfgfile(description_file_soup):
    video_data = description_file_soup.find_all("video")
    intro_video_check = False
    if len(video_data)>0:
            intro_video_check = True
    return intro_video_check

# print(video_metadata_cfgfile(s))

def screenshot_metadata_cfgfile(description_file_soup):
    intro_screenshot_check = False
    screenshot_data = description_file_soup.find_all("img")
    for data in screenshot_data:
        # print(data)
        data = str(data)
        image_maxwidth_percentage = re.findall(IMAGE_STYLE_PATTERN, data, flags=re.DOTALL)
        image_width = re.findall(IMAGE_WIDTH_PATTERN, data, flags=re.DOTALL)
        shields_io_image = re.findall(SHIELDS_IO_PATTERN, data, flags=re.DOTALL)
        
        if(bool(image_width) and not bool(shields_io_image)):
            for i in image_width:
                width_number = int(str(i))
                if width_number > 200 :
                    intro_screenshot_check = True

        if not bool(image_width) and (bool(image_maxwidth_percentage)and not bool(shields_io_image)):
            for i in image_maxwidth_percentage:
                percentage_number = int(str(i))
                if percentage_number > 30:
                    intro_screenshot_check = True
        
        
           
    return intro_screenshot_check

# print(screenshot_metadata_cfgfile(s))


def usage_metadata_cfgfile(description_file_soup):
    usage_check = False
    usage_data = description_file_soup.find_all("a", {'href':'#usage'})
    if bool(usage_data):
            usage_check = True
    return usage_check

# print(usage_metadata_cfgfile(s))


def intro_metadata_cfgfile(description_file_soup):
    possible_intro_paragraph = description_file_soup.select_one('h2').find_all_previous('p', {'dir':'auto'})
    actual_text_in_p_count = 0
    intro_paragraph_check = False
    for intro_paragraph in possible_intro_paragraph:
            if(bool(intro_paragraph.text)):
                actual_text_in_p_count += + 1
    if actual_text_in_p_count > 0:
            intro_paragraph_check = True

    return intro_paragraph_check

# print(intro_metadata_cfgfile(s))





