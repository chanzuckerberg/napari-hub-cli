"""This file contains constants for finding Python package metadata in a directory"""
import pandas as pd
import pathlib

# this csv contains a mapping for each metadata field to all possible sources where it could occur
# e.g. `Authors` could be in config.yml, setup.cfg or setup.py
# each file where the field could occur also contains entries for SECTION and KEY within that file
# e.g. `Authors` is under section `authors`, key `none` in config.yml, but under section `metadata`, key `authors` in setup.cfg
# we keep this information to be able to tell the user where to find metadata, or add it if it's missing
SOURCES_CSV = (
    str(pathlib.Path(__file__).parent.absolute()) + "/resources/metadata_sources.csv"
)
# this csv maps each field to a bool for whether it is used for searching, filtering and/or sorting on the napari hub
USAGE_CSV = (
    str(pathlib.Path(__file__).parent.absolute()) + "/resources/metadata_usage.csv"
)

# standard paths from root folder to the various metadata files
DESC_PTH = "/.napari/DESCRIPTION.md"
YML_PTH = "/.napari/config.yml"
SETUP_CFG_PTH = "/setup.cfg"
SETUP_PY_PTH = "/setup.py"

# max characters to print for the description
DESC_LENGTH = 250
# regex to match github urls
GITHUB_PATTERN = r"https://github\.com/([^/]+)/([^/]+)"

sources_df = pd.read_csv(SOURCES_CSV)
sources_df = sources_df.where(sources_df != "None", None)

# here we split the sources df into the relevant fields for each metadata file
yml_info = sources_df[sources_df.YML]
YML_INFO = dict(zip(yml_info.Field, zip(yml_info.YML_Section, yml_info.YML_Key)))

cfg_info = sources_df[sources_df.CFG]
SETUP_CFG_INFO = dict(zip(cfg_info.Field, zip(cfg_info.CFG_Section, cfg_info.CFG_Key)))

py_info = sources_df[sources_df.PY]
SETUP_PY_INFO = dict(zip(py_info.Field, zip(py_info.PY_Section, py_info.PY_Key)))

FIELDS = list(set(sources_df.Field))

# various URLs the plugin developer can provide that may be displayed on the hub
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
HUB_USES = dict(
    zip(usage_df.Field, zip(usage_df.Filterable, usage_df.Sortable, usage_df.Searched))
)
