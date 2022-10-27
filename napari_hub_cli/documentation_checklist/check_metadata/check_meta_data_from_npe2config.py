from .githubInfo import *
from .htmlScraper import *
from rich import print
from rich.console import Console
import requests
from .patterns_doc_checklist import *


def check_for_file( path: str, name: str) -> bool:
    """Checks for a specific file in a GitHub repository
    Parameters
    ----------
    path : str
        local path to the plugin
    name : str
        name of the file to look for
    Returns
    -------
    bool: True if the file exists, False if it doesn't
    """
    #get Git information from the local plugin path
    git_repo_username,git_repo_name, git_repo_link,git_base_branch = getGitInfo(path)
    #check if a file exists as a title in the scraped github text
    try:
            r = requests.get(git_repo_link)
            html_doc = r.text
            soup = BeautifulSoup(html_doc,'html5lib')
            file = soup.find_all(title=re.compile(name))
            if file:
                return True
            else:
                return False
    except Exception:
            return False


def npe2_file_location(repo_path):
    """Get the npe2 file name
    Parameters
    ----------
    repo_path : str
        local path to the plugin
    
    Returns
    -------
    npe2_file: str
        npe2 file name
    """
    console = Console()
    console.print('Checking npe2 file location...')
    #get Git information from the local plugin path
    git_repo_username,git_repo_name, git_repo_link,git_base_branch = getGitInfo(repo_path)

    napari_manifest_field = False
    #check if the repo contains a setup.py file    
    if(check_for_file( repo_path, 'setup.py')):
        #create URL for the setup.py file location
        NAPARI_NPE2_LINK = git_repo_link + '/blob/%s/setup.py'%(git_base_branch)
        #get the scraped html text 
        napari_npe2_soup = get_html(NAPARI_NPE2_LINK)   
        npe2_napari_manifest = napari_npe2_soup.find_all("table", {'class': 'highlight tab-size js-file-line-container js-code-nav-container js-tagsearch-file'})
        npe2_napari_manifest = str(npe2_napari_manifest)
        #strip the HTML tags
        npe2_napari_manifest = strip_tags(npe2_napari_manifest)
        # find the napari npe2 file in the napari-manifest
        npe2_file = re.findall(NPE2_SETUPPY_ENTRYPOINTS_PATTERN, npe2_napari_manifest, flags=re.DOTALL)
        npe2_file = str(npe2_file)
        npe2_file = re.findall(NPE2_SETUPPY_MANIFEST_FIELD_PATTERN, npe2_file, flags=re.DOTALL)
        npe2_file = str(npe2_file)
        npe2_file = re.findall(NPE2_SETUPPY_FILE_PATTERN, npe2_file, flags=re.DOTALL)
        if(bool(npe2_file)):
            npe2_file = npe2_file[0] + '.yaml'
            napari_manifest_field = True

    #check if the repo contains a setup.cfg file and if ther napari npe2 file was found already in a napari-manifest
    if(check_for_file( repo_path, 'setup.cfg')and not bool(napari_manifest_field)):
        #create URL for the setup.cfg file location
        NAPARI_NPE2_LINK = git_repo_link + '/blob/%s/setup.cfg'%(git_base_branch)
        #get the scraped html text 
        napari_npe2_soup = get_html(NAPARI_NPE2_LINK)   
        npe2_napari_manifest = napari_npe2_soup.find_all("table", {'class': 'highlight tab-size js-file-line-container js-code-nav-container js-tagsearch-file'})
        npe2_napari_manifest = str(npe2_napari_manifest)
        #strip the HTML tags
        npe2_napari_manifest = strip_tags(npe2_napari_manifest)
        # find the napari npe2 file in the napari-manifest
        npe2_file = re.findall(NPE2_SETUPCFG_MANIFEST_PATTERN, npe2_napari_manifest, flags=re.DOTALL)
        npe2_file = str(npe2_file)
        npe2_file = re.findall(NPE2_SETUPCFG_FILE_PATTERN, npe2_file, flags=re.DOTALL)
        if(bool(npe2_file)):
            npe2_file = npe2_file[0] + '.yaml'
            napari_manifest_field = True

    #check if the repo contains a pyproject.toml file    
    if(check_for_file( repo_path, 'pyproject.toml') and not bool(napari_manifest_field)):
        #create URL for the pyproject.toml file location
        NAPARI_NPE2_LINK = git_repo_link + '/blob/%s/pyproject.toml'%(git_base_branch)
        #get the scraped html text 
        napari_npe2_soup = get_html(NAPARI_NPE2_LINK)   
        npe2_napari_manifest = napari_npe2_soup.find_all("table", {'class': 'highlight tab-size js-file-line-container js-code-nav-container js-tagsearch-file'})
        npe2_napari_manifest = str(npe2_napari_manifest)
        #strip the HTML tags
        npe2_napari_manifest = strip_tags(npe2_napari_manifest)
        # find the napari npe2 file name in the napari-manifest
        npe2_file = re.findall(NPE2_PYPROJECT_MANIFEST_PATTERN, npe2_napari_manifest, flags=re.DOTALL)
        npe2_file = str(npe2_file)
        npe2_file = re.findall(NPE2_SETUPCFG_FILE_PATTERN, npe2_file, flags=re.DOTALL)
        if(bool(npe2_file)):
            npe2_file = npe2_file[0] + '.yaml'
    
    return npe2_file


def name_metadata_npe2file(path, npe2file):
    """Check for Display Name data in the npe2 file
    Parameters
    ----------
    path : str
        local path to the plugin
    npe2file : str
        npe2 file name
    
    Returns
    -------
    bool(display_name_data): bool
        True if Display Name is found, False on the contrary
    """
    console = Console()
    #get Git information from the local plugin path
    git_repo_username,git_repo_name, git_repo_link,git_base_branch = getGitInfo(path)
    # link to the github api to get the full list of files in the repository
    files_url = "https://api.github.com/repos/{}/{}/git/trees/{}?recursive=1".format(git_repo_username, git_repo_name,git_base_branch )
    #get the full list of files in the repository
    r = requests.get(files_url)
    res = r.json()
    if(bool(res["tree"])):
        for file in res["tree"]:
            #find a napari.yaml npe2 file location
            if bool(re.findall(NPE2_FOLDER_LOCATION_PATTERN, file["path"], flags=re.DOTALL)):
                npe_location = re.findall(NPE2_FOLDER_LOCATION_PATTERN, file["path"], flags=re.DOTALL)
                #link to the npe2 napari.yaml file in the current github repo
                NAPARI_YAML_LINK = git_repo_link + '/blob/%s/'%(git_base_branch)
                NAPARI_YAML_LINK = NAPARI_YAML_LINK + npe_location[0] + '/' + npe2file 
            else:
                npe2file = str(npe2file)
                NAPARI_YAML_LINK = git_repo_link + '/blob/%s/'%(git_base_branch)
                NAPARI_YAML_LINK = NAPARI_YAML_LINK  + npe2file 
    else:
        npe2file = str(npe2file)
        NAPARI_YAML_LINK = git_repo_link + '/blob/%s/'%(git_base_branch)
        NAPARI_YAML_LINK = NAPARI_YAML_LINK  + npe2file 

    #get scraped text from napari.yaml file
    napari_npe2_soup = get_html(NAPARI_YAML_LINK)   
    npe2_scraped_text = napari_npe2_soup.find_all("table", {'class': 'highlight tab-size js-file-line-container js-code-nav-container js-tagsearch-file'})
    npe2_scraped_text = str(npe2_scraped_text)
    #strip the HTML tags
    npe2_scraped_text = strip_tags(npe2_scraped_text)
    #find the display name in the napari.yaml file
    display_name_data = re.findall(NPE2_DISPLAY_NAME_PATTERN, npe2_scraped_text, flags=re.DOTALL)

    return bool(display_name_data)
