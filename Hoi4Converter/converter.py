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
SPACE = '__SPACE__'
SEP = '/'
RSEP = '__SEP__'
MINUS = '__MINUS__'
DOT = "__DOT__"
FILE_REPLACEMENTS = ((' ', SPACE), ("-", MINUS), (".",DOT))

def paradox2list(filename):
    """
    Takes a file from paradox and converts it to a Python list
    """
    with open(filename, 'r', encoding=U8) as f:
            text = f.read()

    return parser.parse_grammar(text)

def list2paradox(list):
    """
    A converter which takes a lised from a parsed Paradox 
    file and reconstructs the file.
    """
    pass

def _recursive_build(liste):
    code = ""
    key, val = liste[0]
    code += str(key) + EQ
    if isinstance(val, list):
        code += LB + NL + INTEND
        
    

########################
# Tests                #
########################

class ConverterTests(unittest.TestCase):
    def setUp(self):
        self.fnames = ["test/samples/r56_leader_portraits.gfx",
                       "test/samples/AST - Australia.txt",
                       ]
            
    def test_list2paradox(self):
        nrs = [1, 101]
        for nr, fname in zip(nrs, self.fnames):
            result = paradox2list(fname)
            self.assertEqual(len(result), nr)











