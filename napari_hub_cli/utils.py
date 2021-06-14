import re

YML_PTH = "/.napari/config.yml"
SETUP_CFG_PTH = "/setup.cfg"
SETUP_PY_PTH = "/setup.py"
DESC_LENGTH = 250

PROJECT_URLS = [
    "Project Site",
    "Documentation",
    "User Support",
    "Twitter",
    "Source Code",
    "Bug Tracker",
]

YML_META = ["Authors"] + PROJECT_URLS
YML_SOURCES = [("authors", None)] + [("project_urls", url) for url in PROJECT_URLS]
YML_INFO = list(zip(YML_META, YML_SOURCES))

SETUP_META = YML_META + [
    "Name",
    "Summary",
    "License",
    "Python Version",
]
SETUP_CFG_SOURCES = (
    [("metadata", "author")]
    + [("metadata", "url")]
    + YML_SOURCES[2:]
    + [("metadata", "name")]
    + [("metadata", "summary")]
    + [("metadata", "license")]
    + [("options", "python_requires")]
)
SETUP_CFG_INFO = list(zip(SETUP_META, SETUP_CFG_SOURCES))

SETUP_PY_SOURCES = [
    (None, key) if section != "project_urls" else (section, key)
    for (section, key) in SETUP_CFG_SOURCES
]
SETUP_PY_INFO = list(zip(SETUP_META, SETUP_PY_SOURCES))

SETUP_COMPLEX_META = [
    "Operating System",
    "Requirements",
    "Development Status",
    "Version",
    "Description",
]
SETUP_COMPLEX_SOURCES = [
    "classifiers",
    "install_requires",
    "classifiers" "version",
    "long_description",
]


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
