

def add_to_dict( git_title, git_family_name, git_given_name, git_url,family_names, given_names, title, year, url, doi, publisher, journal):
    """Creates the information structure to be dumped into a YAML CITATION.CFF

    Parameters
    ----------
   
    git_title : str
        holds the name of the GitHub Repository
    git_family_name : str
        holds the family name of the GitHub Repository author
    git_given_name : str
        holds the given name of the GitHub Repository author
    git_url : str
         holds the link for the GitHub Repository
    family_names : dict[str]
        from the authors present, holds only the family names for said authors
    given_names : dict[str]
        from the authors present, holds only the given names for said authors
    title : dict[str]
        title of the article/publisher cited in the README.md
    year : dict[str]
        year of release of the article/publisher cited in the README.md
    url : dict[str]
        URL of the article/publisher cited in the README.md
    doi : dict[str]
        DOI of the article/publisher cited in the README.md
    publisher : dict[str]
        publisher of the publisher cited in the README.md
    journal : dict[str]
        journal of the article cited in the README.md

    Returns
    -------
    dict_file : dict
        holds all the entries and expected values for the CITATION.CFF
        
    """
    #base initial entries for the .cff
    dict_file = {'cff-version': '1.2.0',
                 'message': 'If you use this plugin, please cite it using these metadata',
                 }

    #adding title of the software citation
    git_title_dict_file = {'title': git_title}
    #adding field(s) to the base cff
    for key, value in git_title_dict_file.items():
        if key in dict_file:
            dict_file[key].extend(value)
        else:
            dict_file[key] = value

    #adding author of the software citation
    git_author_dict_file = {'authors': [
        {'family-names': git_family_name, 'given-names': git_given_name}], }
    #adding field(s) to the base cff
    for key, value in git_author_dict_file.items():
        if key in dict_file:
            dict_file[key].extend(value)
        else:
            dict_file[key] = value

    #adding URL of the software citation
    git_url_dict_file = {'url':git_url  }
    #adding field(s) to the base cff
    for key, value in git_url_dict_file.items():
                if key in dict_file:
                    dict_file[key].extend(value)
                else:
                    dict_file[key] = value
    #adding year of the software citation, if existent
    if (bool(year)):

        year_dict_file = {'date-released': year + '-01-01'}
        #adding field(s) to the base cff
        for key, value in year_dict_file.items():
            if key in dict_file:
                dict_file[key].extend(value)
            else:
                dict_file[key] = value
    
    #if existent, add a book reference as the preferred citation
    if bool(publisher) and bool(journal) == False:
        publisher = ''.join(map(str, publisher))

        publisher_dict_file = {'preferred-citation': 
                        {'type': 'book', 'publisher': publisher}}

        pub = publisher_dict_file['preferred-citation']
        
        #adding title of the book citation, if existent
        if bool(title):
            title = ''.join(map(str, title))
            pub['title'] = title
        #adding DOI of the book citation, if existent
        if(bool(doi)):
            doi = ''.join(map(str, doi))
            pub['doi'] = doi
        #adding URL of the book citation, if existent
        if(bool(url)):
            url = ''.join(map(str, url))
            pub['url'] = url
        #adding authors of the book citation, if existent
        if bool(family_names):
            for i in range(len(family_names)):
                author_dict_file = {'authors': [
                    {'family-names': family_names[i], 'given-names': given_names[i]}], }
                #adding field(s) to the book dict
                for key, value in author_dict_file.items():
                    if key in pub:
                        pub[key].extend(value)
                    else:
                        pub[key] = value
        #adding field(s) to the base cff    
        for key, value in publisher_dict_file.items():
                            if key in dict_file:
                                dict_file[key].extend(value)
                            else:
                                dict_file[key] = value
    #if existent, add a book reference as the preferred citation
    if bool(journal) and bool(publisher)== False:
        journal = ''.join(map(str, journal))

        journal_dict_file = {'preferred-citation': 
                        {'type': 'journal', 'journal': journal}}

        journ = journal_dict_file['preferred-citation']

        #adding title of the article citation, if existent
        if(bool(title)):
            title = ''.join(map(str, title))
            journ['title'] = title
        #adding DOI of the article citation, if existent
        if(bool(doi)):
            doi = ''.join(map(str, doi))
            journ['doi'] = doi
        #adding URL of the article citation, if existent
        if(bool(url)):
            url = ''.join(map(str, url))
            journ['url'] = url
        #adding authors of the article citation, if existent
        if bool(family_names):
            for i in range(len(family_names)):
                author_dict_file = {'authors': [
                    {'family-names': family_names[i], 'given-names': given_names[i]}], }
                #adding field(s) to the journal dict
                for key, value in author_dict_file.items():
                    if key in journ:
                        journ[key].extend(value)
                    else:
                        journ[key] = value
        #adding field(s) to the base cff    
        for key, value in journal_dict_file.items():
                            if key in dict_file:
                                dict_file[key].extend(value)
                            else:
                                dict_file[key] = value
    #if both journal and publisher ingormation exist, add an article reference as 
    #the preferred citation and a book reference as a sub-reference
    if bool(journal) and bool(publisher):
        journal = ''.join(map(str, journal))
        publisher = ''.join(map(str, publisher))
        journal_dict_file = {'preferred-citation': 
                        {'type': 'journal', 'journal': journal}}

        journ = journal_dict_file['preferred-citation']

        #adding authors of the article citation, if existent
        if(bool(title)):
            title = ''.join(map(str, title))
            journ['title'] = title
        #adding DOI of the article citation, if existent    
        if(bool(doi)):
            doi = ''.join(map(str, doi))
            journ['doi'] = doi
        #adding URL of the article citation, if existent
        if(bool(url)):
            url = ''.join(map(str, url))
            journ['url'] = url
        #adding authors of the article citation, if existent
        if bool(family_names):
            for i in range(len(family_names)):
                author_dict_file = {'authors': [
                    {'family-names': family_names[i], 'given-names': given_names[i]}], }
                #adding field(s) to the journal dict
                for key, value in author_dict_file.items():
                    if key in journ:
                        journ[key].extend(value)
                    else:
                        journ[key] = value
            
        #adding field(s) to the base cff
        for key, value in journal_dict_file.items():
                            if key in dict_file:
                                dict_file[key].extend(value)
                            else:
                                dict_file[key] = value
        

        publisher_dict_file = {'references': [
                        {'type': 'book', 'publisher': publisher}],}

        pub = publisher_dict_file['references'][0]
        #adding title of the book citation, if existent
        if(bool(title)):
            title = ''.join(map(str, title))
            pub['title'] = title
        #adding DOI of the book citation, if existent    
        if(bool(doi)):
            doi = ''.join(map(str, doi))
            pub['doi'] = doi
        #adding field(s) to the base cff
        for key, value in publisher_dict_file.items():
                            if key in dict_file:
                                dict_file[key].extend(value)
                            else:
                                dict_file[key] = value
        
    return dict_file
