import pytest
from pathlib import Path

from napari_hub_cli.citations.citation_scraper.bibtexCitation import *
from napari_hub_cli.citations.citation_scraper.apaCitation import *
from napari_hub_cli.citations.citation_scraper.bibtex_from_doi import *
from napari_hub_cli.citations.citation_scraper.githubInfo import *
from napari_hub_cli.citations.create_dict import *
from napari_hub_cli.filesaccess import MarkdownDescription


@pytest.fixture(scope="module")
def citations_dir():
    return Path(__file__).parent / "resources" / "citations"


def test_bibtex_extraction_empty(citations_dir):
    readme_file = citations_dir / "example_empty.md"
    readme = MarkdownDescription.from_file(readme_file)
    bibtex_db = readme.extract_bibtex_citations()

    assert bibtex_db == []


def test_apa_extraction_empty(citations_dir):
    readme_file = citations_dir / "example_empty.md"
    readme = MarkdownDescription.from_file(readme_file)
    bibtex_db = readme.extract_apa_citations()

    assert bibtex_db == []


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
        == "Tyson, A. L., Vélez-Fort, M., Rousseau, C. V., Cossell, L., Tsitoura, C., Lenzi, S. C., Obenhaus, H. A., Claudi, F., Branco, T., Margrie, T. W."
    )
    assert cit1.year == "2022"
    assert cit1.publisher == "Scientific Reports"
    assert cit1.issue_number == "12"
    assert cit1.pages == "867"
    assert cit1.doi == "doi.org/10.1038/s41598-021-04676-9"

    assert (
        cit2.title
        == "Emotions in storybooks: A comparison of storybooks that represent ethnic and racial groups in the United States"
    )
    assert cit2.author == "Grady, J. S., Her, M., Moreno, G., Perez, C., & Yelinek, J."
    assert cit2.year == "2019"
    assert cit2.publisher == "Psychology of Popular Media Culture"
    assert cit2.issue_number == "8(3)"
    assert cit2.pages == "207–217"
    assert cit2.doi == "https://doi.org/10.1037/ppm0000185"

    assert (
        cit12.title
        == "From simple rules of individual proximity, complex and coordinated collective movement"
    )
    assert cit12.author == "Freeberg, T. M."
    assert cit12.year == "2019"
    assert cit12.additional == "Supplemental material"
    assert cit12.publisher == "Journal of Comparative Psychology"
    assert cit12.issue_number == "133(2)"
    assert cit12.pages == "141–142"
    assert cit12.doi == "10.1037/com0000181"


# def test_doi_method():
#     all_bibtex_citations = get_citation_from_doi(DOI_README_LINK)
#     for individual_citation in all_bibtex_citations:
#         individual_citation = re.sub('"', "}", individual_citation)
#         individual_citation = re.sub("= }", "= {", individual_citation)
#         citation_family_names = get_bibtex_family_names(individual_citation)
#         citation_given_names = get_bibtex_given_names(individual_citation)
#         citation_title = get_bibtex_title(individual_citation)
#         citation_year = get_bibtex_year(individual_citation)
#         citation_publisher = get_bibtex_publisher(individual_citation)
#         citation_journal = get_bibtex_journal(individual_citation)
#         citation_url = get_bibtex_url(individual_citation)
#         citation_doi = get_bibtex_doi(individual_citation)

#     assert bool(get_citation_from_doi(DOI_README_LINK)) == True
#     assert bool(get_citation_from_doi(BIBTEX_README_LINK)) == False
#     assert bool(get_citation_from_doi(APA_README_LINK)) == True

#     assert citation_year == "2022"
#     assert citation_publisher == "Springer Science and Business Media {LLC"
#     assert bool(citation_journal) == False
#     assert citation_url == ["https://doi.org/10.1038%2Fs41598-021-04676-9"]
#     assert citation_doi == "10.1038/s41598-021-04676-9"
