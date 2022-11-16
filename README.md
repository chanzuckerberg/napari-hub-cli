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



## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](https://github.com/chanzuckerberg/.github/blob/master/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [opensource@chanzuckerberg.com](mailto:opensource@chanzuckerberg.com).
