#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import unittest
import Hoi4Converter
from Hoi4Converter import converter



if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    # add tests to the test suite
    tests = loader.loadTestsFromModule(converter)
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
