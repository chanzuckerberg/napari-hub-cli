import os
from pathlib import Path
from unittest import mock

import pytest
from requests import HTTPError

from napari_hub_cli.fs import NapariPlugin
from napari_hub_cli.utils import build_gh_header, read_gh_token

RESOURCES = Path(__file__).parent / "resources"
MOCK_REQUESTS = None


@pytest.fixture(scope="module")
def test_real_repo():
    current_path = Path(__file__).parent.absolute()
    url = "https://github.com/brainglobe/brainreg-napari.git"
    return NapariPlugin(current_path / "resources" / "licenses" / "repo_example1", url)


@pytest.fixture(autouse=True)
def clear_cache(test_real_repo):
    license = test_real_repo.license
    license.get_osi_approved_licenses.cache_clear()  # type: ignore
    yield
    license.get_osi_approved_licenses.cache_clear()  # type: ignore


@pytest.mark.online
def test_get_real_osi_licenses(test_real_repo):
    license = test_real_repo.license
    approved_licenses = license.get_osi_approved_licenses()
    licenses_to_check = [
        "AAL",
        "AFL-3.0",
        "AGPL-3.0",
        "APL-1.0",
        "APSL-2.0",
        "Apache-1.1",
        "Apache-2.0",
        "Artistic-1.0",
        "Artistic-2.0",
        "BSD-2",
        "BSD-3",
        "BSL-1.0",
        "CATOSL-1.1",
        "CDDL-1.0",
        "CECILL-2.1",
        "CNRI-Python",
        "CPAL-1.0",
        "CPL-1.0",
        "CUA-OPL-1.0",
        "CVW",
        "ECL-1.0",
        "ECL-2.0",
        "EFL-1.0",
        "EFL-2.0",
        "EPL-1.0",
        "EUDatagrid",
        "EUPL-1.1",
        "Entessa",
        "Fair",
        "Frameworx-1.0",
        "GPL-2.0",
        "GPL-3.0",
        "HPND",
        "IPA",
        "IPL-1.0",
        "ISC",
        "Intel",
        "LGPL-2.1",
        "LGPL-3.0",
        "LPL-1.0",
        "LPL-1.02",
        "LPPL-1.3c",
        "LiLiQ-P-1.1",
        "LiLiQ-R+",
        "LiLiQ-R-1.1",
        "MIT",
        "MPL-1.0",
        "MPL-1.1",
        "MPL-2.0",
        "MS-PL",
        "MS-RL",
        "MirOS",
        "Motosoto",
        "Multics",
        "NASA-1.3",
        "NCSA",
        "NGPL",
        "NPOSL-3.0",
        "NTP",
        "Naumen",
        "Nokia",
        "OCLC-2.0",
        "OFL-1.1",
        "OGTSL",
        "OPL-2.1",
        "OSL-1.0",
        "OSL-2.1",
        "OSL-3.0",
        "PHP-3.0",
        "PostgreSQL",
        "Python-2.0",
        "QPL-1.0",
        "RPL-1.1",
        "RPL-1.5",
        "RPSL-1.0",
        "RSCPL",
        "SISSL",
        "SPL-1.0",
        "Simple-2.0",
        "Sleepycat",
        "UPL",
        "VSL-1.0",
        "W3C",
        "WXwindows",
        "Watcom-1.0",
        "Xnet",
        "ZPL-2.0",
        "Zlib",
        "jabberpl",
    ]
    for osi_license in licenses_to_check:
        assert osi_license in approved_licenses
    assert len(licenses_to_check) <= len(approved_licenses)
    assert len(set(approved_licenses)) <= len(approved_licenses)


@pytest.mark.online
def test_get_real_github_licenses(test_real_repo):
    try:
        license = test_real_repo.license
        license_id = license.get_github_license()
        assert license_id is not None
        assert len(license_id) > 0
        assert license_id in "MIT"
        return
    except SystemExit as e:
        assert e.code == -127


@pytest.mark.online
def test_check_real_github_osi_license(test_real_repo):
    try:
        license = test_real_repo.license
        approved_licenses = license.get_osi_approved_licenses()
        license_id = license.get_github_license()
        false_license_id = "HELLO"
        assert license_id is not None
        assert license_id in approved_licenses
        assert false_license_id not in approved_licenses
        return
    except SystemExit as e:
        assert e.code == -127


@pytest.mark.online
def test_check_real_github_osi_license_bad_credentials(test_real_repo):
    old_value = os.environ["GITHUB_TOKEN"]
    os.environ["GITHUB_TOKEN"] = "MYTOK"

    with pytest.raises(SystemExit) as exc_info:
        license = test_real_repo.license
        license.get_github_license()

    assert exc_info.value.code == -126
    os.environ["GITHUB_TOKEN"] = old_value


@pytest.fixture(scope="module")
def test_repo():
    current_path = Path(__file__).parent.absolute()
    url = "https://github.com/brainglobe/brainreg-napari"
    return NapariPlugin(current_path / "resources" / "licenses" / "repo_example1", url)


def test_license(test_repo):
    license = test_repo.license
    assert license is not None


@mock.patch("napari_hub_cli.fs.license.requests.get")
def test_get_osi_approved_licenses(mock_get, test_repo):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [
        {"name": "MIT License", "id": "MIT"},
        {"name": "GNU General Public License v3.0", "id": "GPL-3.0"},
    ]
    license = test_repo.license
    assert license.get_osi_approved_licenses() == ["MIT", "GPL-3.0"]
    mock_get.assert_called_once_with("https://api.opensource.org/licenses/")


@mock.patch("napari_hub_cli.fs.license.requests.get")
def test_get_github_license(mock_get, test_repo):
    license = test_repo.license
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"license": {"spdx_id": "MIT"}}
    assert license.get_github_license() == "MIT"
    # mock_get.assert_called_once_with(
    #     "https://api.github.com/repos/brainglobe/brainreg-napari/license"
    # )


def test_is_osi_approved_true(test_repo):
    license = test_repo.license
    with mock.patch.object(license, "get_github_license", return_value="MIT"):
        with mock.patch.object(
            license, "get_osi_approved_licenses", return_value=["MIT"]
        ):
            assert license.is_osi_approved is True


def test_is_osi_approved_false(test_repo):
    license = test_repo.license
    with mock.patch.object(license, "get_github_license", return_value="GPL-3.0"):
        with mock.patch.object(
            license, "get_osi_approved_licenses", return_value=["MIT"]
        ):
            assert license.is_osi_approved == False


def test_access_gh_token():
    old_value = os.environ["GITHUB_TOKEN"]

    os.environ["GITHUB_TOKEN"] = "MYTOK"

    assert read_gh_token() == "MYTOK"
    assert build_gh_header() == {
        'Authorization': 'Bearer MYTOK'
    }

    del os.environ["GITHUB_TOKEN"]

    assert read_gh_token() is None
    assert build_gh_header() == {}

    os.environ["GITHUB_TOKEN"] = old_value

