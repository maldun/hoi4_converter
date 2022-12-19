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

import os
import sys
sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import unittest
import Hoi4Converter
from Hoi4Converter import converter, mappings

MODULES = [converter, mappings]

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    # add tests to the test suite
    for module in MODULES:
        tests = loader.loadTestsFromModule(module)
        suite.addTests(tests)

    # initialize a runner, pass it your suite and run it
    runner = unittest.TextTestRunner(verbosity=3)
    result = runner.run(suite)

    nr_errors = len(result.errors)
    print(f"Errors: {nr_errors} tests with errors: \n")
    for test, res in result.errors:
        print(test, end=': \n\n')
        print(res)
    nr_failed = len(result.failures)
    print(f"Fail: {nr_failed} tests failed: \n")
    for test, res in result.failures:
        print(test, end=': \n\n')
        print(res)
    
    if not result.wasSuccessful():
        sys.exit(nr_failed + nr_errors)
