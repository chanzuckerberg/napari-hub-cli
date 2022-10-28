
# Requirements


The intent of this utility is to check your plugin for specific metadata in the Napari recommended file location. 
With this, it creates a **Documentation Checklist** identifying the following metadata:

- Display Name
- Summary Sentence
- Intro Paragraph
- Intro Video
- Intro Scrennshot
- Usage Section
- Source Code Link
- User Support Link
- Bug Tracker Link
- Author
- Citation

Additionally, the recommended file locations are suggested in two different cases:

- when no metadata is found in either the primary file location or the fallback file location
- when no metadata is found at the primary file location


Below you can find a table with the metadata and its associated primary recommended files and fallback files:


Metadata / Files | Primary File | Fallback File(s) 
--- | --- | --- | 
Display Name | ```npe2``` | ```setup.cfg```  or ```setup.py```
Summary Sentence | ```napari-hub/config.yml``` | ```setup.cfg```  or ```setup.py``` 
Intro Paragraph | ```napari-hub/description.md``` | ```setup.cfg```  or ```setup.py``` 
Intro Video | ```napari-hub/description.md``` | ```setup.cfg```  or ```setup.py``` 
Intro Screenshot | ```napari-hub/description.md``` | ```setup.cfg```  or ```setup.py``` 
Usage Section | ```napari-hub/description.md``` | ```setup.cfg```  or ```setup.py``` 
Source Code Link | ```napari-hub/config.yml``` | ```setup.cfg```  or ```setup.py``` 
User Support Link | ```napari-hub/config.yml``` | ```setup.cfg```  or ```setup.py``` 
Bug Tracker Link | ```napari-hub/config.yml``` | ```setup.cfg```  or ```setup.py``` 
Author | ```napari-hub/config.yml``` | ```setup.cfg```  or ```setup.py``` 
Citation | ```napari-hub/config.yml``` | ```setup.cfg```  or ```setup.py``` 



# Usage

To create the Napari Documentation Checklist for your plugin run

```
 $ napari-hub-cli create-doc-checklist /tmp/example-plugin 
```
having first installed all the requirements for ```napari-hub-cli```.


Example of Documentation Checklist:



