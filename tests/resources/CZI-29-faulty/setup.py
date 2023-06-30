from setuptools import setup

local_scheme = {}

setup(
    use_scm_version={"local_scheme": local_scheme},
    entry_points={
        "napari.plugin": [
            "naparij = napari_j",
        ],
    },
    setup_requires=["setuptools_scm"],
    install_requires=[
        "JPype1>=1.2.1",
        "matplotlib",
        "imageio_ffmpeg",
        "pyqt5-notificator ",
    ],
)
