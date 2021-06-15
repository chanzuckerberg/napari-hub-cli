from typing import Union, List, Optional, Dict


class MetaSource:
    def __init__(
        self, src_file: str, section: Optional[str] = None, key: Optional[str] = None
    ) -> None:
        self.src_file = src_file
        self.section = section
        self.key = key

    def unpack(self):
        return self.src_file, self.section, self.key


class MetaItem:
    def __init__(
        self,
        field_name: str,
        value: Union[str, List[Union[str, Dict[str, str]]]],
        source: Optional[MetaSource] = None,
    ) -> None:
        self.field_name = field_name
        self.value = value
        self.source = source
