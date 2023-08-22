# CHANGELOG

## 1.0.0

This release uses a new endpoint and drop the support for the old endpoint that was used before to query the napari plugin platform.

### List

* Change endpoint for napari plugin queries
* Change the dependency resolution to consider the all platforms

## 0.3.1

This release introduce a patch to overcome a known bug of pip that will be patched in future versions.

## 0.3.0

This release introduce new checks included in the command that checks the quality of a plugin as well as some performances improvements

### List

* Add support for sections in the displayed report
* Split some sections in sub-sections
* Add general "pass/fail" results by section
* Reorganize information for CSV display
* Add overview of installation issues
* Change title for bundle support in progress bar
* Add different title for the linux installation in progress bar

* Check display name only in npe2 file
* Add ability to parse/check source code written in Python for a version superior to the Python's version running the tool
* Add support for hatch backend
* Add preliminary support for poetry
* Add distinction and insights of failing tests
* Add default value to "all platforms" for dependency solver
* Change way of computing version number
* Add nox support for tests discovery
* Add ABI to the dependency solver

* Add warning message when the tool is run without GH token
* Add force clean of tmp directories

* Add progress bar on sub-tasks
* Fix progress bar disapearing

* Add special tag for napari user-agent installations

## 0.2.0

This release introduce a new command to check the "quality" of a plugin or a set of plugins on various criterias

### List

* Use of GH token systematically if possible for questionning Github API
* Addition of `check-quality` and `check-plugin-quality` commands to check about the quality of a plugin (dependencies, npe1/2 hooks, ...)
    * Analyse plugin dependencies (direct and transitive using pip) for forbidden dependencies, C extensions, installability
    * Check codecov coverage
    * Check test success/failure
    * Report installability issues
    * Check license
    * Check Python code for forbidden imports and hook usage
    * Check bundle installability
* Introduction of a new abstraction for checklist definition (currently, a checklist for metadata and one for plugin quality)
* Introduction of a new abstraction for computing and displaying additional information in checklist
* Switch some primary/secondary files in the metadata checklist


## 0.1.0

### Summary

This release introduce new versions of the previous existing commands as well as new commands to automatically create some files.

### List

* Refactor code of old commands. Available commands are now:
    * `check-metadata` to check the consistency of a plugin in the file system
* Add a command to automatically create a `CITATION.cff` file for a plugin in the file system (`create-citation`)
* Introduce new abstraction to help in further developments
* Update and add new unit tests
* Update base code
* Update interaction with github action
