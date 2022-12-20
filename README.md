# napari-hub-cli



Command line utilities for inspecting and validating plugins for the napari hub.



# Installation

First the repository needs to be cloned

```sh
git clone https://github.com/chanzuckerberg/napari-hub-cli.git
cd napari-hub-cli
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
pip install .
```


Alternatively, you can also install the napari hub CLI directly from your console through pip

```
$ pip install napari-hub-cli
```

To check that the installation went well, this command prints the help menu 
```sh
napari-hub-cli --help
```

# Usage 


## Documentation Checklist

The command used to create the Documentation Checklist is
```
 $ napari-hub-cli create-doc-checklist /tmp/example-plugin 
```

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



Below you can find a table with the Napari recommended file locations and fallback files where the metadata is checked:


| Metadata / Files  | Recommended File                | Fallback File(s) |
| ----------------- | ------------------------------- | ---------------- |
| Display Name      | ```npe2 - napari.manifest```    | ```PyPI```       |
| Summary Sentence  | ```napari-hub/config.yml```     | ```PyPI```       |
| Intro Paragraph   | ```napari-hub/description.md``` | ```PyPI```       |
| Intro Video       | ```napari-hub/description.md``` | ```PyPI```       |
| Intro Screenshot  | ```napari-hub/description.md``` | ```PyPI```       |
| Usage Section     | ```napari-hub/description.md``` | ```PyPI```       |
| Source Code Link  | ```PyPI```                      | ```n/a```        |
| User Support Link | ```PyPI```                      | ```n/a```        |
| Bug Tracker Link  | ```PyPI```                      | ```n/a```        |
| Author            | ```PyPI```                      | ```n/a```        |
| Citation          | ```CITATION.cff```              | ```n/a```        |


Example output (with all possible scenarios):

<img width="556" alt="Screenshot at Nov 15 18-32-57" src="https://user-images.githubusercontent.com/99416933/201911155-71871012-8afb-4161-bd84-1794b3cd4735.png">




## Citation

To create a citation file (`CITATION.CFF`) for your plugin run
```
 $ napari-hub-cli create-cff-citation /tmp/example-plugin 
```

This utility works by looking into:

- GitHub Repository metadata
- ```README.md```

and creating a ```CITATION.CFF```, a plain text file with human- and machine-readable citation information for software and datasets.

For citations to be parsed from the ```README.md``` these need to have either the **APA**(American Psychological Association) style or **BibTex** style format.

The ```CITATION.CFF``` file naming needs to be as it is, otherwise GitHub won't recognize it as a citation file.



The format for the CITATION.CFF is the following:

- The first citation that appears references the software
- The preffered citation, the one used in GitHub, references an article/publisher, preferring an article citation when both exist
- when both article and publisher information exist, publisher information is written as a sub-reference


### Citation references


Below you can find some examples of how to use the `CITATION.CFF`.

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

Some more information regarding `.CFF` can be found [here](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files).


## Previewing your plugin's napari hub page

To view a preview of your plugin listing for the napari hub, we recommend using the [napari hub preview page service](https://github.com/chanzuckerberg/napari-hub/blob/main/docs/setting-up-preview.md).
However, legacy commands `preview-metadata` and `check-missing` are available to preview your hub page.
To use these commands, run:

```
napari-hub-cli preview-metadata /tmp/example-plugin
napari-hub-cli check-missing /tmp/example-plugin
```

## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](https://github.com/chanzuckerberg/.github/blob/master/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [opensource@chanzuckerberg.com](mailto:opensource@chanzuckerberg.com).
