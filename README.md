# napari-hub-cli

**This package is not being updated or maintained with the latest napari hub metadata. To view a preview of your plugin listing for the napari hub, we recommend using the [napari hub preview page service](https://github.com/chanzuckerberg/napari-hub/blob/main/docs/setting-up-preview.md).**

Command line utilities for inspecting and validating plugins for the napari hub.

# Installation

From your console, you can install the napari hub CLI through pip

```
$ pip install napari-hub-cli
```

# Usage (**Not Maintained**)

## Metadata

This package provides two utilities for previewing and validating the metadata we 
will inspect from your plugin and display on the napari hub. 

### Previewing Metadata

```
$ napari-hub-cli preview-metadata /tmp/example-plugin
```

or

```
# display one field at a time and wait for input
$ napari-hub-cli preview-metadata /tmp/example-plugin -i
```

This utility will inspect the plugin at the given path for metadata and display it for preview.

Each field of metadata is accompanied by the file and attribute where it was found.
When fields are missing, they are accompanied instead by a suggested source.
When a field is sourced from `setup.py`, it is always an argument to the `setup` method.

**Version** - Depending on how you manage versioning for your package, we may not be able to
parse its latest version. The version of your package displayed on
the napari hub will always be the latest version released on PyPI.

**Project Site** - If your `url` or `Project Site` metadata is a GitHub url, 
it will be displayed as the Source Code field instead.

Example output:

```
--------------------------------------------------------------------------------
Authors
--------------------------------------------------------------------------------
Draga Doncila Pop
        ------
        Source
        ------
        /setup.cfg: metadata, author

--------------------------------------------------------------------------------
Description
--------------------------------------------------------------------------------
This is my napari-hub specific description. It is detailed, and comprehensive.
        ------
        Source
        ------
        /.napari/DESCRIPTION.md

--------------------------------------------------------------------------------
Source Code
--------------------------------------------------------------------------------
https://github.com/DragaDoncila/example-plugin
        ------
        Source
        ------
        /.napari/config.yml: project_urls, Source Code

--------------------------------------------------------------------------------
Summary
--------------------------------------------------------------------------------
~~Not Found~~
        ------
        Suggested Source
        ------
        /setup.cfg: metadata, summary

--------------------------------------------------------------------------------
User Support
--------------------------------------------------------------------------------
https://github.com/DragaDoncila/example-plugin/issues
        ------
        Source
        ------
        /.napari/config.yml: project_urls, User Support
```

You can then use `check-missing` to get a display of just the missing metadata. 
See [Customizing Your Plugin Listing](https://github.com/chanzuckerberg/napari-hub/blob/main/docs/customizing-plugin-listing.md) for a detailed guide on how you can add this metadata
to your project.

### Checking Missing Metadata

```
$ napari-hub-cli check-missing /tmp/example-plugin
```
or
```
# display one field at a time and wait for input
$ napari-hub-cli check-missing /tmp/example-plugin -i
```

This utility will only display the metadata missing from your plugin, and will also suggest where you can add it.
All metadata listed here will be displayed on your plugin's napari hub page. When this metadata might also be used
for sorting, filtering or searching for plugins, this information is also displayed.

Example output:

```
--------------------------------------------------------------------------------
MISSING: Twitter
--------------------------------------------------------------------------------
        SUGGESTED SOURCE:       /.napari/config.yml: project_urls, Twitter

--------------------------------------------------------------------------------
MISSING: Summary
--------------------------------------------------------------------------------
        SUGGESTED SOURCE:       /setup.cfg: metadata, summary
        ------
        Used For
        ------
        Searching

```

For more information on how you can add metadata to your package, and how we use it on the napari hub, check out [Customizing Your Plugin Listing](https://github.com/chanzuckerberg/napari-hub/blob/main/docs/customizing-plugin-listing.md).

## Development Information

The main logic of metadata loading proceeds from the [`load_meta` function](https://github.com/chanzuckerberg/napari-hub-cli/blob/602811b19b11543179d5e22410759be2b305b0b6/napari_hub_cli/napari_hub_cli.py#L34), and each filetype has its own parsing
function. In addition, we use a [`parse_complex_metadata` function](https://github.com/chanzuckerberg/napari-hub-cli/blob/main/napari_hub_cli/napari_hub_cli.py#L137) to handle edge case parsing of certain fields that
may be found in `setup.py` and `setup.cfg`.

### Where do we look for metadata?

The source of truth for both reading metadata and suggesting its source locations is found in [metadata_sources.csv](https://github.com/chanzuckerberg/napari-hub-cli/blob/main/napari_hub_cli/resources/metadata_sources.csv).

Metadata can be found in the following files, with paths given from the root directory, 
and these files are preferentially searched in order:
- `.napari/config.yml`
        - Author information, project URLs
- `.napari/DESCRIPTION.md`
        - Long description
- `setup.cfg`
        - All packaging metadata and potentially long description (could also be a pointer to README.md)
- `setup.py`
        - All packaging metadata and potentially long description. Only used if `setup.cfg` is not present, or not complete.

In addition to these files, we may also search module `__init__.py` files and any `_version.py` files we find for the version number.

### Why so complex?

The main source of complexity for loading this metadata arises from the requirements:
- metadata needs to be parsed before the package is released, so we cannot rely on PyPI
- we prefer not to install the package into the active environment to read the metadata
- we would like to show users where their metadata is being read from, and where they can go to change it

These requirements mean we cannot just build a wheel/inspect package metadata from its distribution,
because its source file will then be irretrievable. As a result, we rely on inspecting
the contents of files individually, and parse `config.yml`, `setup.py` and `setup.cfg` independently.

## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](https://github.com/chanzuckerberg/.github/blob/master/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [opensource@chanzuckerberg.com](mailto:opensource@chanzuckerberg.com).
