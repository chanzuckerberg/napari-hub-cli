import itertools
from pathlib import Path
from tempfile import gettempdir
from unittest import result

TEMPDIR = Path(gettempdir()) / "pipcache"

WIN64 = ["win_amd64"]
WIN32 = ["win32"]
LINUX = [
    "manylinux2014_x86_64",
]
MACOS = ["macosx_10_9_x86_64"]

_platform_specs = {
    "win": WIN64,
    "windows": WIN64,
    "linux": LINUX,
    "macos": MACOS,
}


class Options(dict):
    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        return self[key]


def build_options(python_version, platform, abis=None):
    platforms = _platform_specs.get(platform, platform) if platform else None
    return Options(
        {
            "index_url": "https://pypi.org/simple",
            "extra_index_urls": [],
            "no_index": False,
            "find_links": [],
            "build_isolation": True,
            "check_build_deps": False,
            "progress_bar": "on",
            "require_hashes": False,
            "features_enabled": ["fast-deps"],
            "use_user_site": False,
            "force_reinstall": False,
            "ignore_requires_python": False,
            "ignore_installed": True,
            "isolated_mode": False,
            "ignore_dependencies": False,
            "target_dir": None,
            "python_version": python_version,
            "abis": abis,
            "implementation": None,
            "platforms": platforms,
            "cache_dir": TEMPDIR,
            "timeout": 15,
            "retries": 5,
            "trusted_hosts": [],
            "cert": None,
            "client_cert": None,
            "proxy": "",
            "no_input": False,
            "keyring_provider": None,
            "no_color": False,
            "log": None,
            "no_clean": False,
            "dry_run": True,
            "json_report_file": None,
            "root_path": None,
            "prefix_path": None,
            "override_externally_managed": False,
            "upgrade": False,
            "format_control": None,
            "global": None,
            "pre": None,
            "prefer_binary": False,
            "constraints": [],
            "use_pep517": False,
            "config_settings": None,
            "editables": [],
            "requirements": [],
            "build": [],
            "deprecated_features_enabled": [],
            "src_dir": "",
        }
    )
