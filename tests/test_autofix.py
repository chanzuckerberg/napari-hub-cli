import json
import os
import shutil
from contextlib import suppress
from unittest.mock import patch

import git
import pytest
import requests_mock as req
from git.repo import Repo
from xdg import xdg_config_home

from napari_hub_cli.autofix import (
    autofix_repository,
    create_commit_citation,
    create_commits,
    create_PR_from_analysis,
    read_user_token,
    validate_plugin_selection,
)
from napari_hub_cli.checklist.metadata import analyse_local_plugin
from napari_hub_cli.constants import NAPARI_HUB_API_URL
from napari_hub_cli.fs import NapariPlugin


@pytest.fixture
def napari_hub(requests_mock):
    requests_mock.get(
        req.ANY,
        json={},
    )
    requests_mock.get(
        NAPARI_HUB_API_URL,
        json={
            "avidaq": "0.0.5",
            "mikro-napari": "0.1.49",
            "napari-curtain": "0.1.1",
        },
    )
    requests_mock.get(
        f"{NAPARI_HUB_API_URL}/avidaq",
        json={"code_repository": "http://github.com/user1/avidaq"},
    )
    requests_mock.get(
        f"{NAPARI_HUB_API_URL}/mikro-napari",
        json={"code_repository": "http://github.com/user1/mikro-napari"},
    )
    requests_mock.get(
        f"{NAPARI_HUB_API_URL}/napari-curtain",
        json={"code_repository": "http://github.com/user2/napari-curtain"},
    )
    return requests_mock


@pytest.fixture(scope="module")
def tmp_git_repo1(tmp_path_factory):
    repo_path = tmp_path_factory.mktemp("git_repo1")
    repo = Repo.init(repo_path)
    readme = repo_path / "README.md"
    readme.write_text("# Plugin example")
    index = repo.index
    index.add([readme])
    index.commit("Add README.md")

    changelog = repo_path / "CHANGELOG.md"
    changelog.write_text("# Plugin changelog")
    index = repo.index
    index.add([changelog])
    index.commit("Add CHANGELOG.md")
    return repo_path, repo


@pytest.fixture(scope="module")
def tmp_git_repo2(tmp_path_factory):
    repo_path = tmp_path_factory.mktemp("git_repo2")
    final_path = repo_path / "inside"
    shutil.copytree(src="tests/resources/autofix_repo", dst=final_path)

    repo = Repo.init(final_path)
    readme = final_path / "README.md"
    readme.write_text(
        """# Plugin example
## Installation"""
    )
    index = repo.index
    index.add([readme])
    index.commit("Add README.md")
    return final_path, repo


@pytest.fixture()
def tmp_git_repo3(tmp_path_factory):
    repo_path = tmp_path_factory.mktemp("git_repo3")
    final_path = repo_path / "inside"
    shutil.copytree(src="tests/resources/autofix_repo2", dst=final_path)

    repo = Repo.init(final_path)
    readme = final_path / "README.md"
    readme.write_text(
        """# Plugin example
## Installation"""
    )
    index = repo.index
    index.add([readme])
    index.commit("Add README.md")
    return final_path, repo


def setup_module(module):
    with suppress(KeyError):
        module.GITHUB_USER = os.environ["GITHUB_USER"]
        del os.environ["GITHUB_USER"]

    with suppress(KeyError):
        module.GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
        del os.environ["GITHUB_TOKEN"]


def teardown_module(module):
    with suppress(KeyError, AttributeError):
        os.environ["GITHUB_USER"] = module.GITHUB_USER
        delattr(module, "GITHUB_USER")

    with suppress(KeyError, AttributeError):
        os.environ["GITHUB_TOKEN"] = module.GITHUB_TOKEN
        delattr(module, "GITHUB_TOKEN")


@pytest.fixture
def config_home():
    yield xdg_config_home() / "napari-hub-cli"
    with suppress(KeyError):
        del os.environ["GITHUB_TOKEN"]
    with suppress(KeyError):
        del os.environ["GITHUB_USER"]


def test_get_token_no_varenv(config_home):
    exist_config = (config_home / "config.yml").exists()

    with suppress(KeyError):
        del os.environ["GITHUB_TOKEN"]
    with suppress(KeyError):
        del os.environ["GITHUB_USER"]

    with pytest.raises(SystemExit) as e:
        read_user_token()

    assert e.type is SystemExit
    assert e.value.code == -1

    assert exist_config == (config_home / "config.yml").exists()


def test_get_token_username_token_inmem(config_home):
    exist_config = (config_home / "config.yml").exists()

    os.environ["GITHUB_TOKEN"] = "TOK"
    os.environ["GITHUB_USER"] = "ULOG"

    username, token = read_user_token()

    assert username == "ULOG"
    assert token == "TOK"

    assert exist_config == (config_home / "config.yml").exists()


def test_get_token_only_token_inmem_user_input(tmp_path, monkeypatch):
    home_config = tmp_path
    config_file = home_config / "config.yml"

    monkeypatch.setattr("builtins.input", lambda _: "USER")

    assert config_file.exists() is False

    os.environ["GITHUB_TOKEN"] = "TOK2"
    username, token = read_user_token(home_config=home_config)

    assert username == "USER"
    assert token == "TOK2"


def test_get_token_inmem_user_infile(tmp_path):
    home_config = tmp_path
    config_file = home_config / "config.yml"
    config_file.write_text(
        """---
gh_user: GHUSERNAME
"""
    )

    assert config_file.exists() is True

    os.environ["GITHUB_TOKEN"] = "TOK3"
    username, token = read_user_token(home_config=home_config)

    assert username == "GHUSERNAME"
    assert token == "TOK3"


def test_get_token_inmem_user_notinfile_file_exists(tmp_path, monkeypatch):
    home_config = tmp_path
    config_file = home_config / "config.yml"
    config_file.write_text("")

    monkeypatch.setattr("builtins.input", lambda _: "GHUSERWRITTEN")

    assert config_file.exists() is True

    os.environ["GITHUB_TOKEN"] = "TOK4"
    username, token = read_user_token(home_config=home_config)

    assert username == "GHUSERWRITTEN"
    assert token == "TOK4"


def test_plugin_selection(napari_hub):
    plugins = ["avidaq", "mikro-napari", "napari-curtain"]

    validation, result = validate_plugin_selection(plugins)

    assert validation is True
    assert len(result) == 3
    assert result["avidaq"] == "http://github.com/user1/avidaq"
    assert result["mikro-napari"] == "http://github.com/user1/mikro-napari"
    assert result["napari-curtain"] == "http://github.com/user2/napari-curtain"


def test_plugin_selection_missing(napari_hub):
    plugins = ["avidaq", "mikro-napari", "napari-curta"]

    validation, result = validate_plugin_selection(plugins)

    assert validation is False
    assert len(result) == 1
    assert result["napari-curta"] == "napari-curtain"


def test_create_commits_nothing(tmp_git_repo1):
    path, repo = tmp_git_repo1
    result = analyse_local_plugin(path)

    nb_commits = len(list(repo.iter_commits()))

    commited = create_commits(result, display_info=True)

    new_nb_commits = len(list(repo.iter_commits()))

    assert commited is False
    assert nb_commits == new_nb_commits


def test_create_commits(tmp_git_repo2):
    path, repo = tmp_git_repo2
    result = analyse_local_plugin(path)

    nb_commits = len(list(repo.iter_commits()))
    commited = create_commits(result, display_info=True)
    new_nb_commits = len(list(repo.iter_commits()))

    assert commited is True
    assert nb_commits + 1 == new_nb_commits


def test_create_citation_not_required(tmp_git_repo2):
    path, repo = tmp_git_repo2
    result = analyse_local_plugin(path)

    nb_commits = len(list(repo.iter_commits()))
    commited = create_commit_citation(result, display_info=True)
    new_nb_commits = len(list(repo.iter_commits()))

    assert commited is False
    assert nb_commits == new_nb_commits


def test_create_citation(tmp_git_repo3):
    path, repo = tmp_git_repo3
    result = analyse_local_plugin(path)

    nb_commits = len(list(repo.iter_commits()))
    commited = create_commit_citation(result, display_info=True)
    new_nb_commits = len(list(repo.iter_commits()))

    assert commited is True
    assert nb_commits + 1 == new_nb_commits

    plugin = NapariPlugin(path)

    assert plugin.citation_file.exists is True


def test_autofix_local_plugin(tmp_git_repo3):
    path, repo = tmp_git_repo3

    nb_commits = len(list(repo.iter_commits()))
    autofix_repository(path)
    new_nb_commits = len(list(repo.iter_commits()))

    # one commit for "summary" and one commit for "citation"
    assert nb_commits + 2 == new_nb_commits

    plugin = NapariPlugin(path)

    assert plugin.citation_file.exists is True


# Smoke test
def test_create_pr_issue(mocker, tmp_git_repo3, requests_mock):
    # setup/mocks
    import git.cmd
    import git.refs
    import git.repo
    import github3.repos

    os.environ["GITHUB_TOKEN"] = "TOK"

    requests_mock.get(
        url="https://api.github.com/repos/unexisting/unexisting", json=FAKE
    )
    requests_mock.post(
        url="https://api.github.com/repos/unexisting/unexisting/forks", json=FAKE
    )
    requests_mock.post(
        url="https://api.github.com/repos/unexisting/unexisting/pulls", json=FAKE
    )
    requests_mock.get(url="https://api.github.com/user", json=FAKE_ME)

    mocker.patch("git.repo.Repo.git")
    mocker.patch.object(git.cmd.Git, "push", create=True)
    # mocker.patch.object(git.repo.base.Repo, "HEAD", create=True)
    mocker.patch("git.remote.Remote.pull")
    mocker.patch.object(github3.repos.repo, "Repository")

    path, repo = tmp_git_repo3
    result = analyse_local_plugin(path)

    create_PR_from_analysis(
        result,
        "https://github.com/unexisting/unexisting",
        gh_login="MYLOGIN",
        dry_run=False,
    )


# Smoke test
def test_create_pr_issue_dryrun(monkeypatch, tmp_git_repo3):
    # setup/mocks
    import git.repo

    os.environ["GITHUB_TOKEN"] = "TOK"

    monkeypatch.setattr("builtins.input", lambda _: "USER")

    path, _ = tmp_git_repo3
    result = analyse_local_plugin(path)

    create_PR_from_analysis(
        result,
        "https://github.com/unexisting/unexisting",
        gh_login="MYLOGIN",
        dry_run=True,
    )


# Smoke test
def test_create_pr_issue_dryrun_notgithub(monkeypatch, tmp_git_repo3):
    # setup/mocks
    import git.repo

    os.environ["GITHUB_TOKEN"] = "TOK"

    monkeypatch.setattr("builtins.input", lambda _: "USER")

    path, _ = tmp_git_repo3
    result = analyse_local_plugin(path)

    create_PR_from_analysis(
        result,
        "https://other.com/unexisting/unexisting",
        gh_login="MYLOGIN",
        dry_run=True,
    )


ASSIGNEE = {
    "login": "pyecore",
    "id": 28776027,
    "node_id": "MDEyOk9yZ2FuaXphdGlvbjI4Nzc2MDI3",
    "avatar_url": "https://avatars.githubusercontent.com/u/28776027?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/pyecore",
    "html_url": "https://github.com/pyecore",
    "followers_url": "https://api.github.com/users/pyecore/followers",
    "following_url": "https://api.github.com/users/pyecore/following{/other_user}",
    "gists_url": "https://api.github.com/users/pyecore/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/pyecore/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/pyecore/subscriptions",
    "organizations_url": "https://api.github.com/users/pyecore/orgs",
    "repos_url": "https://api.github.com/users/pyecore/repos",
    "events_url": "https://api.github.com/users/pyecore/events{/privacy}",
    "received_events_url": "https://api.github.com/users/pyecore/received_events",
    "type": "Organization",
    "site_admin": False,
}

FAKE = {
    "active_lock_reason": "",
    "base": {
        "ref": "",
        "label": "",
        "sha": "",
    },
    "body": "x",
    "body_html": "x",
    "body_text": "x",
    "closed_at": "2016-12-13T23:24:58Z",
    "diff_url": "",
    "head": {
        "ref": "",
        "label": "",
        "sha": "",
    },
    "issue_url": "",
    "_links": {},
    "locked": "",
    "merge_commit_sha": "",
    "merged_at": "",
    "number": "",
    "patch_url": "",
    "review_comments_url": [""],
    "review_comment_url": "",
    "assignee": ASSIGNEE,
    "assignees": [ASSIGNEE],
    "id": 76406837,
    "node_id": "MDEwOlJlcG9zaXRvcnk3NjQwNjgzNw==",
    "name": "pyecore",
    "full_name": "unexisting/unexisting",
    "private": False,
    "owner": ASSIGNEE,
    "html_url": "https://github.com/unexisting/unexisting",
    "description": "A Python(nic) Implementation of EMF/Ecore (Eclipse Modeling Framework)",
    "fork": False,
    "url": "https://api.github.com/repos/unexisting/unexisting",
    "forks_url": "https://api.github.com/repos/unexisting/unexisting/forks",
    "keys_url": "https://api.github.com/repos/unexisting/unexisting/keys{/key_id}",
    "collaborators_url": "https://api.github.com/repos/unexisting/unexisting/collaborators{/collaborator}",
    "teams_url": "https://api.github.com/repos/unexisting/unexisting/teams",
    "hooks_url": "https://api.github.com/repos/unexisting/unexisting/hooks",
    "issue_events_url": "https://api.github.com/repos/unexisting/unexisting/issues/events{/number}",
    "events_url": "https://api.github.com/repos/unexisting/unexisting/events",
    "assignees_url": "https://api.github.com/repos/unexisting/unexisting/assignees{/user}",
    "branches_url": "https://api.github.com/repos/unexisting/unexisting/branches{/branch}",
    "tags_url": "https://api.github.com/repos/unexisting/unexisting/tags",
    "blobs_url": "https://api.github.com/repos/unexisting/unexisting/git/blobs{/sha}",
    "git_tags_url": "https://api.github.com/repos/unexisting/unexisting/git/tags{/sha}",
    "git_refs_url": "https://api.github.com/repos/unexisting/unexisting/git/refs{/sha}",
    "trees_url": "https://api.github.com/repos/unexisting/unexisting/git/trees{/sha}",
    "statuses_url": "https://api.github.com/repos/unexisting/unexisting/statuses/{sha}",
    "languages_url": "https://api.github.com/repos/unexisting/unexisting/languages",
    "stargazers_url": "https://api.github.com/repos/unexisting/unexisting/stargazers",
    "contributors_url": "https://api.github.com/repos/unexisting/unexisting/contributors",
    "subscribers_url": "https://api.github.com/repos/unexisting/unexisting/subscribers",
    "subscription_url": "https://api.github.com/repos/unexisting/unexisting/subscription",
    "commits_url": "https://api.github.com/repos/unexisting/unexisting/commits{/sha}",
    "git_commits_url": "https://api.github.com/repos/unexisting/unexisting/git/commits{/sha}",
    "comments_url": "https://api.github.com/repos/unexisting/unexisting/comments{/number}",
    "issue_comment_url": "https://api.github.com/repos/unexisting/unexisting/issues/comments{/number}",
    "contents_url": "https://api.github.com/repos/unexisting/unexisting/contents/{+path}",
    "compare_url": "https://api.github.com/repos/unexisting/unexisting/compare/{base}...{head}",
    "merges_url": "https://api.github.com/repos/unexisting/unexisting/merges",
    "archive_url": "https://api.github.com/repos/unexisting/unexisting/{archive_format}{/ref}",
    "downloads_url": "https://api.github.com/repos/unexisting/unexisting/downloads",
    "issues_url": "https://api.github.com/repos/unexisting/unexisting/issues{/number}",
    "pulls_url": "https://api.github.com/repos/unexisting/unexisting/pulls{/number}",
    "milestones_url": "https://api.github.com/repos/unexisting/unexisting/milestones{/number}",
    "notifications_url": "https://api.github.com/repos/unexisting/unexisting/notifications{?since,all,participating}",
    "labels_url": "https://api.github.com/repos/unexisting/unexisting/labels{/name}",
    "releases_url": "https://api.github.com/repos/unexisting/unexisting/releases{/id}",
    "deployments_url": "https://api.github.com/repos/unexisting/unexisting/deployments",
    "created_at": "2016-12-13T23:24:58Z",
    "updated_at": "2023-01-03T03:42:11Z",
    "pushed_at": "2022-10-25T23:48:57Z",
    "git_url": "git://github.com/unexisting/unexisting.git",
    "ssh_url": "git@github.com:unexisting/unexisting.git",
    "clone_url": "https://github.com/unexisting/unexisting.git",
    "svn_url": "https://github.com/unexisting/unexisting",
    "homepage": "",
    "size": 1386,
    "stargazers_count": 131,
    "watchers_count": 131,
    "language": "Python",
    "has_issues": True,
    "has_projects": True,
    "has_downloads": True,
    "has_wiki": True,
    "has_pages": False,
    "has_discussions": False,
    "forks_count": 41,
    "mirror_url": None,
    "archived": False,
    "disabled": False,
    "open_issues_count": 31,
    "license": {
        "key": "bsd-3-clause",
        "name": 'BSD 3-Clause "New" or "Revised" License',
        "spdx_id": "BSD-3-Clause",
        "url": "https://api.github.com/licenses/bsd-3-clause",
        "node_id": "MDc6TGljZW5zZTU=",
    },
    "allow_forking": True,
    "is_template": True,
    "web_commit_signoff_required": False,
    "topics": [
        "code-generation",
        "ecore",
        "emf",
        "framework",
        "json",
        "metamodel",
        "metamodeling",
        "model-driven-development",
        "model-driven-engineering",
        "modeling",
        "python",
        "xmi",
    ],
    "visibility": "public",
    "forks": 41,
    "open_issues": 31,
    "watchers": 131,
    "default_branch": "master",
    "temp_clone_token": None,
    "organization": {
        "login": "pyecore",
        "id": 28776027,
        "node_id": "MDEyOk9yZ2FuaXphdGlvbjI4Nzc2MDI3",
        "avatar_url": "https://avatars.githubusercontent.com/u/28776027?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/pyecore",
        "html_url": "https://github.com/pyecore",
        "followers_url": "https://api.github.com/users/pyecore/followers",
        "following_url": "https://api.github.com/users/pyecore/following{/other_user}",
        "gists_url": "https://api.github.com/users/pyecore/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/pyecore/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/pyecore/subscriptions",
        "organizations_url": "https://api.github.com/users/pyecore/orgs",
        "repos_url": "https://api.github.com/users/pyecore/repos",
        "events_url": "https://api.github.com/users/pyecore/events{/privacy}",
        "received_events_url": "https://api.github.com/users/pyecore/received_events",
        "type": "Organization",
        "site_admin": False,
    },
    "network_count": 41,
    "subscribers_count": 12,
}


FAKE_ME = {
    "login": "me",
    "id": 9734,
    "node_id": "MDQ6VXNlcjk3MzQ=",
    "avatar_url": "https://avatars.githubusercontent.com/u/9734?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/me",
    "html_url": "https://github.com/me",
    "followers_url": "https://api.github.com/users/me/followers",
    "following_url": "https://api.github.com/users/me/following{/other_user}",
    "gists_url": "https://api.github.com/users/me/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/me/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/me/subscriptions",
    "organizations_url": "https://api.github.com/users/me/orgs",
    "repos_url": "https://api.github.com/users/me/repos",
    "events_url": "https://api.github.com/users/me/events{/privacy}",
    "received_events_url": "https://api.github.com/users/me/received_events",
    "type": "User",
    "site_admin": False,
    "name": "Ivan",
    "company": None,
    "blog": "",
    "location": None,
    "email": None,
    "hireable": None,
    "bio": None,
    "twitter_username": None,
    "public_repos": 44,
    "public_gists": 5,
    "followers": 39,
    "following": 0,
    "created_at": "2008-05-08T21:43:54Z",
    "updated_at": "2022-12-21T09:41:20Z",
}
