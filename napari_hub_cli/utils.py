YML_PTH = "/.napari/config.yml"
SETUP_CFG_PTH = "/setup.cfg"
SETUP_PY_PTH = "/setup.py"

YML_META = [
    "Authors",
    "Project Site",
    "Documentation",
    "User Support",
    "Report Issues",
    "Twitter",
    "Source Code",
]
YML_SOURCES = [(YML_META[0].lower(), None)] + [
    ("project_urls", field.lower()) for field in YML_META[1:]
]
YML_INFO = zip(YML_META, YML_SOURCES)

SETUP_META = [
    "Name",
    "Summary",
    "License",
    "Python Version",
]
SETUP_PY_SOURCES = ["name", "description", "license", "python_requires"]
SETUP_CFG_SOURCES = [("metadata", field) for field in SETUP_PY_SOURCES]
SETUP_INFO = zip(SETUP_META, SETUP_CFG_SOURCES, SETUP_PY_SOURCES)

SETUP_COMPLEX_META = [
    "Operating System",
    "Requirements",
    "Development Status",
    "Version",
    "Description",
]

FIELDS = YML_META + SETUP_META + SETUP_COMPLEX_META
