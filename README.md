# napari-hub-cli

Command line utilities for inspecting and validating plugins for the napari hub.

# Usage

## Metadata

This package provides two utilities for previewing and validating the metadata we 
will inspect from your plugin and display on the napari hub. 

### Previewing Metadata

```
$ napari-hub-cli preview-metadata /tmp/my-napari-plugin
```

This utility will inspect the plugin at the given path for metadata and display it for preview.
Example output:

| Metadata           	|                                                                             Value                                                                            	|         Source         	|
|--------------------	|:------------------------------------------------------------------------------------------------------------------------------------------------------------:	|:----------------------:	|
| Name               	|                                                                           affinder                                                                           	|   ./setup.py Line 28   	|
| Summary            	|                    'Quickly find the affine matrix mapping one image to another using '         'manual correspondence points annotation'                    	|  ./setup.py Line 33-36 	|
| Description        	| '# Description  This GUI plugin allows you to quickly find the affine matrix mapping one image to another using manual correspondence points annotation.'... 	| .napari/DESCRIPTION.md 	|
| Authors            	|                                                                      Juan Nunez-Iglesias                                                                     	|   ./setup.py Line 29   	|
| License            	|                                                                             BSD-3                                                                            	|   ./setup.py Line 31   	|
| Version            	|                                                                              ??                                                                              	|           ??           	|
| Development Status 	|                                                                           3 - Alpha                                                                          	|   ./setup.py Line 45   	|
| Python Version     	|                                                                             >=3.7                                                                            	|   ./setup.py Line 40   	|
| Operating System   	|                                                                        OS Independent                                                                        	|   ./setup.py Line 54   	|
| Requirements       	|                               napari-plugin-engine>=0.1.9 napari>=0.4.3 numpy scikit-image magicgui>=0.2.5,!=0.2.7 napari toolz                              	|   ./requirements.txt   	|
| Project Site       	|                                                                               -                                                                              	|            -           	|
| Documentation      	|                                                                               -                                                                              	|            -           	|
| Support            	|                                                                               -                                                                              	|            -           	|
| Report Issues      	|                                                                               -                                                                              	|            -           	|
| Twitter            	|                                                                               -                                                                              	|            -           	|
| Source Code        	|                                                                https://github.com/jni/affinder                                                               	|   ./setup.py Line 32   	|

Missing metadata is denoted with a `-`. You can then use `check-metadata` to get a display of just the missing metadata, and where 
you can add it into your project. See [below](#sources) for where we look for your metadata.

### Checking Metadata

```
$ napari-hub-cli check-metadata /tmp/my-napari-plugin
```

This utility will only display the metadata missing from your plugin, and will also suggest where you can add it, if desired.
Example output:

| Metadata      	|                            Suggested Source                            	|
|---------------	|:----------------------------------------------------------------------:	|
| Project Site  	|   ./setup.py setup(project_urls={'Project Site': 'https://url.com'})   	|
| Documentation 	|   ./setup.py setup(project_urls={'Documentation': 'https://url.com'})  	|
| Support       	|   ./setup.py setup(project_urls={'User Support': 'https://url.com'})   	|
| Report Issues 	|   ./setup.py setup(project_urls={'Report Issues': 'https://url.com'})  	|
| Twitter       	| ./setup.py setup(project_urls={'Twitter': 'https://twitter.com/user'}) 	|

This utility will also check whether, when a `.napari/DESCRIPTION.md` is present, it is different to the 
boilerplate provided in napari's cookiecutter plugin template. 

<a name="sources"></a>
### Metadata Sources

The table below lists the locations we will search for each metadata value, in order.

| Metadata           	|                                                     Searched In                                                     	|
|--------------------	|:-------------------------------------------------------------------------------------------------------------------:	|
| Name               	|                            **`setup.cfg [metadata] name=`**<br>`setup.py setup(name="")`                            	|
| Summary            	|       **`.napari/config.yml summary:`**<br>`setup.cfg [metadata] summary=`<br>`setup.py setup(description="")`      	|
| Description        	|  **`.napari/DESCRIPTION.md`**<br>`setup.cfg [metadata] long_description=`<br>`setup.py setup(long_description="")`  	|
| Authors            	|          **`.napari/config.yml authors:`**<br>`setup.cfg [metadata] author=`<br>`setup.py setup(author="")`         	|
| License            	|                         **`setup.cfg [metadata] license=`**<br>`setup.py setup(license="")`                         	|
| Version            	|                                                          ??                                                         	|
| Development Status 	|                      **`setup.cfg [metadata] classifier=`**<br>`setup.py setup(classifiers=[])`                     	|
| Python Version     	|                 **`setup.cfg [metadata] python_requires=`**<br>`setup.py setup(python_requires="")`                 	|
| Operating System   	|                      **`setup.cfg [metadata] classifier=`**<br>`setup.py setup(classifiers=[])`                     	|
| Requirements       	|     **`setup.cfg [options] install_requires=`**<br>`setup.py setup(install_requires=[])`<br>`./requirements.txt`    	|
| Project Site       	|          **`.napari/config.yml project_urls:`**<br>`setup.cfg [metadata] url=`<br>`setup.py setup(url="")`          	|
| Documentation      	| **`.napari/config.yml project_urls:`**<br>`setup.cfg [metadata] project_urls=`<br>`setup.py setup(project_urls={})` 	|
| Support            	| **`.napari/config.yml project_urls:`**<br>`setup.cfg [metadata] project_urls=`<br>`setup.py setup(project_urls={})` 	|
| Report Issues      	| **`.napari/config.yml project_urls:`**<br>`setup.cfg [metadata] project_urls=`<br>`setup.py setup(project_urls={})` 	|
| Twitter            	| **`.napari/config.yml project_urls:`**<br>`setup.cfg [metadata] project_urls=`<br>`setup.py setup(project_urls={})` 	|
| Source Code        	| **`.napari/config.yml project_urls:`**<br>`setup.cfg [metadata] project_urls=`<br>`setup.py setup(project_urls={})` 	|

## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](https://github.com/chanzuckerberg/.github/blob/master/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [opensource@chanzuckerberg.com](mailto:opensource@chanzuckerberg.com).
