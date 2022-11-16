# coding: utf8
import pytest
from pathlib import Path

import yaml
from napari_hub_cli.citations.citation import create_cff_citation

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
        == "Tyson, A. L., Velez-Fort, M., Rousseau, C. V., Cossell, L., Tsitoura, C., Lenzi, S. C., Obenhaus, H. A., Claudi, F., Branco, T., Margrie, T. W."
    )
    assert cit1.year == "2022"
    assert cit1.journal == "Scientific Reports"
    assert cit1.issue_number == "12"
    assert cit1.pages == "867"
    assert cit1.doi == "doi.org/10.1038/s41598-021-04676-9"

    assert (
        cit2.title
        == "Emotions in storybooks: A comparison of storybooks that represent ethnic and racial groups in the United States"
    )
    assert cit2.author == "Grady, J. S., Her, M., Moreno, G., Perez, C., & Yelinek, J."
    assert cit2.year == "2019"
    assert cit2.journal == "Psychology of Popular Media Culture"
    assert cit2.issue_number == "8(3)"
    assert cit2.pages == "207-217"
    assert cit2.doi == "https://doi.org/10.1037/ppm0000185"

    assert (
        cit12.title
        == "From simple rules of individual proximity, complex and coordinated collective movement"
    )
    assert cit12.author == "Freeberg, T. M."
    assert cit12.year == "2019"
    assert cit12.additional == "Supplemental material"
    assert cit12.journal == "Journal of Comparative Psychology"
    assert cit12.issue_number == "133(2)"
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


def test_cff_no_information(tmp_path):
    current_path = Path(__file__).parent.absolute()
    repo_path = current_path / "resources" / "CZI-29-faulty"
    repo = NapariPlugin(repo_path)

    assert repo.citation_file.exists is False

    res = create_cff_citation(repo_path)

    assert res is False
    assert repo.citation_file.exists is False


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
