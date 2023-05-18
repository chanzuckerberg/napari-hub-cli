import re
import os
from functools import lru_cache

from ..fs import RepositoryFile
from datetime import datetime

import napari_hub_cli._version as version


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
        now = datetime.now()
        day = now.day
        month = now.strftime("%b")
        year = now.year
        hours = now.hour
        minutes = now.minute
        seconds = now.second
        formatted_date = f"{day} {month} {year} - {hours}h {minutes}m {seconds}s"
        return formatted_date

