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
)
import parsesetup


def load_meta(pth):
    meta_dict = defaultdict(lambda: None)
    # dict of field: (file, detail)
    source_dict = defaultdict(lambda: None)

    desc_pth = pth + DESC_PTH
    if os.path.exists(desc_pth):
        with open(desc_pth) as desc_file:
            full_desc = desc_file.read()
            trimmed_desc = full_desc[:DESC_LENGTH] + "..."
            meta_dict["Description"] = trimmed_desc
            source_dict["Description"] = (DESC_PTH, None)

    yml_pth = pth + YML_PTH
    if os.path.exists(yml_pth):
        read_yml_config(meta_dict, source_dict, yml_pth)

    cfg_pth = pth + SETUP_CFG_PTH
    if os.path.exists(cfg_pth):
        read_setup_cfg(meta_dict, source_dict, cfg_pth, pth)

    py_pth = pth + SETUP_PY_PTH
    if os.path.exists(py_pth):
        read_setup_py(meta_dict, source_dict, py_pth, pth)

    return meta_dict, source_dict


def read_yml_config(meta_dict, source_dict, yml_path):
    with open(yml_path) as yml_file:
        yml_meta = full_load(yml_file)
        for field_name, (section, key) in YML_INFO:
            if section in yml_meta:
                if key and key in yml_meta[section]:
                    meta_dict[field_name] = yml_meta[section][key]
                    source_dict[field_name] = (YML_PTH, f"{section}, {key}")
                elif not key:
                    meta_dict[field_name] = yml_meta[section]
                    source_dict[field_name] = (YML_PTH, section)

def read_setup_cfg(meta_dict, source_dict, setup_path, root_pth):
    c_parser = ConfigParser()
    c_parser.read(setup_path)

    for field, (section, key) in SETUP_CFG_INFO:
        if section in c_parser.sections():
            if key in c_parser[section]:
                if meta_dict[field] is None:
                    meta_dict[field] = c_parser[section][key]
                    source_dict[field] = (SETUP_CFG_PTH, f"{section}, {key}")

    config = flatten(c_parser)
    parse_complex_meta(meta_dict, source_dict, config, root_pth, SETUP_CFG_PTH)


def read_setup_py(meta_dict, source_dict, setup_path, root_pth):
    setup_args = parsesetup.parse_setup(os.path.abspath(setup_path), trusted=True)
    for field, (section, key) in SETUP_PY_INFO:
        if section:
            # project urls
            if section in setup_args:
                url_dict = setup_args[section]
                if key in url_dict and meta_dict[field] is None:
                    meta_dict[field] = url_dict[key]
                    source_dict[field] = (SETUP_PY_PTH, f"{section}, {key}")
        else:
            if key in setup_args and meta_dict[field] is None:
                meta_dict[field] = setup_args[key]
                source_dict[field] = (SETUP_PY_PTH, key)
    parse_complex_meta(meta_dict, source_dict, setup_args, root_pth, SETUP_PY_PTH)


def parse_complex_meta(meta_dict, source_dict, config, root_pth, cfg_pth):
    section = ""
    if 'cfg' in cfg_pth:
        section = "metadata, "

    if "classifiers" in config:
        all_classifiers = config["classifiers"]
        dev_status, os_support = filter_classifiers(all_classifiers)
        if dev_status:
            meta_dict["Development Status"] = dev_status
            source_dict["Development Status"] = (cfg_pth, f"{section}classifiers")
        if os_support:
            meta_dict["Operating System"] = os_support
            source_dict["Operating System"] = (cfg_pth, f"{section}classifiers")

    src, pkg_version = get_pkg_version(config, root_pth)
    meta_dict["Version"] = pkg_version
    if src:
        source_dict["Version"] = (src, None)
    else:
        if is_canonical(pkg_version):
            source_dict["Version"] = (cfg_pth, f"{section}version")

    if meta_dict["Description"] is None:
        long_desc = get_long_description(config, root_pth)
        meta_dict["Description"] = long_desc
        source_dict["Description"] = (cfg_pth, f"{section}long_description")

    if 'cfg' in cfg_pth:
        section = "options, "

    if "install_requires" in config and config["install_requires"]:
        meta_dict["Requirements"] = config["install_requires"]
        source_dict["Requirements"] = (cfg_pth, f"{section}install_requires")

def format_meta(meta, src):
    rep_str = ""
    for field in sorted(FIELDS):
        rep_str += f"{'-'*80}\n{field}\n{'-'*80}\n"
        if field in meta:
            # rep_str += f"{meta[field]}\n{'-'*len(field)}\n"
            rep_str += f"{meta[field]}\n"
            if src[field]:
                rep_str += f"\t{'-'*6}\n\tSource\n\t{'-'*6}\n"
                pth, detail = src[field]
                if pth:
                    rep_str += f"\t{pth}"
                if detail:
                    rep_str += f": {detail}"
                rep_str += "\n"
        else:
            rep_str += f"\t~~Not Found~~\n"
        # rep_str += f"{'#'*(len(field)+10)}\n\n"
        rep_str += "\n\n"
    return rep_str