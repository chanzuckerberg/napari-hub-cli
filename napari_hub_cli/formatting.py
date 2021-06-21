from .constants import (
    # all field names
    FIELDS,
    # how each field is used on the hub (filterable, sortable, searched)
    HUB_USES,
)

def format_missing(missing_meta):
    rep_str = ""
    for field, suggested_source in missing_meta.items():
        rep_str += format_missing_field(field, suggested_source)
    return rep_str


def format_missing_field(field, suggested_source):
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

def print_missing_interactive(missing_meta):
    for field, suggested_source in missing_meta.items():
        rep_str = format_missing_field(field, suggested_source)
        print(rep_str)
        input("Enter to continue >>>")    

def format_meta(meta, missing_meta):
    rep_str = ""
    for field in sorted(FIELDS):
        rep_str += format_field(field, meta, missing_meta)
    return rep_str


def print_meta_interactive(meta, missing_meta):
    for field in sorted(FIELDS):
        rep_str = format_field(field, meta, missing_meta)
        print(rep_str)
        input("Enter to continue >>>")

def format_source(src):
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