##
# This file provides some monkey patching of pip to add information or to remove some logging
#
from typing import Any, Dict
from pip import __version__
from pip._internal.exceptions import HashError
from pip._internal.resolution.resolvelib.candidates import _InstallRequirementBackedCandidate
from pip._internal.req import InstallRequirement
from pip._internal.exceptions import InstallationError
from pip._internal.utils.temp_dir import TempDirectory
from pip._internal.utils.compat import has_tls
from pip._internal.utils.glibc import libc_ver
from pip._internal.metadata import get_default_environment
import pip._internal.network.session as session_module

import json
import os
import platform
import shutil
import subprocess
import sys

from requests import session


# This hack is here to get more information about a failing wheel building
OLD_PREPARE = _InstallRequirementBackedCandidate._prepare
def _prepare(self):
    try:
        dist = self._prepare_distribution()
    except HashError as e:
        # Provide HashError the underlying ireq that caused it. This
        # provides context for the resulting error message to show the
        # offending line to the user.
        e.req = self._ireq # pragma: no cover
        raise  # pragma: no cover

    self._check_metadata_consistency(dist)
    return dist
_InstallRequirementBackedCandidate._prepare = _prepare


# This hack is here to get more information about building from sources
OLD_LOAD_PYPROJECTTOML = InstallRequirement.load_pyproject_toml
def load_pyproject_toml(self):
    try:
        return OLD_LOAD_PYPROJECTTOML(self)
    except InstallationError as e:
        setattr(e, "project", str(self))
        raise
InstallRequirement.load_pyproject_toml = load_pyproject_toml


global_tracker = []
tempdir__init__ = TempDirectory.__init__
def new__init__(self, *args, **kwargs):
    tempdir__init__(self, *args, **kwargs)
    global global_tracker
    global_tracker.append(self)
TempDirectory.__init__ = new__init__


# We patch the function to be able to add a tag for platform
# (we have to copy everything, no other solutions right now)
def user_agent() -> str:
    """
    Return a string representing the user agent.
    """
    data: Dict[str, Any] = {
        "installer": {"name": "pip", "version": __version__},
        "python": platform.python_version(),
        "implementation": {
            "name": platform.python_implementation(),
        },
    }

    if data["implementation"]["name"] == "CPython":
        data["implementation"]["version"] = platform.python_version()
    elif data["implementation"]["name"] == "PyPy":
        pypy_version_info = sys.pypy_version_info  # type: ignore
        if pypy_version_info.releaselevel == "final":
            pypy_version_info = pypy_version_info[:3]
        data["implementation"]["version"] = ".".join(
            [str(x) for x in pypy_version_info]
        )
    elif data["implementation"]["name"] == "Jython":
        # Complete Guess
        data["implementation"]["version"] = platform.python_version()
    elif data["implementation"]["name"] == "IronPython":
        # Complete Guess
        data["implementation"]["version"] = platform.python_version()

    if sys.platform.startswith("linux"):
        from pip._vendor import distro

        linux_distribution = distro.name(), distro.version(), distro.codename()
        distro_infos: Dict[str, Any] = dict(
            filter(
                lambda x: x[1],
                zip(["name", "version", "id"], linux_distribution),
            )
        )
        libc = dict(
            filter(
                lambda x: x[1],
                zip(["lib", "version"], libc_ver()),
            )
        )
        if libc:
            distro_infos["libc"] = libc
        if distro_infos:
            data["distro"] = distro_infos

    if sys.platform.startswith("darwin") and platform.mac_ver()[0]:
        data["distro"] = {"name": "macOS", "version": platform.mac_ver()[0]}

    if platform.system():
        data.setdefault("system", {})["name"] = platform.system()

    if platform.release():
        data.setdefault("system", {})["release"] = f"{platform.release()}-napari"

    if platform.machine():
        data["cpu"] = platform.machine()

    # import ipdb; ipdb.set_trace()


    if has_tls():
        import _ssl as ssl

        data["openssl_version"] = ssl.OPENSSL_VERSION

    setuptools_dist = get_default_environment().get_distribution("setuptools")
    if setuptools_dist is not None:
        data["setuptools_version"] = str(setuptools_dist.version)

    if shutil.which("rustc") is not None:
        # If for any reason `rustc --version` fails, silently ignore it
        try:
            rustc_output = subprocess.check_output(
                ["rustc", "--version"], stderr=subprocess.STDOUT, timeout=0.5
            )
        except Exception:
            pass
        else:
            if rustc_output.startswith(b"rustc "):
                # The format of `rustc --version` is:
                # `b'rustc 1.52.1 (9bc8c42bb 2021-05-09)\n'`
                # We extract just the middle (1.52.1) part
                data["rustc_version"] = rustc_output.split(b" ")[1].decode()

    # Use None rather than False so as not to give the impression that
    # pip knows it is not being run under CI.  Rather, it is a null or
    # inconclusive result.  Also, we include some value rather than no
    # value to make it easier to know that the check has been run.
    # data["ci"] = True if looks_like_ci() else None
    data["ci"] = True  # PATCH: we marked it as

    user_data = os.environ.get("PIP_USER_AGENT_USER_DATA")
    if user_data is not None:
        data["user_data"] = user_data

    return "{data[installer][name]}/{data[installer][version]} {json}".format(
        data=data,
        json=json.dumps(data, separators=(",", ":"), sort_keys=True),
    )

session_module.user_agent = user_agent