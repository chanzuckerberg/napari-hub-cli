# napari-hub-cli

Command line utilities for inspecting and validating plugins for the napari hub.

# Installation

From your console, you can install the napari hub CLI through pip

```
$ pip install napari-hub-cli
```

# Usage

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

You can then use `check-metadata` to get a display of just the missing metadata. 
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

## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](https://github.com/chanzuckerberg/.github/blob/master/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [opensource@chanzuckerberg.com](mailto:opensource@chanzuckerberg.com).
