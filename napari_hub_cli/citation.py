from contextlib import suppress
from pathlib import Path

from git import InvalidGitRepositoryError
from git.repo import Repo
from rich.console import Console

from .fs import NapariPlugin
from .utils import scrap_git_infos


def fake_print(*args):
    ...


def scrap_users(local_repo):
    try:
        repo = Repo(local_repo.absolute())
    except InvalidGitRepositoryError:
        return {}

    # We cloned with depth = 1
    # To get the full history, we try to "unshallow"
    # the current remote
    with suppress(Exception):
        repo.remote().fetch(unshallow=True)

    # we group all contributors by emails
    # this allows us to detect same user with various names
    # that commits with same email
    contributors = {}
    for commiter in repo.iter_commits():
        email = commiter.author.email
        email = email if email else ""
        name = commiter.author.name
        name = name if name else ""
        # try to detect bots (simple detection)
        # simple hack here to order by nbre of commits
        if not ("[bot]" in email or "[bot]" in name or email.startswith("bot@")):
            contributor = contributors.setdefault(email, [1, set()])
            contributor[0] += 1
            contributor[1].add(name)

    # Now that we have users by email,
    # we group user names that are in various emails
    # (e.g. "Jane Doe" commited under "jane.doe@email.com and "jave.doe+github@email.com")
    # We detect this is the same person
    real_names = []
    for commit, names in contributors.values():
        found_idx = [i for i, (_, r) in enumerate(real_names) if names.intersection(r)]
        for i in found_idx:
            real_names[i][0] += commit
            real_names[i][1].update(names)
        if not found_idx:
            real_names.append([commit, names])
    real_names = [
        (commit, list(names)) for commit, names in real_names
    ]  # we pass from a list of set to a list of list

    # we sort all identified names by their number of particules
    [
        (c, r.sort(key=lambda name: -(len(name) + len(name.split()))))
        for c, r in real_names
    ]
    # we get the ones that have the more fragments
    unique_names = [(c, r[0]) for c, r in real_names]
    unique_names.sort(key=lambda e: -e[0])
    authors = []
    for commit, name in unique_names:
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
                    "given-names": f"{name}  # We cannot split your name automatically between 'given-names' and 'family-names', we apologize for that. Please do it manually",
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

    repo = (
        repo_path
        if isinstance(repo_path, NapariPlugin)
        else NapariPlugin(Path(repo_path))
    )
    cff = repo.citation_file
    readme = repo.readme
    if cff.exists:
        print(
            f"[green]\N{HEAVY CHECK MARK} Citation file already exists in {cff.file.absolute()}[/green]"
        )
        return False

    git_infos = scrap_git_infos(repo.path)
    subtitle = f": {repo.summary}" if repo.summary else ""
    title = git_infos.get("title")
    git_infos["title"] = f"{title}{subtitle}" if title else f"{repo.readme.title}"
    if not readme.has_citations:
        print(
            f"[red]\N{BALLOT X} No bibtex/APA citation or DOI reference found in {readme.file.absolute()}[/red]"
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
