import pandas as pd
import pathlib

SOURCES_CSV = str(pathlib.Path(__file__).parent.absolute()) + "/resources/metadata_sources.csv"
USAGE_CSV = str(pathlib.Path(__file__).parent.absolute()) + "/resources/metadata_usage.csv"

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

usage_df = pd.read_csv(USAGE_CSV)
HUB_USES = dict(zip(usage_df.Field, zip(usage_df.Filterable, usage_df.Sortable, usage_df.Searched)))

# FILTERABLE = [
#     False,
#     False,
#     False,
#     True,
#     False,
#     True,
#     False,
#     True,
#     False,
#     True,
#     False,
#     False,
#     False,
#     False,
#     False,
#     False,
# ]

# SORTABLE = [
#     False,
#     False,
#     False,
#     False,
#     False,
#     False,
#     True,
#     False,
#     False,
#     False,
#     False,
#     False,
#     False,
#     False,
#     False,
#     False,
# ]

# SEARCHED = [
#     True,
#     False,
#     True,
#     False,
#     False,
#     False,
#     True,
#     False,
#     False,
#     False,
#     False,
#     False,
#     True,
#     False,
#     False,
#     False,
# ]

# USES = zip(FILTERABLE, SORTABLE, SEARCHED)
# HUB_USES = dict(zip(FIELDS, USES))
