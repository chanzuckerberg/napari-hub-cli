import os
import re
from collections import defaultdict
from configparser import ConfigParser

from .utils import parse_setup
from yaml import full_load

from napari_hub_cli.meta_classes import MetaItem, MetaSource

from .constants import (DESC_LENGTH, DESC_PTH, GITHUB_PATTERN, SETUP_CFG_INFO,
                        SETUP_CFG_PTH, SETUP_PY_INFO, SETUP_PY_PTH, YML_INFO,
                        YML_PTH)
from .utils import (filter_classifiers, flatten, get_github_license,
                    get_long_description, get_pkg_version, is_canonical,
                    split_dangling_list, split_project_urls)


def load_meta(pth):
    """Load all metadata for plugin found at pth

    We preferrentially read napari hub specific metadata (DECRIPTION.md, config.yml),
    followed by setup.cfg and finally setup.py. Each field's source is therefore
    assigned as the first location where it is encountered.

    Parameters
    ----------
    pth : str
        path to local directory containing plugin

    Returns
    -------
    Dict[str, MetaItem]
        dictionary of loaded metadata
    """
    meta_dict = defaultdict(lambda: None)

    # try to read .napari/DESCRIPTION.md if available
    desc_pth = pth + DESC_PTH
    if os.path.exists(desc_pth):
        with open(desc_pth) as desc_file:
            full_desc = desc_file.read()
            if full_desc:
                desc_source = MetaSource(DESC_PTH)
                desc_item = MetaItem("Description", full_desc, desc_source)
                meta_dict[desc_item.field_name] = desc_item

    # read .napari/config.yml for authors and project urls
    yml_pth = pth + YML_PTH
    if os.path.exists(yml_pth):
        read_yml_config(meta_dict, yml_pth)

    # read all metadata available in setup.cfg
    cfg_pth = pth + SETUP_CFG_PTH
    if os.path.exists(cfg_pth):
        read_setup_cfg(meta_dict, cfg_pth, pth)

    # finally, try to read from setup.py
    py_pth = pth + SETUP_PY_PTH
    if os.path.exists(py_pth):
        read_setup_py(meta_dict, py_pth, pth)

    # napari hub will interpret GitHub URLs as Source Code
    if "Project Site" in meta_dict:
        if (
            re.match(GITHUB_PATTERN, meta_dict["Project Site"].value)
            and "Source Code" not in meta_dict
        ):
            meta_dict["Source Code"] = meta_dict["Project Site"]
            del meta_dict["Project Site"]

    # see if we can get a license from GitHub API
    github_license = get_github_license(meta_dict)
    if github_license:
        license_src = MetaSource("GitHub Repository")
        license_item = MetaItem("License", github_license, license_src)
        meta_dict[license_item.field_name] = license_item

    # trim long description so we're not printing the whole file
    if "Description" in meta_dict:
        trimmed_desc = meta_dict["Description"].value
        if len(trimmed_desc) > DESC_LENGTH:
            trimmed_desc = trimmed_desc[:DESC_LENGTH] + "..."
        meta_dict["Description"].value = trimmed_desc

    return meta_dict


def read_yml_config(meta_dict, yml_path):
    """Read available metadata from config.yml

    Parameters
    ----------
    meta_dict : Dict[str, [MetaItem|None]]
        existing metadata
    yml_path : str
        expected path to config.yml file
    """
    with open(yml_path) as yml_file:
        yml_meta = full_load(yml_file)
        for field_name, (section, key) in YML_INFO.items():
            if section in yml_meta:
                # not all fields have both section and key, account for that here
                if key in yml_meta[section]:
                    src = MetaSource(YML_PTH, section, key)
                    item = MetaItem(field_name, yml_meta[section][key], src)
                    meta_dict[field_name] = item
                elif not key:
                    src = MetaSource(YML_PTH, section)
                    item = MetaItem(field_name, yml_meta[section], src)
                    meta_dict[field_name] = item


def read_setup_cfg(meta_dict, setup_path, root_pth):
    """Read available metadata from setup.cfg

    Parameters
    ----------
    meta_dict : Dict[str, [MetaItem|None]]
        dictionary of existing metadata (from other sources)
    setup_path : str
        expected path to setup.cfg
    root_pth : str
        path to root of package, used to try searching version
    """
    c_parser = ConfigParser()
    c_parser.optionxform = str
    c_parser.read(setup_path)

    # project URLs are just read as one big string, so split them into list
    split_project_urls(c_parser)

    for field, (section, key) in SETUP_CFG_INFO.items():
        if (
            field not in meta_dict
            and section in c_parser.sections()
            and key in c_parser[section]
        ):
            item_src = MetaSource(SETUP_CFG_PTH, section, key)
            item = MetaItem(field, c_parser[section][key], item_src)
            meta_dict[field] = item

    # flatten ConfigParser object into dictionary
    config = flatten(c_parser)
    # development status, version, description and requirements all require
    # some bespoke parsing due to their format
    parse_complex_meta(meta_dict, config, root_pth, SETUP_CFG_PTH)


def read_setup_py(meta_dict, setup_path, root_pth):
    """Read available metadata from setup.py

    While this function doesn't install the package, the parsesetup library
    *does* require executing the code in setup.py in order to read the metadata.
    This is executed using `trusted=True` so that users do not have to install docker
    to preview metadata

    Parameters
    ----------
    meta_dict : Dict[str, [MetaItem|None]]
        dictionary of existing metadata
    setup_path : str
        expected path to setup.py
    root_pth : str
        path to root of package, used to try searching version
    """
    setup_args = parse_setup(os.path.abspath(setup_path))
    for field, (section, key) in SETUP_PY_INFO.items():
        if field not in meta_dict:
            if section:
                # project urls are the only fields with a section
                if section in setup_args:
                    url_dict = setup_args[section]
                    if key in url_dict:
                        src = MetaSource(SETUP_PY_PTH, section, key)
                        item = MetaItem(field, url_dict[key], src)
                        meta_dict[field] = item
            else:
                if key in setup_args:
                    src = MetaSource(SETUP_PY_PTH, section, key)
                    item = MetaItem(field, setup_args[key], src)
                    meta_dict[field] = item
    # development status, version, description and requirements all require
    # some bespoke parsing due to their format
    parse_complex_meta(meta_dict, setup_args, root_pth, SETUP_PY_PTH)


def parse_complex_meta(meta_dict, config, root_pth, cfg_pth):
    """Parse metadata requiring additional handling besides section and key.

    Development Status: found in a list of classifiers that needs to be filtered
    Operating System: found in a list of classifiers that needs to be filtered
    Version: we try to look for the version as a literal in setup.py, setup.cfg,
    __init__.py, or the setuptools generated _version.py
    Description: could be found as file:file_pth in setup.cfg or literal string
    Requirements: could be a list of requirements or a string which needs splitting


    Parameters
    ----------
    meta_dict : Dict[str, [MetaItem|None]]
        dictionary of existing metadata
    config : Dict[str, Any]
        current config to search through - could come from setup.cfg or setup.py
    root_pth : str
        path to the root of the package, used for searching for version
    cfg_pth : str
        path to config file currently used
    """
    section = None
    # if we have a setup.cfg file, all meta will be under the metadata section
    if "cfg" in cfg_pth:
        section = "metadata"

    key = "classifiers"
    if key in config:
        all_classifiers = config[key]
        # setup.cfg parser sometimes reads all classifiers as string
        if isinstance(all_classifiers, str):
            all_classifiers = split_dangling_list(all_classifiers)
        # filter irrelvant classifiers
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
        # if we couldn't find version, we return an error message and no src
        if src:
            version_source = MetaSource(src)
        else:
            # check if pkg_version matches the versioning spec
            if is_canonical(pkg_version):
                version_source = MetaSource(cfg_pth, section, "version")
        version_item.source = version_source

    if "Description" not in meta_dict or "file:" in meta_dict["Description"].value:
        # get description by either reading the given file or trying to find the README
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
        # requirements are sometimes read as string
        if isinstance(reqs, str):
            reqs = split_dangling_list(reqs)
        reqs_source = MetaSource(cfg_pth, section, key)
        reqs_item = MetaItem("Requirements", reqs, reqs_source)
        meta_dict[reqs_item.field_name] = reqs_item


def get_missing(meta, pth):
    """Find each missing field and suggest a source based on existing meta

    Parameters
    ----------
    meta : Dict[str, MetaItem]
        existing metadata
    pth : str
        path to root of package

    Returns
    -------
    Dict[str, MetaItem]
        dictionary of missing metadata with suggested sources
    """
    missing_meta = defaultdict(None)
    # missing meta that could be in config.yml gets config.yml as suggested source
    for field, source in YML_INFO.items():
        if field not in meta:
            section, key = source
            src_item = MetaSource(YML_PTH, section, key)
            missing_meta[field] = src_item

    # DESCRIPTION.md is suggested source for description
    if "Description" not in meta:
        src_item = MetaSource(DESC_PTH)
        missing_meta["Description"] = src_item

    cfg_pth = pth + SETUP_CFG_PTH
    py_pth = pth + SETUP_PY_PTH
    # if we already have a cfg or if we don't have setup.py, we prefer setup.cfg
    if os.path.exists(cfg_pth) or not os.path.exists(py_pth):
        suggested_cfg = SETUP_CFG_PTH
        cfg_info = SETUP_CFG_INFO
    # if the user already has setup.py, we use that instead
    else:
        suggested_cfg = SETUP_PY_PTH
        cfg_info = SETUP_PY_INFO

    for field, src in cfg_info.items():
        if field not in meta and field not in missing_meta:
            section, key = src
            src_item = MetaSource(suggested_cfg, section, key)
            missing_meta[field] = src_item

    for field in ["Operating System", "Development Status"]:
        section = None
        if field not in meta:
            if suggested_cfg == SETUP_CFG_PTH:
                section = "metadata"
            src_item = MetaSource(suggested_cfg, section, "classifiers")
            missing_meta[field] = src_item

    section = None
    if "Requirements" not in meta:
        if suggested_cfg == SETUP_CFG_PTH:
            section = "options"
        src_item = MetaSource(suggested_cfg, section, "install_requires")
        missing_meta["Requirements"] = src_item

    return missing_meta
