import os
from itertools import repeat
from yaml import full_load

YML_PTH = '/.napari/config.yml'
YML_META = [
    'authors',
    'project site',
    'documentation',
    'support',
    'issues',
    'twitter',
    'source code',
]

SETUP_CFG = '/setup.cfg'
SETUP_PY = '/setup.py'
SETUP_META = [
    'name',
    'summary',
    'description',
    'license',
    'version',
    'development_status',
    'python_version',
    'os',
    'requirements',
]

def load_meta(pth):
    meta_dict = zip(YML_META+SETUP_META, repeat(None))

    yml_pth = pth+YML_PTH
    if os.path.exists(yml_pth):
        read_yml_config(meta_dict, yml_pth)

def read_yml_config(meta_dict, yml_path):
    with open(yml_path) as yml_file:
        yml_meta = full_load(yml_file)
        print(yml_meta)


def format_meta(meta):
    pass