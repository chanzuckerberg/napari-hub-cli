# napari-hub-cli

Command line utilities for inspecting and validating plugins for the napari hub.

The ```extra``` branch is intended for an administrative user, gaining access to the following additional commands

- ```check-plugin``` - create a documentation checklist for a remote plugin.
- ```autofix``` - automatically creating pull requests and issues that fix some of the concerns addressed by the documentation checklist.
- ```all-plugins-report``` - create a csv report with the documentation information for all existent plugins in the napari hub platform
- ```check-plugin-quality``` - create a report with the code quality information for a remote plugin.

## Supported operating systems

The tool works on Linux and MacOS without issue. On Windows, the tool works without issue in the Windows Subsystem for Linux (WSL) but there is a known issue in Windows without WSL - the result from the plugin installation check is flaky. See [this issue](https://github.com/chanzuckerberg/napari-hub-cli/issues/135) for more details.

To set up WSL, follow the instructions [here](https://learn.microsoft.com/en-us/windows/wsl/install). With WSL set up, you can run the tool from the WSL terminal following the instructions below.

## Installation

First the repository needs to be cloned

```sh
git clone https://github.com/chanzuckerberg/napari-hub-cli.git
cd napari-hub-cli
git checkout extra
```

As any python program, it is recommended to create a virtual env.
You probably have your own and prefered method, here is a classical one using the `venv` module:

```sh
# inside the "napari-hub-cli" folder, where you cloned the repository
python -m venv --symlinks .venv
source .venv/bin/activate  # activating the virtual env
```

Once you activated the virtual env, you can install all the required dependencies and the tool this way:

```sh
# inside the "napari-hub-cli" folder, where you cloned the repository
# and with virtual env activated
python -m pip install -e .

# to check that all the installation went well
# this command should print the help menu
napari-hub-cli --help
```

## Setup

### Creating a GitHub token

The code quality checklist checks access the GitHub API, and the documentation checklist autofix mode performs issue creation and pull request creation on GitHub via the API.
It is possible to use the code quality checklist without a token, but the number of requests is limited, and the autofix mode of the documentation checklist requires a token.
For security reasons this token is not stored by the tool, nor serialized in a file on your file system.
To create a token, please follow the instructions here <https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token> .
To briefly summarize the steps:

You can generate your personal access token from your GitHub account settings.
Go to `Settings>Developer settings>Personal access tokens` and select `Tokens (classic)`.
Click then on `Generate new token (classic)`, give it a note to remember why you generated this token, an expiration date, select the `public_repo` scope, and click `Generate token`.
This will lead you to a new window with the token written in plain text.
Copy the token in a file somewhere on your file system.
Be careful if you store your token in `/tmp` or other non persistent location, once the token have been displayed once in GitHub, there is no way to display it another time. If you lose it, you need to regenerate the token.

### Passing the GitHub configuration to the tool

The `napari-hub-cli` tool looks in the environment variables for the `GITHUB_TOKEN` variable that should hold the token and the `GITHUB_USER` variable that holds your Github handle.
The most important environement variable to have is the `GITHUB_TOKEN`.
This is used for both the code quality checklist and the documentation checklist autofix mode.

The `GITHUB_USER` variable is only used for the `autofix` command, and if not set, the tool will ask you to enter your Github handle and it will store it in a `config.yml` file in your OS local app data location (this directory vary depending on your system and your system configuration, on a Linux system, the location could be `~/.config/napari-hub-cli`).

To pass the GitHub configuration to the tool, you can either:

- set the environment variables `GITHUB_TOKEN` and `GITHUB_USER` in your shell. This depends on your shell, but for `bash` you can do:

```sh
export GITHUB_TOKEN=your_token
export GITHUB_USER=your_github_handle
```

When you do this, you need to do it each time you open a new terminal, or you can add these lines in your `~/.bashrc` file.

- Directly pass the variables to the tool when calling it, like so:

```sh
GITHUB_TOKEN=your_token GITHUB_USER=your_github_handle napari-hub-cli --help
```

If your token is stored in a file, you can do:

```sh
GITHUB_TOKEN=$(cat path/to/your/token) GITHUB_USER=your_github_handle napari-hub-cli --help
```

The `cat` command is not available on Windows, but you can set the environment variable like `set /P GITHUB_TOKEN=< path/to/your/token`. Furthermore, if you use `fish` as your shell, you need to use `GITHUB_TOKEN=(cat path/to/your/token)` instead.

The program will print a warning/error if the `GITHUB_TOKEN` variable is not set, and will ask you to enter your GitHub handle if the `GITHUB_USER` variable is not set but is necessary.

## Usage

### Code quality checklist

The command used to create the **Code quality checklist for a local plugin** is

```bash
 napari-hub-cli check-quality /tmp/example-plugin
```

while the command used to create the **Documentation checklist for a remote plugin** (only accessible in the ```extra``` branch) is

```bash
 napari-hub-cli check-plugin-quality example-napari-hub-plugin-name
```

The intent of this utility is to check plugins for a set of code quality metrics, and create a Code Quality Checklist identifying if a plugin has the metrics listed in [the wiki page](https://github.com/chanzuckerberg/napari-hub-cli/wiki/Plugin-quality-checklist-sources).
Additionally, the `check-plugin-quality` command will create a `.csv` file with the code quality information for all the plugins in the napari hub platform that were specified in the command line.

The options to the `check-plugin-quality` command are:

```
usage: napari-hub-cli check-plugin-quality [-h] [-p PLUGINS [PLUGINS ...]] [--csv CSV] [-d DIR] [-a] [--disable-pip-based-analysis]

options:
  -h, --help            show this help message and exit
  -p PLUGINS [PLUGINS ...], --plugins PLUGINS [PLUGINS ...]
                        List of plugins name to audit
  --csv CSV             File where to write the CSV report
  -d DIR, --dir DIR     Working directory in which plugins will be cloned (by default the tmp directory of your OS)
  -a, --all             Passing on all plugins registed in napari hub platform
  --disable-pip-based-analysis
                        Disable the pip based analysis (installability, number of dependencies, ...)
```

Example output:

![Code quality check from command line using the napari-hub-cli tool](./docs/images/code-quality-example.png)

### Documentation checklist

The command used to create the **Documentation checklist for a local plugin** is

```bash
 napari-hub-cli check-metadata /tmp/example-plugin
```

while the command used to create the **Documentation checklist for a remote plugin** (only accessible in the ```extra``` branch) is

```bash
 napari-hub-cli check-plugin example-napari-hub-plugin-name
```

The intent of this utility is to check your plugin for specific metadata in the [napari-Hub recommended file locations](https://github.com/chanzuckerberg/napari-hub/wiki/Customizing-your-plugin's-listing).
With this, it creates a Documentation checklist identifying if a plugin has the metadata listed [in the wiki](https://github.com/chanzuckerberg/napari-hub-cli/wiki/Plugin-metadata-checklist-sources).

Example output:

![Metadata check from command line using the napari-hub-cli tool](./docs/images/code-metadata-example.png)

### Citation

To create a citation file (`CITATION.CFF`) for your plugin run

```bash
 napari-hub-cli create-citation /tmp/example-plugin
```

This utility works by looking into:

- GitHub Repository metadata
- `README.md`

and creating a `CITATION.CFF`, a plain text file with human- and machine-readable citation information for software and datasets.

For citations to be parsed from the `README.md` these need to have either the **APA**(American Psychological Association) style or **BibTex** style format.

The `CITATION.CFF` file naming needs to be as it is, otherwise GitHub won't recognize it as a citation file.

The format for the CITATION.CFF is the following:

- The first citation that appears references the software
- The preffered citation, the one used in GitHub, references an article/publisher, preferring an article citation when both exist
- when both article and publisher information exist, publisher information is written as a sub-reference

#### Citation references

Below you can find some examples of how to use the `CITATION.CFF`.

Referencing other work:

```yaml
cff-version: 1.2.0
authors:
  - family-names: Druskat
    given-names: Stephan
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

```yaml
cff-version: 1.2.0
authors:
  - family-names: Druskat
    given-names: Stephan
message: "If you use this software, please cite both the article from preferred-citation and the software itself."
preferred-citation:
  authors:
    - family-names: Druskat
      given-names: Stephan
  title: "Software paper about My Research Software"
  type: article
title: "My Research Software"
```

Some more information regarding `.CFF` can be found [here](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files).

### Plugins Metadata Report

 Generates a CSV report with consistency analysis of all plugins in the napari hub platform.

 To create the CSV report run

 ```bash
 napari-hub-cli all-plugins-report report_csv
 ```

having ```report_csv``` as the name of the generated file.

The generated report contains all the documentation checklist information for each of the repositories.
You can find an example below:

![image](https://user-images.githubusercontent.com/99416933/208660275-e2d1725a-0c55-4cce-b0be-12340820eb63.png)

Note that some of the repositories are not accessible, being identified with

- ```BAD_URL```, where the repository URL provided has the wrong format
- ```MISSING_URL```, where no source code information was provided in the napari hub platform
- ```UNACCESSIBLE_REPOSITORY```, where the source code page could not be found or is a private repository

### Autofix Metadata

`napari-hub-cli` can scan remote plugin repositories and checks how metadata could be improved: _i.e_, checking that all required metadata are present and that they are located in a primary source configuration file.
In addition to this feature, `napari-hub-cli` can also automatically fix some metadata or more (_e.g._, `CITATION.cff` file creation) and report the other missing features.
The fixed files are then proposed to the owner of a plugin repository in the form of a GitHub pull request, and missing/non-autofixeable metadata are reported in the form of a GitHub issue.

The subcommand for this feature is `autofix`, it takes various options:

```
usage: napari-hub-cli autofix [-h] [-p PLUGINS [PLUGINS ...]] [-d DIR] [-a] [--push-on-github]

options:
  -h, --help            show this help message and exit
  -p PLUGINS [PLUGINS ...], --plugins PLUGINS [PLUGINS ...]
                        List of plugins name to automatically audit/fix
  -d DIR, --dir DIR     Working directory in which plugins will be cloned (by default the tmp directory of your OS)
  -a, --all             Passing on all plugins registed in napari hub plateform
  --push-on-github      Perform the analysis/commit and creates pull request/issue on GitHub
```

Here, the most important options to use are:

- `--push-on-github` to perform the analysis and actually creating the PR/issue (by default, this option is set to `False`),
- `-p` to give a list of plugin names to analyse,
- `--dir` to tell the tool where to clone all repositories.

For the `--dir` option, if the option is not set, a directory in the temporary directory of your system is used (_e.g._, a directory in `/tmp` for UNIX systems).

Prior to the analysis, the tool checks if the plugin names are actual plugins registered in the platform.
If one of them is not, the analysis is not performed and a message displays what are the faulty names with a proposal to fix them:

```sh
napari-hub-cli autofix --dir /tmp/cloned -p affander PartSet
```

Will yield:

```
Some of the input plugins are not existing on the platform:
 * 'affander' do you mean 'affinder'?
 * 'PartSet' do you mean 'PartSeg'?
```

#### Dry Run

The tool is able to perform the automatic modification of the base code without actually creating the pull-requests or the issues.
To let you inspect what will be done, it only clones the repository to scan, perform the various commits, but does not delete the cloned repository after analysis until you press the `enter` key.

It also displays in the terminal the pull-requests and issue messages that will be created (using `USERNAME` and `PRID` as substitutes for your name and the pull request ID), and stops after each repository analysis.

Here is an example of how to perform a dry run over `affinder` and `PartSeg` plugins:

```sh
napari-hub-cli autofix --dir /tmp/cloned -p affinder PartSeg
```

#### Automatic creation of pull-requests and issues

Creating automatically the pull-requests and the issues requires a small setup and slightly changes the way the tool need to be called.
See [Setup](#setup) for more information on how to create a GitHub token and pass the token and your GitHub username to the tool.

Technically, the operations performed in GitHub will be:

- forking the analysed plugin repository,
- creating a pull request if necessary,
- creating an issue if necessary.

Now, considering that you have your token saved in this location `/tmp/gh_token.tok`, with your handle being `foo` here is how to call the autofix feature without creating a config file or setting environment variables:

```bash
GITHUB_TOKEN=$(cat gh-token.tok) GITHUB_USER=foo napari-hub-cli autofix --dir /tmp/cloned -p affinder PartSeg --push-on-github
```

## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](https://github.com/chanzuckerberg/.github/blob/master/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [opensource@chanzuckerberg.com](mailto:opensource@chanzuckerberg.com).
