import codecs
import difflib
import glob
import os
import re
from contextlib import suppress

import requests
import setuptools
from requests.exceptions import HTTPError

from .constants import GITHUB_PATTERN, NAPARI_HUB_API_LINK


def flatten(config_parser):
    """Flatten ConfigParser object into dictionary of dictionaries

    Parameters
    ----------
    config_parser : ConfigParser
        object containing parsed setup.cfg metadata

    Returns
    -------
    Dict[str, Dict[str, Any]]
        dictionary of parsed metadata
    """
    config = {}
    for section in config_parser.sections():
        config.update(config_parser[section].items())
    return config


def get_long_description(given_meta, root_pth):
    """Get long description by either parsing file or taking parsed string

    Parameters
    ----------
    given_meta : Dict[str, MetaItem]
        existing metadata
    root_pth : str
        path to root of plugin package

    Returns
    -------
    str
        full long description
    """
    full_desc = ""
    # setup.cfg parser reads as "long_description"
    if "long_description" in given_meta:
        # could be a string or a file pointer
        if "file:" in given_meta["long_description"]:
            _, desc_pth = tuple(given_meta["long_description"].strip().split(":"))
            desc_pth = desc_pth.rstrip().lstrip()
            readme_pth = os.path.join(root_pth, desc_pth)
            # read the file into description
            if os.path.exists(readme_pth):
                with open(readme_pth) as desc_file:
                    full_desc = desc_file.read()
        # already been parsed, so just keep the string
        else:
            full_desc = given_meta["long_description"]
    return full_desc


def parse_setuptools_version(f_pth):
    """Parse setuptools autogenerated version.py file

    Parameters
    ----------
    f_pth : str
        path to version.py file

    Returns
    -------
    str
        version number
    """
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
    github_token = os.environ.get("GITHUB_TOKEN")
    auth_header = None
    if github_token:
        auth_header = {"Authorization": f"token {github_token}"}

    if "Source Code" in meta and re.match(GITHUB_PATTERN, meta["Source Code"].value):
        repo_url = meta["Source Code"].value
        api_url = repo_url.replace(
            "https://github.com/", "https://api.github.com/repos/"
        )
        with suppress(HTTPError):
            response = requests.get(f"{api_url}/license", headers=auth_header)
            if response.status_code != requests.codes.ok:
                response.raise_for_status()
            response_json = response.json()
            if "license" in response_json and "spdx_id" in response_json["license"]:
                spdx_id = response_json["license"]["spdx_id"]
                if spdx_id != "NOASSERTION":
                    return spdx_id


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
    """Try to find pkg version in a number of possible locations

    We check all files with `version` in the title for a canonical version
    number, as well as __init__.py files which may also list it

    Parameters
    ----------
    given_meta : Dict[str, MetaItem]
        existing metadata
    root_pth : str
        path to root of package

    Returns
    -------
    Tuple[[str|None], str]
        tuple of source, version or None, error message
    """
    version_file_regex = r"^_*version_*(.py)?$"
    pkg_version = (
        "We could not parse the version of your package."
        " Check PyPi for your latest version."
    )

    # literal version resolved in meta
    if "version" in given_meta:
        if is_canonical(given_meta["version"]):
            return None, given_meta["version"]

    # versioning scheme with version file declared somewhere
    search_pth = os.path.join(root_pth, "**")
    pkg_files = glob.glob(search_pth, recursive=True)
    for f_pth in pkg_files:
        if "build" not in f_pth and "dist" not in f_pth:
            mtch = re.match(version_file_regex, os.path.basename(f_pth).lower())
            if mtch:
                # ends with .py - likely setuptools-scm
                if mtch.groups()[0] is not None:
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
    """Filter list of classifiers to only include Development Status or Operating System

    Parameters
    ----------
    classifiers : List[str]
        list of all classifiers

    Returns
    -------
    Tuple[List, List]
        development status classifier list and operating system classifier list
    """

    dev_status = list(filter(lambda cls: "Development Status" in cls, classifiers))
    os_support = list(filter(lambda cls: "Operating System" in cls, classifiers))

    return dev_status, os_support


def split_dangling_list(dangling_list_str):
    """Split dangling list string into list of strings

    Parameters
    ----------
    dangling_list_str : str
        dangling list string

    Returns
    -------
    list[str]
        list of values
    """
    str_trimmed = dangling_list_str.lstrip().rstrip()
    val_list = str_trimmed.split("\n")
    return val_list


def split_project_urls(config):
    """Split project urls string into dict of url type: url

    Parameters
    ----------
    config : ConfigParser
        parsed setup.cfg metadata
    """
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
            r"^([1-9][0-9]*!)?(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*((a|b|rc)(0|[1-9][0-9]*))?(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?$",  # noqa
            version,
        )
        is not None
    )


class NonExistingNapariPluginError(Exception):
    def __init__(self, plugin_name, closest=None, *args, **kwargs):
        self.plugin_name = plugin_name
        self.closest = closest
        additional_msg = f", did you mean '{closest}'?" if closest else ""
        self.message = (
            f"The plugin: '{plugin_name}' does not exist in napari-hub{additional_msg}"
        )
        super().__init__(
            self.message,
            *args,
            **kwargs,
        )


def closest_plugin_name(plugin_name, api_url=NAPARI_HUB_API_LINK):
    """Returns the plugin name the closest to the one entered as parameter.
    The search of the closest name considers all registered plugin in the Napari HUB api.

    Parameters
    ----------
    plugin_name: str
        The plugin name to search for.

    api_url: Optional[str] = NAPARI_HUB_API_LINK
        The Napari HUB api url, default value is NAPARI_HUB_API_LINK from the 'napari_hub_cli.constants' module

    Returns
    -------
    str | None
        The closest plugin name found in the Napari HUB api, None if no closest match could be found
    """
    plugin_names = requests.get(api_url).json().keys()
    closest = difflib.get_close_matches(plugin_name, plugin_names, n=1)
    if closest:
        return closest[0]
    return None


def get_repository_url(plugin_name, api_url=NAPARI_HUB_API_LINK):
    """Returns the git repository url of a Napari plugin.
    The function searches directly from the Napari HUB api.

    Parameters
    ----------
    plugin_name : str
        The plugin name to get the repository url for.

    api_url: Optional[str] = NAPARI_HUB_API_LINK
        The Napari HUB api url, default value is NAPARI_HUB_API_LINK from the 'napari_hub_cli.constants' module

    Returns
    -------
    str
        The git repository url.

    Raises
    ------
    NonExistingNapariPluginError
        If the plugin does not exist in the Naparai HUB api
    """
    napari_hub_plugin_url = f"{api_url}/{plugin_name}"
    plugin_info_req = requests.get(napari_hub_plugin_url)

    if plugin_info_req.status_code != 200:
        # This line is never called, api.napari-hub.org never gives a status code != 200 even if the plugin doesn't exist
        # let it there in case they fix that in the future.
        closest_name = closest_plugin_name(plugin_name)
        raise NonExistingNapariPluginError(plugin_name, closest=closest_name)

    plugin_info = plugin_info_req.json()
    if not plugin_info:
        # If the plugin doesn't exist, an empty json is returned by the current version of the API
        closest_name = closest_plugin_name(plugin_name)
        raise NonExistingNapariPluginError(plugin_name, closest=closest_name)

    return plugin_info["code_repository"]


# TODO Improve me by mocking failing imports
# In the meantime, if setup.py includes other imports that perform computation
# over the parameters that are passed to "setup(...)", this function
# or any library relying on monkey patching of "setup(...)" will give bad results.
def parse_setup(filename):
    result = []
    setup_path = os.path.abspath(filename)
    wd = os.getcwd()  # save current directory
    os.chdir(os.path.dirname(setup_path))  # we change there
    old_setup = setuptools.setup
    setuptools.setup = lambda **kwargs: result.append(kwargs)
    with open(setup_path, "r") as f:
        try:
            exec(
                f.read(),
                {
                    "__name__": "__main__",
                    "__builtins__": __builtins__,
                    "__file__": setup_path,
                },
            )
        finally:
            setuptools.setup = (
                old_setup  # we reset setuptools function to the original one
            )
            os.chdir(wd)  # we go back to our working directory
    if result:
        return result[0]
    raise ValueError("setup wasn't called from setup.py")
