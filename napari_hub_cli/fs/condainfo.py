import functools
from functools import lru_cache

import requests

from ..fs import VirtualJsonFile


class CondaInfo(VirtualJsonFile):
    URL = "https://npe2api.vercel.app/api/conda"

    def __init__(self, virtualpath, name, python_version, platforms):
        super().__init__(virtualpath)
        self.python_version = python_version
        self.platforms = platforms
        self.name = name

    @lru_cache()
    def _fetch_data(self):
        infos = requests.get(f"{self.URL}/{self.name}")
        if infos.status_code != 200:
            return {}
        return infos.json()

    def _query_platforms(self):
        data = self._fetch_data()
        if not data:
            return []
        return data.get("conda_platforms", [])

    @property
    def is_on_conda(self):
        infos = self._fetch_data()
        if not infos:
            return False
        return True

    @property
    def is_windows_supported(self):
        platforms = self._query_platforms()
        return "noarch" in platforms or "win-32" in platforms or "win-64" in platforms

    @property
    def is_linux_supported(self):
        platforms = self._query_platforms()
        return (
            "noarch" in platforms
            or "linux-ppc64le" in platforms
            or "linux-64" in platforms
        )

    @property
    def is_macos_supported(self):
        platforms = self._query_platforms()
        return (
            "noarch" in platforms
            or "osx-64" in platforms
            or "osx-arm64" in platforms
        )
