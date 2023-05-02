from setuptools import setup

local_scheme = {}

setup(
    use_scm_version={"local_scheme": local_scheme},
    entry_points={
        "napari.plugin": [
            "naparij = napari_j",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Framework :: napari",
    ],
    setup_requires=["setuptools_scm"],
    install_requires=[
        "JPype1>=1.2.1",
        "matplotlib",
        "imageio_ffmpeg",
    ],
)
