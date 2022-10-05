from .htmlScraper import *
import re
from ..patterns import *


def get_apa_citations(link):
    """Collects all APA formatted citations existent in the README.md

    Parameters
    ----------
    link : str
        url from where you want to check for APA citations

    Returns
    -------
    APA_text : str
        collects all html text that has the APA formatting style, wether from lists or from paragraph text
    all_apa_authors : str 
        from the APA formatted HTML text, holds information about all the authors present
    all_apa_citations : str
        from the APA formatted HTML text, holds information about all the fields in a citation except for the authors

    """
    #collecting the HTML text from the link provided
    soup = get_html(link)

    #citations could be in either paragraph type text or in lists
    paragraphs = soup.find_all("p", {'dir': 'auto'})
    paragraphs = str(paragraphs)
    lists = soup.find_all("li")
    lists = str(lists)

    #identify in what HTML tag is the citation text in 
    if (bool(re.findall(SMALLER_DOI_PATTERN, paragraphs, flags=re.DOTALL))):
        p_text_w_citation = re.findall(SMALLER_DOI_PATTERN, paragraphs, flags=re.DOTALL)
    else:
        p_text_w_citation = re.findall(APA_ALTERNATIVE_TO_DOI, paragraphs, flags=re.DOTALL)
    
    if (bool(re.findall(SMALLER_DOI_PATTERN, lists, flags=re.DOTALL))):
        l_text_w_citation = re.findall(SMALLER_DOI_PATTERN, lists, flags=re.DOTALL)
    else:
        l_text_w_citation = re.findall(APA_ALTERNATIVE_TO_DOI, lists, flags=re.DOTALL) 
    
    #stripping the HTML tags from the APA formatted text
    if(bool(p_text_w_citation)):
        APA_text = strip_tags(paragraphs)
    elif(bool(l_text_w_citation)):
        APA_text = strip_tags(lists) 
    else:
        APA_text = False


    if(bool(APA_text)):
        #data transformations needed to ensure the correct formatting outcome
        APA_text = APA_text.replace("\xa0", " ") 
        APA_text = re.sub('\.\\s\w\.', '.', APA_text)
        #finding all the authors within the citation APA text
        all_apa_authors = re.findall(APA_AUTHORS_PATTERN, APA_text, flags=re.DOTALL)
        all_apa_authors = ', '.join(all_apa_authors)
        
        apa_pattern_wo_authors = APA_YEAR_NUM_PATTERN + "(.*?)" + FULL_DOI_PATERN
        #finding all other citation information within the citation APA text
        if(bool(re.findall(apa_pattern_wo_authors, APA_text, flags=re.DOTALL))):
            all_apa_citations = re.findall(
            apa_pattern_wo_authors, APA_text, flags=re.DOTALL)
        else:
            all_apa_citations = re.findall(
            APA_ALTERNATIVE_TO_DOI, APA_text, flags=re.DOTALL)
        
        return APA_text, all_apa_authors, all_apa_citations


def get_apa_family_names(all_apa_authors):
    """Collects all APA author family names existent in the README.md

    Parameters
    ----------
    all_apa_authors : str
        from the APA formatted HTML text, holds information about all the authors present

    Returns
    -------
    apa_citation_family_names : list
        from the authors present, holds only the family names for said authors
   
    """
    #finding all the authors family names within the citation APA formatted authors text
    apa_citation_family_names = re.findall(
        APA_FAMILY_NAME_PATTERN, all_apa_authors, flags=re.DOTALL)
    #data transformations needed to ensure the correct formatting outcome
    apa_citation_family_names = [w.replace(',', '') for w in apa_citation_family_names]
    
    return apa_citation_family_names


def get_apa_given_names(all_apa_authors):
    """Collects all APA author given names existent in the README.md

    Parameters
    ----------
    all_apa_authors : str
        from the APA formatted HTML text, holds information about all the authors present

    Returns
    -------
    apa_citation_given_names : list
        from the authors present, holds only the given names for said authors
   
    """
    #finding all the authors given names within the citation APA formatted authors text  
    apa_citation_given_names = re.findall(
        APA_GIVEN_NAME_PATTERN, all_apa_authors, flags=re.DOTALL)
    #data transformations needed to ensure the correct formatting outcome
    apa_citation_given_names = [w.replace(', ', '') for w in apa_citation_given_names]

    return apa_citation_given_names


def get_apa_year(individual_citation):
    """Collects the year of release of the article/book existent in the README.md

    Parameters
    ----------
    individual_citation : str
        holds an individual citation from the APA formatted HTML text

    Returns
    -------
    apa_citation_year : list
        year of release of the article/book cited in the README.md
   
    """
    #finding the year within the citation APA formatted text  
    if(bool(re.findall(APA_YEAR_PATTERN, individual_citation, flags=re.DOTALL))):
        apa_citation_year = re.findall(APA_YEAR_PATTERN, individual_citation, flags=re.DOTALL)
    else:
        apa_citation_year = re.findall(APA_SMALL_YEAR_PATTERN, individual_citation, flags=re.DOTALL)
    
    #data transformations needed to ensure the correct formatting outcome
    apa_citation_year = [w.replace('.', '') for w in apa_citation_year]
    apa_citation_year = [w.replace(' ', '') for w in apa_citation_year]
    apa_citation_year = ''.join(map(str, apa_citation_year))

    return apa_citation_year


def get_apa_title(individual_citation):
    """Collects the title of the article/book existent in the README.md

    Parameters
    ----------
    individual_citation : str
        holds an individual citation from the APA formatted HTML text

    Returns
    -------
    apa_citation_title : list
        title of the article/book cited in the README.md
   
    """
    #finding the title within the citation APA formatted text  
    if(bool(re.findall(APA_TITLE_PATTERN, individual_citation, flags=re.DOTALL))):
        apa_citation_title = re.findall(APA_TITLE_PATTERN, individual_citation, flags=re.DOTALL)
    else:
        apa_citation_title = re.findall(APA_ALTERNATIVE_TITLE_PATTERN, individual_citation, flags=re.DOTALL)
    
    apa_citation_title = ' '.join(map(str, apa_citation_title))

    return apa_citation_title


def get_apa_journal(apa_citation_title, APA_text):
    """Collects the journal name of the article existent in the README.md

    Parameters
    ----------
    apa_citation_title : str
        holds the title of the article/book cited in the README.md
    APA_text : str
        holds all html text that has the APA formatting style, wether from lists or from paragraph text

    Returns
    -------
    apa_citation_journal : list
        journal of the article cited in the README.md
   
    """
    #finding the journal within the citation APA formatted text  
    apa_citation_journal = re.findall(apa_citation_title +'.'+ '(.*?)(?:doi)', APA_text, flags=re.DOTALL)

    return apa_citation_journal


def get_apa_doi(APA_text):
    """Collects the DOI of the article/book existent in the README.md

    Parameters
    ----------
    APA_text : str
        holds all html text that has the APA formatting style, wether from lists or from paragraph text

    Returns
    -------
    apa_citation_doi : list
        DOI of the article/book cited in the README.md
   
    """
    #finding the DOI within the citation APA formatted text  
    apa_citation_doi = re.findall(DOI_IN_HTML_PATTERN, APA_text, flags=re.DOTALL)

    return apa_citation_doi




