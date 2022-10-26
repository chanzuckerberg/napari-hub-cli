from .githubInfo import *
from .htmlScraper import *
from rich import print
from rich.console import Console

repo_path = '/Users/simaosa/Desktop/MetaCell/Projects/CZI/CLI_29/brainreg-napari'

SETUPPY_DISPLAY_NAME_PATTERN = '(?:\sname\=\")(.*?)(?=\")'
SETUPPY_SUMMARY_SENTENCE_PATTERN = '(?:\sdescription\=\")(.*?)(?=\")'
SETUPPY_LONG_DESCRIPTION_PATTERN = '(?:long_description\s\=\s)(.*?)(?=\s\n)'
SETUPPY_SOURCE_CODE_PATTERN = '(?:\"Source\sCode\"\:)(.*?)(?=\"\,)'
SETUPPY_AUTHOR_PATTERN = '(?:author\=\")(.*?)(?=\")'
SETUPPY_BUG_TRACKER_PATTERN = '(?:\"Bug\sTracker\"\:)(.*?)(?=\"\,)'
SETUPPY_USER_SUPPORT_PATTERN = '(?:\"User\sSupport\"\:)(.*?)(?=\"\,)'


FILE_IN_LONG_DESCRIPTION_PATTERN = '(?:file\:\s)(.*?)(?=\s)'

IMAGE_STYLE_PATTERN = '(?:max-width\:\s)(.*?)(?=\%)'
IMAGE_WIDTH_PATTERN ='(?:width\=\")(.*?)(?=\")'

SHIELDS_IO_PATTERN = '(?:img.shields.io)'

        
def setuppy_soup(path):
    console = Console()
    console.print('Checking setup.py file...')
    git_repo_username,git_repo_name, git_repo_link,git_base_branch = getGitInfo(path)
    SET_UP_PY_LINK = git_repo_link + '/blob/%s/setup.py'%(git_base_branch)

    soup = get_html(SET_UP_PY_LINK)

    setup_py_scraped_text = soup.find_all("table", {'class': 'highlight tab-size js-file-line-container js-code-nav-container js-tagsearch-file'})
    setup_py_scraped_text = str(setup_py_scraped_text)
    setup_py_scraped_text = strip_tags(setup_py_scraped_text)

    return setup_py_scraped_text, git_repo_link



def name_metadata_pysetupfile(scraped_text):
    display_name_data = re.findall(SETUPPY_DISPLAY_NAME_PATTERN, scraped_text, flags=re.DOTALL)
    display_name_value = False
    if(bool(display_name_data)):
        display_name_value = True
   
    return display_name_value


def summary_metadata_pysetupfile(scraped_text):
    summary_sentence_data = re.findall(SETUPPY_SUMMARY_SENTENCE_PATTERN, scraped_text, flags=re.DOTALL)
    summary_sentence_check = False
    if(bool(summary_sentence_data)):
        summary_sentence_check = True
        
    return summary_sentence_check

def sourcecode_metadata_pysetupfile(scraped_text):
    source_code_check = False
    source_code_data = re.findall(SETUPPY_SOURCE_CODE_PATTERN, scraped_text, flags=re.DOTALL)
    if(bool(source_code_data)):
        source_code_check = True
        
    return source_code_check

# print(sourcecode_metadata_cfgfile(p))

def author_metadata_pysetupfile(scraped_text):
    author_check = False
    author_data = re.findall(SETUPPY_AUTHOR_PATTERN, scraped_text, flags=re.DOTALL)
    # print('\n Author')
    if(bool(author_data)):
        author_check = True

    return author_check

# print(author_metadata_cfgfile(p))

def bug_metadata_pysetupfile(scraped_text):
    bug_tracker_data = re.findall(SETUPPY_BUG_TRACKER_PATTERN, scraped_text, flags=re.DOTALL)

    bug_tracker_check = False
    if(bool(bug_tracker_data)):
        bug_tracker_check = True
 
    return bug_tracker_check



def usersupport_metadata_pysetupfile(scraped_text):
    user_support_data = re.findall(SETUPPY_USER_SUPPORT_PATTERN, scraped_text, flags=re.DOTALL)

    user_support_check = False
    if(bool(user_support_data)):
        user_support_check = True
    

    return user_support_check


def long_description_pysetupfile(scraped_text, repo_link):
    console = Console()
    
    long_description_data = re.findall(SETUPPY_LONG_DESCRIPTION_PATTERN, scraped_text, flags=re.DOTALL)
    link_data_soup = []
    if(bool(long_description_data)):
        console.print('Checking setup.py long_description associated file....')
        for data in long_description_data:
            long_description_file = re.findall(FILE_IN_LONG_DESCRIPTION_PATTERN, data, flags=re.DOTALL)
            
            if bool(long_description_file):
            
                long_description_file = ''.join(long_description_file)
                LONG_DESCRIPTION_LINK = repo_link + '#%s'%(long_description_file)
                long_description_soup = get_html(LONG_DESCRIPTION_LINK)
                link_data_soup = long_description_soup.find_all("article",{'class': 'markdown-body entry-content container-lg'})
                link_data_soup = link_data_soup[0]
            
            else:
                LONG_DESCRIPTION_LINK = repo_link + '#readme'
                long_description_soup = get_html(LONG_DESCRIPTION_LINK)
                link_data_soup = long_description_soup.find_all("article",{'class': 'markdown-body entry-content container-lg'})
                link_data_soup = link_data_soup[0]

    return link_data_soup

def video_metadata_pysetupfile(description_file_soup):
    intro_video_check = False
    if(bool(description_file_soup)):
        video_data = description_file_soup.find_all("video")
        if len(video_data)>0:
                intro_video_check = True
    return intro_video_check


def screenshot_metadata_pysetupfile(description_file_soup):
    intro_screenshot_check = False
    if(bool(description_file_soup)):
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



def usage_metadata_pysetupfile(description_file_soup):
    usage_check = False
    if(bool(description_file_soup)):
        usage_data = description_file_soup.find_all("a", {'href':'#usage'})
        if bool(usage_data):
                usage_check = True
    return usage_check



def intro_metadata_pysetupfile(description_file_soup):
    intro_paragraph_check = False
    if(bool(description_file_soup)):
        possible_intro_paragraph = description_file_soup.select_one('h2').find_all_previous('p', {'dir':'auto'})
        actual_text_in_p_count = 0
        for intro_paragraph in possible_intro_paragraph:
                if(bool(intro_paragraph.text)):
                    actual_text_in_p_count += + 1
        if actual_text_in_p_count > 0:
                intro_paragraph_check = True

    return intro_paragraph_check







# a,b = setuppy_soup(repo_path)

# # print(a)

# c = name_metadata_pysetupfile(a)

# # print(c)

# # print(summary_metadata_pysetupfile(a))

# # print(usersupport_metadata_pysetupfile(a))

# # print(sourcecode_metadata_pysetupfile(a))

# # print(author_metadata_pysetupfile(a))

# # print(bug_metadata_pysetupfile(a))
# # print(usersupport_metadata_pysetupfile(a))

# d = long_description_pysetupfile(a, 'https://github.com/brainglobe/brainreg-napari')

# print(video_metadata_pysetupfile(d))

# print(screenshot_metadata_pysetupfile(d))

# print(usage_metadata_pysetupfile(d))

# print(intro_metadata_pysetupfile(d))


