#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 16:05:53 2024

@author: samuel
"""

import re

def checkDill(candidates: list):
    for candidate in candidates:
        substitutionsInCandidate(candidate)

def substitutionsInCandidate(candidate: str):
    # is the second s supposed to be ṣ or z or something?
    emphaticS = ['s','s', 'ḍ']
    candidateString = substitute(candidate.strip(), emphaticS, 'normal')

def substitute(candidate: str, homophones: list, mode: str):
    for homophone in homophones:
        for q in candidate:
            if homophone in candidate:
                options = []
                for homophone2 in homophones:
                    if homophone != homophone2:
                        replace([candidate], homophone, homophone2)
                        continue

def replace(candidate:list, match: str, substitute: int) -> list:
    matchIndeces = [m.start() for m in re.finditer(match, candidate)]
    
    if len(matchIndeces) == 0:
        return candidate
    
    newStrings = []
    for index in matchIndeces:
        newCandidate = candidate
        newCandidate[index] = substitute
        newStrings = newStrings + [replace(newCandidate, match, substitute)]
    
    return newStrings
            