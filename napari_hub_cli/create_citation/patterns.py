GIT_FAMILY_NAMES_PATTERN = '(?<=Author:\\s)(.*?)(?=\\s)'

APA_DOI_PATTERN = '(?:doi.org/)(.*?)(?=\,)'
APA_AUTHORS_PATTERN = "(?:[A-Z][A-Za-z'`-]+)" + ", " + "(?:\w\.)"
APA_YEAR_NUM_PATTERN = '\(([0-9]{4})\)'
APA_FULL_DOI_PATTERN = '(10.(\d)+/([^(\s\>\"\<)])+)'
APA_FAMILY_NAME_PATTERN = "(?:[A-Z][A-Za-z'`-]+,)"
APA_GIVEN_NAME_PATTERN = "(\,\\s[A-Z]\.)"
APA_TITLE_PATTERN = '(?:[0-9]{4}\.\\s)([A-Z].*?)(?=\.)'
APA_ALTERNATIVE_TITLE_PATTERN = '(?:\([0-9]{4}\)\.\\s)([A-Z].*?)(?=\.)'
APA_YEAR_PATTERN = '(\\s[0-9]{4})'
APA_SMALL_YEAR_PATTERN= '(\([0-9]{4}\))'
APA_ALTERNATIVE_TO_DOI = '(\([0-9]{4}\)\.\\s[A-Z])(.*?)(\.)'

SMALLER_DOI_PATTERN = '(10.(\d)+/)'
FULL_DOI_PATERN = '(10.(\d)+/([^(\s\>\"\<)])+)'
DOI_IN_HTML_PATTERN = '(10[.][0-9]{4,}[^\s"/<>]*/[^\s"<>]+)(?=\])'

BIBTEX_PATTERN = '(?<=@)(.*?)(?=\}\s*\}\s)'
BIBTEX_AUTHORS_PATTERN = '(?<=author\\s=\\s\{)(.*?)(?=\},)'
BIBTEX_INDIVIDUAL_AUTHOR_PATTERN = "(?:[A-Z][A-Za-z'`-]+,)" + "\\s[A-Z][A-Za-z'`-]+"
BIBTEX_FAMILY_NAME_PATTERN = "(?:[A-Z][A-Za-z'`-]+,)"
BIBTEX_GIVEN_NAMES_PATTERN = "(,\\s[A-Z][A-Za-z'`-]+)"
BIBTEX_YEAR_NUM_PATTERN = '(?<=year\\s=\\s\{)(.*?)(?=\},)'
BIBTEX_YEAR_PATTERN = '(?<=year\\s=\\s)(.*?)(?=,)'
BIBTEX_DATE_PATTERN = '(?<=date\\s=\\s)(.*?)(?=,)'
BIBTEX_TITLE_PATTERN = '(?<=title\\s=\\s)(.*?)(?=\})'
BIBTEX_PUBLISHER_PATTERN = '(?<=publisher\\s=\\s\{)(.*?)(?=\})'
BIBTEX_DOI_PATTERN = '(?<=doi\\s=\\s\{)(.*?)(?=\})'
BIBTEX_URL_PATTERN = '(?<=URL\\s=\\s\{)(.*?)(?=\})'
BIBTEX_url_PATTERN = '(?<=url\\s=\\s\{)(.*?)(?=\})'
BIBTEX_JOURNAL_PATTERN = '(?<=journal\\s=\\s\{)(.*?)(?=\})'
BIBTEX_PATTERN = '(?<=@)(.*?)(?=\}\s*\})'
BIBTEX_PUBLISHER_ALTERNATIVE_PATTERN = '(?<=publisher\\s=\\s\{)(.*?)(?=\{)'


template_ref_othwr_work = """
#authors:
  #- family-names: Druskat
  #  given-names: Stephan
#cff-version: 1.2.0
#message: "If you use this software, please cite it using these metadata."
#references:
  #- authors:
      #- family-names: Spaaks
      #  given-names: "Jurriaan H."
    #title: "The foundation of Research Software"
    #type: software
  #- authors:
      #- family-names: Haines
      #  given-names: Robert
    #title: "Ruby CFF Library"
    #type: software
    #version: 1.0
#title: "My Research Software"
    """

template_cred_redirect = """
#authors:
  #- family-names: Druskat
  #  given-names: Stephan
#cff-version: 1.2.0
#message: "If you use this software, please cite both the article from preferred-citation and the software itself."
#preferred-citation:
  #authors:
    #- family-names: Druskat
    #  given-names: Stephan
  #title: "Software paper about My Research Software"
  #type: article
#title: "My Research Software"
"""
