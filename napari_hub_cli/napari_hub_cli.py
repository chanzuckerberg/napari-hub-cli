import os
import re
import glob
import codecs
from yaml import full_load
from configparser import ConfigParser
from collections import defaultdict
from .utils import (
    SETUP_PY_INFO,
    YML_PTH,
    SETUP_CFG_PTH,
    SETUP_PY_PTH,
    YML_INFO,
    SETUP_CFG_INFO,
    SETUP_COMPLEX_META,
    DESC_LENGTH,
    is_canonical,
)
import parsesetup


def load_meta(pth):
    meta_dict = defaultdict(lambda: None)

    desc_pth = pth + "/.napari/DESCRIPTION.md"
    if os.path.exists(desc_pth):
        with open(desc_pth) as desc_file:
            full_desc = desc_file.read()
            trimmed_desc = full_desc[:DESC_LENGTH] + "..."
            meta_dict["Description"] = trimmed_desc

    yml_pth = pth + YML_PTH
    if os.path.exists(yml_pth):
        read_yml_config(meta_dict, yml_pth)

    cfg_pth = pth + SETUP_CFG_PTH
    if os.path.exists(cfg_pth):
        read_setup_cfg(meta_dict, cfg_pth, pth)

    py_pth = pth + SETUP_PY_PTH
    if os.path.exists(py_pth):
        read_setup_py(meta_dict, py_pth, pth)

    for k, v in meta_dict.items():
        print(f"{k:<18}:\t{v}")


def read_yml_config(meta_dict, yml_path):
    with open(yml_path) as yml_file:
        yml_meta = full_load(yml_file)
        for field_name, (section, key) in YML_INFO:
            if section in yml_meta:
                if key and key in yml_meta[section]:
                    meta_dict[field_name] = yml_meta[section][key]
                elif not key:
                    meta_dict[field_name] = yml_meta[section]


def flatten(config_parser):
    config = {}
    for section in config_parser.sections():
        config.update(config_parser[section].items())
    return config

def read_setup_cfg(meta_dict, setup_path, root_pth):
    c_parser = ConfigParser()
    c_parser.read(setup_path)

    for field, (section, key) in SETUP_CFG_INFO:
        if section in c_parser.sections():
            if key in c_parser[section]:
                if meta_dict[field] is None:
                    meta_dict[field] = c_parser[section][key]
    
    config = flatten(c_parser)
    parse_complex_meta(meta_dict, config, root_pth)


def read_setup_py(meta_dict, setup_path, root_pth):
    setup_args = parsesetup.parse_setup(os.path.abspath(setup_path), trusted=True)
    for field, (section, key) in SETUP_PY_INFO:
        if section:
            # project urls
            if section in setup_args:
                url_dict = setup_args[section]
                if key in url_dict and meta_dict[field] is None:
                    meta_dict[field] = url_dict[key]
        else:
            if key in setup_args and meta_dict[field] is None:
                meta_dict[field] = setup_args[key]
    parse_complex_meta(meta_dict, setup_args, root_pth)


cls_filter = lambda cls: "Development Status" in cls
os_filter = lambda cls: "Operating System" in cls


def get_long_description(given_meta, root_pth):
    if "long_description" in given_meta:
        if "file:" in given_meta["long_description"]:
            _, desc_pth = tuple(given_meta["long_description"].strip().split(":"))
            desc_pth = desc_pth.rstrip().lstrip()
            readme_pth = os.path.join(root_pth, desc_pth)
            with open(readme_pth) as desc_file:
                full_desc = desc_file.read()
        else:
            full_desc = given_meta["long_description"]
    return full_desc[:DESC_LENGTH] + "..."


def parse_setuptools_version(f_pth):
    with open(f_pth) as version_file:
        for line in version_file:
            trim_line = "".join(line.split(" "))
            if "version=" in trim_line:
                _, version_number = tuple(trim_line.split("="))
                delim = '"' if '"' in line else "'"
                return version_number.split(delim)[1]


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_init_version(rel_path):
    """Retrieved from
    https://packaging.python.org/guides/single-sourcing-package-version/

    Parameters
    ----------
    rel_path : str
        path to __init__

    Returns
    -------
    str, or None
        version number stored in __init__
    """
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]


def get_pkg_version(given_meta, root_pth):
    version_file_regex = r"_*version_*(.py)?"
    pkg_version = "We could not parse the version of your package. Check PyPi for your latest version."

    # literal version resolved in meta
    if "version" in given_meta:
        if is_canonical(given_meta["version"]):
            return given_meta["version"]

    # versioning scheme with version file declared somewhere
    search_pth = os.path.join(root_pth, "**")
    pkg_files = glob.glob(search_pth, recursive=True)
    for f_pth in pkg_files:
        mtch = re.match(version_file_regex, os.path.basename(f_pth).lower())
        if mtch:
            # ends with .py - likely setuptools-scm
            if mtch.groups():
                potential_version = parse_setuptools_version(f_pth)
                if is_canonical(potential_version):
                    return potential_version
            # just a version file with no extension, should be version number only
            else:
                with open(f_pth) as version_file:
                    potential_version = version_file.read().strip()
                    if is_canonical(potential_version):
                        return potential_version

    # version number declared in __init__
    init_files = list(
        filter(lambda fn: os.path.basename(fn) == "__init__.py", pkg_files)
    )
    for pth in init_files:
        if "_tests" not in pth:
            potential_version = get_init_version(pth)
            if potential_version and is_canonical(potential_version):
                return potential_version

    return pkg_version

def filter_classifiers(classifiers):
    dev_status = list(filter(cls_filter, classifiers))
    os_support = list(filter(os_filter, classifiers))

    return dev_status, os_support

def parse_complex_meta(meta_dict, config, root_pth):
    if "classifiers" in config:
        all_classifiers = config["classifiers"]
        dev_status, os_support = filter_classifiers(all_classifiers)
        if dev_status:
            meta_dict["Development Status"] = dev_status
        if os_support:
            meta_dict["Operating System"] = os_support
    pkg_version = get_pkg_version(config, root_pth)
    meta_dict["Version"] = pkg_version

    if "install_requires" in config and config["install_requires"]:
        meta_dict["Requirements"] = config["install_requires"]    

    if meta_dict['Description'] is None:
        long_desc = get_long_description(config, root_pth)
        meta_dict["Description"] = long_desc    

def format_meta(meta):
    pass
