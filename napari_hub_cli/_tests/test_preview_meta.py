# Test fixture for generating temp directories
    # could take any combination of 
    # .napari/DESCRIPTION.md, .napari/config.yml, setup.py, setup.cfg
# It just puts together temp directories with those files
    # our test directory will need example files
        # write some manually
import pytest
from .config_enum import CONFIG
@pytest.fixture
def make_pkg_dir(tmpdir, request):
    fn_arg_marker = request.node.get_closest_marker("required_configs")
    if fn_arg_marker:
        print(fn_arg_marker.args[0])
    else:
        print("Not Given Data")


@pytest.mark.required_configs([CONFIG.YML])
def test_config_yml(make_pkg_dir):
    assert False


# test fixture for different version options?

# test reading yml config separately
    # containing authors
    # not containing authors
    # containing some urls but not all
    # containing different urls

# test reading setup cfg separately
    # a few combinations of simple metadata
    # all options for complex metadata

# test reading setup py separately
    # a few combinations of simple metadata
    # all options for complex metadata

# version reading should be separate

# test not overriden once set

# test source ?