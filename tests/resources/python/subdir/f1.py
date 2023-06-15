import ast
import sys
import inspect

import napari_plugin_engine as npe


tree = ast.parse(inspect.getsource(sys.modules[__name__]))
print(tree)



@npe.napari_hook_implementation(specname="napari_get_reader")
def whatever_name_you_want(path: str):
    ...
