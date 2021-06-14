from enum import Enum

class CONFIG(Enum):
    YML = '.napari/config.yml'
    CFG = 'setup.cfg'
    PY = 'setup.py'
    DESC = '.napari/DESCRIPTION.md'
    INIT = '__init__.py'
    SCM_VERS = '_version.py'
    VERS = 'VERSION'