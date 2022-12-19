# Hoi4 Converter

The idea of this package is to provide tools for parsing, writing and modifying
HOI4 files. It should enable modders to automate the boring tasks and let them focus 
on the creation process.

## Examples

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



