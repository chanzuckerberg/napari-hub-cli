YML_PTH = "/.napari/config.yml"
SETUP_CFG_PTH = "/setup.cfg"
SETUP_PY_PTH = "/setup.py"

YML_META = [
    "Authors",
    "Project Site",
    "Documentation",
    "User Support",
    "Twitter",
    "Source Code",
    "Report Issues",
]
YML_SOURCES = (
    [("authors", None)]
    + [("project_urls", field) for field in YML_META[1:-1]]
    + [("project_urls", "Bug Tracker")]
)
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

# SETUP_PY_SOURCES = ["name", "description", "license", "python_requires"]
# SETUP_CFG_SOURCES = [("metadata", field) for field in SETUP_PY_SOURCES]
# SETUP_INFO = zip(SETUP_META, SETUP_CFG_SOURCES, SETUP_PY_SOURCES)

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
    "version",
    "long_description",
]

FIELDS = YML_META + SETUP_META + SETUP_COMPLEX_META
