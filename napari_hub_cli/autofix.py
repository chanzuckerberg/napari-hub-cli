import os
import re
from contextlib import suppress
from pathlib import Path
from textwrap import indent

import yaml
from git import GitCommandError
from git.repo import Repo
from github3 import login
from rich.console import Console
from rich.markdown import Markdown
from xdg import xdg_config_home

from .checklist import analyse_local_plugin, analyse_remote_plugin_url
from .checklist.metadata import CITATION, CITATION_VALID, AnalysisStatus
from .citation import create_cff_citation
from .utils import NonExistingNapariPluginError, delete_file_tree, get_repository_url

PR_TITLE = "[Napari HUB cli] Metadata enhancement suggestions"
ISSUE_TITLE = "[Napari HUB cli] Metadata enhancement"

MOTIVATION = """In [CZI user experience studies](https://github.com/chanzuckerberg/napari-hub/discussions/463), we found that napari hub users place higher value on plugins with complete metadata and are more likely to use them.
The suggested modifications may help provide a better user experience with your plugin on the napari hub (e.g. make your plugin easier to find) and increase its popularity and adoption.
Furthermore, metadata in deprecated sources may no longer be displayed correctly on the napari hub in the future and are not guaranteed to be supported beyond 2023.
"""

GENERAL_INTRO = """I'm {user} from MetaCell, I would like to thank you for participating in the napari ecosystem with your work!

I am here to help you maintain and improve the metadata of your [napari hub](https://napari-hub.org) listing, so today I scanned your repository and I might have found some fields that are missing, follow an unexpected format, or could be improved.
"""

PR_BODY = f"""Hi there,

{GENERAL_INTRO}

{MOTIVATION}

To make your work easier, I created this pull request that contains some suggestions to improve the metadata of your repository. Since there might be some minor inaccuracies, could you please review and accept the PR when everything looks good to you?

If any information is inaccurate, please feel free to edit it as you already have editing rights. Then proceed to commit/push this pull request.

This is an automatic procedure that we are developing and constantly improving, so if you have any questions or comments, please feel free to reach out me or [neuromusic](https://github.com/neuromusic) and let us know what you think, we appreciate your feedback!

We all hope this pull request will be helpful to you,
Thank you for your help and feedback,

The napari hub and MetaCell teams.
"""

REDUNDANT_INTRO = """I'm {user}, and I created this issue to complement #{pr_id}.

While scanning your repository, I identified some metadata that are either missing, follow an unexpected format, or are located in secondary/deprecated sources.
"""

ISSUE_INTRO_NO_PR = """I'm {user} from MetaCell, I would like to thank you for participating in the napari ecosystem with your work!

{MOTIVATION}

I am here to help you maintain and improve the metadata of your [napari hub](https://napari-hub.org) listing, so today I scanned your repository and I may have identified some metadata that are either missing, or that follows an unexpected format, and/or misplaced in files that are considered as secondary or deprecated sources."""

METADATA_DIFFICULTIES = """Since metadata sometimes is hard to fix automatically I created a list of what improvements you might want to look into to improve the overall quality of your [napari hub](https://napari-hub.org) listing:
"""

CONCLUSION_NO_PR = """<!--
If you need, here are [more details about metadata and their locations](https://github.com/chanzuckerberg/napari-hub/wiki/Customizing-your-plugin%27s-listing).
-->
If some metadata is already present and I overlooked it, please feel free to contact me or [neuromusic](https://github.com/neuromusic) to tell us what could be improved!

We all hope this issue will be helpful to you,
Thank you for your help and feedback,

The napari hub and MetaCell teams.
"""

CONCLUSION_PR = """<!--
If you need, here are [more details about metadata and their locations](https://github.com/chanzuckerberg/napari-hub/wiki/Customizing-your-plugin%27s-listing).
-->
As I mentioned in my PR, if some metadata is already present and I overlooked it, please feel free to contact me or [neuromusic](https://github.com/neuromusic) to tell us what could be improved!


Thank you for your help and feedback,

The napari hub and MetaCell teams.
"""

ISSUE_BODY = """{greetings}

{introduction}
{difficulties}
{issues}
{docs}

{conclusion}
"""


def build_PR_message(user):
    return PR_BODY.format(user=user)


def build_issue_message(first_name, pr_id, results):
    pr_opened = pr_id is not None
    greetings = "Hi again," if pr_opened else "Hi there,"
    introduction = (
        REDUNDANT_INTRO.format(user=first_name, pr_id=pr_id)
        if pr_opened
        else ISSUE_INTRO_NO_PR.format(user=first_name, MOTIVATION=MOTIVATION)
    )
    difficulties = METADATA_DIFFICULTIES
    conclusion = CONCLUSION_PR if pr_opened else CONCLUSION_NO_PR

    assert results.repository
    repo_path = results.repository.path

    issues = []
    docs = {}
    citation_result = results[CITATION]
    for feature in results.missing_features():
        if feature.meta is CITATION_VALID and citation_result.found:
            msg = f"* Your citation file `{feature.scanned_files[0].file.relative_to(repo_path)}` has not a valid format (it cannot be properly parsed)"
            issues.append(msg)
            continue
        if feature.meta in (CITATION_VALID, CITATION):
            continue
        scanned_files = (
            f"`{x.file.relative_to(repo_path)}`"
            for x in feature.scanned_files
            if x.exists
        )
        msg = f"* {feature.meta.name!r} entry was not found or follows an unexpected format (scanned files: {', '.join(scanned_files)})"
        issues.append(msg)
        docs.setdefault(feature.meta.doc_url, []).append(feature.meta)

    issues.append("")
    for feature in results.only_in_fallbacks():
        if feature.meta.automatically_fixable:
            continue

        preferred_sources = [
            x for x in feature.scanned_files if x not in feature.fallbacks
        ]
        if not preferred_sources:
            preferred_sources = feature.main_files
        preferred_sources = [
            f"`{f.file.relative_to(repo_path)}`" for f in preferred_sources
        ]
        assert feature.found_in
        if not feature.meta.force_main_file_usage:
            if feature.main_files[0].exists:
                msg = f"* {feature.meta.name} was found in `{feature.found_in.file.relative_to(repo_path)}`. You can also place this information in your {' or '.join(preferred_sources)} if you want."
                issues.append(msg)
            continue
        msg = f"* {feature.meta.name} was found in `{feature.found_in.file.relative_to(repo_path)}`, but it is preferred to place this information in {' or '.join(preferred_sources)}"
        issues.append(msg)
        docs.setdefault(feature.meta.doc_url, []).append(feature.meta)

    if len(issues) <= 1:
        return ""

    # Build the message for documentation
    doc_msgs = []
    for url, meta in docs.items():
        tested_features = ", ".join(f"'{m.name}'" for m in meta)
        doc_msgs.append(
            f"If you need more details about: {tested_features}, you can refer to [this documentation page]({url})."
        )

    return ISSUE_BODY.format(
        greetings=greetings,
        introduction=introduction,
        difficulties=difficulties,
        issues="\n".join(issues),
        docs="\n".join(doc_msgs),
        conclusion=conclusion,
    )


def create_commits(results, display_info=False):
    assert results.repository, "There is no results for this repository"
    plugin_repo = results.repository
    git_repo = Repo(plugin_repo.path)

    commited = False
    for feature in results.only_in_fallbacks():
        if not feature.meta.automatically_fixable:
            continue  # pragma: no cover
        target = feature.main_files[0]
        source = feature.found_in
        assert target
        assert source
        feature_name = feature.meta.attribute[
            4:
        ]  # we skip the "has_", refactor in the future
        setattr(target, feature_name, getattr(source, feature_name))
        target.save()
        # if the target have not been created, we do not commit
        # this can happen if a modification is attempted
        # on a gen 1 plugin
        if not target.exists:
            continue
        git_repo.git.add(target.file)
        msg = f"""
Copy "{feature.meta.name}" from secondary to primary file

{feature.meta.name} was found in a secondary file and copied in the primary one:
* (found here)  "{source.file.relative_to(plugin_repo.path)}"
* (copied here) "{target.file.relative_to(plugin_repo.path)}"
"""
        if display_info:
            print(msg)
        git_repo.git.add(update=True)
        git_repo.git.commit(m=msg)
        commited = True
    return commited


def create_commit_citation(results, display_info=False):
    if results[CITATION].found:
        return False

    assert results.repository, "There is no results for this repository"
    plugin_repo = results.repository
    git_repo = Repo(plugin_repo.path)
    create_cff_citation(plugin_repo, display_info=display_info)
    git_repo.git.add(plugin_repo.citation_file.file)
    git_repo.git.commit(m="Add 'CITATION.cff' file")
    return True


def validate_plugin_selection(names):
    closest = {}
    urls = {}
    for name in names:
        try:
            urls[name] = get_repository_url(name)
        except NonExistingNapariPluginError as e:
            closest[name] = e.closest
    if closest:
        return False, closest
    return True, urls


def analyse_plugins_then_create_PR(plugin_names, directory=None, dry_run=False):
    valid, result = validate_plugin_selection(plugin_names)
    if not valid:
        print("Some of the input plugins are not existing on the platform:")
        for pname, closest in result.items():
            if closest is not None:
                print(f" * {pname!r} do you mean {closest!r}?")
            else:
                print(f" * {pname!r} (no close matches found)")
        return False
    for plugin_name, plugin_url in result.items():
        analyse_then_create_PR(
            plugin_name, plugin_url, directory=directory, dry_run=dry_run
        )
    return True


def analyse_then_create_PR(
    plugin_name, plugin_url, directory=None, gh_login=None, dry_run=False
):
    # analysis
    result = analyse_remote_plugin_url(
        plugin_name, plugin_url, directory=directory, cleanup=False, display_info=True
    )
    if result.status is not AnalysisStatus.SUCCESS:
        print(f"There is an issue with {plugin_name}: {result.status.value}")
        return
    if not (result.missing_features() or result.only_in_fallbacks()):
        print(f"All is good for {plugin_name}!")
        return

    create_PR_from_analysis(
        result, plugin_url, directory=directory, gh_login=gh_login, dry_run=dry_run
    )


def autofix_repository(path):
    # creates the checklist
    result = analyse_local_plugin(path)

    # perform modifications on the files
    # modify + add + commit
    # citation is created first otherwise, the other commits made by the bot will be scrapped and it will appear as author
    assert result.repository is not None
    create_commit_citation(result, display_info=True)
    create_commits(result, display_info=True)


def create_PR_from_analysis(
    result, plugin_url, directory=None, gh_login=None, dry_run=False
):
    # we can only automatically fix repositories and open issues in github
    match = re.match(
        r"https://github\.com/(?P<repo_user>[^/]+)/(?P<repo_name>[^/]+)", plugin_url
    )
    if not match:
        print(
            f"{plugin_url!r} is not hosted on github, automatic modification and issue/PR creation cannot be performed"
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

    if dry_run:
        console = Console()

        console.print(
            Markdown(
                f"# Here is a preview of what PR/issue will be created for {plugin_url}"
            )
        )
        if need_pr:
            console.print(Markdown("## PULL REQUEST"))
            pr = build_PR_message("USERNAME")
            console.print(Markdown(indent(pr, "> ", predicate=lambda _: True)))
        issue_msg = build_issue_message(
            "USERNAME", "PR_ID" if need_pr else None, result
        )
        if issue_msg:
            console.print(Markdown("## ISSUE"))
            console.print(Markdown(indent(issue_msg, "> ", predicate=lambda _: True)))
        console.print(Markdown("## Additional information"))
        console.print(
            Markdown(
                f"You can review the performed commits (if any) here: {result.repository.path}"
            )
        )
        console.print(
            Markdown(
                "After you review them, pressing 'enter' will delete the cloned repository from your file system"
            )
        )
        input("Press enter to continue...")
        console.print(f"Deleting {result.repository.path}")
        delete_file_tree(result.repository.path)
        return

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
    fork_name = "napari_cli"
    with suppress(GitCommandError):
        local_repository.create_remote(
            fork_name,
            f"https://{gh_login}:{token}@github.com/{gh_login}/{remote_name}",
        )

    # fetch/pull the new remote
    branch = local_repository.active_branch.name
    local_repository.remotes.napari_cli.pull(branch)

    # create local branch
    fork_branch = "metadata_enhancement"
    local_repository.git.checkout("-b", fork_branch)
    with suppress(GitCommandError):
        local_repository.remotes.napari_cli.pull(fork_branch)

    # push branch in the new remote
    local_repository.git.push("--set-upstream", fork_name, fork_branch)

    # prepare the PR
    me = gh.me()
    assert me
    first_name = me.name.split()[0]
    pr_id = None
    if need_pr:
        title = PR_TITLE
        body = build_PR_message(first_name)
        pull_request = orig.create_pull(
            title,
            body=body,
            head=f"{gh_login}:{fork_branch}",
            base=branch,
            maintainer_can_modify=True,
        )
        assert pull_request
        pr_id = pull_request.number

    # prepare the issue
    issue_msg = build_issue_message(first_name, pr_id, result)
    if issue_msg:
        title = ISSUE_TITLE
        body = issue_msg
        orig.create_issue(title, body)

    delete_file_tree(result.repository.path)


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
