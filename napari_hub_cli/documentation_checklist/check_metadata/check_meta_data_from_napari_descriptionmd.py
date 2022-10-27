from .htmlScraper import *
from .githubInfo import *
from rich import print
from rich.console import Console
from .patterns_doc_checklist import *


def description_soup(path):
    """Gets the napari-hub/description.md file scraped text from a plugin repo local path
    Parameters
    ----------
    path : str
        local path to the plugin
    
    Returns
    -------
    get_html(NAPARI_DESCRIPTION_LINK): func
        napari-hub/description.md file scraped text
    """
    console = Console()
    console.print('Checking napari-hub/description.md file...')

    #get Git information from the local plugin path
    git_repo_username,git_repo_name, git_repo_link,git_base_branch = getGitInfo(path)
    #create URL for the napari-hub/DESCRIPTION.md file location
    NAPARI_DESCRIPTION_LINK = git_repo_link + '/blob/%s/.napari-hub/DESCRIPTION.md'%(git_base_branch)

    return get_html(NAPARI_DESCRIPTION_LINK)


def screenshot_metadata_descriptionfile(soup):
    """Checks for Screenshot data on the napari-hub/description.md file
    Parameters
    ----------
    soup : str
        napari-hub/description.md file scraped text
    
    Returns
    -------
    image_check: bool
        True if Screenshot is found, False on the contrary
    """
    
    image_check = False
    if(bool(soup)):
        #getting all image tags found in the scraped napari-hub/DESCRIPTION.md text
        screenshot_data = soup.find_all("img")
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
                        image_check = True

            #if an image max width percentage is bigger than 30% and is not a shields.io logo image then it's considered an actual image
            if not bool(image_width) and (bool(image_maxwidth_percentage)and not bool(shields_io_image)):
                for i in image_maxwidth_percentage:
                    percentage_number = int(str(i))
                    if percentage_number > 30:
                        image_check = True
        
           
    return image_check



def video_metadata_descriptionfile(soup):
    """Checks for Video data on the napari-hub/description.md file
    Parameters
    ----------
    soup : str
        napari-hub/description.md file scraped text
    
    Returns
    -------
    video_check: bool
        True if Video is found, False on the contrary
    """
    video = 0
    video_check = False
    #getting all video tags found in the scraped napari-hub/DESCRIPTION.md text
    for tag in soup.find_all("div", {'class': 'Box-body readme blob js-code-block-container p-5 p-xl-6 gist-border-0'}):
        for anchor in tag.find_all('video'):
            # if there's a video found it's added to the video count
            if (bool(anchor)):
                video += 1
    #if a video is found then we can assume it has a introductory video
    if(video>0):
        video_check = True
    return(video_check)



def usage_metadata_descriptionfile(soup):
    """Checks for Usage section on the napari-hub/description.md file
    Parameters
    ----------
    soup : str
        napari-hub/description.md file scraped text
    
    Returns
    -------
    usage: bool
        True if Usage section is found, False on the contrary
    """

    usage = False
    #getting all usage title tags found in the scraped napari-hub/DESCRIPTION.md text
    for tag in soup.find_all("div", {'class': 'Box-body readme blob js-code-block-container p-5 p-xl-6 gist-border-0'}):
        for anchor in tag.find_all("a", {'href':'#usage'}):
            # if there's a usage section found then the checklist value for usage is True
            if (bool(anchor)):
                usage = True
    return(usage)



def intro_metadata_descriptionfile(soup):
    """Checks for Intro Paragraph data on the napari-hub/description.md file
    Parameters
    ----------
    soup : str
        napari-hub/description.md file scraped text
    
    Returns
    -------
    intro_paragraph_check: bool
        True if Intro Paragraph is found, False on the contrary
    """

    intro_paragraph_check = False
    #getting all paragraph tags found in the scraped napari-hub/DESCRIPTION.md text
    for tag in soup.find_all("div", {'class': 'Box-body readme blob js-code-block-container p-5 p-xl-6 gist-border-0'}):
        #intro paragraph is the first paragraph found, so it precedes a h2 tag
        for anchor in tag.select_one('h2').find_all_previous('p', {'dir':'auto'}):
            if (bool(anchor)):
                anchor = str(anchor)
                anchor = strip_tags(anchor)
                # if there's text found then the checklist value for intro paragraph is True
                if(len(anchor) > 0):
                    intro_paragraph_check = True
    return(intro_paragraph_check)

