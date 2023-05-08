import difflib
import errno
import os
import shutil
import stat
import tempfile
import warnings
import weakref
from re import sub

import requests
import setuptools
from git import GitError, InvalidGitRepositoryError
from git.repo import Repo

from .constants import NAPARI_HUB_API_URL

# def get_github_license(meta):
#     """Use Source Code field to get license from GitHub repo

#     Parameters
#     ----------
#     meta : dict
#         dictionary of loaded metadata

#     Returns
#     -------
#     str
#         the license spdx identifier, or None
#     """
#     github_token = os.environ.get("GITHUB_TOKEN")
#     auth_header = None
#     if github_token:
#         auth_header = {"Authorization": f"token {github_token}"}

#     if "Source Code" in meta and re.match(GITHUB_PATTERN, meta["Source Code"].value):
#         repo_url = meta["Source Code"].value
#         api_url = repo_url.replace(
#             "https://github.com/", "https://api.github.com/repos/"
#         )
#         with suppress(HTTPError):
#             response = requests.get(f"{api_url}/license", headers=auth_header)
#             if response.status_code != requests.codes.ok:
#                 response.raise_for_status()
#             response_json = response.json()
#             if "license" in response_json and "spdx_id" in response_json["license"]:
#                 spdx_id = response_json["license"]["spdx_id"]
#                 if spdx_id != "NOASSERTION":
#                     return spdx_id


class NonExistingNapariPluginError(Exception):
    def __init__(self, plugin_name, closest=None, *args, **kwargs):
        self.plugin_name = plugin_name
        self.closest = closest
        additional_msg = f", did you mean '{closest}'?" if closest else ""
        self.message = (
            f"The plugin: '{plugin_name}' does not exist in napari-hub{additional_msg}"
        )
        super().__init__(
            self.message,
            *args,
            **kwargs,
        )


def get_all_napari_plugin_names(api_url=NAPARI_HUB_API_URL):
    return requests.get(api_url).json().keys()


def closest_plugin_name(plugin_name, api_url=NAPARI_HUB_API_URL):
    """Returns the plugin name the closest to the one entered as parameter.
    The search of the closest name considers all registered plugin in the Napari HUB api.

    Parameters
    ----------
    plugin_name: str
        The plugin name to search for.

    api_url: Optional[str] = NAPARI_HUB_API_LINK
        The Napari HUB api url, default value is NAPARI_HUB_API_LINK from the 'napari_hub_cli.constants' module

    Returns
    -------
    str | None
        The closest plugin name found in the Napari HUB api, None if no closest match could be found
    """
    plugin_names = requests.get(api_url).json().keys()
    closest = difflib.get_close_matches(plugin_name, plugin_names, n=1)
    if closest:
        return closest[0]
    return None


def get_repository_url(plugin_name, api_url=NAPARI_HUB_API_URL):
    """Returns the git repository url of a Napari plugin.
    The function searches directly from the Napari HUB api.

    Parameters
    ----------
    plugin_name : str
        The plugin name to get the repository url for.

    api_url: Optional[str] = NAPARI_HUB_API_LINK
        The Napari HUB api url, default value is NAPARI_HUB_API_LINK from the 'napari_hub_cli.constants' module

    Returns
    -------
    str
        The git repository url.

    Raises
    ------
    NonExistingNapariPluginError
        If the plugin does not exist in the Naparai HUB api
    """
    napari_hub_plugin_url = f"{api_url}/{plugin_name}"
    plugin_info_req = requests.get(napari_hub_plugin_url)

    if plugin_info_req.status_code != 200:
        # This line is never called, api.napari-hub.org never gives a status code != 200 even if the plugin doesn't exist
        # let it there in case they fix that in the future.
        closest_name = closest_plugin_name(plugin_name)
        raise NonExistingNapariPluginError(plugin_name, closest=closest_name)

    plugin_info = plugin_info_req.json()
    if not plugin_info:
        # If the plugin doesn't exist, an empty json is returned by the current version of the API
        closest_name = closest_plugin_name(plugin_name)
        raise NonExistingNapariPluginError(plugin_name, closest=closest_name)

    return plugin_info["code_repository"]


def scrap_git_infos(local_repo):
    try:
        repo = Repo(local_repo.absolute())
    except InvalidGitRepositoryError:
        return {}

    try:
        url = repo.remote().url  # pragma: no cover

        title = sub(r"\.git$", "", [s for s in url.split("/") if s][-1])
        return {
            "title": title,
            "url": url,
        }
    except Exception:
        return {"title": "", "url": ""}


# TODO Improve me by mocking failing imports
# In the meantime, if setup.py includes other imports that perform computation
# over the parameters that are passed to "setup(...)", this function
# or any library relying on monkey patching of "setup(...)" will give bad results.
def parse_setup(filename):
    result = []
    setup_path = os.path.abspath(filename)
    wd = os.getcwd()  # save current directory
    os.chdir(os.path.dirname(setup_path))  # we change there
    old_setup = setuptools.setup
    setuptools.setup = lambda **kwargs: result.append(kwargs)
    with open(setup_path, "r") as f:
        try:
            exec(
                f.read(),
                {
                    "__name__": "__main__",
                    "__builtins__": __builtins__,
                    "__file__": setup_path,
                },
            )
        finally:
            setuptools.setup = (
                old_setup  # we reset setuptools function to the original one
            )
            os.chdir(wd)  # we go back to our working directory
    if result:
        return result[0]
    raise ValueError("setup wasn't called from setup.py")  # pragma: no cover


# Fix issue with tmpedir library with windows and Python 3.7
# See: https://bugs.python.org/issue26660
# Fix code is copied from https://github.com/copier-org/copier
def handle_remove_readonly(func, path, exc):  # pragma: no cover
    excvalue = exc[1]
    if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise


def delete_file_tree(path):
    shutil.rmtree(path, ignore_errors=False, onerror=handle_remove_readonly)


class TemporaryDirectory(tempfile.TemporaryDirectory):
    """A custom version of `tempfile.TemporaryDirectory` that handles read-only files better.
    On Windows, before Python 3.8, `shutil.rmtree` does not handle read-only files very well.
    This custom class makes use of a [special error handler][copier.tools.handle_remove_readonly]
    to make sure that a temporary directory containing read-only files (typically created
    when git-cloning a repository) is properly cleaned-up (i.e. removed) after using it
    in a context manager.
    """

    def __init__(
        self,
        suffix=None,
        prefix=None,
        dir=None,
        ignore_cleanup_errors=False,
        delete=True,
    ):
        self.name = tempfile.mkdtemp(suffix, prefix, dir)
        self._delete = delete
        self._ignore_cleanup_errors = ignore_cleanup_errors
        self._finalizer = weakref.finalize(
            self,
            self._cleanup,
            self.name,
            warn_message="Implicitly cleaning up {!r}".format(self),
            ignore_errors=self._ignore_cleanup_errors,
            delete=self._delete,
        )

    @classmethod
    def _cleanup(
        cls, name, warn_message, ignore_errors=False, delete=True
    ):  # pragma: no cover
        if not delete:
            return
        cls._robust_cleanup(name)
        warnings.warn(warn_message, ResourceWarning)

    def cleanup(self):
        if self._finalizer.detach():
            self._robust_cleanup(self.name)

    @staticmethod
    def _robust_cleanup(name):
        delete_file_tree(name)

    def __exit__(self, exc, value, tb):
        if not self._delete:
            return
        self.cleanup()


class LocalDirectory(object):
    def __init__(self, path, delete):
        self.path = path
        self.delete = delete

    def __enter__(self):
        return self.path.absolute()

    def __exit__(self, exc, value, tb):
        if not self.delete:
            return
        delete_file_tree(self.path.absolute())
