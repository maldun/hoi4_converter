#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from . import parser
import unittest
import os

U8 = 'utf-8-sig' # MS BS ...
INTEND = " "*4
NL = '\n'
EQ = ' = '
LB = '{'
RB = '}'
DQ = '"'
SPACE = '__SPACE__'
SEP = '/'
RSEP = '__SEP__'
MINUS = '__MINUS__'
DOT = "__DOT__"
FILE_REPLACEMENTS = ((' ', SPACE), ("-", MINUS), (".",DOT))

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
    if isinstance(val, str):
        code += DQ + val + DQ + NL
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
    key, val = member
    code = str(key) + EQ
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
            if len(liste) == 2 and isinstance(liste[1], list): # liste is key object pair
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
            

            code += write_object(member)
            
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
        GFX = "GFX_portrait_kr_nancy_wake"
        traits = {
            "operative_escape_artist"
            
        }
        bypass_recruitment = no
        available_to_spy_master = yes
        female = yes
        nationalities = {
            "NZL"
            "AST"
            
        }
        
    }
"""

class ConverterTests(unittest.TestCase):
    def setUp(self):
        self.fnames = ["test/samples/r56_leader_portraits.gfx",
                       "test/samples/AST - Australia.txt",
                       ]
            
    def test_paradox2list(self):
        nrs = [1, 101]
        for nr, fname in zip(nrs, self.fnames):
            result = paradox2list(fname)
            self.assertEqual(len(result), nr)

    def test_list2paradox(self):
        snippets = [snippet1, snippet2]
        for snip, fname in zip(snippets, self.fnames):
            result = paradox2list(fname)
            result = list2paradox(result)
            self.assertIn(snip, result)

    def test_intend_code(self):
        snippet = "{0}a\n{0}b\n{0}"
        code = snippet.format('')
        icode = snippet.format(INTEND)
        result = intend_code(code)
        self.assertEqual(icode, result)
        
            













