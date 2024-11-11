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
    upperEmphaticS = ['S','Ś', 'Ḍ']
    candidateString = substitute(candidate.strip(), upperEmphaticS, 'normal')
    a = ['a','ä']
    candidateString = substitute(candidate.strip(), a, 'normal')
    upperA = ['A','Ä']
    candidateString = substitute(candidate.strip(), upperA, 'normal')
    
    e = ['e','ǝ','ə','ē']
    candidateString = substitute(candidate.strip(), e, 'normal')
    upperE = ['E','Ǝ','Ē']
    candidateString = substitute(candidate.strip(), upperE, 'normal')
    
    w = ['w','ʷ']
    candidateString = substitute(candidate.strip(), w, 'normal')
    
    alay = ['ʾ', 'ʿ', '`']
    candidateString = substitute(candidate.strip(), alay, 'ws')
    
    laringals14 = ['ሀ', 'ሐ', 'ኀ', 'ሃ', 'ሓ', 'ኃ']
    candidateString = substitute(candidate.strip(), laringals14, 'normal')
    
    laringals2 = ['ሀ', 'ሐ', 'ኀ']
    candidateString = substitute(candidate.strip(), laringals2, 'normal')
    laringals3 = ['ሂ', 'ሒ', 'ኂ']
    candidateString = substitute(candidate.strip(), laringals3, 'normal')
    laringals4 = ['ሁ', 'ሑ', 'ኁ']
    candidateString = substitute(candidate.strip(), laringals4, 'normal')
    laringals5 = ['ሄ', 'ሔ', 'ኄ']
    candidateString = substitute(candidate.strip(), laringals5, 'normal')
    laringals6 = ['ህ', 'ሕ', 'ኅ']
    candidateString = substitute(candidate.strip(), laringals6, 'normal')
    laringals7 = ['ሆ', 'ሖ', 'ኆ']
    candidateString = substitute(candidate.strip(), laringals7, 'normal')
    
    ssound1 = ['ሠ','ሰ']
    candidateString = substitute(candidate.strip(), ssound1, 'normal')
    ssound2 = ['ሡ','ሱ']
    candidateString = substitute(candidate.strip(), ssound2, 'normal')
    ssound3 = ['ሢ','ሲ']
    candidateString = substitute(candidate.strip(), ssound3, 'normal')
    ssound4 = ['ሣ','ሳ']
    candidateString = substitute(candidate.strip(), ssound4, 'normal')
    ssound5 = ['ሥ','ስ']
    candidateString = substitute(candidate.strip(), ssound5, 'normal')
    ssound6 = ['ሦ','ሶ']
    candidateString = substitute(candidate.strip(), ssound6, 'normal')
    ssound7 = ['ሤ','ሴ']
    candidateString = substitute(candidate.strip(), ssound7, 'normal')
    
    emphaticT1 = ['ጸ', 'ፀ']
    candidateString = substitute(candidate.strip(), emphaticT1, 'normal')
    emphaticT2 = ['ጹ', 'ፁ']
    candidateString = substitute(candidate.strip(), emphaticT2, 'normal')
    emphaticT3 = ['ጺ', 'ፂ']
    candidateString = substitute(candidate.strip(), emphaticT3, 'normal')
    emphaticT4 = ['ጻ', 'ፃ']
    candidateString = substitute(candidate.strip(), emphaticT4, 'normal')
    emphaticT5 = ['ጼ', 'ፄ']
    candidateString = substitute(candidate.strip(), emphaticT5, 'normal')
    emphaticT6 = ['ጽ', 'ፅ']
    candidateString = substitute(candidate.strip(), emphaticT6, 'normal')
    emphaticT7 = ['ጾ', 'ፆ']
    candidateString = substitute(candidate.strip(), emphaticT7, 'normal')
    
    asounds14 = ['አ', 'ዐ', 'ኣ', 'ዓ']
    candidateString = substitute(candidate.strip(), asounds14, 'normal')
    
    asounds2 = ['ኡ', 'ዑ']
    candidateString = substitute(candidate.strip(), asounds2, 'normal')
    asounds3 = ['ኢ', 'ዒ']
    candidateString = substitute(candidate.strip(), asounds3, 'normal')
    asounds5 = ['ኤ', 'ዔ']
    candidateString = substitute(candidate.strip(), asounds5, 'normal')
    asounds6 = ['እ', 'ዕ']
    candidateString = substitute(candidate.strip(), asounds6, 'normal')
    asounds7 = ['ኦ', 'ዖ']
    candidateString = substitute(candidate.strip(), asounds7, 'normal')

def substitute(candidate: str, homophones: list, mode: str) -> list:
    options = []
    
    for homophone in homophones:
        if homophone in candidate:
            for homophone2 in homophones:
                if homophone2 != homophone:
                    for replaced in replace(candidate, homophone, homophone2, mode):
                        if replaced not in options:
                            options = options + [replaced]

    return options

def replace(candidate:str, match: str, substitute: str, mode: str) -> list:
    matchIndeces = [m.start() for m in re.finditer(match, candidate)]
    
    if len(matchIndeces) == 0:
        return [candidate]
    
    result = []
    for index in matchIndeces:
        byteList = list(candidate)
        byteList[index] = substitute
        newCandidate = ''.join(byteList)
        
        if mode == 'ws':
            newCandidate = newCandidate.replace(substitute, '')
        
        result = appendResult(result, candidate, newCandidate, replace(newCandidate, match, substitute, mode))
    return result

def appendResult(result: list, candidate: str, newCandidate: str, children: list):
    if candidate not in result:
        result = result + [candidate]
    if newCandidate not in result:
        result = result + [newCandidate]
    for child in children:
        if child not in result:
            result = result + [child]
    return result