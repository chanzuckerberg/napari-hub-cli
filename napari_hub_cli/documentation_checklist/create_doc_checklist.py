
from rich import print
from rich.progress import track
from rich.console import Console
from rich.table import Table

from check_metadata.check_meta_data_from_cfg import *
from check_metadata.check_meta_data_from_napari_config_yml import *
from check_metadata.check_meta_data_from_napari_descriptionmd import *
from check_metadata.check_meta_data_from_npe2config import *
from check_metadata.check_citation import *

repo_path = '/Users/simaosa/Desktop/MetaCell/Projects/CZI/Issue29/CZI-29-test'


def create_checklist(repo):
    print('\n')
    
    cfg_scraped_text, git_link = cfg_soup(repo)
    longdescription_scraped_text = long_description_file(cfg_scraped_text,git_link )
    napari_cfg_scraped_text = napari_cfgfile_soup(repo)
    description_scraped_text = description_soup(repo)
    npe2_napari_file = npe2_file_location(repo)

    checked_element = u'\u2713'
    non_checked_element = u'\u2717'
    checked_style = 'bold green'
    unchecked_style = 'bold red'

    #Initializations
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

    if (name_metadata_npe2file(repo,npe2_napari_file) or (name_metadata_cfgfile(cfg_scraped_text)) ):
        display_name_check = checked_element
        display_name_column_style = checked_style
    
    if (summary_metadata_cfgfile(cfg_scraped_text)) or (summary_metadata_naparicfg(napari_cfg_scraped_text)):
        summary_sentence_check = checked_element
        summary_sentence_column_style = checked_style
   
    if (sourcecode_metadata_cfgfile(cfg_scraped_text)) or (sourcecode_metadata_naparicfg(napari_cfg_scraped_text)):
        sc_link_check = checked_element
        sc_link_column_style = checked_style

    if (author_metadata_cfgfile(cfg_scraped_text)) or (author_metadata_naparicfg(napari_cfg_scraped_text)):
        author_name_check = checked_element
        author_name_column_style = checked_style
   
    if (bug_metadata_cfgfile(cfg_scraped_text)) or (bugtracker_metadata_naparicfg(napari_cfg_scraped_text)):
        issue_submission_check = checked_element
        issue_submission_column_style = checked_style  

    if (usersupport_metadata_cfgfile(cfg_scraped_text)) or (usersupport_metadata_naparicfg(napari_cfg_scraped_text)):
        support_channel_check = checked_element
        support_channel_column_style = checked_style  

    if (video_metadata_cfgfile(longdescription_scraped_text)) or (video_metadata_descriptionfile(description_scraped_text)or screenshot_metadata_descriptionfile(description_scraped_text)) or (screenshot_metadata_cfgfile(longdescription_scraped_text)):
        intro_video_or_screenshot_check = checked_element
        intro_video_or_screenshot_column_style = checked_style

    if (usage_metadata_cfgfile(longdescription_scraped_text)) or (usage_metadata_descriptionfile(description_scraped_text)):
        usage_check = checked_element
        usage_column_style = checked_style

    if (intro_metadata_descriptionfile(description_scraped_text)) or (intro_metadata_cfgfile(longdescription_scraped_text)):
        intro_paragraph_check = checked_element
        intro_paragraph_column_style = checked_style
    
    if(check_for_citation(repo , 'CITATION.CFF')):
        citation_check = checked_element
        citation_column_style = checked_style
   
    
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


    FALLBACK_TEXT = ' found only in the fallback file'
    NOT_FOUND_TEXT = ' not found'

    display_name_fallback = False
    usage_fallback = False
    summary_sentence_fallback = False
    source_code_link_fallback = False
    bug_tracker_link_fallback = False
    user_support_link_fallback = False
    screenshot_or_video_fallback = False
    intro_paragraph_fallback = False
    author_fallback = False

    if(name_metadata_cfgfile(cfg_scraped_text)) and not name_metadata_npe2file(repo,npe2_napari_file) :
        # console.print('Display name' + FALLBACK_TEXT, style = 'yellow')
        display_name_fallback = True
    if(usage_metadata_cfgfile(longdescription_scraped_text)) and not usage_metadata_descriptionfile(description_scraped_text) :
        # console.print('Usage ' + FALLBACK_TEXT, style = 'yellow')
        usage_fallback = True
    if(summary_metadata_cfgfile(cfg_scraped_text)) and not summary_metadata_naparicfg(napari_cfg_scraped_text) :
        # console.print('Summary sentence' + FALLBACK_TEXT, style = 'yellow')
        summary_sentence_fallback = True
    if (sourcecode_metadata_cfgfile(cfg_scraped_text)) and not sourcecode_metadata_naparicfg(napari_cfg_scraped_text):
        # console.print('Source Code Link ' + FALLBACK_TEXT, style = 'yellow')
        source_code_link_fallback = True
    if (bug_metadata_cfgfile(cfg_scraped_text)) and not bugtracker_metadata_naparicfg(napari_cfg_scraped_text):
        # console.print('Bug Tracker Link ' + FALLBACK_TEXT, style = 'yellow')
        bug_tracker_link_fallback = True
    if (usersupport_metadata_cfgfile(cfg_scraped_text)) and not usersupport_metadata_naparicfg(napari_cfg_scraped_text):
        # console.print('User Support link' + FALLBACK_TEXT, style = 'yellow')
        user_support_link_fallback = True
    if (video_metadata_cfgfile(longdescription_scraped_text)) and not video_metadata_descriptionfile(description_scraped_text):
        # console.print('Video ' + FALLBACK_TEXT, style = 'yellow')
        screenshot_or_video_fallback = True
    if(intro_metadata_cfgfile(longdescription_scraped_text)) and not intro_metadata_descriptionfile(description_scraped_text) :
        # console.print('Intro Paragraph' + FALLBACK_TEXT, style = 'yellow')
        intro_paragraph_fallback = True
    if (screenshot_metadata_cfgfile(longdescription_scraped_text)) and not screenshot_metadata_descriptionfile(description_scraped_text):
        # console.print('Screenshot' + FALLBACK_TEXT, style = 'yellow')
        screenshot_or_video_fallback = True
    if (author_metadata_cfgfile(cfg_scraped_text)) and not author_metadata_naparicfg(napari_cfg_scraped_text):
        # console.print('Author Name' + FALLBACK_TEXT, style = 'yellow')
        author_fallback = True

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


    for idx, i in enumerate(fallback_check_array):
        if i == True:
            console.print('\n-' + checks_array_text[idx] + FALLBACK_TEXT, style = 'yellow')
            console.print('  Recommended file location - '+ main_file_array[idx], style = 'white')
            
    for idx,i in enumerate(checks_array):
        if i == non_checked_element:
            console.print('\n'+non_checked_element + checks_array_text[idx] + NOT_FOUND_TEXT, style = 'yellow')
            console.print('  Recommended file location - '+ main_file_array[idx], style = 'white')

    



    return 

create_checklist(repo_path)

