import os
from contextlib import suppress

import pytest
from xdg import xdg_config_home

from napari_hub_cli.autofix import read_user_token


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
