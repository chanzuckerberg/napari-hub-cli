from .htmlScraper import *
from .githubInfo import *
from rich import print
from rich.console import Console

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

    git_repo_username,git_repo_name, git_repo_link,git_base_branch = getGitInfo(path)
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

    images = 0
    image_check = False
    for tag in soup.find_all("div", {'class': 'Box-body readme blob js-code-block-container p-5 p-xl-6 gist-border-0'}):
        for anchor in tag.find_all('img'):
            if (bool(anchor)):
                images += 1
    if (images>0):
        image_check = True
    return(image_check)



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
    for tag in soup.find_all("div", {'class': 'Box-body readme blob js-code-block-container p-5 p-xl-6 gist-border-0'}):
        for anchor in tag.find_all('video'):
            if (bool(anchor)):
                video += 1
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
    for tag in soup.find_all("div", {'class': 'Box-body readme blob js-code-block-container p-5 p-xl-6 gist-border-0'}):
        for anchor in tag.find_all("a", {'href':'#usage'}):
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
    for tag in soup.find_all("div", {'class': 'Box-body readme blob js-code-block-container p-5 p-xl-6 gist-border-0'}):
        for anchor in tag.select_one('h2').find_all_previous('p', {'dir':'auto'}):
            if (bool(anchor)):
                anchor = str(anchor)
                anchor = strip_tags(anchor)
                if(len(anchor) > 0):
                    intro_paragraph_check = True
    return(intro_paragraph_check)

