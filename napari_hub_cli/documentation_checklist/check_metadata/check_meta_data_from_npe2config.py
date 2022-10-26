from .githubInfo import *
from .htmlScraper import *
from rich import print
from rich.console import Console
import requests



NPE2_DISPLAY_NAME_PATTERN = '(?:\sname\:\s)(.*?)(?=\s\n)'
NPE2_SETUPCFG_MANIFEST_PATTERN = '(?=napari.manifest\s\=)(.*?)(?:\.yaml\n)'
NPE2_SETUPCFG_FILE_PATTERN = '(?:\:)(.*?)(?=\'\])'
NPE2_SETUPPY_ENTRYPOINTS_PATTERN = '(?=entry_points\=\{)(.*?)(?:\})'
NPE2_SETUPPY_MANIFEST_FIELD_PATTERN = '(?=\'napari.manifest\')(.*?)(?:\.yaml\')'
NPE2_SETUPPY_FILE_PATTERN = '(?:\=\s)(.*?)(?=\"])'
NPE2_PYPROJECT_MANIFEST_PATTERN = '(?=napari.manifest\")(.*?)(?:\.yaml)'
NPE2_PYPROJECT_FILE_PATTERN = '(?:\:)(.*?)(?=\'\])'
NPE2_FOLDER_LOCATION_PATTERN = '(.*?)(?=\/napari\.yaml)'



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
    git_repo_username,git_repo_name, git_repo_link,git_base_branch = getGitInfo(path)
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

    git_repo_username,git_repo_name, git_repo_link,git_base_branch = getGitInfo(repo_path)

    napari_manifest_field = False
        
    if(check_for_file( repo_path, 'setup.py')):
        NAPARI_NPE2_LINK = git_repo_link + '/blob/%s/setup.py'%(git_base_branch)

        napari_npe2_soup = get_html(NAPARI_NPE2_LINK)   
        npe2_napari_manifest = napari_npe2_soup.find_all("table", {'class': 'highlight tab-size js-file-line-container js-code-nav-container js-tagsearch-file'})
        npe2_napari_manifest = str(npe2_napari_manifest)
        npe2_napari_manifest = strip_tags(npe2_napari_manifest)
        npe2_file = re.findall(NPE2_SETUPPY_ENTRYPOINTS_PATTERN, npe2_napari_manifest, flags=re.DOTALL)
        npe2_file = str(npe2_file)
        npe2_file = re.findall(NPE2_SETUPPY_MANIFEST_FIELD_PATTERN, npe2_file, flags=re.DOTALL)
        npe2_file = str(npe2_file)
        npe2_file = re.findall(NPE2_SETUPPY_FILE_PATTERN, npe2_file, flags=re.DOTALL)
        if(bool(npe2_file)):
            npe2_file = npe2_file[0] + '.yaml'
            napari_manifest_field = True

    if(check_for_file( repo_path, 'setup.cfg')and not bool(napari_manifest_field)):
        NAPARI_NPE2_LINK = git_repo_link + '/blob/%s/setup.cfg'%(git_base_branch)
        napari_npe2_soup = get_html(NAPARI_NPE2_LINK)   
        npe2_napari_manifest = napari_npe2_soup.find_all("table", {'class': 'highlight tab-size js-file-line-container js-code-nav-container js-tagsearch-file'})
        npe2_napari_manifest = str(npe2_napari_manifest)
        npe2_napari_manifest = strip_tags(npe2_napari_manifest)
        npe2_file = re.findall(NPE2_SETUPCFG_MANIFEST_PATTERN, npe2_napari_manifest, flags=re.DOTALL)
        npe2_file = str(npe2_file)
        npe2_file = re.findall(NPE2_SETUPCFG_FILE_PATTERN, npe2_file, flags=re.DOTALL)
        if(bool(npe2_file)):
            npe2_file = npe2_file[0] + '.yaml'
            napari_manifest_field = True

    if(check_for_file( repo_path, 'pyproject.toml') and not bool(napari_manifest_field)):
        NAPARI_NPE2_LINK = git_repo_link + '/blob/%s/pyproject.toml'%(git_base_branch)
        napari_npe2_soup = get_html(NAPARI_NPE2_LINK)   
        npe2_napari_manifest = napari_npe2_soup.find_all("table", {'class': 'highlight tab-size js-file-line-container js-code-nav-container js-tagsearch-file'})
        npe2_napari_manifest = str(npe2_napari_manifest)
        npe2_napari_manifest = strip_tags(npe2_napari_manifest)
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

    git_repo_username,git_repo_name, git_repo_link,git_base_branch = getGitInfo(path)
    
    files_url = "https://api.github.com/repos/{}/{}/git/trees/master?recursive=1".format(git_repo_username, git_repo_name)
    r = requests.get(files_url)
    res = r.json()

    for file in res["tree"]:
        if bool(re.findall(NPE2_FOLDER_LOCATION_PATTERN, file["path"], flags=re.DOTALL)):
            npe_location = re.findall(NPE2_FOLDER_LOCATION_PATTERN, file["path"], flags=re.DOTALL)
            NAPARI_YAML_LINK = git_repo_link + '/blob/%s/'%(git_base_branch)
            NAPARI_YAML_LINK = NAPARI_YAML_LINK + npe_location[0] + '/napari.yaml'

    napari_npe2_soup = get_html(NAPARI_YAML_LINK)   
    npe2_scraped_text = napari_npe2_soup.find_all("table", {'class': 'highlight tab-size js-file-line-container js-code-nav-container js-tagsearch-file'})
    npe2_scraped_text = str(npe2_scraped_text)
    npe2_scraped_text = strip_tags(npe2_scraped_text)

    display_name_data = re.findall(NPE2_DISPLAY_NAME_PATTERN, npe2_scraped_text, flags=re.DOTALL)
   
    return bool(display_name_data)
