from unittest import mock
from napari_hub_cli.fs import NapariPlugin
from napari_hub_cli.fs.license import License
import tempfile
from pathlib import Path

import pytest
import requests_mock
import json
from .config_enum import CONFIG, DEMO_GITHUB_REPO

RESOURCES = Path(__file__).parent / "resources"
MOCK_REQUESTS = None



@pytest.fixture(scope="module")
def test_real_repo():
    current_path = Path(__file__).parent.absolute()
    url = 'https://github.com/brainglobe/brainreg-napari'
    return NapariPlugin(current_path / "resources" / "licenses", url)

    
def test_get_real_osi_licenses(test_real_repo):
    license = test_real_repo.license
    print(dir(license))
    approved_licenses = license.get_osi_approved_licenses()
    print(approved_licenses)
    license_id = license.get_github_license()
    
    assert 'AAL' in approved_licenses
    assert 'AFL-3.0' in approved_licenses
    assert license_id is not None
    assert license_id in approved_licenses

    # def test_get_real_github_license(self, test_real_repo):
    #     license = test_real_repo.license
    #     print(license.get_osi_approved_licenses())
    #     assert license.get_github_license() in license.get_osi_approved_licenses()


    # def test_real_is_osi_approved(self, test_real_repo):
    #     license = test_real_repo.license
    #     assert license.is_osi_approved



@pytest.fixture(scope="module")
def test_repo():
    current_path = Path(__file__).parent.absolute()
    url = 'https://github.com/brainglobe/brainreg-napari'
    return NapariPlugin(current_path / "resources" / "licenses"/"repo_example1", url)


def test_license(test_repo):
    license = test_repo.license
    assert license is not None


@mock.patch('napari_hub_cli.fs.license.requests.get')
def test_get_osi_approved_licenses(mock_get, test_repo):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [
        {'name': 'MIT License', 'id': 'MIT'},
        {'name': 'GNU General Public License v3.0', 'id': 'GPL-3.0'}
    ]
    license = test_repo.license
    assert license.get_osi_approved_licenses() == ['MIT', 'GPL-3.0']
    mock_get.assert_called_once_with('https://api.opensource.org/licenses/')


@mock.patch('napari_hub_cli.fs.license.requests.get')
def test_get_github_license(mock_get, test_repo):
    license = test_repo.license
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'license': {'spdx_id': 'MIT'}}
    assert license.get_github_license() == 'MIT'
    mock_get.assert_called_once_with(
        'https://api.github.com/repos/brainglobe/brainreg-napari/license')


def test_is_osi_approved_true(test_repo):
    license = test_repo.license
    with mock.patch.object(license, 'get_github_license', return_value='MIT'):
        with mock.patch.object(license, 'get_osi_approved_licenses', return_value=['MIT']):
            assert license.is_osi_approved is True


def test_is_osi_approved_false(test_repo):
    license = test_repo.license
    with mock.patch.object(license, 'get_github_license', return_value='GPL-3.0'):
        with mock.patch.object(license, 'get_osi_approved_licenses', return_value=['MIT']):
            assert license.is_osi_approved == False
