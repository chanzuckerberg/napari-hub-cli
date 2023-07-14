##
# This file provides some monkey patching of pip to add information or to remove some logging
#
from pip._internal.exceptions import HashError
from pip._internal.resolution.resolvelib.candidates import _InstallRequirementBackedCandidate
from pip._internal.req import InstallRequirement
from pip._internal.exceptions import InstallationError
from pip._internal.utils.temp_dir import TempDirectory

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