import logging
from functools import partial

from pip._internal.cli.cmdoptions import make_target_python
from pip._internal.commands.install import InstallCommand
from pip._internal.index.package_finder import PackageFinder
from pip._internal.operations.build.build_tracker import get_build_tracker
from pip._internal.operations.prepare import RequirementPreparer
from pip._internal.req.constructors import install_req_from_req_string
from pip._internal.req.req_set import RequirementSet
from pip._internal.resolution.resolvelib.provider import PipProvider
from pip._internal.resolution.resolvelib.reporter import PipReporter
from pip._internal.resolution.resolvelib.resolver import Resolver
from pip._internal.utils.temp_dir import (
    TempDirectory,
    global_tempdir_manager,
    tempdir_registry,
)
from pip._vendor.resolvelib import ResolutionImpossible
from pip._vendor.resolvelib import Resolver as RLResolver


class MyResolver(Resolver):
    def resolve(self, root_reqs, check_supported_wheels):
        collected = self.factory.collect_root_requirements(root_reqs)
        provider = PipProvider(
            factory=self.factory,
            constraints=collected.constraints,
            ignore_dependencies=self.ignore_dependencies,
            upgrade_strategy=self.upgrade_strategy,
            user_requested=collected.user_requested,
        )
        reporter = PipReporter()
        resolver = RLResolver(provider, reporter)

        try:
            limit_how_complex_resolution_can_be = 200000
            result = self._result = resolver.resolve(
                collected.requirements, max_rounds=limit_how_complex_resolution_can_be
            )

        except ResolutionImpossible as e:
            error = self.factory.get_installation_error(
                e,
                collected.constraints,
            )
            raise error from e

        req_set = RequirementSet(check_supported_wheels=check_supported_wheels)
        for candidate in result.mapping.values():
            ireq = candidate.get_install_requirement()
            if ireq is None:
                continue
            req_set.add_named_requirement(ireq)
        return req_set, result


class DependencySolver(InstallCommand):
    def __init__(self, name, summary):
        super().__init__(name, summary)
        self.verbosity = 0

    @classmethod
    def make_resolver(
        cls,
        preparer: RequirementPreparer,
        finder: PackageFinder,
        options,
        wheel_cache=None,
        use_user_site: bool = False,
        ignore_installed: bool = True,
        ignore_requires_python: bool = False,
        force_reinstall: bool = False,
        upgrade_strategy: str = "to-satisfy-only",
        use_pep517=None,
        py_version_info=None,
    ):
        make_install_req = partial(
            install_req_from_req_string,
            isolated=options.isolated_mode,
            use_pep517=use_pep517,
        )
        return MyResolver(
            preparer=preparer,
            finder=finder,
            wheel_cache=wheel_cache,
            make_install_req=make_install_req,
            use_user_site=use_user_site,
            ignore_dependencies=options.ignore_dependencies,
            ignore_installed=ignore_installed,
            ignore_requires_python=ignore_requires_python,
            force_reinstall=force_reinstall,
            upgrade_strategy=upgrade_strategy,
            py_version_info=py_version_info,
        )

    def resolve(self, packages, options):
        self.tempdir_registry = self.enter_context(tempdir_registry())
        self.enter_context(global_tempdir_manager())
        # level_number = setup_logging(
        #     verbosity=logging.DEBUG,
        #     no_color=options.no_color,
        #     user_log_file=options.log,
        # )
        # logging.disable(logging.WARNING)

        session = self.get_default_session(options)

        target_python = make_target_python(options)
        finder = self._build_package_finder(
            options=options,
            session=session,
            target_python=target_python,
            ignore_requires_python=options.ignore_requires_python,
        )

        build_tracker = self.enter_context(get_build_tracker())

        directory = TempDirectory(
            delete=not options.no_clean,
            kind="install",
            globally_managed=True,
        )

        reqs = self.get_requirements(packages, options, finder, session)

        preparer = self.make_requirement_preparer(
            temp_build_dir=directory,
            options=options,
            build_tracker=build_tracker,
            session=session,
            finder=finder,
            use_user_site=options.use_user_site,
            verbosity=self.verbosity,
        )
        resolver = self.make_resolver(
            preparer=preparer,
            finder=finder,
            options=options,
            use_user_site=options.use_user_site,
            ignore_installed=options.ignore_installed,
            ignore_requires_python=options.ignore_requires_python,
            force_reinstall=options.force_reinstall,
            use_pep517=options.use_pep517,
        )

        _, res = resolver.resolve(reqs, check_supported_wheels=not options.target_dir)
        return res

    def solve_dependencies(self, *args, **kwargs):
        logger = logging.getLogger("pip._internal.cli.req_command")
        logger.disabled = True
        logging.shutdown()
        with self.main_context():
            return self.resolve(*args, **kwargs)
