from pathlib import Path

import pytest

from napari_hub_cli.dependencies_solver.checker import InstallationRequirements, NO_DEPENDENCIES
from napari_hub_cli.fs import NapariPlugin


@pytest.fixture(scope="module")
def resources():
    return Path(__file__).parent.absolute() / "resources"


@pytest.fixture(scope="module")
def plugin(resources):
    return NapariPlugin(resources / "CZI-29-test2")


@pytest.mark.online
def test_requirements_resolution(plugin):
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


@pytest.mark.online
def test_requirements_resolution_installable(plugin):
    reqs = plugin.requirements

    installable, all_wheel, c_exts, installed = reqs.analysis_package(
        options=reqs.options_list[0]
    )
    assert installable
    assert all_wheel
    assert len(c_exts) >= 2
    assert "lxml" in c_exts
    assert "numpy" in c_exts
    assert set(name for name, _ in installed) == {
        "numpy",
        "cython",
        "pyecore",
        "lxml",
        "ordered-set",
        "future-fstrings",
        "restrictedpython",
    }

    assert reqs.num_installed_packages(options=reqs.options_list[0]) == 7
    assert reqs.has_no_C_extensions_dependencies(options=reqs.options_list[0]) is False
    assert reqs.alldeps_wheel(options=reqs.options_list[0]) is True
    assert reqs.is_installable(options=reqs.options_list[0]) is True

    installable, all_wheel, c_exts, installed = reqs.analysis_package(
        options=reqs.options_list[1]
    )
    assert installable
    assert all_wheel
    assert len(c_exts) >= 2
    assert "lxml" in c_exts
    assert "numpy" in c_exts
    assert set(name for name, _ in installed) == {
        "numpy",
        "cython",
        "pyecore",
        "lxml",
        "ordered-set",
        "future-fstrings",
        "restrictedpython",
    }

    assert reqs.num_installed_packages(options=reqs.options_list[1]) == 7
    assert reqs.has_no_C_extensions_dependencies(options=reqs.options_list[1]) is False
    assert reqs.alldeps_wheel(options=reqs.options_list[1]) is True
    assert reqs.is_installable(options=reqs.options_list[1]) is True


def test_requirements_build():
    reqs = InstallationRequirements(
        path=None, requirements=["unexisfgs_nop", "pyecore"]
    )
    installable, all_wheel, c_exts, installed = reqs.analysis_package(
        options=reqs.options_list[0]
    )
    assert installable is False
    assert all_wheel is True
    assert c_exts == []
    assert installed == []

    assert reqs.had_no_unknown_error is True


@pytest.mark.online
def test_requirements_build_notallwheels():
    reqs = InstallationRequirements(path=None, requirements=["probreg"])
    installable, all_wheel, c_exts, installed = reqs.analysis_package(
        options=reqs.options_list[0]
    )
    assert installable is False
    assert all_wheel is True
    assert len(c_exts) == 0

    assert reqs.has_no_C_ext_macos is False
    assert reqs.has_no_C_ext_windows is False
    assert reqs.has_no_C_ext_linux is False

    assert reqs.installable_linux is False
    assert reqs.installable_windows is False
    assert reqs.installable_macos is False

    assert reqs.allwheel_linux is False
    assert reqs.allwheel_macos is False
    assert reqs.allwheel_windows is False


@pytest.mark.online
def test_requirements_integration():
    reqs = InstallationRequirements(
        path=None, requirements=["numpy"], platforms=["win", "linux", "macos"]
    )
    assert reqs.installable_linux is True
    assert reqs.installable_windows is True
    assert reqs.installable_macos is True

    assert reqs.has_no_C_ext_windows is True
    assert reqs.has_no_C_ext_linux is True
    assert reqs.has_no_C_ext_macos is True

    assert reqs.allwheel_linux is True
    assert reqs.allwheel_macos is True
    assert reqs.allwheel_windows is True


@pytest.mark.online
def test_requirements_integration2():
    reqs = InstallationRequirements(
        path=None,
        python_versions=((3, 10),),
        requirements=["lxml"],
        platforms=["win", "linux", "macos"],
    )

    assert reqs.installable_linux is True
    assert reqs.installable_windows is True
    assert reqs.installable_macos is True

    assert reqs.has_no_C_ext_windows is False
    assert reqs.has_no_C_ext_linux is False
    assert reqs.has_no_C_ext_macos is False

    assert reqs.allwheel_linux is True
    assert reqs.allwheel_macos is True
    assert reqs.allwheel_windows is True


def test_platform_support(plugin):
    reqs = plugin.requirements
    assert reqs.has_windows_support is True
    assert reqs.has_linux_support is True
    assert reqs.has_macos_support is False


@pytest.mark.online
def test_requirements_installability():
    reqs = InstallationRequirements(path=None, requirements=["probreg"])
    assert reqs.installable_linux is False
    assert reqs.installable_windows is False
    assert reqs.installable_macos is False

    reqs = InstallationRequirements(
        path=None,
        requirements=["triton"],
        python_versions=((3, 9),),
        platforms=("win", "linux", "macos"),
    )

    assert reqs.installable_linux is True
    assert reqs.installable_windows is False
    assert reqs.installable_macos is False


@pytest.mark.online
def test_nodeps_message():
    reqs = InstallationRequirements(
        path=None,
        python_versions=((3, 10),),
        requirements=[
            "numpy>=2.0",
            "panda<=1.0"
        ],
        platforms=["linux"],
    )

    assert reqs.installable_linux is False
    assert reqs.number_of_dependencies == NO_DEPENDENCIES