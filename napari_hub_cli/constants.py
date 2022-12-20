"""This file contains constants for finding Python package metadata in a directory"""
# import pathlib
# from ast import literal_eval
# from csv import DictReader


# def read_csv(filepath):
#     def parse_value(v):
#         try:
#             return literal_eval(v)
#         except Exception:
#             return v

#     with open(filepath, "r", newline="") as f:
#         reader = DictReader(f)
#         return [{k: parse_value(v) for k, v in row.items()} for row in reader]


# def extract_config_infos(sources, kind):
#     infos = tuple(row for row in sources if row.get(kind, False))
#     return extract_infos(infos, (f"{kind}_Section", f"{kind}_Key"))


# def extract_infos(infos, columns, key="Field"):
#     return {info[key]: tuple(info[k] for k in columns) for info in infos}


# """
# this csv contains a mapping for each metadata field to all possible sources
# e.g. `Authors` could be in config.yml, setup.cfg or setup.py
# each possible source file also contains entries for SECTION and KEY within that file
# e.g. `Authors` is under section `authors`, key `none` in config.yml, but under
# section `metadata`, key `authors` in setup.cfg
# we keep this information to be able to tell the user where to find metadata,
# or add it if it's missing
# """
# _PARENT_PATH = pathlib.Path(__file__).parent.absolute()
# SOURCES_CSV = f"{_PARENT_PATH}/resources/metadata_sources.csv"
# # this csv maps each field to a bool for whether it is used for searching,
# # filtering and/or sorting on the napari hub
# USAGE_CSV = f"{_PARENT_PATH}/resources/metadata_usage.csv"

# # standard paths from root folder to the various metadata files
# DESC_PTH = ".napari/DESCRIPTION.md"
# YML_PTH = ".napari/config.yml"
# SETUP_CFG_PTH = "setup.cfg"
# SETUP_PY_PTH = "setup.py"

# # max characters to print for the description
# DESC_LENGTH = 250
# # regex to match github urls
# GITHUB_PATTERN = r"https://github\.com/([^/]+)/([^/]+)"

# # here we split the sources df into the relevant fields for each metadata file
# sources = read_csv(SOURCES_CSV)
# YML_INFO = extract_config_infos(sources, "YML")
# SETUP_CFG_INFO = extract_config_infos(sources, "CFG")
# SETUP_PY_INFO = extract_config_infos(sources, "PY")

# FIELDS = list(set(info["Field"] for info in sources))

# # various URLs the plugin developer can provide that may be displayed on the hub
# PROJECT_URLS = [
#     "Project Site",
#     "Documentation",
#     "User Support",
#     "Twitter",
#     "Source Code",
#     "Bug Tracker",
# ]

# YML_META = YML_INFO

# usage = read_csv(USAGE_CSV)
# HUB_USES = extract_infos(usage, ("Filterable", "Sortable", "Searched"))

NAPARI_HUB_API_URL = "https://api.napari-hub.org/plugins"
