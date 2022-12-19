#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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
"""

from . import parser
import unittest
import os

U8 = 'utf-8-sig' # MS BS ...
UTF8 = 'utf-8'
INTEND = " "*4
NL = '\n'
EQ = ' = '
LT = ' < '
GT = ' > '
LB = '{'
RB = '}'
DQ = '"'
SPACE = '__SPACE__'
SEP = '/'
RSEP = '__SEP__'
MINUS = '__MINUS__'
DOT = "__DOT__"
FILE_REPLACEMENTS = ((' ', SPACE), ("-", MINUS), (".",DOT))
RELS = ['<', '>']

def intend_code(code):
    """
    intends a code snippet
    """
    lines = code.split(NL)
    lines = [INTEND + line for line in lines]
    result = NL.join(lines)
    return result

def paradox2list(filename):
    """
    Takes a file from paradox and converts it to a Python list
    """
    with open(filename, 'r', encoding=U8) as f:
            text = f.read()

    return parser.parse_grammar(text)

def write_value(val):
    code = ''
    if isinstance(val, str) and val != '':
        code += val + NL
    # An empty value is not allowed
    elif isinstance(val, str) and val == '':
        code += LB + RB + NL
    elif val is True:
        code += 'yes' + NL
    elif val is False:
        code += 'no' + NL
    else:
        code += str(val) + NL
    return code

def write_object(member):
    #if member[0] == "limit":
    #    import pdb; pdb.set_trace()
    if len(member) == 2:
        key, val = member
        rel_code = " = "
    elif len(member) == 3 and member[1] in RELS:
        key, rel, val = member
        rel_code = f" {rel} "
        
    code = str(key) + rel_code
    # assume we have single value
    if len(val) == 1 and not isinstance(val[0], list):
        code += write_value(val[0])
    # here we go again ...
    else:
        code += LB + NL
        obj = list2paradox(val)
        obj = intend_code(obj)
        code += obj
        code += NL + RB + NL
    return code

def list2paradox(liste):
    """
    A converter which takes a lised from a parsed Paradox 
    file and reconstructs the file.
    """
    code = ""
    for member in liste:
        # member is actually key:
        if isinstance(member, str):
            # liste is key object pair
            if len(liste) == 3 and liste[1] in RELS and isinstance(liste[2], list): 
                code += write_object(liste)
            else:
                code += write_value(member)
        # Solo value
        elif isinstance(member, list) and len(member) == 1:
            val = member[0]
            if isinstance(val, list):
                code += list2paradox(val)
            else:
                code += write_value(val)
        # value with = 
        elif (isinstance(member, list) and len(member) == 2
              and isinstance(member[0], str)
              and isinstance(member[1], list)
              ):
            try:
                code += write_object(member)
            except:
                import pdb; pdb.set_trace()

        elif (isinstance(member, list) and len(member) == 3
              and isinstance(member[0], str)
              and isinstance(member[2], list)
              ):
            try:
                if member[1] in RELS:
                    code += write_object(member)
            except:
                pass

            
    return code

########################
# Tests                #
########################
snippet1 = """    spriteType = {
        name = "GFX_Portrait_South_America_Generic_new_7"
        texturefile = "gfx/leaders/kr_generic/Portrait_South_America_Generic_new_7.png"
        
    }
"""

snippet2 = """if = {
    limit = {
        has_dlc = "La Resistance"
        
    }
    create_operative_leader = {
        name = "Nancy Wake"
        GFX = GFX_portrait_kr_nancy_wake
        traits = {
            operative_escape_artist
            
        }
        bypass_recruitment = no
        available_to_spy_master = yes
        female = yes
        nationalities = {
            NZL
            AST
            
        }
        
    }
"""

snippet3 = """                    has_country_leader = {
                        name = "Anarchist Commune"
                        ruling_only = yes
                        
                    }
"""

snippet_rel = """threat > 0.05"""

class ConverterTests(unittest.TestCase):
    def setUp(self):
        self.fnames = ["test/samples/r56_leader_portraits.gfx",
                       "test/samples/AST - Australia.txt",
                       "test/samples/r56i_laws_gender.txt",
                       ]
        self.fname_with_rel = "test/samples/r56i_laws_war.txt"
        self.fname_with_square_brackets = "test/samples/China_decisions.txt"
        self.fname_with_empty_brackets = "test/samples/INC - Indochina.txt"
        self.fname_with_AT_symbol = "test/samples/BAT - United Baltic Duchy.txt"
        self.fname_with_percent = "test/samples/gui_sample.txt"
        self.fname_with_numbered_vars = "test/samples/01_American Civil War effects.txt"
        self.fname_infantry_tech = "test/samples/infantry.txt"
            
    def test_paradox2list(self):
        nrs = [1, 101]
        for nr, fname in zip(nrs, self.fnames):
            result = paradox2list(fname)
            self.assertEqual(len(result), nr)

    def test_list2paradox(self):
        snippets = [snippet1, snippet2, snippet3]
        for snip, fname in zip(snippets, self.fnames):
            result = paradox2list(fname)
            result = list2paradox(result)

            self.assertIn(snip, result)

    def test_list2paradoxwithrel(self):
        result = paradox2list(self.fname_with_rel)
        result = list2paradox(result)
        self.assertIn(snippet_rel, result)

    def test_intend_code(self):
        snippet = "{0}a\n{0}b\n{0}"
        code = snippet.format('')
        icode = snippet.format(INTEND)
        result = intend_code(code)
        self.assertEqual(icode, result)

    def test_handle_square_brackets(self):
        fname = self.fname_with_square_brackets
        from .mappings import has_key_and_val
        obj = paradox2list(fname)
        result = has_key_and_val(obj, ["has_idea", ['[IDEA_NAME]']])
        self.assertEqual(len(result[0]), 3)
        result = has_key_and_val(obj, ["idea", ['[IDEA_NAME]']])
        self.assertEqual(len(result[0]), 3)

    def test_handle_empty_brackets(self):
        fname = self.fname_with_empty_brackets
        obj = paradox2list(fname)
        result = list2paradox(obj)
        self.assertIn("40 = {}", result)

    def test_handle_empty_brackets(self):
        fname = self.fname_with_AT_symbol
        obj = paradox2list(fname)
        result = list2paradox(obj)
        self.assertIn("BAT.BAT_mission_general_@LIT = THIS", result)

    def test_percent(self):
        fname = self.fname_with_percent
        obj = paradox2list(fname)
        result = list2paradox(obj)
        self.assertIn('width = 100%', result)

    def test_numbered_vars(self):
        fname = self.fname_with_numbered_vars
        obj = paradox2list(fname)
        result = list2paradox(obj)
        self.assertIn("ohio_factories = 261.building_level@industrial_complex",
                      result)

    def test_alternative_date(self):
        snippet = """modifier = {
                factor = 2
                date > 1940-01-01
                
            }
        """
        result = parser.parse_grammar(snippet)
        self.assertEqual('1940-01-01', result[0][1][1][2][0])

    def test_number_suffix(self):
        fname = self.fname_infantry_tech
        obj = paradox2list(fname)
        self.assertEqual(obj[0][1][0][1][0][1][0][1][0], '0.15f')
        result = list2paradox(obj)
        self.assertIn("acclimatization_cold_climate_gain_factor = 0.15f", result)

    def test_slash(self):
        code = """
        spriteType = {
		name = GFX_GER_advanced_heavy_td
		texturefile = gfx/interface/technologies/ger_advanced_heavy_td.dds
	}
        """
        obj = parser.parse_grammar(code)
        self.assertEqual(obj[0][1][1][1][0], 'gfx/interface/technologies/ger_advanced_heavy_td.dds')
