from .githubInfo import *
from .htmlScraper import *
from rich import print
from rich.console import Console

repo_path = '/Users/simaosa/Desktop/MetaCell/Projects/CZI/CLI_29/CZI-29-test'

NPE2_DISPLAY_NAME_PATTERN = '(?:\sname\:\s)(.*?)(?=\s\n)'
NPE2_SETUPCFG_MANIFEST_PATTERN = '(?=napari.manifest\s\=)(.*?)(?:\.yaml\n)'
NPE2_SETUPCFG_FILE_PATTERN = '(?:\:)(.*?)(?=\'\])'
NPE2_SETUPPY_ENTRYPOINTS_PATTERN = '(?=entry_points\=\{)(.*?)(?:\})'
NPE2_SETUPPY_MANIFEST_FIELD_PATTERN = '(?=\'napari.manifest\')(.*?)(?:\.yaml\')'
NPE2_SETUPPY_FILE_PATTERN = '(?:\=\s)(.*?)(?=\"])'
NPE2_PYPROJECT_MANIFEST_PATTERN = '(?=napari.manifest\")(.*?)(?:\.yaml)'
NPE2_PYPROJECT_FILE_PATTERN = '(?:\:)(.*?)(?=\'\])'



def check_for_file( path: str, name: str) -> bool:
    git_repo_username,git_repo_name, git_repo_link,git_base_branch = getGitInfo(repo_path)
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
        # print(npe2_file)

        

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
        # print(npe2_file)

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
        # print(npe2_file)

    return npe2_file


def name_metadata_npe2file(path, npe2file):
    console = Console()

    git_repo_username,git_repo_name, git_repo_link,git_base_branch = getGitInfo(path)

    NAPARI_YAML_LINK = git_repo_link + '/blob/%s/'%(git_base_branch)
    NAPARI_YAML_LINK = NAPARI_YAML_LINK + '%s'%(npe2file)

    napari_npe2_soup = get_html(NAPARI_YAML_LINK)   
    npe2_scraped_text = napari_npe2_soup.find_all("table", {'class': 'highlight tab-size js-file-line-container js-code-nav-container js-tagsearch-file'})
    npe2_scraped_text = str(npe2_scraped_text)
    npe2_scraped_text = strip_tags(npe2_scraped_text)

    display_name_data = re.findall(NPE2_DISPLAY_NAME_PATTERN, npe2_scraped_text, flags=re.DOTALL)
    if(bool(display_name_data)):
        console.print('Checking npe2 data in %s file...'%(npe2file), style = 'yellow')
    return bool(display_name_data)


# npe2_napari_file = npe2_file_location(repo_path)
# print(name_metadata_npe2file(repo_path, npe2_napari_file))