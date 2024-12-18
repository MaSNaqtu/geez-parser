#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 22:29:46 2024

@author: samuel
"""

import unittest
from modules.query.dillman import checkDill
import requests

class TestStringMethods(unittest.TestCase):

    def test_replace(self):     
        self.assertEqual(['ab'], checkDill.replace('ab', 'c', 'd', 'normal'))
        
        result1 = checkDill.replace('ab', 'a', 'c', 'normal')
        result1.sort()
        self.assertEqual(['ab', 'cb'], result1)
        
        result2 = checkDill.replace('aba', 'a', 'c', 'normal')
        result2.sort()
        self.assertEqual(['aba', 'abc', 'cba', 'cbc'],  result2)
        
        result3 = checkDill.replace('b', 'a', 'c', 'ws')
        result3.sort()
        self.assertEqual(['b'],  result3)
        
    def test_substitutionsInQuery(self):
        result1 = checkDill.substitutionsInCandidate('ሠለሠ')
        result1.sort()
        answer1 = ['ሠለሠ', 'ሰለሠ', 'ሰለሰ', 'ሠለሰ']
        answer1.sort()
        self.assertEqual(answer1, result1)

if __name__ == '__main__':
    unittest.main()