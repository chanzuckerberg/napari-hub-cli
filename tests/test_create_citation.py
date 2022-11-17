# coding: utf8
import os
from pathlib import Path

import pytest
import requests_mock
import yaml

from napari_hub_cli.citations.citation import (
    create_cff_citation,
    scrap_git_infos,
    scrap_users,
)
from napari_hub_cli.filesaccess import CitationFile, MarkdownDescription, NapariPlugin


@pytest.fixture(scope="module")
def citations_dir():
    return Path(__file__).parent / "resources" / "citations"


def test_bibtex_extraction_empty(citations_dir):
    readme_file = citations_dir / "example_empty.md"
    readme = MarkdownDescription.from_file(readme_file)
    bibtex_db = readme.extract_bibtex_citations()

    assert bibtex_db == []
    assert readme.has_citations is False
    assert readme.has_bibtex_citations is False
    assert readme.has_apa_citations is False


def test_apa_extraction_empty(citations_dir):
    readme_file = citations_dir / "example_empty.md"
    readme = MarkdownDescription.from_file(readme_file)
    bibtex_db = readme.extract_apa_citations()

    assert bibtex_db == []
    assert readme.has_citations is False
    assert readme.has_bibtex_citations is False
    assert readme.has_apa_citations is False


def test_bibtex_extraction(citations_dir):
    readme_file = citations_dir / "example.md"
    readme = MarkdownDescription.from_file(readme_file)
    bibtex_db = readme.extract_bibtex_citations()

    assert len(bibtex_db) == 3

    cit1, cit2, cit3 = bibtex_db

    assert cit1.ID == "other"
    assert cit1.title == "VMTL: a language for end-user model transformation"
    assert cit1.author == "Acreţoaie, Vlad and Störrle, Harald and Strüber, Daniel ã"
    assert cit1.publisher == "Springer"
    assert cit1.year == "2018"

    assert cit2.ID == "Conrad2022.03.17.484806"
    assert cit2.author == "Conrad, Ryan and Narayan, Kedar"
    assert cit2.year == "2022"
    assert cit2.doi == "10.1101/2022.03.17.484806"

    assert cit3.ID == "acrectoaie2018vmtl"
    assert cit3.title == "VMTL: a language for end-user model transformation"
    assert cit3.author == "Acreţoaie, Vlad and Störrle, Harald and Strüber, Daniel ã"
    assert cit3.publisher == "Springer"
    assert cit3.year == "2018"


def test_apa_extraction(citations_dir):
    readme_file = citations_dir / "example.md"
    readme = MarkdownDescription.from_file(readme_file)
    apa_db = readme.extract_apa_citations()

    assert len(apa_db) == 12

    cit1, cit2, *_, cit12 = apa_db

    assert (
        cit1.title
        == "Accurate determination of marker location within whole-brain microscopy images"
    )
    assert (
        cit1.author
        == "Tyson, A. L., Velez-Fort, M. and  Rousseau, C. V., Cossell, L., Tsitoura, C., Lenzi, S. C., Obenhaus, H. A., Claudi, F., Branco, T. and  Margrie, T. W."
    )
    assert cit1.year == "2022"
    assert cit1.journal == "Scientific Reports"
    assert cit1.volume == "12"
    assert cit1.pages == "867"
    assert cit1.doi == "10.1038/s41598-021-04676-9"

    assert (
        cit2.title
        == "Emotions in storybooks: A comparison of storybooks that represent ethnic and racial groups in the United States"
    )
    assert cit2.author == "Grady, J. S., Her, M., Moreno, G., Perez, C., & Yelinek, J."
    assert cit2.year == "2019"
    assert cit2.journal == "Psychology of Popular Media Culture"
    assert cit2.volume == "8(3)"
    assert cit2.pages == "207-217"
    assert cit2.doi == "10.1037/ppm0000185"

    assert (
        cit12.title
        == "From simple rules of individual proximity, complex and coordinated collective movement"
    )
    assert cit12.author == "Freeberg, T. M."
    assert cit12.year == "2019"
    assert cit12.additional == "Supplemental material"
    assert cit12.journal == "Journal of Comparative Psychology"
    assert cit12.volume == "133(2)"
    assert cit12.pages == "141-142"
    assert cit12.doi == "10.1037/com0000181"


def test_create_cff_bibtex(tmp_path, citations_dir):
    readme_file = citations_dir / "example.md"
    readme = MarkdownDescription.from_file(readme_file)

    cff_file = tmp_path / "CITATIONS.cff"
    cff = CitationFile(cff_file)

    bibtex_citations = readme.extract_bibtex_citations()

    cff.override_with(bibtex_citations[0])

    assert len(cff.data["authors"]) == 3
    assert cff.data["authors"][0]["given-names"] == "Vlad"
    assert cff.data["year"] == 2018

    cff.save()
    with cff.file.open(mode="r") as f:
        result = yaml.safe_load(f)

    assert len(result["authors"]) == 3
    assert result["authors"][0]["given-names"] == "Vlad"
    assert result["year"] == 2018


def test_create_cff_apa(tmp_path, citations_dir):
    readme_file = citations_dir / "example.md"
    readme = MarkdownDescription.from_file(readme_file)

    cff_file = tmp_path / "CITATIONS.cff"
    cff = CitationFile(cff_file)

    apa_citations = readme.extract_apa_citations()

    cff.override_with(apa_citations[0])

    assert len(cff.data["authors"]) == 10
    assert cff.data["authors"][0]["family-names"] == "Tyson"
    assert cff.data["year"] == 2022

    cff.save()
    with cff.file.open(mode="r") as f:
        result = yaml.safe_load(f)

    assert len(result["authors"]) == 10
    assert result["authors"][0]["family-names"] == "Tyson"
    assert result["year"] == 2022


def test_cff_already_existing(tmp_path):
    current_path = Path(__file__).parent.absolute()
    repo_path = current_path / "resources" / "CZI-29-small"
    repo = NapariPlugin(repo_path)

    assert repo.citation_file.exists is True

    res = create_cff_citation(repo_path)

    assert repo.citation_file.exists is True
    assert res is False


def test_cff_already_existing_no_display(tmp_path):
    current_path = Path(__file__).parent.absolute()
    repo_path = current_path / "resources" / "CZI-29-small"
    repo = NapariPlugin(repo_path)

    assert repo.citation_file.exists is True

    res = create_cff_citation(repo_path, display_info=False)

    assert repo.citation_file.exists is True
    assert res is False


def test_cff_no_information(tmp_path):
    current_path = Path(__file__).parent.absolute()
    repo_path = current_path / "resources" / "CZI-29-faulty"
    repo = NapariPlugin(repo_path)

    assert repo.citation_file.exists is False

    res = create_cff_citation(repo_path)

    assert res is True
    assert repo.citation_file.exists is True
    repo.citation_file.file.unlink()


def test_cff_bibtex(tmp_path):
    current_path = Path(__file__).parent.absolute()
    repo_path = current_path / "resources" / "CZI-29-test2"
    repo = NapariPlugin(repo_path)

    assert repo.citation_file.exists is False

    res = create_cff_citation(repo_path)

    assert res is True

    repo = NapariPlugin(repo_path)  # force reload
    assert repo.citation_file.exists is True
    assert repo.citation_file.data != {}

    repo.citation_file.file.unlink()


def test_cff_apa(tmp_path):
    current_path = Path(__file__).parent.absolute()
    repo_path = current_path / "resources" / "CZI-29-test"
    repo = NapariPlugin(repo_path)

    assert repo.citation_file.exists is False

    res = create_cff_citation(repo_path)

    assert res is True

    repo = NapariPlugin(repo_path)  # force reload
    assert repo.citation_file.exists is True
    assert repo.citation_file.data != {}

    repo.citation_file.file.unlink()


def test_bibtex_extraction_authors(citations_dir):
    readme_file = citations_dir / "citation1.md"
    readme = MarkdownDescription.from_file(readme_file)
    bibtex_db = readme.extract_bibtex_citations()

    assert len(bibtex_db) == 3

    cit1 = bibtex_db[0]

    assert cit1.ID == "10.1007/978-3-030-66415-2_30"
    assert (
        cit1.title
        == "Registration of Multi-modal Volumetric Images by Establishing Cell Correspondence"
    )
    assert (
        cit1.author
        == "Lalit, Manan and Handberg-Thorsager, Mette and Hsieh, Yu-Wen and Jug, Florian and Tomancak, Pavel"
    )
    assert cit1.publisher == "Springer International Publishing"
    assert cit1.year == "2020"

    authors = cit1.authors
    assert len(authors) == 5

    a1, a2, a3, a4, a5 = authors
    assert a1["family-names"] == "Lalit"
    assert a1["given-names"] == "Manan"

    assert a2["family-names"] == "Handberg-Thorsager"
    assert a2["given-names"] == "Mette"

    assert a3["family-names"] == "Hsieh"
    assert a3["given-names"] == "Yu-Wen"

    assert a4["family-names"] == "Jug"
    assert a4["given-names"] == "Florian"

    assert a5["family-names"] == "Tomancak"
    assert a5["given-names"] == "Pavel"


def test_bibtex_extraction_faulty_aythors(citations_dir):
    readme_file = citations_dir / "citation1.md"
    readme = MarkdownDescription.from_file(readme_file)
    bibtex_db = readme.extract_bibtex_citations()

    assert len(bibtex_db) == 3

    _, cit2, _ = bibtex_db

    assert cit2.ID == "aicsimageio"
    assert (
        cit2.title
        == "AICSImageIO: Image Reading, Metadata Conversion, and Image Writing for Microscopy Images in Pure Python"
    )
    assert (
        cit2.author
        == "Brown, Eva Maxfield and Toloudis, Dan and Sherman, Jamie and Swain-Bowden, Madison and Lambert, Talley and AICSImageIO Contributors"
    )
    assert cit2.publisher == "GitHub"
    assert cit2.year == "2021"

    authors = cit2.authors
    assert len(authors) == 6

    a1, a2, a3, a4, a5, a6 = authors
    assert a1["family-names"] == "Brown"
    assert a1["given-names"] == "Eva Maxfield"

    assert a2["family-names"] == "Toloudis"
    assert a2["given-names"] == "Dan"

    assert a3["family-names"] == "Sherman"
    assert a3["given-names"] == "Jamie"

    assert a4["family-names"] == "Swain-Bowden"
    assert a4["given-names"] == "Madison"

    assert a5["family-names"] == "Lambert"
    assert a5["given-names"] == "Talley"

    assert a6["given-names"] == "AICSImageIO Contributors"


def test_create_cff_bibtex_append_all(tmp_path, citations_dir):
    readme_file = citations_dir / "example.md"
    readme = MarkdownDescription.from_file(readme_file)

    cff_file = tmp_path / "CITATIONS.cff"
    cff = CitationFile(cff_file)

    old = dict(cff.data)
    cff.append_citations([])
    assert old == cff.data

    bibtex_citations = readme.extract_bibtex_citations()

    cff.append_citations(bibtex_citations)

    pref = cff.data["preferred-citation"]
    assert len(pref["authors"]) == 3
    assert pref["authors"][0]["given-names"] == "Vlad"
    assert pref["year"] == 2018

    refs = cff.data["references"]
    assert len(refs) == 2

    r1, r2 = cff.data["references"]
    assert len(r1["authors"]) == 2
    assert len(r2["authors"]) == 3

    # tests round-trip
    cff.save()
    with cff.file.open(mode="r") as f:
        result = yaml.safe_load(f)

    pref = result["preferred-citation"]
    assert len(pref["authors"]) == 3
    assert pref["authors"][0]["given-names"] == "Vlad"
    assert pref["year"] == 2018

    refs = result["references"]
    assert len(refs) == 2

    r1, r2 = cff.data["references"]
    assert len(r1["authors"]) == 2
    assert len(r2["authors"]) == 3


def test_github_scrapping(requests_mock):
    os.environ["GITHUB_TOKEN"] = "MYTOK"
    requests_mock.get(
        "https://api.github.com/repos/test/repo/contributors",
        json=[
            {"login": "u1", "type": "User"},
            {"login": "u2", "type": "User"},
            {"login": "u3", "type": "User"},
            {"login": "u4", "type": "bot"},
        ],
    )
    requests_mock.get("https://api.github.com/users/u1", json={"name": "Jane Doe"})
    requests_mock.get("https://api.github.com/users/u2", json={"name": "John Doe"})
    requests_mock.get("https://api.github.com/users/u3", json={"name": "Jack Von B"})

    infos = scrap_git_infos(None, url="https://github.com/test/repo")
    authors = scrap_users(infos["url"])

    assert len(infos) == 2
    assert infos["url"] == "https://github.com/test/repo"
    assert infos["title"] == "repo"

    assert len(authors["authors"]) == 3

    a1, a2, a3 = authors["authors"]
    assert a1["given-names"] == "Jane"
    assert a2["given-names"] == "John"
    assert a3["given-names"].startswith("Jack Von B  #")

    assert a1["family-names"] == "Doe"
    assert a2["family-names"] == "Doe"
    assert "family-names" not in a3


@pytest.mark.online
def test_github_scrapping__online():
    infos = scrap_git_infos(None, url="https://github.com/aranega/iguala")
    authors = scrap_users(infos["url"])

    assert len(infos) == 2
    assert infos["url"] == "https://github.com/aranega/iguala"
    assert infos["title"] == "iguala"

    assert len(authors["authors"]) == 1

    (a1,) = authors["authors"]
    assert a1["given-names"] == "Vincent"
    assert a1["family-names"] == "Aranega"
