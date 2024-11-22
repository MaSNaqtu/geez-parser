#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 16:05:53 2024

@author: samuel
"""

import re
import xml.etree.ElementTree as ET
import requests

def checkDill(candidates: list) -> list:
    tree = ET.parse('./in/morpho/lemmas.xml')
    
    dillmanCheck = []
    for candidate in candidates:
        substitutions = substitutionsInCandidate(candidate)
        lemmas = []
        for lemma in tree.getroot().iter('{http://fidal.parser}lemma'):
            for child in lemma:
                if child.text in substitutions:
                    lemmas = lemmas + [lemma]
            continue
        
        for lemma in lemmas:
            entry = {
                'link': lemma.attrib['{http://www.w3.org/XML/1998/namespace}id'],
                'root': candidate
                }
            if entry not in dillmanCheck:
                dillmanCheck = dillmanCheck + [entry]
    
    for entry in dillmanCheck:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
            'Connection': 'keep-alive'
            }
        url = 'https://betamasaheft.eu/Dillmann/lemma/' + entry['link'] + '.xml'
        response = requests.get(url, headers=headers)
        continue
    

def substitutionsInCandidate(candidate: str) -> list:
    candidateList = []
    # is the second s supposed to be ṣ or z or something?
    emphaticS = ['s','s', 'ḍ']
    candidateList = candidateList + substitute(candidate.strip(), emphaticS, 'normal')
    upperEmphaticS = ['S','Ś', 'Ḍ']
    candidateList = candidateList + substitute(candidate.strip(), upperEmphaticS, 'normal')
    a = ['a','ä']
    candidateList = candidateList + substitute(candidate.strip(), a, 'normal')
    upperA = ['A','Ä']
    candidateList = candidateList + substitute(candidate.strip(), upperA, 'normal')
    
    e = ['e','ǝ','ə','ē']
    candidateList = candidateList + substitute(candidate.strip(), e, 'normal')
    upperE = ['E','Ǝ','Ē']
    candidateList = candidateList + substitute(candidate.strip(), upperE, 'normal')
    
    w = ['w','ʷ']
    candidateList = candidateList + substitute(candidate.strip(), w, 'normal')
    
    alay = ['ʾ', 'ʿ', '`']
    candidateList = candidateList + substitute(candidate.strip(), alay, 'ws')
    
    laringals14 = ['ሀ', 'ሐ', 'ኀ', 'ሃ', 'ሓ', 'ኃ']
    candidateList = candidateList + substitute(candidate.strip(), laringals14, 'normal')
    
    laringals2 = ['ሀ', 'ሐ', 'ኀ']
    candidateList = candidateList + substitute(candidate.strip(), laringals2, 'normal')
    laringals3 = ['ሂ', 'ሒ', 'ኂ']
    candidateList = candidateList + substitute(candidate.strip(), laringals3, 'normal')
    laringals4 = ['ሁ', 'ሑ', 'ኁ']
    candidateList = candidateList + substitute(candidate.strip(), laringals4, 'normal')
    laringals5 = ['ሄ', 'ሔ', 'ኄ']
    candidateList = candidateList + substitute(candidate.strip(), laringals5, 'normal')
    laringals6 = ['ህ', 'ሕ', 'ኅ']
    candidateList = candidateList + substitute(candidate.strip(), laringals6, 'normal')
    laringals7 = ['ሆ', 'ሖ', 'ኆ']
    candidateList = candidateList + substitute(candidate.strip(), laringals7, 'normal')
    
    ssound1 = ['ሠ','ሰ']
    candidateList = candidateList + substitute(candidate.strip(), ssound1, 'normal')
    ssound2 = ['ሡ','ሱ']
    candidateList = candidateList + substitute(candidate.strip(), ssound2, 'normal')
    ssound3 = ['ሢ','ሲ']
    candidateList = candidateList + substitute(candidate.strip(), ssound3, 'normal')
    ssound4 = ['ሣ','ሳ']
    candidateList = candidateList + substitute(candidate.strip(), ssound4, 'normal')
    ssound5 = ['ሥ','ስ']
    candidateList = candidateList + substitute(candidate.strip(), ssound5, 'normal')
    ssound6 = ['ሦ','ሶ']
    candidateList = candidateList + substitute(candidate.strip(), ssound6, 'normal')
    ssound7 = ['ሤ','ሴ']
    candidateList = candidateList + substitute(candidate.strip(), ssound7, 'normal')
    
    emphaticT1 = ['ጸ', 'ፀ']
    candidateList = candidateList + substitute(candidate.strip(), emphaticT1, 'normal')
    emphaticT2 = ['ጹ', 'ፁ']
    candidateList = candidateList + substitute(candidate.strip(), emphaticT2, 'normal')
    emphaticT3 = ['ጺ', 'ፂ']
    candidateList = candidateList + substitute(candidate.strip(), emphaticT3, 'normal')
    emphaticT4 = ['ጻ', 'ፃ']
    candidateList = candidateList + substitute(candidate.strip(), emphaticT4, 'normal')
    emphaticT5 = ['ጼ', 'ፄ']
    candidateList = candidateList + substitute(candidate.strip(), emphaticT5, 'normal')
    emphaticT6 = ['ጽ', 'ፅ']
    candidateList = candidateList + substitute(candidate.strip(), emphaticT6, 'normal')
    emphaticT7 = ['ጾ', 'ፆ']
    candidateList = candidateList + substitute(candidate.strip(), emphaticT7, 'normal')
    
    asounds14 = ['አ', 'ዐ', 'ኣ', 'ዓ']
    candidateList = candidateList + substitute(candidate.strip(), asounds14, 'normal')
    
    asounds2 = ['ኡ', 'ዑ']
    candidateList = candidateList + substitute(candidate.strip(), asounds2, 'normal')
    asounds3 = ['ኢ', 'ዒ']
    candidateList = candidateList + substitute(candidate.strip(), asounds3, 'normal')
    asounds5 = ['ኤ', 'ዔ']
    candidateList = candidateList + substitute(candidate.strip(), asounds5, 'normal')
    asounds6 = ['እ', 'ዕ']
    candidateList = candidateList + substitute(candidate.strip(), asounds6, 'normal')
    asounds7 = ['ኦ', 'ዖ']
    candidateList = candidateList + substitute(candidate.strip(), asounds7, 'normal')
    
    result = []
    for candidate in candidateList:
        if candidate not in result:
            result = result + [candidate]
    
    return result

def substitute(candidate: str, homophones: list, mode: str) -> list:
    result = []
    
    for homophone in homophones:
        if homophone in candidate:
            for homophone2 in homophones:
                if homophone2 != homophone:
                    for replaced in replace(candidate, homophone, homophone2, mode):
                        if replaced not in result:
                            result = result + [replaced]

    if len(result) == 0:
        return [candidate]
    return result

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