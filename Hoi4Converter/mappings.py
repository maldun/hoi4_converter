#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import os
import copy
from . import converter as conv

MAP_MAP = {}


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

    
def retriver(func):
    MAP_MAP[func.__name__.upper()] = func
    return ObjectRetriever(func)


@retriver
def has_key(obj, key):
    if not isinstance(obj, list):
        return False
    if len(obj) > 1 and obj[0] == key:
        return True
    return False

@retriver
def has_value(obj, val):
    if obj == val:
        return True

    return False


@retriver
def has_key_and_val(obj, key_val):
    key, val = key_val
    if not isinstance(obj, list):
        return False
    if len(obj) > 1 and obj[0] == key and obj[1] == val:
        return True
    if len(obj) > 2 and obj[0] == key and obj[2] == val:
        try:
             if obj[1] in conv.RELS:
                 return True
        except:
            pass
                     
    return False

@retriver
def contains(obj, val):
    if isinstance(obj, list) is True:
        if val in obj:
            return True

    return False


@retriver
def is_relation_with_key(obj, key):
    if not isinstance(obj, list):
        return False
    if len(obj) > 2 and obj[0] == key and obj[1] in conv.RELS:
        return True

    return False

@retriver
def contains_multiple(obj, liste):
    if isinstance(obj, list) is True:
        if all(val in obj for val in liste):
            return True

        return False


class ObjectManipulator:
    def __init__(self, op):
        self._operation = op
    
    def _manipulate(self, obj, indices, *args):
        if len(indices) == 1:
            ind = indices[0]
            self._operation(obj, ind, *args)
            return obj
        
        inds = indices[1:]
        self._manipulate(obj[indices[0]], inds, *args)
        return obj

    def manipulate(self, obj, indices, *args):
        obj = copy.deepcopy(obj)
        return self._manipulate(obj, indices, *args)

    def __call__(self, obj, indices, *args):
        return self.manipulate(obj, indices, *args)

def operation(func):
    MAP_MAP[func.__name__.upper()] = func
    return ObjectManipulator(func)

    
@operation
def replace(obj, ind, to_replace):
    obj[ind] = to_replace


@operation
def remove(obj, ind, *args):
    del obj[ind]


@operation
def add(obj, ind, to_add):
    obj[ind] += [to_add]

    
@operation
def add_multiple(obj, ind, list_to_add):
    obj += list_to_add


@operation
def add_multiple_values(obj, ind, vals_to_add):
    val_ind = 1
    if obj[ind][1] in list(conv.RELS):
        val_ind = 2
    obj[ind][val_ind] += vals_to_add

   
def apply_map(obj, mapping, nr_found=False):
    source, target = mapping
    
    crit, val = source
    op, val2 = target

    found, inds = crit(obj, val)
    # Delete is always special ...
    # as it changes indices
    if op == remove:
        if len(found) == 0:
            if nr_found is False:
                return obj
            else:
                return obj, 0
        else:
            obj = op(obj, inds[0], found[0])
            if nr_found is False:
                return apply_map(obj, mapping)
            else:
                return apply_map(obj, mapping), len(found)
    
    for f, i in zip(found, inds):
        obj = op(obj, i, val2)

    if nr_found is False:
        return obj
    return obj, len(found)

def apply_maps_on_file(in_file, out_file, maps):
    obj = conv.paradox2list(in_file)
    nr_changes = 0
    for mapping in maps:
        res, nr_found = apply_map(obj, mapping, nr_found=True)
        if nr_found > 0:
            obj = list(res)
            nr_changes += nr_found
        #obj = apply_map(obj, mapping)
    if obj is not None and nr_changes > 0:
        with open(out_file, 'w', encoding=conv.UTF8) as file:
            content = conv.list2paradox(list(obj))
            file.write(content)
    else:
        print(f"No operations on {out_file}!")
    

########################
# Tests                #
########################
class ConverterTests(unittest.TestCase):
    def setUp(self):
        self.fnames = ["test/samples/r56_leader_portraits.gfx",
                       "test/samples/AST - Australia.txt",
                       "test/samples/r56i_laws_gender.txt",
                       "test/samples/r56i_laws_war.txt",
                       "test/samples/r56i_laws_leadership.txt",
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
        self.assertEqual(found[0][1][0], '"AST"')

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

    def test_contains2(self):
        obj = self.objects[1]
        val = ["AST_oversized_fleet"]
        found, inds = contains(obj, val)
        self.assertEqual(len(found[0]),4)

    def test_contains_multiple(self):
         obj = self.objects[2]
         val = [["original_tag", ["AST"]], ["original_tag", ["NZL"]]]
         found, inds = contains_multiple(obj, val)
         obj2 = found[0]
         found2, inds2 = has_key(obj2, "any_owned_state")
         self.assertEqual(len(found2), 1)

    def test_add_multiple(self):
        obj = self.objects[2]
        key = "has_government"
        val = "fascism"
        to_add = [[key, ["national_populist"]],
		 [key, ["paternal_autocrat"]],
                  ]
                  
        found, inds = has_key(obj, key)
        inds_found = [k for k, found in enumerate(found) if len(has_value(found, val)[0]) > 0]
        foundf = [found[k] for k in inds_found]
        indsf = [inds[k] for k in inds_found]

        for f, i in zip(foundf, indsf):
            obj = add_multiple(obj, i, to_add)

        found2, inds2 = has_key(obj, "modifier")
        for t in to_add:
            self.assertIn(t, found2[4][1])

    def test_has_key_and_val(self):
        obj = self.objects[2]
        key = "has_government"
        val = ["fascism"]
        to_add = [[key, ["national_populist"]],
		 [key, ["paternal_autocrat"]],
                  ]
        found, inds = has_key_and_val(obj, [key, val])
        self.assertEqual(len(found), 2)

        for f, i in zip(found, inds):
            obj = add_multiple(obj, i, to_add)

        found2, inds2 = has_key(obj, "modifier")
        for t in to_add:
            self.assertIn(t, found2[4][1])

    def test_has_key_and_val2(self):
        obj = self.objects[3]
        key = "has_government"
        val = ["fascism"]
        key_and_val = [key, val]

        found2, inds2 = has_key_and_val(obj, key_and_val)
        self.assertEqual(len(found2), 1)

    def test_mapping(self):
        obj = self.objects[2]
        key = "has_government"
        val = ["fascism"]
        to_add = [[key, ["national_populist"]],
		 [key, ["paternal_autocrat"]],
                  ]
        source = [has_key_and_val, [key, val]]
        target = [add_multiple, to_add]
        new_obj = apply_map(obj, (source, target))
        
        found2, inds2 = has_key(new_obj, "modifier")
        for t in to_add:
            self.assertIn(t, found2[4][1])

        source = [has_key_and_val, [key, val]]
        target = [remove, []]
        new_obj2 = apply_map(new_obj,(source, target))

        found2, inds2 = has_key(new_obj2, "modifier")
        self.assertNotIn([key, val], found2[4][1])

    def test_mapping2(self):
        obj = self.objects[4]
        key = "has_government"
        val = "fascism"
        mapping = [[has_key_and_val, [key, [val]]], [remove, [key,[val]]]]

        obj = apply_map(obj, mapping)
        found, ind = has_key_and_val(obj, [key, [val]])
        self.assertEqual(len(found), 0)

    def test_is_relation_with_key(self):
        obj = self.objects[4]
        key = "fascism"

        found, ind = is_relation_with_key(obj, key)
        self.assertGreater(len(found), 0)
        mapping = [[is_relation_with_key, key], [remove, key]]
        obj = apply_map(obj, mapping)
        found, ind = is_relation_with_key(obj, key)
        self.assertEqual(len(found), 0)

    def test_add2(self):
        obj = self.objects[2]
        key = "original_tag"
        val = "TUR"
        val2 = "OTT"
        mapping = [[has_key_and_val, [key, [val]]], [add, [key, [val2]]]]
        maps = [mapping]
        for mapping in maps:
            obj = apply_map(obj, mapping)
        found2, inds2 = has_value(obj, val2)
        self.assertEqual(len(found2),1)

    def test_add_multiple_vals(self):
        obj = self.objects[1]
        key = "set_technology"
        vals = [["etax_doctrine",[1]], ["camo", [1]]]
        mapping = [[has_key, key], [add_multiple_values, vals]]
        
        obj = apply_map(obj, mapping)
        found2, inds2 = has_key(obj, key)
        for val in vals:
            self.assertIn(val ,found2[1][1])
