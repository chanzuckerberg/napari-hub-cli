# CHANGELOG

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
*

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
