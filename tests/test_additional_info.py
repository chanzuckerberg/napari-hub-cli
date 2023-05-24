from pathlib import Path
from datetime import datetime
import pytest
from napari_hub_cli.fs import NapariPlugin


@pytest.fixture(scope="module")
def test_real_repo():
    current_path = Path(__file__).parent.absolute()
    return NapariPlugin(current_path / "resources" / "licenses" / "repo_example1")


@pytest.mark.online
def test_existent_cli_tool_version(test_real_repo):
    # Test the get_cli_tool_version value
    additional_info = test_real_repo.additional_info
    cli_tool_version = additional_info.get_cli_tool_version
    assert cli_tool_version is not None


@pytest.mark.online
def test_get_cli_tool_version(test_real_repo):
    # Test the get_cli_tool_version property
    additional_info = test_real_repo.additional_info
    cli_tool_version = additional_info.get_cli_tool_version
    assert isinstance(cli_tool_version, str)


@pytest.mark.online
def test_timestamp(test_real_repo):
    # Test the timestamp property
    additional_info = test_real_repo.additional_info
    formatted_date = additional_info.timestamp
    assert isinstance(formatted_date, str)
    assert formatted_date.startswith(datetime.now().strftime("%d %b %Y"))


@pytest.mark.online
def test_existent_timestamp(test_real_repo):
    # Test the timestamp value
    additional_info = test_real_repo.additional_info
    timestamp = additional_info.timestamp
    assert timestamp is not None
    assert '202' in timestamp


@pytest.mark.online
def test_inherited_properties(test_real_repo):
    # Test the inherited properties from RepositoryFile
    additional_info = test_real_repo.additional_info
    assert additional_info.exists is not None
    assert isinstance(additional_info.exists, bool)