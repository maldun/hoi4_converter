# Hoi4 Converter

The idea of this package is to provide tools for parsing, writing and modifying
HOI4 files. It should enable modders to automate the boring tasks and let them focus 
on the creation process.

The Package was originally based on [ClauseWizard by Shadark](https://github.com/Shadark/ClauseWizard) 
but grew to be its own package.

## Installation

### Requirements

The package needs Python 3.10 or higher and the package pyparsing, which can be installed via

```
pip install pyparsing
```

### Installation Steps

[PyPI Repo can be found here](https://pypi.org/project/hoi4-converter/)

Installation with:

```
pip install hoi4-converter
```

## Examples

I assume some basic knowldege of Python in this section. If you're new check out the [official Python
tutorial](https://docs.python.org/3/tutorial/). The package can only be as powerful as your Python skills.

### A first example

Let's start with something simple to get some ideas. Assume you are in the folder
of interface/ and we investigate for example the file [r56_leader_portraits.gfx](https://github.com/maldun/hoi4_converter/blob/main/test/samples/r56_leader_portraits.gfx) (you can find it in [test/samples of the source code](https://github.com/maldun/hoi4_converter/tree/main/test/samples). Now we start Python from the commandline:

```python
>>> from Hoi4Converter.converter import paradox2list
>>> obj = paradox2list("r56_leader_portraits.gfx")
```
obj is a list of lists in Python. We can now for example access the first sprite in the list,
using the proper indies
```python
>>> obj[0][1][0]
['spriteType', [['name', ['"GFX_CZE_Portrait_milan_hodza"']], ['textureFile', ['"gfx/leaders/CZE/r56_portrait_CZE_Milan_Hodza.dds"']]]]
```
The reason we need lists is that Paradox files are not dictionaries but proper code, so keywords can repeat.
Also this is the result the pyparsing parser returns) 

This can be tiresome ofc. to search through and also it can happen that something we search for is hidden
deeper due to some OR or IF. Luckily Hoi4Converter provides us with some tools. Let's for example
search for all 'textureFile' entries in the graphics:

```python
>>> from Hoi4Converter.mappings import has_key
>>> objects, indices = has_key.search(obj)
```
The variable objects now is a list of the objects we found. So the first entry is:
```python
>>> objects[0]
['textureFile', ['"gfx/leaders/CZE/r56_portrait_CZE_Milan_Hodza.dds"']]
```
We see here also the basic structure of these list objects: 'textureFile' is the **key** word which defines
the object, the second entry ['"gfx/leaders/CZE/r56_portrait_CZE_Milan_Hodza.dds"'] is the **value** of the
object. We can use the list2paradox function to look at the corresponding code again:

```python
>>> print(list2paradox([objects[0]]))
textureFile = "gfx/leaders/CZE/r56_portrait_CZE_Milan_Hodza.dds"
>>> print(list2paradox([objects[1]]))
textureFile = "gfx/leaders/CZE/r56_portrait_CZE_Radola_Gajda.dds"
```
Note that I added [] around the objets. The reason is that the reverse-parser needs to be given a 
proper output, as the struture is based on the pyparsing structure. So a little playing around sure
does not hurt to get the indices right. For comparsion
```python
>>> print(list2paradox(objects[1]))
textureFile
"gfx/leaders/CZE/r56_portrait_CZE_Radola_Gajda.dds"
```
is understandable but it wouldn't be the proper code. So we have to be careful with the brackets!.

The variable indices is a corresponding list of the indices where inside of obj the entry was found:
```python
>>> indices[0]
[0, 1, 0, 1, 1]
>>> obj[0][1][0][1][1]
['textureFile', ['"gfx/leaders/CZE/r56_portrait_CZE_Milan_Hodza.dds"']]
>>> 
```
This would be quite a lot to type, so here is the shortcut:
```python
>>> from Hoi4Converter.mappings import get_object_from_inds
>>> get_object_from_inds(obj, indices[1])
['textureFile', ['"gfx/leaders/CZE/r56_portrait_CZE_Radola_Gajda.dds"']]
```
But for now it would be enough for us to collect all the file names so that we can check everything is there:
```python
>>> from Hoi4Converter.mappings import get_object_from_inds
>>> get_object_from_inds(obj, indices[1])
['textureFile', ['"gfx/leaders/CZE/r56_portrait_CZE_Radola_Gajda.dds"']]
>>> filenames = []
>>> for o in objects:
...     filename = o[1][0] # access filename
...     filename = filename.replace('"','').replace("'",'') # get rid of quotes
...     filenames += [filename]
... 
>>> filenames
['gfx/leaders/CZE/r56_portrait_CZE_Milan_Hodza.dds', 'gfx/leaders/CZE/r56_portrait_CZE_Radola_Gajda.dds', ...
]
```
Now we can actually do stuff! For example checking if the files from our .gfx are actually there,
and write the checklist into a .json file which can be opened with any text editor:
```python
>>> import os
>>> rt56_folder = os.path.expanduser("~/.local/share/Steam/steamapps/workshop/content/394360/2076426030/")
>>> is_there = {}
>>> for file in filenames: is_there[file] = os.path.isfile(os.path.join(rt56_folder, file))
>>> is_there
{'gfx/leaders/CZE/r56_portrait_CZE_Milan_Hodza.dds': False, ...} 
>>> import json
>>> with open('gfx_there.json', 'w') as fp: fp.write(json.dumps(is_there))
```

### More examples

The parser allows to convert Hoi4 code into lists of lists objects:

We can create objects from code:

```python
code = """
guiTypes = {

	containerWindowType = {
		name ="frontend_background"
		position = { x=0 y =0 }	
		size = { 
			width = 1920 
			height = 1440 
			min = { width = 100% height = 100% }
			preserve_aspect_ratio = yes
		}
		Orientation = center
		Origo = center
		clipping = no 
		
		background = {
			name = "Background"		
			quadTextureSprite ="GFX_frontend_bg"
			alwaystransparent = yes
		}
	}
}
"""

from Hoi4Converter.parser import parse_grammar as code2obj
obj = code2obj(code)
print(obj)
```

this gives:
```
['guiTypes', [['containerWindowType', [['name', ['"frontend_background"']], ['position', [['x', [0]], ['y', [0]]]], ['size', [['width', [1920]], ['height', [1440]], ['min', [['width', ['100%']], ['height', ['100%']]]], ['preserve_aspect_ratio', [True]]]], ['Orientation', ['center']], ['Origo', ['center']], ['clipping', [False]], ['background', [['name', ['"Background"']], ['quadTextureSprite', ['"GFX_frontend_bg"']], ['alwaystransparent', [True]]]]]]]]]
```

The function paradox2list does the same, but on files instead of lists:


```python
from Hoi4Converter.converter import paradox2list
with open("test_file.txt", 'w') as fp:
	fp.write(code)
obj2 = paradox2list("test_file.txt")

assert obj == obj2

```

list2paradox takes a paradox object, and returns the code as a string:


The code
```python
from Hoi4Converter.converter import list2paradox
print(list2paradox(obj))
```
gives:

```
guiTypes = {
    containerWindowType = {
        name = "frontend_background"
        position = {
            x = 0
            y = 0
            
        }
        size = {
            width = 1920
            height = 1440
            min = {
                width = 100%
                height = 100%
                
            }
            preserve_aspect_ratio = yes
            
        }
        Orientation = center
        Origo = center
        clipping = no
        background = {
            name = "Background"
            quadTextureSprite = "GFX_frontend_bg"
            alwaystransparent = yes
            
        }
        
    }
    
}

```

The package also includes mappings for you convenience to apply changes.
Since HOI4 files have a nested structure, a functional approach was chosen
to avoid unecessary for loops.
For example the entries "national_populist" and "paternal_autocrat" everywhere 
"fascism" is found and at the end removes the "fascism tag":

```python
from Hoi4Converter.mappings import *
from Hoi4Converter.converter import *
fname_with_rel = "test/samples/r56i_laws_war.txt"
obj = paradox2list(fname_with_rel)
key = "has_government"
val = ["fascism"]
to_add = [[key, ["national_populist"]],
		 [key, ["paternal_autocrat"]],
                  ]
source = [has_key_and_val, [key, val]]
target = [add_multiple, to_add]
new_obj = apply_map(obj, (source, target))

source = [has_key_and_val, [key, val]]
target = [remove, []]
new_obj2 = apply_map(new_obj,(source, target))
```

Patching code with search-replace is often not viable as whitespace or lines may change.

Here an example how to add an Entry to a specific file:

```python
from Hoi4Converter.mappings import *
from Hoi4Converter.converter import *

def patch_main_menu(kx_path, out_folder):
    filename = "frontendmainview.gui"
    in_file, out_file = make_folder_in_out_file(INTERFACE_FOLDER, filename,
                                                kx_path, out_folder)
    
    tmap = [[has_key_and_val, ["name", ['"frontend_background"']]],
             [add_multiple, [["iconType", [["name",['"autobahn_logo"']],
                                            ["spriteType",['"GFX_autobahn_logo"']],
                                            ["position",
                                             [['x',[1600]],
                                              ['y',[1200]],
                                              ]
                                           ]
                                           ]
                              ]
              ]]
            ]
    apply_maps_on_file(in_file, out_file, [tmap])
```



Here a script to cleanly apply patches:

```python
from Hoi4Converter.mappings import *
from Hoi4Converter.converter import *
from Hoi4Converter.parser import parse_grammar as code2obj

def patch_object(r56_obj, org_code, patched_code):
    key_val = code2obj(org_code)[0]
    if isinstance(patched_code, str) and len(patched_code) > 0:
        key_val_replace = code2obj(patched_code)[0]
        mapping = [[has_key_and_val, key_val], [replace, key_val_replace]]
    else:
        mapping = [[has_key_and_val, key_val], [remove, key_val]]
        
    r56_obj = apply_map(r56_obj, mapping)
    return r56_obj

infantry_snippet = """
                      OR = { 
                        original_tag = SWE
                        original_tag = FIN
                        original_tag = SAM
                        original_tag = GRL
                        original_tag = ICE
                        original_tag = QBC
                }
                      """
infantry_patch = """
                      OR = { 
                        original_tag = SWE
                        original_tag = FIN
                        original_tag = ICE
                      }
                      """

obj = list2paradox("infantry.txt")
new_object = patch_object(obj, infantry_snippet, infantry_patch)
                      
```

To give an advanced example here we apply the contents of an Excel/.csv onto a list of files to add certain entries:

```python
def apply_equipment_table(file_name):
    df = pd.read_csv(file_name,header=0, index_col=0)
    techs = list(df.columns)
    country_folder = os.path.join(MAIN_MOD, HISTORY_COUNTRY_PATH)
    file_dict = {fname[:3]: fname for fname in os.listdir(country_folder)}
    maps = {}
    for fname in os.listdir(country_folder):
        tag = fname[:3]
        vals = [[tech, [df.loc[tag, tech] if pd.isna(df.loc[tag, tech]) else int(df.loc[tag, tech])]]
                for tech in techs if not pd.isna(df.loc[tag, tech])]
        mapping = [[has_key_and_max_level, [SET_TECH_KEY, 1]],
                   [add_multiple_values, vals]
                   ]
        maps[tag] = mapping
    return maps

    
def apply_equipment_maps(general_maps, specific_maps):
    in_folder = os.path.join(MAIN_MOD, HISTORY_COUNTRY_PATH)
    out_folder = os.path.join(OUT_FOLDER, HISTORY_COUNTRY_PATH) 
    file_list = os.listdir(in_folder)
    #file_list = ["FRA - France.txt"]
    os.makedirs(out_folder, exist_ok=True)

    for file in file_list:
        tag = file[:3]
        maps = general_maps + [specific_maps[tag]]
        try:
            apply_maps_on_file(os.path.join(in_folder, file),
                           os.path.join(out_folder, file),
                           maps)
        except:
            import pdb; pdb.set_trace()
```

For more examples look into my scripts I use for my own mod: [https://github.com/maldun/autobahn/tree/main/.scripts](https://github.com/maldun/autobahn/tree/main/.scripts)
I also created a small graphical tool as a showcase: [HoiIdeaWizard](https://github.com/maldun/hoi4_spirit_wizard)


## License


This code uses assets from ClauseWizard by Shadark (https://github.com/Shadark/ClauseWizard). 
To honor the spirit (and the rules) of the GPL this work is licensed with the GPL3 as well.

NOTE: This API just generates HOI4 files, so the products of this package are not under GPL! So no worries!


hoi4_converter: A Python package for HOI4 modding
Copyright (C) 2022  Stefan Reiterer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.



