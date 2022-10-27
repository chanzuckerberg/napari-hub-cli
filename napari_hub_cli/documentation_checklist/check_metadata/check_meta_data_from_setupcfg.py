from .githubInfo import *
from .htmlScraper import *
from rich import print
from rich.console import Console
from .patterns_doc_checklist import *

        
def cfg_soup(path):
    """Get the scarped text from setup.cfg file
    Parameters
    ----------
    path : str
        local path to the plugin
    
    Returns
    -------
    setup_cfg_scraped_text : str
        setup.cfg scraped text
    git_repo_link : str
        GitHub Repository Link

    """
    console = Console()
    console.print('Checking setup.cfg file...')
    #get Git information from the local plugin path
    git_repo_username,git_repo_name, git_repo_link,git_base_branch = getGitInfo(path)
    #URL for the setup.py file location
    SET_UP_CFG_LINK = git_repo_link + '/blob/%s/setup.cfg'%(git_base_branch)
    #get scraped HTML text
    soup = get_html(SET_UP_CFG_LINK)
    setup_cfg_scraped_text = soup.find_all("table", {'class': 'highlight tab-size js-file-line-container js-code-nav-container js-tagsearch-file'})
    setup_cfg_scraped_text = str(setup_cfg_scraped_text)
    #strip the HTML tags
    setup_cfg_scraped_text = strip_tags(setup_cfg_scraped_text)

    return setup_cfg_scraped_text, git_repo_link

def name_metadata_cfgfile(scraped_text):
    """Checks for Display Name data on the setup.cfg file
    Parameters
    ----------
    scraped_text : str
        setup.cfg scraped text
    
    Returns
    -------
    display_name_value: bool
        True if Display Name is found, False on the contrary
    """
    #check if a display name metadata field exists
    display_name_data = re.findall(PYCFG_DISPLAY_NAME_PATTERN, scraped_text, flags=re.DOTALL)
    display_name_value = False
    if(bool(display_name_data)):
        display_name_value = True
   
    return display_name_value


def summary_metadata_cfgfile(scraped_text):
    """Checks for Summary Sentence data on the setup.cfg file
    Parameters
    ----------
    scraped_text : str
        setup.cfg scraped text
    
    Returns
    -------
    summary_sentence_check: bool
        True if Summary Sentence is found, False on the contrary
    """
    #check if a summary sentence metadata field exists
    summary_sentence_data = re.findall(PYCFG_SUMMARY_SENTENCE_PATTERN, scraped_text, flags=re.DOTALL)
    summary_sentence_check = False
    if(bool(summary_sentence_data)):
        summary_sentence_check = True
        
    return summary_sentence_check


def sourcecode_metadata_cfgfile(scraped_text):
    """Checks for Source Code Link data on the setup.cfg file
    Parameters
    ----------
    scraped_text : str
        setup.cfg scraped text
    
    Returns
    -------
    source_code_check: bool
        True if Source Code Link is found, False on the contrary
    """
    #check if a source code metadata field exists
    source_code_check = False
    source_code_data = re.findall(PYCFG_SOURCE_CODE_PATTERN, scraped_text, flags=re.DOTALL)
    if(bool(source_code_data)):
        source_code_check = True
        
    return source_code_check


def author_metadata_cfgfile(scraped_text):
    """Checks for Author data on the setup.cfg file
    Parameters
    ----------
    scraped_text : str
        setup.cfg scraped text
    
    Returns
    -------
    author_check: bool
        True if Author is found, False on the contrary
    """
    #check if a author metadata field exists
    author_check = False
    author_data = re.findall(PYCFG_AUTHOR_PATTERN, scraped_text, flags=re.DOTALL)
    if(bool(author_data)):
        author_check = True

    return author_check

def bug_metadata_cfgfile(scraped_text):
    """Checks for Bug Tracker Link data on the setup.cfg file
    Parameters
    ----------
    scraped_text : str
        setup.cfg scraped text
    
    Returns
    -------
    bug_tracker_check: bool
        True if Bug Tracker Link is found, False on the contrary
    """
    #check if a bug tracker link metadata field exists
    bug_tracker_data = re.findall(PYCFG_BUG_TRACKER_PATTERN, scraped_text, flags=re.DOTALL)
    bug_tracker_check = False
    if(bool(bug_tracker_data)):
        bug_tracker_check = True
 
    return bug_tracker_check


def usersupport_metadata_cfgfile(scraped_text):
    """Checks for User Support Link data on the setup.cfg file
    Parameters
    ----------
    scraped_text : str
        setup.cfg scraped text
    
    Returns
    -------
    user_support_check: bool
        True if User Support Link is found, False on the contrary
    """
    #check if a user support link metadata field exists
    user_support_data = re.findall(PYCFG_USER_SUPPORT_PATTERN, scraped_text, flags=re.DOTALL)
    user_support_check = False
    if(bool(user_support_data)):
        user_support_check = True
    

    return user_support_check



def long_description_file(scraped_text, repo_link):
    """Get the scraped text from the file location referenced in the long_description field of setup.cfg
    Parameters
    ----------
    scraped_text : str
        setup.cfg scraped text
    repo_link : str
        GitHub Repository URL
    
    Returns
    -------
    link_data_soup: str
        scraped text from the file location referenced in the long_description field
    """
    console = Console()
    #check if a long description metadata field exists, which redirects to another file
    long_description_data = re.findall(PYCFG_LONG_DESCRIPTION_PATTERN, scraped_text, flags=re.DOTALL)
    link_data_soup = []
    if(bool(long_description_data)):
        console.print('Checking setup.cfg long_description associated file....')
        for data in long_description_data:
            #file to which the long description redirects to
            long_description_file = re.findall(FILE_IN_LONG_DESCRIPTION_PATTERN, data, flags=re.DOTALL)
            #if a file is indicated, go to its location and scrape the HTML text
            if bool(long_description_file):
                long_description_file = ''.join(long_description_file)
                LONG_DESCRIPTION_LINK = repo_link + '#%s'%(long_description_file)
                long_description_soup = get_html(LONG_DESCRIPTION_LINK)
                link_data_soup = long_description_soup.find_all("article",{'class': 'markdown-body entry-content container-lg'})
                link_data_soup = link_data_soup[0]
            #otherwise, scrape the HTML text from the READ.ME
            else:
                LONG_DESCRIPTION_LINK = repo_link + '#readme'
                long_description_soup = get_html(LONG_DESCRIPTION_LINK)
                link_data_soup = long_description_soup.find_all("article",{'class': 'markdown-body entry-content container-lg'})
                link_data_soup = link_data_soup[0]

    return link_data_soup


def video_metadata_cfgfile(description_file_soup):
    """Checks for Video data on the file location referenced in the long_description field of setup.cfg
    Parameters
    ----------
    description_file_soup : str
        scraped text from long_description referenced file 
    
    Returns
    -------
    intro_video_check: bool
        True if Video is found, False on the contrary
    """
    intro_video_check = False
    #getting all video tags found in the scraped text
    if(bool(description_file_soup)):
        video_data = description_file_soup.find_all("video")
        if len(video_data)>0:
                intro_video_check = True
    return intro_video_check


def screenshot_metadata_cfgfile(description_file_soup):
    """Checks for Screenshot data on the file location referenced in the long_description field of setup.cfg
    Parameters
    ----------
    description_file_soup : str
        scraped text from long_description referenced file 
    
    Returns
    -------
    intro_screenshot_check: bool
        True if Screenshot is found, False on the contrary
    """
    intro_screenshot_check = False
    if(bool(description_file_soup)):
        #getting all image tags found in the scraped text
        screenshot_data = description_file_soup.find_all("img")
        for data in screenshot_data:
            data = str(data)
            #getting the found images max width percentage
            image_maxwidth_percentage = re.findall(IMAGE_STYLE_PATTERN, data, flags=re.DOTALL)
            #getting the found images width value
            image_width = re.findall(IMAGE_WIDTH_PATTERN, data, flags=re.DOTALL)
            #checking for shields.io image (logos and status)
            shields_io_image = re.findall(SHIELDS_IO_PATTERN, data, flags=re.DOTALL)
             #if an image width is bigger than 200 and is not a shields.io logo image then it's considered an actual image
            if(bool(image_width) and not bool(shields_io_image)):
                for i in image_width:
                    width_number = int(str(i))
                    if width_number > 200 :
                        intro_screenshot_check = True
            #if an image max width percentage is bigger than 30% and is not a shields.io logo image then it's considered an actual image
            if not bool(image_width) and (bool(image_maxwidth_percentage)and not bool(shields_io_image)):
                for i in image_maxwidth_percentage:
                    percentage_number = int(str(i))
                    if percentage_number > 30:
                        intro_screenshot_check = True
        
           
    return intro_screenshot_check



def usage_metadata_cfgfile(description_file_soup):
    """Checks for Usage section data on the file location referenced in the long_description field of setup.cfg
    Parameters
    ----------
    description_file_soup : str
        scraped text from long_description referenced file 
    
    Returns
    -------
    usage_check: bool
        True if Usage section is found, False on the contrary
    """
    usage_check = False
    #getting all usage title tags found in the scraped text
    if(bool(description_file_soup)):
        usage_data = description_file_soup.find_all("a", {'href':'#usage'})
        #if there's a usage section found then the checklist value for usage is True
        if bool(usage_data):
                usage_check = True
    return usage_check



def intro_metadata_cfgfile(description_file_soup):
    """Checks for Intro Paragraph data on the file location referenced in the long_description field of setup.cfg
    Parameters
    ----------
    description_file_soup : str
        scraped text from long_description referenced file 
    
    Returns
    -------
    intro_paragraph_check: bool
        True if Intro Paragraph is found, False on the contrary
    """
    intro_paragraph_check = False
    if(bool(description_file_soup)):
        #intro paragraph is the first paragraph found, so it precedes a h2 tag
        possible_intro_paragraph = description_file_soup.select_one('h2').find_all_previous('p', {'dir':'auto'})
        actual_text_in_p_count = 0
        for intro_paragraph in possible_intro_paragraph:
                if(bool(intro_paragraph.text)):
                    actual_text_in_p_count += + 1
        # if there's text found then the checklist value for intro paragraph is True
        if actual_text_in_p_count > 0:
                intro_paragraph_check = True

    return intro_paragraph_check






