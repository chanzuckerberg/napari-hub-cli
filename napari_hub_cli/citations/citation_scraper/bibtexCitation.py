import re
from .htmlScraper import *
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from ..patterns import *


def get_bibtex_citation_from_url(url):
    ...


def get_bibtex_family_names(individual_citation):
    """Collects all BibTex author family names existent in the citation captured from the README.md

    Parameters
    ----------
    individual_citation : str
        holds an individual citation from the BibTex formated HTML text

    Returns
    -------
    family_names : list
        from the authors present, holds only the family names for said authors

    """

    # finding all the authors within the citation BibTex formatted text
    author = re.findall(BIBTEX_AUTHORS_PATTERN, individual_citation, flags=re.DOTALL)
    if author:
        author_string = " ".join(map(str, author))
        # getting the individual authors within the full list of authors
        individual_author = re.findall(
            BIBTEX_INDIVIDUAL_AUTHOR_PATTERN, author_string, flags=re.DOTALL
        )
        individual_author_string = " ".join(map(str, individual_author))
        if bool(individual_author) == False:
            # data transformations needed to ensure the correct formatting outcome
            author_string = re.sub(" ", ", ", author_string)
            author_string = re.sub(", and,", " and", author_string)
            # getting the individual authors within the full list of authors
            individual_author = re.findall(
                BIBTEX_INDIVIDUAL_AUTHOR_PATTERN, author_string, flags=re.DOTALL
            )
            individual_author_string = " ".join(map(str, individual_author))
        # getting the family names within the full list of individual authors
        family_names = re.findall(
            BIBTEX_FAMILY_NAME_PATTERN, individual_author_string, flags=re.DOTALL
        )
        # data transformations needed to ensure the correct formatting outcome
        family_names = [w.replace(",", "") for w in family_names]

        return family_names


def get_bibtex_given_names(individual_citation):
    """Collects all BibTex author given names existent in the citation captured from the README.md

    Parameters
    ----------
    individual_citation : str
        holds an individual citation from the BibTex formated HTML text

    Returns
    -------
    given_names : list
        from the authors present, holds only the given names for said authors

    """
    # finding all the authors within the citation BibTex formatted text
    author = re.findall(BIBTEX_AUTHORS_PATTERN, individual_citation, flags=re.DOTALL)
    if author:
        author_string = " ".join(map(str, author))
        # getting the individual authors within the full list of authors
        individual_author = re.findall(
            BIBTEX_INDIVIDUAL_AUTHOR_PATTERN, author_string, flags=re.DOTALL
        )
        individual_author_string = " ".join(map(str, individual_author))
        if bool(individual_author) == False:
            # data transformations needed to ensure the correct formatting outcome
            author_string = re.sub(" ", ", ", author_string)
            author_string = re.sub(", and,", " and", author_string)
            # getting the individual authors within the full list of authors
            individual_author = re.findall(
                BIBTEX_INDIVIDUAL_AUTHOR_PATTERN, author_string, flags=re.DOTALL
            )
            individual_author_string = " ".join(map(str, individual_author))
        # getting the given names within the full list of individual authors
        given_names = re.findall(
            BIBTEX_GIVEN_NAMES_PATTERN, individual_author_string, flags=re.DOTALL
        )
        # data transformations needed to ensure the correct formatting outcome
        given_names = [w.replace(", ", "") for w in given_names]

        return given_names


def get_bibtex_year(individual_citation):
    """Collects the year of release of the article/book existent in the README.md

    Parameters
    ----------
    individual_citation : str
        holds an individual citation from the BibTex formatted HTML text

    Returns
    -------
    year : list
        year of release of the article/book cited in the README.md

    """
    # getting the year of release from an individual citation using different patterns
    if bool(re.findall(BIBTEX_YEAR_NUM_PATTERN, individual_citation, flags=re.DOTALL)):
        year = re.findall(BIBTEX_YEAR_NUM_PATTERN, individual_citation, flags=re.DOTALL)
        year = "".join(map(str, year))
    elif (
        bool(re.findall(BIBTEX_YEAR_NUM_PATTERN, individual_citation, flags=re.DOTALL))
        == False
        and bool(re.findall(BIBTEX_YEAR_PATTERN, individual_citation, flags=re.DOTALL))
        == True
    ):
        year = re.findall(BIBTEX_YEAR_PATTERN, individual_citation, flags=re.DOTALL)
        year = "".join(map(str, year))
    elif (
        bool(re.findall(BIBTEX_YEAR_PATTERN, individual_citation, flags=re.DOTALL))
        == False
    ):
        year = re.findall(BIBTEX_DATE_PATTERN, individual_citation, flags=re.DOTALL)
        year = "".join(map(str, year))
        # getting only the year from {date}
        year = year[1:5:1]

    return year


def get_bibtex_title(individual_citation):
    """Collects the title of the article/book existent in the README.md

    Parameters
    ----------
    individual_citation : str
        holds an individual citation from the BibTex formatted HTML text

    Returns
    -------
    title : list
        title of the article/book cited in the README.md

    """
    # getting the title from an individual citation
    title = re.findall(BIBTEX_TITLE_PATTERN, individual_citation, flags=re.DOTALL)
    title = "".join(map(str, title))
    return title


def get_bibtex_publisher(individual_citation):
    """Collects the publisher name of the book existent in the README.md

    Parameters
    ----------
    individual_citation : str
        holds an individual citation from the BibTex formatted HTML text

    Returns
    -------
    publisher : list
        publisher of the book cited in the README.md

    """
    # getting the publisher from an individual citation using different patterns
    publisher = re.findall(
        BIBTEX_PUBLISHER_PATTERN, individual_citation, flags=re.DOTALL
    )
    if bool(publisher) == False:
        publisher = re.findall(
            BIBTEX_PUBLISHER_ALTERNATIVE_PATTERN, individual_citation, flags=re.DOTALL
        )

    publisher = "".join(map(str, publisher))
    return publisher


def get_bibtex_doi(individual_citation):
    """Collects the DOI of the article/book existent in the README.md

    Parameters
    ----------
    individual_citation : str
        holds an individual citation from the BibTex formatted HTML text

    Returns
    -------
    doi : list
        DOI of the article/book cited in the README.md

    """
    # getting the DOI from an individual citation
    doi = re.findall(BIBTEX_DOI_PATTERN, individual_citation, flags=re.DOTALL)
    doi = "".join(map(str, doi))
    return doi


def get_bibtex_url(individual_citation):
    """Collects the URL of the article/book existent in the README.md

    Parameters
    ----------
    individual_citation : str
        holds an individual citation from the BibTex formatted HTML text

    Returns
    -------
    url : list
        URL of the article/book cited in the README.md

    """
    # getting the URL from an individual citation using different patterns
    url = re.findall(BIBTEX_URL_PATTERN, individual_citation, flags=re.DOTALL)

    if bool(url) == False:
        url = re.findall(BIBTEX_url_PATTERN, individual_citation, flags=re.DOTALL)

    return url


def get_bibtex_journal(individual_citation):
    """Collects the journal name of the article existent in the README.md

    Parameters
    ----------
    individual_citation : str
        holds an individual citation from the BibTex formatted HTML text

    Returns
    -------
    journal : list
        journal of the article cited in the README.md

    """
    # getting the journal from an individual citation
    journal = re.findall(BIBTEX_JOURNAL_PATTERN, individual_citation, flags=re.DOTALL)
    return journal
