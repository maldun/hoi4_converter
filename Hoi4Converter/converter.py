#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from . import parser
import unittest
import os

U8 = 'utf-8'

def paradox2list(filename_or_text):
    if os.path.isfile(filename_or_text):
        with open(filename_or_text, 'r', encoding=U8) as f:
            text = f.read()
    else:
        text = filename_or_text

    return parser.parse_grammar(text)

########################
# Tests                #
########################

class ConverterTests(unittest.TestCase):
    def setUp(self):
        self.fname = "../samples/r56_leader_portraits.gfx"
            
    def test_list2paradox(self):
        result = paradox2list(self.fname)
        self.assertEqual(len(result), 1)










