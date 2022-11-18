from contextlib import suppress
import os
from pathlib import Path
from git import GitError, InvalidGitRepositoryError, Repo
import requests
from rich.console import Console

from napari_hub_cli.filesaccess import NapariPlugin
from re import sub


def fake_print(*args):
    ...


def scrap_git_infos(local_repo):
    try:
        repo = Repo(local_repo.absolute())
    except InvalidGitRepositoryError:
        return {}

    url = repo.remote().url  # pragma: no cover
    title = sub(r"\.git$", "", [s for s in url.split("/") if s][-1])
    return {
        "url": url,
        "title": title,
    }


def scrap_users(local_repo):
    try:
        repo = Repo(local_repo.absolute())
    except InvalidGitRepositoryError:
        return {}

    # We cloned with depth = 1
    # To get the full history, we try to "unshallow"
    # the current remote
    with suppress(GitError):
        repo.remote().fetch(unshallow=True)

    # we group all contributors by emails
    # this allows us to detect same user with various names
    # that commits with same email
    contributors = {}
    for commiter in repo.iter_commits():
        contributors.setdefault(commiter.author.email, set()).add(commiter.author.name)

    # Now that we have users by email,
    # we group user names that are in various emails
    # (e.g. "Jane Doe" commited under "jane.doe@email.com and "jave.doe+github@email.com")
    # We detect this is the same person
    real_names = []
    for names in contributors.values():
        found_idx = [i for i, r in enumerate(real_names) if names.intersection(r)]
        if found_idx:
            [real_names[i].update(names) for i in found_idx]
        else:
            real_names.append(names)
    real_names = [
        list(r) for r in real_names
    ]  # we pass from a list of set to a list of list

    # we sort all identified names by their number of particules
    [r.sort(key=lambda name: -(len(name) + len(name.split()))) for r in real_names]
    # we get the ones that have the more fragments
    unique_names = [r[0] for r in real_names]
    authors = []
    for name in unique_names:
        s = name.split()
        if len(s) == 2:
            authors.append(
                {
                    "given-names": s[0].strip(),
                    "family-names": s[1].strip(),
                }
            )
        else:
            authors.append(
                {
                    "given-names": f"{name}  # We cannot split your name automatically bewteen 'given-names' and 'family-names', we apologize for that. Please do it manually",
                }
            )
    return {"authors": authors}


def create_cff_citation(repo_path, save=True, display_info=True):
    if display_info:
        console = Console()
        print = console.print
    else:
        print = fake_print
    print("[bold][yellow]Auto CFF Citation Creation[/yellow][/bold]")

    repo = NapariPlugin(Path(repo_path))
    cff = repo.citation_file
    readme = repo.readme
    if cff.exists:
        print(
            f"[green]\N{HEAVY CHECK MARK} Citation file already exists in {cff.file.absolute()}[/green]"
        )
        return False

    git_infos = scrap_git_infos(repo.path)
    if not readme.has_citations:
        print(
            f"[red]\N{BALLOT X} No bibtex or APA citation reference found in {readme.file.absolute()}[/red]"
        )
        print(f"[yellow]- Using git repository metadata if possible")

        cff.add_header()
        cff.update_data(git_infos)
        cff.update_data(scrap_users(repo.path))
        if save:
            cff.save()
        return True

    if readme.has_bibtex_citations:
        print(
            f"[green]\N{HEAVY CHECK MARK}[/green] Bibtex citations found in '{readme.file.absolute()}'"
        )
    elif readme.has_apa_citations:
        print(
            f"[green]\N{HEAVY CHECK MARK}[/green] APA citations found in '{readme.file.absolute()}'"
        )

    scrapped_citations = readme.extract_citations()
    first_citation = scrapped_citations[0]  # we take the first citation

    print("[yellow]\nExtracted informations for preferred citation[/yellow]")
    for field, value in first_citation.as_dict().items():
        display_value = value
        if field == "authors":
            display_value = ""
            for author in value:
                for author_field, author_value in author.items():
                    display_value += f"\n  {author_field}: {author_value}"
                display_value += "\n"
        print(f"- {field}: {display_value}")
    cff.add_header()
    cff.update_data(git_infos)
    # We add authors of first citation as plugin author
    cff.update_data({"authors": first_citation.authors})
    cff.append_citations(scrapped_citations)
    if save:
        cff.save()
    return True
