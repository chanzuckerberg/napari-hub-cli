from requests.exceptions import MissingSchema
from napari_hub_cli.meta_classes import MetaItem, MetaSource
import os
from yaml import full_load
from configparser import ConfigParser
from collections import defaultdict
from .utils import (
    flatten,
    filter_classifiers,
    get_long_description,
    get_pkg_version,
    is_canonical,
    split_dangling_list,
)
from .constants import (
    # length of description to preview
    DESC_LENGTH,
    # paths to various configs from root
    DESC_PTH,
    SETUP_CFG_PTH,
    SETUP_PY_PTH,
    YML_PTH,
    # field names and sources for different metadata
    SETUP_CFG_INFO,
    SETUP_PY_INFO,
    YML_INFO,
    # all field names
    FIELDS,
    # how each field is used on the hub (filterable, sortable, searched)
    HUB_USES,
)
import parsesetup


def load_meta(pth):
    meta_dict = defaultdict(lambda: None)

    desc_pth = pth + DESC_PTH
    if os.path.exists(desc_pth):
        with open(desc_pth) as desc_file:
            full_desc = desc_file.read()
            trimmed_desc = full_desc[:DESC_LENGTH]
            if len(trimmed_desc) == DESC_LENGTH:
                trimmed_desc += "..."
            desc_source = MetaSource(DESC_PTH)
            desc_item = MetaItem("Description", trimmed_desc, desc_source)
            meta_dict[desc_item.field_name] = desc_item

    yml_pth = pth + YML_PTH
    if os.path.exists(yml_pth):
        read_yml_config(meta_dict, yml_pth)

    cfg_pth = pth + SETUP_CFG_PTH
    if os.path.exists(cfg_pth):
        read_setup_cfg(meta_dict, cfg_pth, pth)

    py_pth = pth + SETUP_PY_PTH
    if os.path.exists(py_pth):
        read_setup_py(meta_dict, py_pth, pth)

    return meta_dict


def read_yml_config(meta_dict, yml_path):
    with open(yml_path) as yml_file:
        yml_meta = full_load(yml_file)
        for field_name, (section, key) in YML_INFO:
            if section in yml_meta:
                if key and key in yml_meta[section]:
                    src = MetaSource(YML_PTH, section, key)
                    item = MetaItem(field_name, yml_meta[section][key], src)
                    meta_dict[field_name] = item
                elif not key:
                    src = MetaSource(YML_PTH, section)
                    item = MetaItem(field_name, yml_meta[section], src)
                    meta_dict[field_name] = item


def read_setup_cfg(meta_dict, setup_path, root_pth):
    c_parser = ConfigParser()
    c_parser.read(setup_path)

    for field, (section, key) in SETUP_CFG_INFO:
        if section in c_parser.sections():
            if key in c_parser[section]:
                if meta_dict[field] is None:
                    item_src = MetaSource(SETUP_CFG_PTH, section, key)
                    item = MetaItem(field, c_parser[section][key], item_src)
                    meta_dict[field] = item

    config = flatten(c_parser)
    parse_complex_meta(meta_dict, config, root_pth, SETUP_CFG_PTH)


def read_setup_py(meta_dict, setup_path, root_pth):
    setup_args = parsesetup.parse_setup(os.path.abspath(setup_path), trusted=True)
    for field, (section, key) in SETUP_PY_INFO:
        if section:
            # project urls are the only fields with a section
            if section in setup_args:
                url_dict = setup_args[section]
                if key in url_dict and meta_dict[field] is None:
                    src = MetaSource(SETUP_PY_PTH, section, key)
                    item = MetaItem(field, url_dict[key], src)
                    meta_dict[field] = item
        else:
            if key in setup_args and meta_dict[field] is None:
                src = MetaSource(SETUP_PY_PTH, section, key)
                item = MetaItem(field, setup_args[key], src)
                meta_dict[field] = item
    parse_complex_meta(meta_dict, setup_args, root_pth, SETUP_PY_PTH)


def parse_complex_meta(meta_dict, config, root_pth, cfg_pth):
    section = None
    if "cfg" in cfg_pth:
        section = "metadata"

    key = "classifiers"
    if key in config:
        all_classifiers = config[key]
        if isinstance(all_classifiers, str):
            all_classifiers = split_dangling_list(all_classifiers)
        dev_status, os_support = filter_classifiers(all_classifiers)
        if dev_status:
            dev_status_source = MetaSource(cfg_pth, section, key)
            dev_status_item = MetaItem(
                "Development Status", dev_status, dev_status_source
            )
            meta_dict[dev_status_item.field_name] = dev_status_item
        if os_support:
            os_support_source = MetaSource(cfg_pth, section, key)
            os_support_item = MetaItem(
                "Operating System", os_support, os_support_source
            )
            meta_dict[os_support_item.field_name] = os_support_item

    if "Version" not in meta_dict:
        src, pkg_version = get_pkg_version(config, root_pth)
        version_item = MetaItem("Version", pkg_version)
        meta_dict[version_item.field_name] = version_item
        version_source = None
        if src:
            version_source = MetaSource(src)
        else:
            if is_canonical(pkg_version):
                version_source = MetaSource(cfg_pth, section, "version")
        version_item.source = version_source

    if meta_dict["Description"] is None:
        long_desc = get_long_description(config, root_pth)
        if long_desc:
            desc_source = MetaSource(cfg_pth, section, "long_description")
            desc_item = MetaItem("Description", long_desc, desc_source)
            meta_dict[desc_item.field_name] = desc_item

    if "cfg" in cfg_pth:
        section = "options"
    key = "install_requires"
    if key in config and config[key]:
        reqs = config[key]
        if isinstance(reqs, str):
            reqs = split_dangling_list(reqs)
        reqs_source = MetaSource(cfg_pth, section, key)
        reqs_item = MetaItem("Requirements", reqs, reqs_source)
        meta_dict[reqs_item.field_name] = reqs_item


def get_missing(meta, pth):
    missing_meta = defaultdict(None)
    for field, source in YML_INFO:
        if field not in meta:
            section, key = source
            src_item = MetaSource(YML_PTH, section, key)
            missing_meta[field] = src_item

    if "Description" not in meta:
        src_item = MetaSource(DESC_PTH)
        missing_meta["Description"] = src_item

    cfg_pth = pth + SETUP_CFG_PTH
    py_pth = pth + SETUP_PY_PTH
    # if we already have a cfg or if we don't have setup.py
    if os.path.exists(cfg_pth) or not os.path.exists(py_pth):
        suggested_cfg = SETUP_CFG_PTH
        cfg_info = SETUP_CFG_INFO
    else:
        suggested_cfg = SETUP_PY_PTH
        cfg_info = SETUP_PY_INFO

    for field, src in cfg_info:
        if field not in meta and field not in missing_meta:
            section, key = src
            src_item = MetaSource(suggested_cfg, section, key)
            missing_meta[field] = src_item
    return missing_meta


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
