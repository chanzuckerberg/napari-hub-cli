import os
from pathlib import Path
from git import InvalidGitRepositoryError, Repo
import requests
from rich.console import Console

from napari_hub_cli.filesaccess import NapariPlugin


def fake_print(*args):
    ...


def scrap_git_infos(local_repo, url=None):
    if not url:
        try:
            repo = Repo(local_repo.absolute())
        except InvalidGitRepositoryError:
            return {}

        url = repo.remote().url  # pragma: no cover

    return {"url": url, "title": [s for s in url.split("/") if s][-1]}


def scrap_users(url):
    if not url:
        return {}
    github_token = os.environ.get("GITHUB_TOKEN")
    auth_header = None
    if github_token:
        auth_header = {"Authorization": f"token {github_token}"}
    github_url = url.replace("https://github.com/", "https://api.github.com/repos/")

    contributors_json = requests.get(
        f"{github_url}/contributors", headers=auth_header
    ).json()
    contributors = []
    for contributor in contributors_json:
        if contributor["type"] == "User":
            user = requests.get(
                f"https://api.github.com/users/{contributor['login']}",
                headers=auth_header,
            ).json()
            contributors.append(user["name"])

    authors = []
    for name in contributors:
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
        cff.update_data(scrap_users(git_infos.get("url", None)))
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
