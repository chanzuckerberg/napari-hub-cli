# napari-hub-cli



Command line utilities for inspecting and validating plugins for the napari hub.



# Installation

From your console, you can install the napari hub CLI through pip

```
$ pip install napari-hub-cli
```



# Usage 


## Documentation Checklist

The intent of this utility is to check your plugin for specific metadata in the Napari-Hub recommended file locations.
With this, it creates a Documentation Checklist identifying if a plugin has the following metadata:

- Display Name
- Summary Sentence
- Intro Paragraph
- Intro Video
- Intro Scrennshot
- Usage Section
- Installation section
- Source Code Link
- User Support Link
- Bug Tracker Link
- Author
- Citation

Additionally, the recommended file locations for each metadata are suggested in different cases:

- when the metadata is not found in either the Napari recommended file location and a fallback file location
- when the metadata is not found at the Napari recommended file location

To create the Napari Documentation Checklist for your plugin there are two alternatives:

- creating the Documentation Checklist from the local plugin path, useful before a release
- creating the Documentation Checklist from the remote plugin path, requiring the plugin to be released into Napari-Hub

For the first, the command used to create the Documentation Checklist is
```
 $ napari-hub-cli create-doc-checklist /tmp/example-plugin 
```

while for the latter, the command used to create the Documentation Checklist is

```
 $ napari-hub-cli check-plugin example-plugin 
```

having first installed all the requirements for napari-hub-cli.

Below you can find a table with the Napari recommended file locations and fallback files where the metadata is checked:


Metadata / Files | Recommended File | Fallback File(s) 
--- | --- | --- | 
Display Name | ```npe2 - napari.manifest``` | ```PyPI```
Summary Sentence | ```napari-hub/config.yml``` | ```PyPI``` 
Intro Paragraph | ```napari-hub/description.md``` | ```PyPI``` 
Intro Video | ```napari-hub/description.md``` | ```PyPI``` 
Intro Screenshot | ```napari-hub/description.md``` | ```PyPI``` 
Usage Section | ```napari-hub/description.md``` | ```PyPI``` 
Source Code Link | ```PyPI``` | ```n/a```  
User Support Link | ```PyPI``` | ```n/a```  
Bug Tracker Link | ```PyPI``` | ```n/a```  
Author | ```PyPI``` | ```n/a```  
Citation | ```CITATION.cff``` | ```n/a```  


Example output (with all possible scenarios):

<img width="556" alt="Screenshot at Nov 15 18-32-57" src="https://user-images.githubusercontent.com/99416933/201911155-71871012-8afb-4161-bd84-1794b3cd4735.png">




## Citation

This utility works by looking into:

- GitHub Repository metadata
- ```README.md```

and creating a ```CITATION.CFF```, a plain text file with human- and machine-readable citation information for software and datasets.

For citations to be parsed from the ```README.md``` these need to have either the **APA**(American Psychological Association) style or **BibTex** style format.

The ```CITATION.CFF``` file naming needs to be as it is, otherwise GitHub won't recognize it as a citation file.

To create the CITATION.CFF for your plugin run
```
 $ napari-hub-cli create-cff-citation /tmp/example-plugin 
```
having first installed all the requirements for napari-hub-cli.

The format for the CITATION.CFF is the following:

- The first citation that appears references the software
- The preffered citation, the one used in GitHub, references an article/publisher, preferring an article citation when both exist
- when both article and publisher information exist, publisher information is written as a sub-reference


### Citation references


Below you can find some examples of how to use the CITATION.CFF.

Referencing other work:
```
authors:
  - family-names: Druskat
    given-names: Stephan
cff-version: 1.2.0
message: "If you use this software, please cite it using these metadata."
references:
  - authors:
      - family-names: Spaaks
        given-names: "Jurriaan H."
    title: "The foundation of Research Software"
    type: software
  - authors:
      - family-names: Haines
        given-names: Robert
    title: "Ruby CFF Library"
    type: software
    version: 1.0
title: "My Research Software"
```

Credit Redirection:

```
authors:
  - family-names: Druskat
    given-names: Stephan
cff-version: 1.2.0
message: "If you use this software, please cite both the article from preferred-citation and the software itself."
preferred-citation:
  authors:
    - family-names: Druskat
      given-names: Stephan
  title: "Software paper about My Research Software"
  type: article
title: "My Research Software"
```

Some more information regarding .CFF can be found here https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files 


## Plugins Metadata Report

 Generates a CSV report with consistency analysis of all plugins in the Napari-HUB platform.

 To create the CSV report run

 ```
 $ napari-hub-cli all-plugins-report report_csv
 ```
having ```report_csv``` as the name of the generated file.

The generated report contains all the documentation checklist information for each of the repositories.
You can find an example below:

image.png


Note that some of the repositories are not accessible, being identified with 
- ```BAD_URL```, where the repository URL provided has the wrong format
- ```MISSING_URL```, where no source code information was provided in the Napari-HUB platform
- ```UNACCESSIBLE_REPOSITORY```, where the source code page could not be found or is a private repository


## Autofix Metadata

`napari-hub-cli` comes with various features.
One of them scans remote plugin repositories and checks how metadata could be improved: _i.e_, checking that all required metadata are present and that they are located in a primary source configuration file.
In addition to this feature, `napari-hub-cli` can also automatically fix some metadata or more (_e.g._, `CITATION.cff` file creation) and report the other missing features.
The fixed files are then proposed to the owner of a plugin repository in the form of a Github pull request, and missing/non-autofixeable metadata are reported in the form of a Github issue.

The subcommand for this feature is `autofix`, it takes various options:

```
usage: napari-hub-cli autofix [-h] [-p PLUGINS [PLUGINS ...]] [-d DIR] [-a] [--dry-run]

options:
  -h, --help            show this help message and exit
  -p PLUGINS [PLUGINS ...], --plugins PLUGINS [PLUGINS ...]
                        List of plugins name to automatically audit/fix
  -d DIR, --dir DIR     Working directory in which plugins will be cloned (by default the tmp directory of your OS)
  -a, --all             Passing on all plugins registed in Napari-HUB plateform
  --push-on-github      Perform the analysis/commit and creates pull request/issue on Github
```

Here, the most important options to use are:

* `--push-on-github` to perform the analysis and actually creating the PR/issue (by default, this option is set to `False`),
* `-p` to give a list of plugin names to analyse,
* `--dir` to tell the tool where to clone all repositories.

For the `--dir` option, if the option is not set, a directory in the temporary directory of your system is used (_e.g._, a directory in `/tmp` for UNIX systems).

For more information on this command, please see the detailed documentation here https://gist.github.com/aranega/8dc2a1bf46f880071c21e3d4db078b1b .


### Dry Run

The tool is able to perform the automatic modification of the base code without actually creating the pull-requests or the issues.
To let you inspect what will be done, it only clones the repository to scan, perform the various commits, but does not delete the cloned repository after analysis until you press the `enter` key.

It also displays in the terminal the pull-requests and issue messages that will be created (using `USERNAME` and `PRID` as substitutes for your name and the pull request ID), and stops after each repository analysis.

Here is an example of how to perform a dry run over `affinder` and `PartSeg` plugins:

```sh
napari-hub-cli autofix --dir /tmp/cloned -p affinder PartSeg
```


### Automatic creation of pull-requests and issues

Creating automatically the pull-requests and the issues requires a small setup and slightly changes the way the tool need to be called.
Technically, the operations performed in Github will be:

* forking the analysed plugin repository,
* creating a pull request if necessary,
* creating an issue if necessary.

As any operation that would require an access to the Github API, it's necessary to get a personal accesss token.
For security reasons this token is not stored by the tool, nor serialized in a file on your file system (it let you this responsibility).

Now, considering that you have your token saved in this location `/tmp/gh_token.tok`, with your handle being `foo` here is how to call the autofix feature without creating config file:

```bash
GITHUB_TOKEN=$(cat gh-token.log) GITHUB_USER=foo napari-hub-cli autofix --dir /tmp/cloned -p affinder PartSeg --push-on-github
```

## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](https://github.com/chanzuckerberg/.github/blob/master/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [opensource@chanzuckerberg.com](mailto:opensource@chanzuckerberg.com).
