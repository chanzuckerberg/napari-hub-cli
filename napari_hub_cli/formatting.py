"""This file contains utility functions for formatting and printing metadata"""

from .constants import (
    # all field names
    FIELDS,
    # how each field is used on the hub (filterable, sortable, searched)
    HUB_USES,
)


def format_missing(missing_meta):
    """Format all missing metadata for printing

    Parameters
    ----------
    missing_meta : Dict[str, str]
        Dictionary of field name to suggested source (file, section, key) for all missing metadata

    Returns
    -------
    str
        formatted missing metadata string
    """
    rep_str = ""
    for field, suggested_source in missing_meta.items():
        rep_str += format_missing_field(field, suggested_source)
    return rep_str


def format_missing_field(field, suggested_source):
    """Format a missing metadata field with its name, suggested placement and hub use.

    Parameters
    ----------
    field : str
        name of the metadata field
    suggested_source : MetaSource
        suggested file, section and key to add the field

    Returns
    -------
    str
        formatted metadata information
    """
    rep_str = f"{'-'*80}\nMISSING: {field}\n{'-'*80}\n"
    rep_str += "\tSUGGESTED SOURCE: "
    rep_str += format_source(suggested_source)
    filterable, sortable, searched = HUB_USES[field]
    if filterable or sortable or searched:
        rep_str += f"\t{'-'*6}\n\tUsed For\n\t{'-'*6}\n"
    if filterable:
        rep_str += f"\tFiltering\n"
    if sortable:
        rep_str += f"\tSorting\n"
    if searched:
        rep_str += f"\tSearching\n"
    rep_str += "\n"
    return rep_str


def format_source(src):
    """Format source string using file and section, key if available

    Parameters
    ----------
    src : MetaSource
        source of metadata with file, section and key attributes

    Returns
    -------
    str
        formatted source string
    """
    rep_str = ""
    if src.src_file:
        rep_str += f"\t{src.src_file}"
    if src.section and src.key:
        rep_str += f": {src.section}, {src.key}"
    else:
        if src.section:
            rep_str += f": {src.section}"
        if src.key:
            rep_str += f": {src.key}"
    rep_str += "\n"
    return rep_str


def format_field(field, meta, missing_meta):
    """Format a field (included or missing) and its source

    Parameters
    ----------
    field : str
        name of the field to format
    meta : Dict[str, MetaItem]
        metadata present for this plugin
    missing_meta : Dict[str, MetaItem]
        missing metadata for this plugin

    Returns
    -------
    str
        formatted metadata for this field
    """
    rep_str = f"{'-'*80}\n{field}\n{'-'*80}\n"
    if field in meta:
        meta_item = meta[field]
        val = meta_item.value
        src = meta_item.source
        if isinstance(val, list):
            for i in range(len(val)):
                rep_str += f"{val[i]}\n"
        else:
            rep_str += f"{val}\n"
        if src:
            rep_str += f"\t{'-'*6}\n\tSource\n\t{'-'*6}\n"
            rep_str += format_source(src)
    else:
        rep_str += f"~~Not Found~~\n"
        if field in missing_meta:
            rep_str += f"\t{'-'*6}\n\tSuggested Source\n\t{'-'*6}\n"
            rep_str += format_source(missing_meta[field])

    rep_str += "\n"
    return rep_str


def format_meta(meta, missing_meta):
    """Format all metadata and missing metadata for this plugin

    Parameters
    ----------
    meta : Dict[str, MetaItem]
        present metadata for this plugin
    missing_meta : Dict[str, MetaItem]
        missing metadata for this plugin

    Returns
    -------
    str
        formatted metadata string
    """
    rep_str = ""
    for field in sorted(FIELDS):
        rep_str += format_field(field, meta, missing_meta)
    return rep_str


def print_missing_interactive(missing_meta):
    """Print formatted metadata, but wait for input after each field

    Parameters
    ----------
    missing_meta : Dict[str, MetaItem]
        missing metadata for this plugin
    """
    for field, suggested_source in missing_meta.items():
        rep_str = format_missing_field(field, suggested_source)
        print(rep_str)
        quit = input("Enter to continue (any to quit)>>>")
        if quit:
            break


def print_meta_interactive(meta, missing_meta):
    """Print formatted present and missing metadata, but wait for input after each field

    Parameters
    ----------
    meta : Dict[str, MetaItem]
        present metadata for this plugin
    missing_meta : Dict[str, MetaItem]
        missing metadata for this plugin
    """
    for field in sorted(FIELDS):
        rep_str = format_field(field, meta, missing_meta)
        print(rep_str)
        quit = input("Enter to continue (any to quit)>>>")
        if quit:
            break
