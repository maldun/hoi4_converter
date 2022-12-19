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

from Hoi4Converter.converter import paradox2list
with open("test_file.txt", 'w') as fp:
	fp.write(code)
obj2 = paradox2list("test_file.txt")

assert obj == obj2

from Hoi4Converter.converter import list2paradox
print(list2paradox(obj))
