from pathlib import Path

import pytest

from napari_hub_cli.dependencies_solver.checker import (
    NO_DEPENDENCIES,
    InstallationRequirements,
)
from napari_hub_cli.dependencies_solver.solver import DependencySolver
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

    assert len(reqs.options_list) == 3
    result = reqs.solve_dependencies(options=reqs.options_list[0])
    assert result

    result = reqs.solve_dependencies(options=reqs.options_list[1])
    assert result

    result = reqs.solve_dependencies(options=reqs.options_list[2])
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


@pytest.mark.online
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
    try:
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
    except Exception:
        pytest.skip("Fails when executed on some windows version")


@pytest.mark.online
def test_requirements_integration2():
    reqs = InstallationRequirements(
        path=None,
        python_versions=((3, 10),),
        requirements=["lxml==4.9.2"],
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
        requirements=["numpy>=2.0", "panda<=1.0"],
        platforms=["linux"],
    )

    assert reqs.installable_linux is False
    assert reqs.number_of_dependencies == NO_DEPENDENCIES
    assert reqs._installation_issues

    assert len(reqs._installation_issues) == 3

    info = next(iter(reqs._installation_issues.values()))
    assert "No matching distribution found for numpy>=2.0" in info[0]

    info = next(iter(reqs._installation_issues.values()))
    assert "No matching distribution found for numpy>=2.0" in info[0]

    info = next(iter(reqs._installation_issues.values()))
    assert "No matching distribution found for numpy>=2.0" in info[0]


from pip._internal.exceptions import DistributionNotFound, InstallationSubprocessError, MetadataGenerationFailed, InstallationError

class FakeRaiseException(DependencySolver):
    def __init__(self, exception):
        def inner(*args, **kwargs):
            print("RAISE", exception)
            raise exception
        self.solve_dependencies = inner


class FakeOption(object):
    def __init__(self, version, platforms):
        self.python_version = version
        self.platforms = platforms


@pytest.mark.online
def test_solver_messages():
    reqs = InstallationRequirements(
        path=None,
        python_versions=((3, 10),),
        requirements=["numpy>=2.0", "panda<=1.0"],
        platforms=["linux"],
    )

    reqs.solver = FakeRaiseException(DistributionNotFound("_foo"))
    reqs.solve_dependencies(FakeOption(((3, 7),),  ["linux"]))
    assert "transitive dependency cannot be resolved" in reqs.installation_issues
    assert "_foo" in reqs.installation_issues

    reqs = InstallationRequirements(
        path=None,
        python_versions=((3, 10),),
        requirements=["numpy>=2.0", "panda<=1.0"],
        platforms=["linux"],
    )
    reqs.solver = FakeRaiseException(InstallationSubprocessError(command_description="d", exit_code=1, output_lines=None))
    reqs.solve_dependencies(FakeOption(((3, 7),),  ["win"]))
    assert "occured in a sub-process" in reqs.installation_issues

    reqs = InstallationRequirements(
        path=None,
        python_versions=((3, 10),),
        requirements=["numpy>=2.0", "panda<=1.0"],
        platforms=["linux"],
    )
    reqs.solver = FakeRaiseException(MetadataGenerationFailed(package_details="_bar"))
    reqs.solve_dependencies(FakeOption(((3, 7),),  ["linux"]))
    assert "while building one of the dependencies" in reqs.installation_issues
    assert "_bar" in reqs.installation_issues

    reqs = InstallationRequirements(
        path=None,
        python_versions=((3, 10),),
        requirements=["numpy>=2.0", "panda<=1.0"],
        platforms=["linux"],
    )
    reqs.solver = FakeRaiseException(InstallationError)
    reqs.solve_dependencies(FakeOption(tuple(),  ["macos"]))
    assert "while installing this dependency" in reqs.installation_issues

    reqs = InstallationRequirements(
        path=None,
        python_versions=((3, 10),),
        requirements=["numpy>=2.0", "panda<=1.0"],
        platforms=["linux"],
    )
    reqs.solver = FakeRaiseException(Exception)
    reqs.solve_dependencies(FakeOption(tuple(),  ["linux"]))
    assert reqs.installation_issues == "No information"
