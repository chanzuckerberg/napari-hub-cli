
from rich import print
from rich.progress import track
from rich.console import Console
from rich.table import Table

from collect_data_checks.check_meta_data_from_cfg import *
from collect_data_checks.check_meta_data_from_napari_config_yml import *
from collect_data_checks.check_meta_data_from_napari_descriptionmd import *
from collect_data_checks.check_meta_data_from_npe2config import *
from collect_data_checks.check_citation import *

repo_path = '/Users/simaosa/Desktop/MetaCell/Projects/CZI/Issue29/CZI-Issue-29'


def create_checklist(repo):

    checked_element = u'\u2713'
    non_checked_element = u'\u2717'
    checked_style = 'green'
    unchecked_style = 'red'

    cfg_scraped_text, git_link = cfg_soup(repo)
    longdescription_scraped_text = long_description_file(cfg_scraped_text,git_link )


    napari_cfg_scraped_text = napari_cfgfile_soup(repo)

    description_scraped_text = description_soup(repo)
    npe2_napari_file = npe2_file_location(repo)

    
    if (name_metadata_cfgfile(cfg_scraped_text)) or (name_metadata_npe2file(repo,npe2_napari_file)):
        display_name_check = checked_element
        display_name_column_style = checked_style
    else:
        display_name_check = non_checked_element
        display_name_column_style = unchecked_style

    
    if (summary_metadata_cfgfile(cfg_scraped_text)) or (summary_metadata_naparicfg(napari_cfg_scraped_text)):
        summary_sentence_check = checked_element
        summary_sentence_column_style = checked_style
    else:
        summary_sentence_check = non_checked_element
        summary_sentence_column_style = unchecked_style

    if (sourcecode_metadata_cfgfile(cfg_scraped_text)) or (sourcecode_metadata_naparicfg(napari_cfg_scraped_text)):
        sc_link_check = checked_element
        sc_link_column_style = checked_style
    else:
        sc_link_check = non_checked_element
        sc_link_column_style = unchecked_style

    if (author_metadata_cfgfile(cfg_scraped_text)) or (author_metadata_naparicfg(napari_cfg_scraped_text)):
        author_name_check = checked_element
        author_name_column_style = checked_style
    else:
        author_name_check = non_checked_element
        author_name_column_style = unchecked_style

    if (bug_metadata_cfgfile(cfg_scraped_text)) or (bugtracker_metadata_naparicfg(napari_cfg_scraped_text)):
        issue_submission_check = checked_element
        issue_submission_column_style = checked_style
    else:
        issue_submission_check = non_checked_element
        issue_submission_column_style = unchecked_style

    if (usersupport_metadata_cfgfile(cfg_scraped_text)) or (usersupport_metadata_naparicfg(napari_cfg_scraped_text)):
        support_channel_check = checked_element
        support_channel_column_style = checked_style
    else:
        support_channel_check = non_checked_element
        support_channel_column_style = unchecked_style

    if (video_metadata_cfgfile(longdescription_scraped_text)) or (video_metadata_descriptionfile(description_scraped_text)or screenshot_metadata_descriptionfile(description_scraped_text)) or (screenshot_metadata_cfgfile(longdescription_scraped_text)):
        intro_video_or_screenshot_check = checked_element
        intro_video_or_screenshot_column_style = checked_style
    else:
        intro_video_or_screenshot_check = non_checked_element
        intro_video_or_screenshot_column_style = unchecked_style


    if (usage_metadata_cfgfile(longdescription_scraped_text)) or (usage_metadata_descriptionfile(description_scraped_text)):
        usage_check = checked_element
        usage_column_style = checked_style
    else:
        usage_check = non_checked_element
        usage_column_style = unchecked_style

    if (intro_metadata_descriptionfile(description_scraped_text)) or (intro_metadata_cfgfile(longdescription_scraped_text)):
        intro_paragraph_check = checked_element
        intro_paragraph_column_style = checked_style
    else:
        intro_paragraph_check = non_checked_element
        intro_paragraph_column_style = unchecked_style

    if(check_for_citation(repo , 'CITATION.CFF')):
        citation_check = checked_element
        citation_column_style = checked_style
    else:
        citation_check = non_checked_element
        citation_column_style = unchecked_style

        
    console = Console()
    console.print("\n[ Napari Plugin - Documentation Checklist ]\n", style = 'blue')
    console.print('- Author name ', author_name_check, style = author_name_column_style)
    console.print('- Summary Sentence ', summary_sentence_check, style = summary_sentence_column_style)
    console.print('- Intro Paragraph ', intro_paragraph_check, style = intro_paragraph_column_style)
    console.print('- Intro Screenshot/Video ',intro_video_or_screenshot_check, style = intro_video_or_screenshot_column_style)
    console.print('- Usage Overview ', usage_check, style = usage_column_style)
    console.print('- Source Code Link ',sc_link_check, style = sc_link_column_style)
    console.print('- Support Channel Link ', support_channel_check, style = support_channel_column_style)
    console.print('- Issue Submission Link ', issue_submission_check, style = issue_submission_column_style)
    console.print('- Display Name ', display_name_check, style = display_name_column_style)
    console.print('\n[ OPTIONAL ] ')
    console.print('- Citation ', citation_check, style = citation_column_style)
    console.print('\n')

    return 

create_checklist(repo_path)
