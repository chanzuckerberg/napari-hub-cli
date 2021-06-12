import os
import re
from itertools import repeat
from yaml import full_load
from configparser import ConfigParser
from .utils import (
    SETUP_META,
    YML_PTH,
    SETUP_CFG_PTH,
    SETUP_PY_PTH,
    YML_INFO,
    SETUP_INFO,
    SETUP_COMPLEX_META,
    SETUP_COMPLEX_SOURCES,
    FIELDS,
    SETUP_PY_SOURCES
)
import parsesetup

def load_meta(pth):
    meta_dict = dict(zip(FIELDS, repeat(None)))

    yml_pth = pth + YML_PTH
    if os.path.exists(yml_pth):
        read_yml_config(meta_dict, yml_pth)

    cfg_pth = pth + SETUP_CFG_PTH
    if os.path.exists(cfg_pth):
        read_setup_cfg(meta_dict, cfg_pth)

    py_pth = pth + SETUP_PY_PTH
    if os.path.exists(py_pth):
        read_setup_py(meta_dict, py_pth)


def read_yml_config(meta_dict, yml_path):
    with open(yml_path) as yml_file:
        yml_meta = full_load(yml_file)
        for field_name, (section, key) in YML_INFO:
            if section in yml_meta:
                if key and key in yml_meta[section]:
                    meta_dict[field_name] = yml_meta[section][key]
                elif not key:
                    meta_dict[field_name] = yml_meta[section]
        for k, v in meta_dict.items():
            print(f'{k} : {v}')



def read_setup_cfg(meta_dict, setup_path):
    c_parser = ConfigParser()
    c_parser.read(setup_path)

def read_setup_py(meta_dict, setup_path):
    setup_args = parsesetup.parse_setup(os.path.abspath(setup_path), trusted=True)
            

def format_meta(meta):
    pass
