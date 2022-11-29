import os
from contextlib import suppress

import pytest
import requests_mock as req
from xdg import xdg_config_home

from napari_hub_cli.autofix import read_user_token, validate_plugin_selection
from napari_hub_cli.constants import NAPARI_HUB_API_URL


@pytest.fixture
def napari_hub(requests_mock):
    requests_mock.get(
        req.ANY,
        json={},
    )
    requests_mock.get(
        NAPARI_HUB_API_URL,
        json={
            "avidaq": "0.0.5",
            "mikro-napari": "0.1.49",
            "napari-curtain": "0.1.1",
        },
    )
    requests_mock.get(
        f"{NAPARI_HUB_API_URL}/avidaq",
        json={"code_repository": "http://github.com/user1/avidaq"},
    )
    requests_mock.get(
        f"{NAPARI_HUB_API_URL}/mikro-napari",
        json={"code_repository": "http://github.com/user1/mikro-napari"},
    )
    requests_mock.get(
        f"{NAPARI_HUB_API_URL}/napari-curtain",
        json={"code_repository": "http://github.com/user2/napari-curtain"},
    )
    return requests_mock


def setup_module(module):
    with suppress(KeyError):
        module.GITHUB_USER = os.environ["GITHUB_USER"]
        del os.environ["GITHUB_USER"]

    with suppress(KeyError):
        module.GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
        del os.environ["GITHUB_TOKEN"]


def teardown_module(module):
    with suppress(KeyError, AttributeError):
        os.environ["GITHUB_USER"] = module.GITHUB_USER
        delattr(module, "GITHUB_USER")

    with suppress(KeyError, AttributeError):
        os.environ["GITHUB_TOKEN"] = module.GITHUB_TOKEN
        delattr(module, "GITHUB_TOKEN")


@pytest.fixture
def config_home():
    yield xdg_config_home() / "napari-hub-cli"
    with suppress(KeyError):
        del os.environ["GITHUB_TOKEN"]
    with suppress(KeyError):
        del os.environ["GITHUB_USER"]


def test_get_token_no_varenv(config_home):
    exist_config = (config_home / "config.yml").exists()

    with suppress(KeyError):
        del os.environ["GITHUB_TOKEN"]
    with suppress(KeyError):
        del os.environ["GITHUB_USER"]

    with pytest.raises(SystemExit) as e:
        read_user_token()

    assert e.type is SystemExit
    assert e.value.code == -1

    assert exist_config == (config_home / "config.yml").exists()


def test_get_token_username_token_inmem(config_home):
    exist_config = (config_home / "config.yml").exists()

    os.environ["GITHUB_TOKEN"] = "TOK"
    os.environ["GITHUB_USER"] = "ULOG"

    username, token = read_user_token()

    assert username == "ULOG"
    assert token == "TOK"

    assert exist_config == (config_home / "config.yml").exists()


def test_get_token_only_token_inmem_user_input(tmp_path, monkeypatch):
    home_config = tmp_path
    config_file = home_config / "config.yml"

    monkeypatch.setattr("builtins.input", lambda _: "USER")

    assert config_file.exists() is False

    os.environ["GITHUB_TOKEN"] = "TOK2"
    username, token = read_user_token(home_config=home_config)

    assert username == "USER"
    assert token == "TOK2"


def test_get_token_inmem_user_infile(tmp_path):
    home_config = tmp_path
    config_file = home_config / "config.yml"
    config_file.write_text(
        """---
gh_user: GHUSERNAME
"""
    )

    assert config_file.exists() is True

    os.environ["GITHUB_TOKEN"] = "TOK3"
    username, token = read_user_token(home_config=home_config)

    assert username == "GHUSERNAME"
    assert token == "TOK3"


def test_get_token_inmem_user_notinfile_file_exists(tmp_path, monkeypatch):
    home_config = tmp_path
    config_file = home_config / "config.yml"
    config_file.write_text("")

    monkeypatch.setattr("builtins.input", lambda _: "GHUSERWRITTEN")

    assert config_file.exists() is True

    os.environ["GITHUB_TOKEN"] = "TOK4"
    username, token = read_user_token(home_config=home_config)

    assert username == "GHUSERWRITTEN"
    assert token == "TOK4"


def test_plugin_selection(napari_hub):
    plugins = ["avidaq", "mikro-napari", "napari-curtain"]

    validation, result = validate_plugin_selection(plugins)

    assert validation is True
    assert len(result) == 3
    assert result["avidaq"] == "http://github.com/user1/avidaq"
    assert result["mikro-napari"] == "http://github.com/user1/mikro-napari"
    assert result["napari-curtain"] == "http://github.com/user2/napari-curtain"


def test_plugin_selection_missing(napari_hub):
    plugins = ["avidaq", "mikro-napari", "napari-curta"]

    validation, result = validate_plugin_selection(plugins)

    assert validation is False
    assert len(result) == 1
    assert result["napari-curta"] == "napari-curtain"
