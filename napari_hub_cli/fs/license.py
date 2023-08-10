import re
from functools import lru_cache

import requests
from requests.exceptions import HTTPError

from ..utils import build_gh_header

from ..fs import RepositoryFile


class License(RepositoryFile):
    """
    Represents a license file in a GitHub repository and provides methods for
    retrieving its SPDX identifier and checking if it is an OSI-approved license.

    Parameters
    ----------
    file : str
        The path of the license file.
    url : str
        The URL of the repository.
    """

    def __init__(self, file, url):
        super().__init__(file)
        self.url = url

    @classmethod
    @lru_cache()
    def get_osi_approved_licenses(cls):
        """
        Retrieves the list of SPDX identifiers for all OSI-approved licenses from https://opensource.org/licenses/.

        Returns
        -------
        List
            The list of SPDX identifiers for all OSI-approved licenses.
        """
        OSI_LICENSES_URL = "https://api.opensource.org/licenses/"
        response = requests.get(OSI_LICENSES_URL)
        if response.status_code == 200:
            all_ids = (
                [entry["id"]]
                + [ident["identifier"] for ident in entry.get("identifiers", [])]
                for entry in response.json()
            )
            return [id for ids in all_ids for id in ids]
        return []

    def get_github_license(self):
        """
        Use the GitHub API to retrieve the SPDX identifier of the repository's license.

        Returns
        -------
        [str, None]
            The SPDX identifier of the license, or None if not found or not an OSI-approved license.
        """
        GITHUB_PATTERN = r"https://github.com/.+/.+"
        url = self.url or ""
        if url.endswith(".git"):
            url = url[:-4]
        if re.match(GITHUB_PATTERN, url):
            api_url = url.replace(
                "https://github.com/", "https://api.github.com/repos/"
            )
            response = requests.get(f"{api_url}/license", headers=build_gh_header())
            if response.status_code == 401:  # token revokation
                print(
                    f"{response.status_code} Client Error: {response.reason} for url: {response.url}"
                )
                print("Your Github token is not correct or have been revoked.")
                exit(-126)
            if response.status_code == 403:  # rate limit exceed
                print(
                    f"{response.status_code} Client Error: {response.reason} for url: {response.url}"
                )
                exit(-127)
            if response.status_code != requests.codes.ok:
                return None
            response_json = response.json()
            if "license" in response_json and "spdx_id" in response_json["license"]:
                spdx_id = response_json["license"]["spdx_id"]
                if spdx_id != "NOASSERTION":
                    return spdx_id

    @property
    def is_osi_approved(self):
        """
        Checks if the license file is an OSI-approved license.

        Returns
        -------
        bool
            True if the license is OSI-approved, False otherwise.
        """
        spdx_id = self.get_github_license()
        return spdx_id in self.get_osi_approved_licenses()
