from citation_scraper.bibtexCitation import *
from citation_scraper.apaCitation import *
from citation_scraper.bibtex_from_doi import *
from create_dict import *
from git_pr_logic.pull_request import *
import yaml
import warnings
from patterns import *
from citation_scraper.githubInfo import *
from git_pr_logic.git_interaction import *
import os
from ruamel.yaml import YAML
import ruamel.yaml


"""
    ----------
   The main code works as the following:
   - first checks for BibTex citations in the GitHub Repo's README.md page
   - then checks for APA citations in the GitHub Repo's README.md page
   - If none of the first was found, checks for a DOI in the GitHub Repo's README.md,
   and using a DOI scraper produces a BibTex citation which is converted to the CFF formatting
   - In the case that no citation was found in the README.md page, a warning
   is issued


   CITATION.CFF format:
   - The first citation that appears references the software
   - The preffered citation, which is the one used in GitHub, references an article/book, preffarably article when both exist
   - when both article and book information exist, book information is written as a sub-reference

    ----------

"""

def cff_citation(repo_path):
    #setting branch name from which the citation will be pushed
    branch_name = 'feature/create_citation_cff'

    # get the current GitHub Repository info
    git_repo_username,git_repo_name, git_author_family_name, git_author_given_name, git_repo_link,git_base_branch = getGitInfo(repo_path)
    # get the current GitHub Repository README.md link, in which the search for citation will happen
    README_LINK = git_repo_link + '/blob/%s/README.md'%(git_base_branch)
    #creating the branch where the CITATION.CFF will be pushed from
    # git_branch( repo_path, branch_name)
    #getting the GitHub authorization token as input, to be used for the PR
    # git_token = input("Enter the authentication git token: ")

    #Initializing the citation fields
    citation_title = {}
    citation_publisher = {}
    citation_url = {}
    citation_family_names = {}
    citation_given_names = {}
    citation_year = {}
    citation_journal = {}
    citation_doi = {}


    #first check if there's any BibTex citation information in the README.md
    if (bool(get_bibtex_citations(README_LINK))):
        print('BibTex Citation')
        all_bibtex_citations = get_bibtex_citations(README_LINK)

        for individual_citation in all_bibtex_citations:
            #data transformations needed to ensure the correct formatting outcome
            individual_citation = re.sub('"', '}', individual_citation)
            individual_citation = re.sub('= }', '= {', individual_citation)
            individual_citation = individual_citation + '}'
            #collecting all citation fields from the BibTex READ.ME citation
            citation_family_names = get_bibtex_family_names(individual_citation)
            citation_given_names = get_bibtex_given_names(individual_citation)
            citation_title = get_bibtex_title(individual_citation)
            citation_year = get_bibtex_year(individual_citation)
            citation_publisher = get_bibtex_publisher(individual_citation)
            citation_journal = get_bibtex_journal(individual_citation)
            citation_url = get_bibtex_url(individual_citation)
            citation_doi = get_bibtex_doi(individual_citation)

        #creating the dict that serves as a template for the CITATION.CFF
        filedict = add_to_dict(
                git_repo_name, 
                git_author_family_name, 
                git_author_given_name, 
                git_repo_link,
                citation_family_names, 
                citation_given_names, 
                citation_title, 
                citation_year, 
                citation_url, 
                citation_doi, 
                citation_publisher, 
                citation_journal )



    #then check if there's any APA citation information in the README.md
    elif bool(get_bibtex_citations(README_LINK))==False and bool(get_apa_citations(README_LINK)):
        
        APA_text, all_apa_authors, all_apa_citations = get_apa_citations(
            README_LINK)
        
        if (bool(all_apa_citations)):
            print('APA Citation')
            APA_text, all_apa_authors, all_apa_citations = get_apa_citations(
                README_LINK)

            for individual_citation in all_apa_citations:
                #data transformations needed to ensure the correct formatting outcome
                individual_citation = ''.join(map(str, individual_citation))
                individual_citation = all_apa_authors + ' ' + individual_citation
                #collecting all citation fields from the APA READ.ME citation
                citation_family_names = get_apa_family_names(all_apa_authors)
                citation_given_names = get_apa_given_names(all_apa_authors)
                citation_year = get_apa_year(individual_citation)
                citation_year = citation_year
                citation_title = get_apa_title(individual_citation)
                citation_journal = get_apa_journal(citation_title, APA_text)
                citation_doi = get_apa_doi(APA_text)

            #creating the dict that serves as a template for the CITATION.CFF
            filedict = add_to_dict(
                git_repo_name, 
                git_author_family_name, 
                git_author_given_name, 
                git_repo_link,
                citation_family_names, 
                citation_given_names, 
                citation_title, 
                citation_year, 
                citation_url, 
                citation_doi, 
                citation_publisher, 
                citation_journal )

        

        # when no citation information is found, check for an APA formatted DOI
        else:
            print('DOI Citation')
            #using a DOI scraper, get a BibTex citation from the DOI found
            all_bibtex_citations = get_citation_from_doi(README_LINK)
            for individual_citation in all_bibtex_citations:
                #data transformations needed to ensure the correct formatting outcome
                individual_citation = re.sub('"', '}', individual_citation)
                individual_citation = re.sub('= }', '= {', individual_citation)
                individual_citation = individual_citation + '}}'
                #collecting all citation fields from the BibTex READ.ME citation
                citation_family_names = get_bibtex_family_names(individual_citation)
                citation_given_names = get_bibtex_given_names(individual_citation)
                citation_title = get_bibtex_title(individual_citation)
                citation_year = get_bibtex_year(individual_citation)
                citation_publisher = get_bibtex_publisher(individual_citation)
                citation_journal = get_bibtex_journal(individual_citation)
                citation_url = get_bibtex_url(individual_citation)
                citation_doi = get_bibtex_doi(individual_citation)

            #creating the dict that serves as a template for the CITATION.CFF
            filedict = add_to_dict(
                git_repo_name, 
                git_author_family_name, 
                git_author_given_name, 
                git_repo_link,
                citation_family_names, 
                citation_given_names, 
                citation_title, 
                citation_year, 
                citation_url, 
                citation_doi, 
                citation_publisher, 
                citation_journal )



    else:
        #warning in the console, since no citation or DOI was found
        print('\n')
        warnings.warn("Warning...........Please insert citation or DOI ")

        #creating the dict that serves as a template for the CITATION.CFF
        filedict = add_to_dict(
                git_repo_name, 
                git_author_family_name, 
                git_author_given_name, 
                git_repo_link,
                citation_family_names, 
                citation_given_names, 
                citation_title, 
                citation_year, 
                citation_url, 
                citation_doi, 
                citation_publisher, 
                citation_journal )
    
    #creating pull request with the CITATION.CFF
    # git_pull_request(repo_path,branch_name, git_token )
    #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


    if(filedict):
        print('\n')
        print(filedict)
        print('\n')
        #dump the dict contents into the final YAML file CITATION.CFF
        with open(r'{}/CITATION.cff'.format(repo_path), 'w') as f:
            ruamel.yaml.dump(
                filedict, f, Dumper=ruamel.yaml.RoundTripDumper,
                default_flow_style=False)
            #adding citation templates
            f.write('\n#Please use the templates below if any of the citation information \n#was not captured or is not available in the README.md\n#Uncomment and Replace/Add the values as you see fit\n')
            f.write('\n#Full Citation Template for referencing other work:')
            f.writelines(template_ref_othwr_work)
            f.write('\n#Full Citation Template for Credit Redirection:')
            f.writelines(template_cred_redirect)

