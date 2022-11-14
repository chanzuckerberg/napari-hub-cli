"""Metadata classes mainly to support the use of named attributes"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Union


@dataclass
class MetaSource:
    src_file: str
    section: Optional[str] = None
    key: Optional[str] = None

    def unpack(self):
        return self.src_file, self.section, self.key


@dataclass
class MetaItem:
    field_name: str
    value: Union[str, List[Union[str, Dict[str, str]]]]
    source: Optional[MetaSource] = None
