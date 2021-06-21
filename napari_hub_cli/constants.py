import pandas as pd
import pathlib

SOURCES_CSV = str(pathlib.Path(__file__).parent.absolute()) + "/resources/metadata_sources.csv"

DESC_PTH = "/.napari/DESCRIPTION.md"
YML_PTH = "/.napari/config.yml"
SETUP_CFG_PTH = "/setup.cfg"
SETUP_PY_PTH = "/setup.py"
DESC_LENGTH = 250
GITHUB_PATTERN = r'https://github\.com/([^/]+)/([^/]+)'

sources_df = pd.read_csv(SOURCES_CSV)
sources_df = sources_df.where(sources_df != 'None', None)

yml_info = sources_df[sources_df.YML]
YML_INFO = dict(zip(yml_info.Field, zip(yml_info.YML_Section, yml_info.YML_Key)))

cfg_info = sources_df[sources_df.CFG]
SETUP_CFG_INFO = dict(zip(cfg_info.Field, zip(cfg_info.CFG_Section, cfg_info.CFG_Key)))

py_info = sources_df[sources_df.PY]
SETUP_PY_INFO = dict(zip(py_info.Field, zip(py_info.PY_Section, py_info.PY_Key)))

FIELDS = list(sources_df.Field)

PROJECT_URLS = [
    "Project Site",
    "Documentation",
    "User Support",
    "Twitter",
    "Source Code",
    "Bug Tracker",
]

YML_META = list(yml_info.Field)

# YML_META = ["Authors"] + PROJECT_URLS
# YML_SOURCES = [("authors", None)] + [("project_urls", url) for url in PROJECT_URLS]
# YML_INFO = list(zip(YML_META, YML_SOURCES))

# SETUP_META = YML_META + [
#     "Name",
#     "Summary",
#     "Summary",
#     "License",
#     "Python Version",
# ]
# SETUP_CFG_SOURCES = (
#     [("metadata", "author")]
#     + [("metadata", "url")]
#     + YML_SOURCES[2:]
#     + [("metadata", "name")]
#     + [("metadata", "summary")]
#     + [('metadata', 'description')]
#     + [("metadata", "license")]
#     + [("options", "python_requires")]
# )
# SETUP_CFG_INFO = list(zip(SETUP_META, SETUP_CFG_SOURCES))

# SETUP_PY_SOURCES = [
#     (None, key) if section != "project_urls" else (section, key)
#     for (section, key) in SETUP_CFG_SOURCES
# ]
# SETUP_PY_INFO = list(zip(SETUP_META, SETUP_PY_SOURCES))

# FIELDS = sorted(list(set(SETUP_META)) + [
#     "Description",
#     "Operating System",
#     "Development Status",
#     "Requirements",
#     "Version",
# ])



FILTERABLE = [
    False,
    False,
    False,
    True,
    False,
    True,
    False,
    True,
    False,
    True,
    False,
    False,
    False,
    False,
    False,
    False,
]

SORTABLE = [
    False,
    False,
    False,
    False,
    False,
    False,
    True,
    False,
    False,
    False,
    False,
    False,
    False,
    False,
    False,
    False,
]

SEARCHED = [
    True,
    False,
    True,
    False,
    False,
    False,
    True,
    False,
    False,
    False,
    False,
    False,
    True,
    False,
    False,
    False,
]

USES = zip(FILTERABLE, SORTABLE, SEARCHED)
HUB_USES = dict(zip(FIELDS, USES))
