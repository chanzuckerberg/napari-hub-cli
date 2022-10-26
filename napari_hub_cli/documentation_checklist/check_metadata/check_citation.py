import re
import requests
from bs4 import BeautifulSoup
from .githubInfo import *
from rich import print
from rich.console import Console



def check_for_citation( path: str, name: str) -> bool:
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
    console = Console()
    console.print('Checking citation file...')
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

