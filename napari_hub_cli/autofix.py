import os
import re
from contextlib import suppress
from pathlib import Path

import yaml
from git import GitCommandError
from git.repo import Repo
from github3 import login
from xdg import xdg_config_home

from .citations import create_cff_citation

from .checklist import analyse_remote_plugin_url
from .checklist.metadata_checklist import CITATION, CITATION_VALID
from .utils import delete_file_tree

PR_TITLE = "[Napari HUB cli] Metadata enhancement proposition"
ISSUE_TITLE = "[Napari HUB cli] Metadata enhancement"

GENERAL_INTRO = """I am the Napari-hub virtual assistant, and I would like to thank you for participating in the Napari-hub ecosystem with your work!

I am here to help you maintain and improve the metadata of your repository, so today I scanned your repo and I might have found some fields that are missing or that could be improved.
"""

PR_BODY = f"""Hi there,

{GENERAL_INTRO}

To make your work easier, I created this pull request that contains some suggestions to improve the metadata of your repository. Since there might be some minor inaccuracies, could you please review and accept the PR when everything looks good to you?

If any information is inaccurate, please feel free to edit it as you already have editing rights. Then proceed to commit/push this pull request.

This is an automatic procedure that we are developing and constantly improving, so if you have any question or comment, please feel free to reach out [neuromusic](https://github.com/neuromusic) and let us know what you think, we appreciate your feedback!

We all hope this pull request will be helpful to you,
Thank you for your help and feedback,

The Napari-hub and MetaCell teams.
"""

REDUNDANT_INTRO = """This issue comes as complement of #{pr_id}.

Scanning your repository, I identified some metadata that are either missing, or in files that are considered as secondary sources.
"""

METADATA_DIFFICULTIES = """While Scanning your repository, I identified some metadata that are either missing, or misplaced in files that are considered as secondary sources.

Since metadata sometimes is hard to fix automatically I created a list of what improvements you might want to look into to improve the overall quality of your repository:
"""

METADATA_DIFFICULTIES_NO_PR = """Metadata sometimes cannot be fixed automatically, so I created a list of what improvements you might want to look into to improve the overall quality of your repository:
"""

ISSUE_BODY = """{greetings}

{introduction}
{difficulties}
{issues}

If some metadata is already present and I overlooked it, please feel free to contact [neuromusic](https://github.com/neuromusic) to tell us what could be improved!

We all hope this issue will be helpful to you,
Thank you for your help and feedback,

The Napari-hub and MetaCell teams.
"""


def build_PR_message():
    return PR_BODY


def build_issue_message(pr_id, results):
    pr_opened = pr_id is not None
    greetings = "Hi again" if pr_opened else "Hi there"
    introduction = REDUNDANT_INTRO.format(pr_id=pr_id) if pr_opened else GENERAL_INTRO
    difficulties = METADATA_DIFFICULTIES if pr_opened else METADATA_DIFFICULTIES_NO_PR

    assert results.repository
    repo_path = results.repository.path

    issues = []
    citation_result = results[CITATION]
    for feature in results.missing_features():
        if feature.meta is CITATION_VALID and citation_result.found:
            msg = f"* Your citation file `{feature.scanned_files[0].file.relative_to(repo_path)}` has not a valid format (it cannot be properly parsed)"
            issues.append(msg)
            continue
        if feature.meta in (CITATION_VALID, CITATION):
            continue
        scanned_files = (
            f"`{x.file.relative_to(repo_path)}`" for x in feature.scanned_files
        )
        msg = f"* {feature.meta.name!r} entry was not found (scanned files: {', '.join(scanned_files)})"
        issues.append(msg)

    issues.append("")
    for feature in results.only_in_fallbacks():
        if feature.meta.automatically_fixable:
            continue
        scanned_files = (x for x in feature.scanned_files if x not in feature.fallbacks)
        scanned_files = (f"`{f.file.relative_to(repo_path)}`" for f in scanned_files)
        assert feature.found_in
        msg = f"* {feature.meta.name} was found in `{feature.found_in.file.relative_to(repo_path)}`, but it is preferred to place this information in {' or '.join(scanned_files)}"
        issues.append(msg)

    if len(issues) <= 1:
        return ""

    return ISSUE_BODY.format(
        greetings=greetings,
        introduction=introduction,
        difficulties=difficulties,
        issues="\n".join(issues),
    )


def create_commits(results):
    assert results.repository, "There is no results for this repository"
    plugin_repo = results.repository
    git_repo = Repo(plugin_repo.path)

    commited = False
    for feature in results.only_in_fallbacks():
        if not feature.meta.automatically_fixable:
            continue
        target = feature.main_files[0]
        source = feature.found_in
        assert target
        assert source
        feature_name = feature.meta.attribute[
            4:
        ]  # we skip the "has_", refactor in the future
        setattr(target, feature_name, getattr(source, feature_name))
        target.save()
        git_repo.git.add(target.file)
        msg = f"""
Copy "{feature.meta.name}" from secondary to primary file

{feature.meta.name} was found in a secondary file and copied in the primary one:
* (found here)  "{source.file.relative_to(plugin_repo.path)}"
* (copied here) "{target.file.relative_to(plugin_repo.path)}"
"""
        git_repo.git.commit(m=msg)
        commited = True
    return commited


def create_commit_citation(results):
    if results[CITATION].found:
        return False

    assert results.repository, "There is no results for this repository"
    plugin_repo = results.repository
    git_repo = Repo(plugin_repo.path)
    create_cff_citation(plugin_repo, display_info=False)
    git_repo.git.add(plugin_repo.citation_file.file)
    git_repo.git.commit(m="Add 'CITATION.cff' file")
    return True


def analyse_then_create_PR(plugin_name, plugin_url, directory=None, gh_login=None):
    # analysis
    result = analyse_remote_plugin_url(
        plugin_name, plugin_url, directory=directory, cleanup=False
    )
    if not (result.missing_features() or result.only_in_fallbacks()):
        print(f"All is good for {plugin_name}!")
        return

    # we con only automatically fix repositories in github
    match = re.match(
        r"https://github\.com/(?P<repo_user>[^/]+)/(?P<repo_name>[^/]+)", plugin_url
    )
    if not match:
        print(
            f"The {plugin_name!r} repository is not on github, automatic modification and issue/PR creation cannot be performed"
        )
        return
    remote_user, remote_name = match.groupdict().values()

    # perform modifications on the files
    assert result.repository is not None
    local_repository = Repo(result.repository.path)

    # modify + add + commit
    # citation is created first otherwise, the other commits made by the bot will be scrapped and it will appear as author
    need_pr = create_commit_citation(result)
    need_pr = create_commits(result) or need_pr

    # fork/prepare the remote/push/pr
    # login in GH
    if gh_login:
        os.environ["GITHUB_USER"] = gh_login
    gh_login, token = read_user_token()
    gh = login(gh_login, password=token)
    assert gh is not None

    # create the fork
    orig = gh.repository(remote_user, remote_name)
    assert orig is not None
    fork = orig.create_fork()
    assert fork is not None

    # init the new remote
    with suppress(GitCommandError):
        local_repository.create_remote(
            "napari_cli",
            f"https://{gh_login}:{token}@github.com/{gh_login}/{remote_name}",
        )

    # fetch/pull the new remote
    branch = local_repository.active_branch.name
    local_repository.remotes.napari_cli.pull(branch)

    # push in the new remote
    local_repository.remotes.napari_cli.push()

    # prepare the PR
    pr_id = None
    if need_pr:
        title = PR_TITLE
        body = build_PR_message()
        pull_request = orig.create_pull(
            title,
            body=body,
            head=f"{gh_login}:{branch}",
            base=branch,
            maintainer_can_modify=True,
        )
        assert pull_request
        pr_id = pull_request.number

    # prepare the issue
    issue_msg = build_issue_message(pr_id, result)
    if issue_msg:
        title = ISSUE_TITLE
        body = issue_msg
        orig.create_issue(title, body)

    to_remove = directory if directory else result.repository.path.parent
    delete_file_tree(to_remove)


def read_user_token(home_config=None):
    # token access use var env
    token = os.environ.get("GITHUB_TOKEN", None)
    if not token:
        print("Please provide your token as 'GITHUB_TOKEN' environement variable")
        exit(-1)

    username = os.environ.get("GITHUB_USER", None)
    if username:
        return username, token

    config_dir = (
        Path(home_config) if home_config else (xdg_config_home() / "napari-hub-cli")
    )
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.yml"
    if config_file.exists():
        with config_file.open(mode="r") as f:
            data = yaml.safe_load(f)
            data = data or {}
        with suppress(KeyError):
            username = data["gh_user"]
            return username, token
    username = input("Please enter your github username: ")
    username = username.strip()
    with config_file.open(mode="w") as f:
        yaml.dump({"gh_user": username}, stream=f, sort_keys=False)
    return username, token
