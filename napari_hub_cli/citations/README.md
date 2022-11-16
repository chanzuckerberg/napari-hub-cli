# Requirements

This utility works by looking into:
- GitHub Repository metadata 
- README.md

and creating a CITATION.CFF, a plain text file with human- and machine-readable citation information for software and datasets.


For citations to be parsed from the README.md these need to have either the **APA**(American Psychological Association) style or **BibTex** style format.


The **CITATION.CFF** file naming needs to be as it is, otherwise GitHub won't recognize it as a citation file.


# Usage

To create the CITATION.CFF for your plugin run

```
 $ napari-hub-cli create-cff-citation /tmp/example-plugin 
```
having first installed all the requirements for ```napari-hub-cli```


The format for the CITATION.CFF is the following:
- The first citation that appears references the software
- The preffered citation, the one used in GitHub, references an article/publisher, preferring an article citation when both exist
- when both article and publisher information exist, publisher information is written as a sub-reference


# Citation references

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

