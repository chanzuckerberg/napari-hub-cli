from .htmlScraper import *
from .githubInfo import *
from rich import print
from rich.console import Console

def description_soup(path):
    console = Console()
    console.print('Checking napari-hub/description.md file...')

    git_repo_username,git_repo_name, git_repo_link,git_base_branch = getGitInfo(path)
    NAPARI_DESCRIPTION_LINK = git_repo_link + '/blob/%s/.napari-hub/DESCRIPTION.md'%(git_base_branch)

    return get_html(NAPARI_DESCRIPTION_LINK)


def screenshot_metadata_descriptionfile(soup):

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

    usage = False
    for tag in soup.find_all("div", {'class': 'Box-body readme blob js-code-block-container p-5 p-xl-6 gist-border-0'}):
        for anchor in tag.find_all("a", {'href':'#usage'}):
            if (bool(anchor)):
                usage = True
    return(usage)



def intro_metadata_descriptionfile(soup):

    intro_paragraph_check = False
    for tag in soup.find_all("div", {'class': 'Box-body readme blob js-code-block-container p-5 p-xl-6 gist-border-0'}):
        for anchor in tag.select_one('h2').find_all_previous('p', {'dir':'auto'}):
            if (bool(anchor)):
                anchor = str(anchor)
                anchor = strip_tags(anchor)
                if(len(anchor) > 0):
                    intro_paragraph_check = True
    return(intro_paragraph_check)


repo_path = '/Users/simaosa/Desktop/MetaCell/Projects/CZI/CLI_29/CZI-29-test'
print('\n')

x_soup = description_soup(repo_path)
y = screenshot_metadata_descriptionfile(x_soup)
print('Screenshot found?')
print(y)
print('\n')

z = video_metadata_descriptionfile(x_soup)
print('Video found?')
print(z)
print('\n')


c = usage_metadata_descriptionfile(x_soup)
print('Usage section found?')
print(c)
print('\n')


d = intro_metadata_descriptionfile(x_soup)
print('Intro paragraph found?')
print(d)
print('\n')
