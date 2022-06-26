#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import os
import copy
from . import converter as conv

HAS_VAL = "HAS_VALUE"
HAS_KEY = "HAS_KEY"
HAS_OBJ = "HAS_OBJECT"


class ObjectRetriever:
    def __init__(self, criterium):
        self.criterium = criterium
        
    def search(self, liste, reference, indices=None):
        
        if indices is None:
            indices = []
        objects = []
        index_list = []
        
        for ind, member in enumerate(liste):
            if self.criterium(member, reference) is True:
                objects += [member]
                index_list += [indices + [ind]]
                #return member, indices + [ind]
            if isinstance(member, list):
                obj_list, inds_list = self.search(member, reference,
                                              indices=indices + [ind])
                objects += obj_list
                index_list += inds_list 
                
        return objects, index_list

    def __call__(self, liste, reference):
        return self.search(liste, reference)


def _has_key(obj, key):
    if not isinstance(obj, list):
        return False
    if len(obj) > 1 and obj[0] == key:
        return True
    return False


has_key = ObjectRetriever(_has_key)


def _has_value(obj, val):
    if obj == val:
        return True

    return False


has_value = ObjectRetriever(_has_value)


def _contains(obj, val):
    if isinstance(obj, list) is True:
        if val in obj:
            return True

    return False


contains = ObjectRetriever(_contains)


class ObjectManipulator:
    def _manipulate(self, obj, indices, *args):
        if len(indices) == 1:
            ind = indices[0]
            self._operation(obj, ind, *args)
            return obj
        
        inds = indices[1:]
        self._manipulate(obj[indices[0]], inds, *args)
        return obj
        

class Replacer(ObjectManipulator):
    def _operation(self, obj, ind, to_replace):
        obj[ind] = to_replace

    def __call__(self, obj, indices, to_replace):
        obj = copy.deepcopy(obj)
        self._manipulate(obj, indices, to_replace)

replace = Replacer()

class Remover(ObjectManipulator):
    def _operation(self, obj, ind):
        del obj[ind]

    def __call__(self, obj, indices):
        return self._manipulate(obj, indices)

remove = Remover()


def paradox_remove(liste):
    pass

def paradox_add(liste):
    pass

def paradox_change(liste):
    pass


########################
# Tests                #
########################
class ConverterTests(unittest.TestCase):
    def setUp(self):
        self.fnames = ["test/samples/r56_leader_portraits.gfx",
                       "test/samples/AST - Australia.txt",
                       "test/samples/r56i_laws_gender.txt",
                       ]
        self.objects = [conv.paradox2list(fname) for fname in self.fnames]

    def test_has_key(self):
        obj = self.objects[2]
        key = "has_country_leader"

        found, inds = has_key.search(obj, key)
        self.assertEqual(found[0][0], key)
        self.assertEqual(len(found),3)
        found2, inds2 = has_key(obj, key)
        self.assertEqual(found, found2)
        self.assertEqual(inds, inds2)

    def test_has_key2(self):
        obj = self.objects[1]
        key = "oob"

        found, inds = has_key.search(obj, key)
        self.assertEqual(len(found),1)
        self.assertEqual(found[0][1][0], "AST")

    def test_remove(self):
        obj = self.objects[2]
        key = "has_country_leader"
        found, inds = has_key.search(obj, key)
        obj2 = remove(obj, inds[0])
        found2, inds2 = has_key.search(obj2, key)
        self.assertEqual(len(found2), 2)
        for k in range(2):
            self.assertIn(inds2[k], inds)
        
    def test_has_value(self):
        obj = self.objects[1]
        val = ["infantry_weapons", [1]]

        found, inds = has_value.search(obj, val)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0], val)

    def test_contains(self):
        obj = self.objects[1]
        val = ["infantry_weapons", [1]]

        found, inds = contains(obj, val)
        self.assertEqual(len(found), 1)
        self.assertIn(val, found[0])

