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
    FIELDS,
    SETUP_PY_SOURCES
)
from ast import parse, Call, Attribute, walk, literal_eval, dump

def load_meta(pth):
    meta_dict = zip(FIELDS, repeat(None))

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
        print(yml_meta)


def read_setup_cfg(meta_dict, setup_path):
    c_parser = ConfigParser()
    c_parser.read(setup_path)
    print([val for val in c_parser["metadata"]])

def read_setup_py(meta_dict, setup_path):
    setup_func_regex = r"setup\((.*)\)"
    with open(setup_path) as setup_file:
        module = parse(setup_file.read())
        filtered = []
        for node in module.body:
            for node in walk(node):
                if isinstance(node,Call):
                    if not isinstance(node.func, Attribute) and node.func.id == "setup":
                        ast_keywords = node.keywords
                        print([kwd.arg for kwd in ast_keywords])
                        print(SETUP_PY_SOURCES)
                        filtered = list(filter(lambda kwd:kwd.arg in SETUP_PY_SOURCES, ast_keywords))
                        
        print([(kwd.arg, literal_eval(kwd.value)) for kwd in filtered])
            

def format_meta(meta):
    pass
