import ast
import sys
import inspect


tree = ast.parse(inspect.getsource(sys.modules[__name__]))
print(tree)