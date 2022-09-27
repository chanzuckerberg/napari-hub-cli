
import requests
import json

def create_pull_request(project_name, repo_name, title, description, head_branch, base_branch, git_token):
    """Creates the pull request for the head_branch against the base_branch

    Parameters
    ----------
    project_name : str
        holds the name of the GitHub Repository project
    repo_name : str
        holds the name of the GitHub Repository
    title : str
        title of the Pull Request
    description : str
        description of the Pull Request
    head_branch : str
        holds the name of the GitHub Repository head branch
    base_branch : str
        holds the name of the GitHub Repository base branch
    git_token : str
        holds the input value for the git authorization token

    Returns
    -------
        pull request for the head_branch against the base_branch
        
    """
   #getting the correct API to create the PR
    git_pulls_api = "https://api.github.com/repos/{0}/{1}/pulls".format(
        project_name,
        repo_name)
    headers = {
        "Authorization": "token {0}".format(git_token),
        "Content-Type": "application/vnd.github+json"}

    payload = {
        "title": title,
        "body": description,
        "head": head_branch,
        "base": base_branch,
    }
    #post request for the Pull Request
    r = requests.post(
        git_pulls_api,
        headers=headers,
        data=json.dumps(payload))

    if not r.ok:
        print("Request Failed: {0}".format(r.text))