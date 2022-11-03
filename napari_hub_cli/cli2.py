#https://api.napari-hub.org/plugins

import requests
import re
import pathlib
import git
import json

input_plugin = 'brainreg-napari' #get this from console input

NAPARI_HUB_API_LINK = 'https://api.napari-hub.org/plugins'

r = requests.get(NAPARI_HUB_API_LINK)
res = r.json()
res = res.keys()

for i in res:
    if(re.findall(input_plugin, i, flags=re.DOTALL)):
        plugin_name = i
        print(i)
        print('True')
        NAPARI_HUB_API_LINK = NAPARI_HUB_API_LINK + '/'+ i
        print(NAPARI_HUB_API_LINK)
        r2 = requests.get(NAPARI_HUB_API_LINK)
        res2 = r2.json()
        print(res2['code_repository'])
        plugin_url = res2['code_repository']



git.Git(str(pathlib.Path().resolve())).clone(plugin_url)

TEST_REPO_LINK = (str(pathlib.Path().resolve())) + '/'+plugin_name

