import napari_hub_cli.dependencies_solver.pip_patch  as pippatch # This has to be set first as it patches "pip"
import pip._internal.network.session as session_module


def test_useragent_tag():
    tag = session_module.user_agent()

    assert pippatch.NAPARI_HUB_PIP_TAG in tag
