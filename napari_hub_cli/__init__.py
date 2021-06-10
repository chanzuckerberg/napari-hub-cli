try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from .cli import main

__all__ = ["main"]
