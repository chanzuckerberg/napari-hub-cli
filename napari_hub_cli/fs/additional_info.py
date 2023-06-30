import os
import re
from datetime import datetime
from functools import lru_cache

import napari_hub_cli._version as version

from ..fs import RepositoryFile


class AdditionalInfo(RepositoryFile):
    """
    Represents a license file in a GitHub repository and provides methods for
    retrieving its SPDX identifier and checking if it is an OSI-approved license.

    Parameters
    ----------
    file : str
        The path of the license file.

    """

    @property
    def get_cli_tool_version(self):
        """
        Gets the version of the CLI tool as a string.

        Returns
        -------
        str
            The version of the CLI tool.
        """
        return version.__version__

    @property
    def timestamp(self):
        """
        Gets the current date and time as a formatted string.

        Returns
        -------
        str
            A formatted string representing the current date and time.
        """
        return datetime.now().strftime("%d %b %Y - %Hh %Mm %Ss")
