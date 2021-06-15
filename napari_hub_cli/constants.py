DESC_PTH = "/.napari/DESCRIPTION.md"
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
    + YML_SOURCES[1:]
    + [("metadata", "url")]
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

FIELDS = SETUP_META + [
    "Description",
    "Operating System",
    "Development Status",
    "Requirements",
    "Version",
]
