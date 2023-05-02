from pathlib import Path

import pytest

from napari_hub_cli.fs import NapariPlugin


@pytest.fixture(scope="module")
def resources():
    return Path(__file__).parent.absolute() / "resources"


def test_requirements_resolution(resources):
    plugin = NapariPlugin(resources / "CZI-29-test2")

    reqs = plugin.requirements
    assert len(reqs.requirements) == 3
    assert "numpy" in reqs.requirements
    assert "cython" in reqs.requirements
    assert "pyecore==0.13.1" in reqs.requirements

    assert len(reqs.options_list) == 2
    result = reqs.solve_dependencies(options=reqs.options_list[0])
    assert result

    result = reqs.solve_dependencies(options=reqs.options_list[1])
    assert result