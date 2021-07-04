import re
import glob
import codecs
import os
import json
import requests
from requests.exceptions import HTTPError

from .constants import GITHUB_PATTERN


def flatten(config_parser):
    config = {}
    for section in config_parser.sections():
        config.update(config_parser[section].items())
    return config


def get_long_description(given_meta, root_pth):
    full_desc = ""
    if "long_description" in given_meta:
        if "file:" in given_meta["long_description"]:
            _, desc_pth = tuple(given_meta["long_description"].strip().split(":"))
            desc_pth = desc_pth.rstrip().lstrip()
            readme_pth = os.path.join(root_pth, desc_pth)
            if os.path.exists(readme_pth):
                with open(readme_pth) as desc_file:
                    full_desc = desc_file.read()
        else:
            full_desc = given_meta["long_description"]
    return full_desc


def parse_setuptools_version(f_pth):
    with codecs.open(f_pth, "r", encoding="utf-8", errors="ignore") as version_file:
        for line in version_file:
            trim_line = "".join(line.split(" "))
            if "version=" in trim_line:
                _, version_number = tuple(trim_line.split("="))
                delim = '"' if '"' in line else "'"
                version_number_split = version_number.split(delim)
                if len(version_number_split) > 1:
                    return version_number_split[1]
                else: 
                    return None


def read(rel_path):
    with codecs.open(rel_path, "r") as fp:
        return fp.read()


def get_github_license(meta):
    """Use Source Code field to get license from GitHub repo

    Parameters
    ----------
    meta : dict
        dictionary of loaded metadata

    Returns
    -------
    str
        the license spdx identifier, or None
    """
    if "Source Code" in meta and re.match(GITHUB_PATTERN, meta["Source Code"].value):
        repo_url = meta["Source Code"].value
        api_url = repo_url.replace("https://github.com/",
                              "https://api.github.com/repos/")
        try:
            response = requests.get(f'{api_url}/license')
            if response.status_code != requests.codes.ok:
                response.raise_for_status()
            response_json = json.loads(response.text.strip())
            if 'license' in response_json and 'spdx_id' in response_json['license']: 
                return response_json['license']["spdx_id"]
        except HTTPError:
            return None


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
    version_file_regex = r"^_*version_*(.py)?$"
    pkg_version = "We could not parse the version of your package. Check PyPi for your latest version."

    # literal version resolved in meta
    if "version" in given_meta:
        if is_canonical(given_meta["version"]):
            return None, given_meta["version"]

    # versioning scheme with version file declared somewhere
    search_pth = os.path.join(root_pth, "**")
    pkg_files = glob.glob(search_pth, recursive=True)
    for f_pth in pkg_files:
        if 'build' not in f_pth and 'dist' not in f_pth:
            mtch = re.match(version_file_regex, os.path.basename(f_pth).lower())
            if mtch:
                # ends with .py - likely setuptools-scm
                if mtch.groups()[0] != None:
                    potential_version = parse_setuptools_version(f_pth)
                    if potential_version and is_canonical(potential_version):
                        return f_pth, potential_version
                # just a version file with no extension, should be version number only
                else:
                    with codecs.open(
                        f_pth, "r", encoding="utf-8", errors="ignore"
                    ) as version_file:
                        potential_version = version_file.read().strip()
                        if is_canonical(potential_version):
                            return f_pth, potential_version

    # version number declared in __init__
    init_files = list(
        filter(lambda fn: os.path.basename(fn) == "__init__.py", pkg_files)
    )
    for pth in init_files:
        if "_tests" not in pth:
            potential_version = get_init_version(pth)
            if potential_version and is_canonical(potential_version):
                return pth, potential_version

    return None, pkg_version


def filter_classifiers(classifiers):
    cls_filter = lambda cls: "Development Status" in cls
    os_filter = lambda cls: "Operating System" in cls

    dev_status = list(filter(cls_filter, classifiers))
    os_support = list(filter(os_filter, classifiers))

    return dev_status, os_support


def split_dangling_list(dangling_list_str):
    str_trimmed = dangling_list_str.lstrip().rstrip()
    val_list = str_trimmed.split("\n")
    return val_list


def split_project_urls(config):
    if "metadata" in config.sections() and "project_urls" in config["metadata"]:
        url_str = config["metadata"]["project_urls"]
        del config["metadata"]["project_urls"]

        url_list = split_dangling_list(url_str)
        url_dict = {}
        for url in url_list:
            split_url = url.split(" = ")
            url_dict[split_url[0]] = split_url[1]

        config["project_urls"] = url_dict


def is_canonical(version):
    """Returns true if version is in canonical PEP440 format,
    otherwise False.

    See
    https://www.python.org/dev/peps/pep-0440/#appendix-b-parsing-version-strings-with-regular-expressions
    for detail.

    Parameters
    ----------
    version : str
        String to check for canonical version.

    Returns
    -------
    bool
        True if version matches canonical PEP440 format, otherwise False
    """
    return (
        re.match(
            r"^([1-9][0-9]*!)?(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*((a|b|rc)(0|[1-9][0-9]*))?(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?$",
            version,
        )
        is not None
    )
