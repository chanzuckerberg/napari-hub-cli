from enum import Enum

class CONFIG(Enum):
    YML = ('.napari', 'config.yml')
    CFG = 'setup.cfg'
    PY = 'setup.py'
    DESC = ('.napari', 'DESCRIPTION.md')
    INIT = ('test_plugin_name', '__init__.py')
    SCM_VERS = ('test_plugin_name', '_version.py')
    VERS = 'VERSION'