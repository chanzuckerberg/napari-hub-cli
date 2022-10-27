
from rich import print
from rich.progress import track
from rich.console import Console
from rich.table import Table
from .check_metadata.check_meta_data_from_setupcfg import *
from .check_metadata.check_meta_data_from_pysetup import *
from .check_metadata.check_meta_data_from_napari_config_yml import *
from .check_metadata.check_meta_data_from_napari_descriptionmd import *
from .check_metadata.check_meta_data_from_npe2config import *
from .check_metadata.check_citation import *



def create_checklist(repo):
    """Create the documentation checklist and the subsequent suggestions by looking at metadata in multiple files
    Parameters
    ----------
    repo : str
        local path to the plugin
    
    Returns
    -------
        Console Checklist and Suggestions

    """
    print('\n')
    
    #get the setup.cfg scraped text and github repo link
    cfg_scraped_text, git_link = cfg_soup(repo)
    #get the scraped text from the long_description (field in setup.cfg) indicated file
    longdescription_scraped_text = long_description_file(cfg_scraped_text,git_link )
    #get the setup.py scraped text and github repo link
    setupy_scraped_text, git_link = setuppy_soup(repo)
    #get the scraped text from the long_description (field in setup.py) indicated file
    longdescription_pysetup_scraped_text = long_description_pysetupfile(setupy_scraped_text, git_link)
    #get the scraped text from mapari-hub/config.yml
    napari_cfg_scraped_text = napari_cfgfile_soup(repo)
    #get the scraped text from mapari-hub/DESCRIPTION.md
    description_scraped_text = description_soup(repo)
    #get the scraped text from the npe2 file
    npe2_napari_file = npe2_file_location(repo)

    #setting styles for the checklist
    checked_element = u'\u2713'
    checked_style = 'bold green'
    non_checked_element = u'\u2717'
    unchecked_style = 'bold red'

    #Setting every check and column style to a default 'not checked' and 'not checked style'
    display_name_check = non_checked_element
    display_name_column_style = unchecked_style
    summary_sentence_check = non_checked_element
    summary_sentence_column_style = unchecked_style
    sc_link_check = non_checked_element
    sc_link_column_style = unchecked_style
    author_name_check = non_checked_element
    author_name_column_style = unchecked_style
    issue_submission_check = non_checked_element
    issue_submission_column_style = unchecked_style
    support_channel_check = non_checked_element
    support_channel_column_style = unchecked_style
    intro_video_or_screenshot_check = non_checked_element
    intro_video_or_screenshot_column_style = unchecked_style
    usage_check = non_checked_element
    usage_column_style = unchecked_style
    intro_paragraph_check = non_checked_element
    intro_paragraph_column_style = unchecked_style
    citation_check = non_checked_element
    citation_column_style = unchecked_style

    #if any display name data is found in either the fallback files or primary files, it is marked as checked for the documentation checklist
    if (name_metadata_npe2file(repo,npe2_napari_file) or (name_metadata_cfgfile(cfg_scraped_text)) or name_metadata_pysetupfile(setupy_scraped_text) ):
        display_name_check = checked_element
        display_name_column_style = checked_style
    
    #if any summary sentence data is found in either the fallback files or primary files, it is marked as checked for the documentation checklist
    if (summary_metadata_cfgfile(cfg_scraped_text)) or (summary_metadata_naparicfg(napari_cfg_scraped_text) or summary_metadata_pysetupfile(setupy_scraped_text)):
        summary_sentence_check = checked_element
        summary_sentence_column_style = checked_style
    
    #if any source code data is found in either the fallback files or primary files, it is marked as checked for the documentation checklist
    if (sourcecode_metadata_cfgfile(cfg_scraped_text)) or (sourcecode_metadata_naparicfg(napari_cfg_scraped_text) or sourcecode_metadata_pysetupfile(setupy_scraped_text)):
        sc_link_check = checked_element
        sc_link_column_style = checked_style

    #if any author data is found in either the fallback files or primary files, it is marked as checked for the documentation checklist
    if (author_metadata_cfgfile(cfg_scraped_text)) or (author_metadata_naparicfg(napari_cfg_scraped_text) or author_metadata_pysetupfile(setupy_scraped_text)):
        author_name_check = checked_element
        author_name_column_style = checked_style
   
    #if any bug tracker data is found in either the fallback files or primary files, it is marked as checked for the documentation checklist
    if (bug_metadata_cfgfile(cfg_scraped_text)) or (bugtracker_metadata_naparicfg(napari_cfg_scraped_text) or bug_metadata_pysetupfile(setupy_scraped_text)):
        issue_submission_check = checked_element
        issue_submission_column_style = checked_style  

    #if any user support data is found in either the fallback files or primary files, it is marked as checked for the documentation checklist
    if (usersupport_metadata_cfgfile(cfg_scraped_text)) or (usersupport_metadata_naparicfg(napari_cfg_scraped_text)) or usersupport_metadata_pysetupfile(setupy_scraped_text):
        support_channel_check = checked_element
        support_channel_column_style = checked_style  

    #if any video data oir screenshot data is found in either the fallback files or primary files, it is marked as checked for the documentation checklist
    if (video_metadata_cfgfile(longdescription_scraped_text)) or (video_metadata_descriptionfile(description_scraped_text)or screenshot_metadata_descriptionfile(description_scraped_text)) or (screenshot_metadata_cfgfile(longdescription_scraped_text) or screenshot_metadata_pysetupfile(longdescription_pysetup_scraped_text) or video_metadata_pysetupfile(longdescription_pysetup_scraped_text)):
        intro_video_or_screenshot_check = checked_element
        intro_video_or_screenshot_column_style = checked_style

    #if any usage data is found in either the fallback files or primary files, it is marked as checked for the documentation checklist
    if (usage_metadata_cfgfile(longdescription_scraped_text)) or (usage_metadata_descriptionfile(description_scraped_text) or usage_metadata_pysetupfile(longdescription_pysetup_scraped_text)):
        usage_check = checked_element
        usage_column_style = checked_style

    #if any intro paragraph data is found in either the fallback files or primary files, it is marked as checked for the documentation checklist
    if (intro_metadata_descriptionfile(description_scraped_text)) or (intro_metadata_cfgfile(longdescription_scraped_text) or intro_metadata_pysetupfile(longdescription_pysetup_scraped_text)):
        intro_paragraph_check = checked_element
        intro_paragraph_column_style = checked_style
    
    #if any citation data is found, it is marked as checked for the documentation checklist
    if(check_for_citation(repo , 'CITATION.CFF')):
        citation_check = checked_element
        citation_column_style = checked_style
   
    #create the Console Documentation Checklist
    console = Console()
    console.print("\n\nNapari Plugin - Documentation Checklist\n", style = 'bold underline2 blue')
    console.print(author_name_check + ' Author name ', style = author_name_column_style)
    console.print(summary_sentence_check + ' Summary Sentence ', style = summary_sentence_column_style)
    console.print(intro_paragraph_check + ' Intro Paragraph ', style = intro_paragraph_column_style)
    console.print(intro_video_or_screenshot_check + ' Intro Screenshot/Video ',style = intro_video_or_screenshot_column_style)
    console.print(usage_check + ' Usage Overview ',  style = usage_column_style)
    console.print(sc_link_check + ' Source Code Link ', style = sc_link_column_style)
    console.print(support_channel_check + ' Support Channel Link ', style = support_channel_column_style)
    console.print(issue_submission_check + ' Issue Submission Link ', style = issue_submission_column_style)
    console.print(display_name_check + ' Display Name ', style = display_name_column_style)
    console.print('\nOPTIONAL ', style = 'underline')
    console.print(citation_check + ' Citation ', style = citation_column_style)
    console.print('\n')

    #setting the suggestions main text
    FALLBACK_TEXT = ' found only in the fallback file'
    NOT_FOUND_TEXT = ' not found'

    #setting all fields as not found in the corresponding fallback files
    display_name_fallback = False
    usage_fallback = False
    summary_sentence_fallback = False
    source_code_link_fallback = False
    bug_tracker_link_fallback = False
    user_support_link_fallback = False
    screenshot_or_video_fallback = False
    intro_paragraph_fallback = False
    author_fallback = False

    #checking if display name data was only found in the fallback file
    if(name_metadata_cfgfile(cfg_scraped_text) or name_metadata_pysetupfile(setupy_scraped_text))  and not name_metadata_npe2file(repo,npe2_napari_file) :
        display_name_fallback = True
    
    #checking if usage data was only found in the fallback file
    if(usage_metadata_cfgfile(longdescription_scraped_text) or usage_metadata_pysetupfile(longdescription_pysetup_scraped_text)) and not usage_metadata_descriptionfile(description_scraped_text) :
        usage_fallback = True
    
    #checking if summary sentence data was only found in the fallback file
    if(summary_metadata_cfgfile(cfg_scraped_text) or summary_metadata_pysetupfile(setupy_scraped_text)) and not summary_metadata_naparicfg(napari_cfg_scraped_text) :
        summary_sentence_fallback = True
    
    #checking if source code link data was only found in the fallback file
    if (sourcecode_metadata_cfgfile(cfg_scraped_text) or sourcecode_metadata_pysetupfile(setupy_scraped_text)) and not sourcecode_metadata_naparicfg(napari_cfg_scraped_text):
        source_code_link_fallback = True
    
    #checking if bug tracker link data was only found in the fallback file
    if (bug_metadata_cfgfile(cfg_scraped_text) or bug_metadata_pysetupfile(setupy_scraped_text)) and not bugtracker_metadata_naparicfg(napari_cfg_scraped_text):
        bug_tracker_link_fallback = True
    
    #checking if user support link data was only found in the fallback file
    if (usersupport_metadata_cfgfile(cfg_scraped_text) or usersupport_metadata_pysetupfile(setupy_scraped_text)) and not usersupport_metadata_naparicfg(napari_cfg_scraped_text):
        user_support_link_fallback = True
    
    #checking if video data was only found in the fallback file
    if (video_metadata_cfgfile(longdescription_scraped_text) or video_metadata_pysetupfile(longdescription_pysetup_scraped_text)) and not video_metadata_descriptionfile(description_scraped_text):
        screenshot_or_video_fallback = True
    
    #checking if intro paragraph data was only found in the fallback file
    if(intro_metadata_cfgfile(longdescription_scraped_text) or intro_metadata_pysetupfile(longdescription_pysetup_scraped_text)) and not intro_metadata_descriptionfile(description_scraped_text) :
        intro_paragraph_fallback = True
    
    #checking if screenshot data was only found in the fallback file
    if (screenshot_metadata_cfgfile(longdescription_scraped_text) or  screenshot_metadata_pysetupfile(longdescription_pysetup_scraped_text)) and not screenshot_metadata_descriptionfile(description_scraped_text):
        screenshot_or_video_fallback = True
    
    #checking if author data was only found in the fallback file
    if (author_metadata_cfgfile(cfg_scraped_text) or author_metadata_pysetupfile(setupy_scraped_text)) and not author_metadata_naparicfg(napari_cfg_scraped_text):
        author_fallback = True

    #fallback file status (only fallback file or not) for all checklist fields
    fallback_check_array = [display_name_fallback,
                            summary_sentence_fallback,
                            source_code_link_fallback,
                            author_fallback,
                            screenshot_or_video_fallback,
                            intro_paragraph_fallback,
                            usage_fallback,
                            user_support_link_fallback,
                            bug_tracker_link_fallback,
                            ]
    #all the checklist fields check status (found anywhere or not found at all)
    checks_array = [display_name_check,
                   summary_sentence_check,
                   sc_link_check,
                   author_name_check,
                   intro_video_or_screenshot_check,
                   intro_paragraph_check,
                   usage_check,
                   support_channel_check,
                   issue_submission_check,
                   citation_check 
                    ]
    #all the checklist fields
    checks_array_text = [' Display name ',
                        ' Summary Sentence ',
                        ' Source Code ',
                        ' Author Name ',
                        ' Video or screenshot ',
                        ' Intro Paragraph ',
                        ' Usage ',
                        ' User Support link ',
                        ' Bug Tracker link ',
                        ' Citation ',]
    
    #suggestions for the recommended primary file location
    main_file_array = ['npe2 file: napari.yaml',
                       'napari-hub/config.yml',
                       'napari-hub/config.yml',
                       'napari-hub/config.yml',
                       'napari-hub/description.md',
                       'napari-hub/description.md',
                       'napari-hub/description.md',
                       'napari-hub/config.yml',
                       'napari-hub/config.yml',
                       'CITATION.CFF',]

    #creating the checklist file suggestions for when information is only available in the corresponding fallback files
    for idx, i in enumerate(fallback_check_array):
        if i == True:
            console.print('\n-' + checks_array_text[idx] + FALLBACK_TEXT, style = 'yellow')
            console.print('  Recommended file location - '+ main_file_array[idx], style = 'white')

    #creating the checklist file suggestions for when information is not found at all      
    for idx,i in enumerate(checks_array):
        if i == non_checked_element:
            console.print('\n'+non_checked_element + checks_array_text[idx] + NOT_FOUND_TEXT, style = 'yellow')
            console.print('  Recommended file location - '+ main_file_array[idx], style = 'white')

    return 


