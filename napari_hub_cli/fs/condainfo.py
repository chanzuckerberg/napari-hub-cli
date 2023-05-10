import functools
from functools import lru_cache

import requests

from ..fs import VirtualJsonFile


class CondaInfo(VirtualJsonFile):
    BASE_URL = "https://npe2api.vercel.app/"
    CONDA_URL = f"{BASE_URL}/api/conda"
    ERRORS_URL = f"{BASE_URL}/errors.json"

    def __init__(self, virtualpath, name, python_version, platforms):
        super().__init__(virtualpath)
        self.python_version = python_version
        self.platforms = platforms
        self.name = name

    @lru_cache()
    def _fetch_data(self, url):
        infos = requests.get(url)
        if infos.status_code != 200:
            return {}
        return infos.json()

    def _query_platforms(self):
        data = self._fetch_data(f"{self.CONDA_URL}/{self.name}")
        if not data:
            return []
        return data.get("conda_platforms", [])

    def _query_errors(self):
        return self._fetch_data(self.ERRORS_URL)

    @property
    def has_npe_parse_errors(self):
        data = self._query_errors()
        return self.name in data

    @property
    def is_on_conda(self):
        infos = self._query_platforms()
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
            "noarch" in platforms or "osx-64" in platforms or "osx-arm64" in platforms
        )
