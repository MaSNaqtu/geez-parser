#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 16:05:53 2024

@author: samuel
"""

import re
from lxml import etree
import requests

namespace = {'fidal': 'http://fidal.parser'}

# Expands candidates by performing substitutions and check against Dillman
def checkDill(candidates: list) -> list:
    lemmas = etree.parse('./in/morpho/lemmas.xml')
    
    dillmanCheck = []
    resultingLemmas = []
    for candidate in candidates:
        substitutions = substitutionsInCandidate(candidate)
        for lemma in lemmas.xpath('//fidal:lemma', namespaces=namespace):
            for child in lemma:
                if child.text in substitutions:
                    resultingLemmas = resultingLemmas + [lemma]
            continue
        
        for lemma in lemmas:
            entry = {
                'link': lemma.attrib['{http://www.w3.org/XML/1998/namespace}id'],
                'root': candidate
                }
            if entry not in dillmanCheck:
                dillmanCheck = dillmanCheck + [entry]
    
    for entry in dillmanCheck:
        #Apparently you need to specify a user-agent, no idea why though, I just took a random one
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
            'Connection': 'keep-alive'
            }
        url = 'https://betamasaheft.eu/Dillmann/lemma/' + entry['link'] + '.xml'
        response = requests.get(url, headers=headers)
        # If status code is 200 (OK), the candidate exists in Dillman, otherwise it would be 404 (NOT_FOUND)
        entry['inDillman'] = (response.status_code == 200)
    return dillmanCheck
    

# Expands candidates by executing all possible letter substitutions
def substitutionsInCandidate(candidate: str) -> list:
    candidateList = []
    # is the second s supposed to be ṣ or z or something?
    emphaticS = ['s','s', 'ḍ']
    candidateList = candidateList + substitute(candidate['root'].strip(), emphaticS, 'normal')
    upperEmphaticS = ['S','Ś', 'Ḍ']
    candidateList = candidateList + substitute(candidate['root'].strip(), upperEmphaticS, 'normal')
    a = ['a','ä']
    candidateList = candidateList + substitute(candidate['root'].strip(), a, 'normal')
    upperA = ['A','Ä']
    candidateList = candidateList + substitute(candidate['root'].strip(), upperA, 'normal')
    
    e = ['e','ǝ','ə','ē']
    candidateList = candidateList + substitute(candidate['root'].strip(), e, 'normal')
    upperE = ['E','Ǝ','Ē']
    candidateList = candidateList + substitute(candidate['root'].strip(), upperE, 'normal')
    
    w = ['w','ʷ']
    candidateList = candidateList + substitute(candidate['root'].strip(), w, 'normal')
    
    alay = ['ʾ', 'ʿ', '`']
    candidateList = candidateList + substitute(candidate['root'].strip(), alay, 'ws')
    
    laringals14 = ['ሀ', 'ሐ', 'ኀ', 'ሃ', 'ሓ', 'ኃ']
    candidateList = candidateList + substitute(candidate['root'].strip(), laringals14, 'normal')
    
    laringals2 = ['ሀ', 'ሐ', 'ኀ']
    candidateList = candidateList + substitute(candidate['root'].strip(), laringals2, 'normal')
    laringals3 = ['ሂ', 'ሒ', 'ኂ']
    candidateList = candidateList + substitute(candidate['root'].strip(), laringals3, 'normal')
    laringals4 = ['ሁ', 'ሑ', 'ኁ']
    candidateList = candidateList + substitute(candidate['root'].strip(), laringals4, 'normal')
    laringals5 = ['ሄ', 'ሔ', 'ኄ']
    candidateList = candidateList + substitute(candidate['root'].strip(), laringals5, 'normal')
    laringals6 = ['ህ', 'ሕ', 'ኅ']
    candidateList = candidateList + substitute(candidate['root'].strip(), laringals6, 'normal')
    laringals7 = ['ሆ', 'ሖ', 'ኆ']
    candidateList = candidateList + substitute(candidate['root'].strip(), laringals7, 'normal')
    
    ssound1 = ['ሠ','ሰ']
    candidateList = candidateList + substitute(candidate['root'].strip(), ssound1, 'normal')
    ssound2 = ['ሡ','ሱ']
    candidateList = candidateList + substitute(candidate['root'].strip(), ssound2, 'normal')
    ssound3 = ['ሢ','ሲ']
    candidateList = candidateList + substitute(candidate['root'].strip(), ssound3, 'normal')
    ssound4 = ['ሣ','ሳ']
    candidateList = candidateList + substitute(candidate['root'].strip(), ssound4, 'normal')
    ssound5 = ['ሥ','ስ']
    candidateList = candidateList + substitute(candidate['root'].strip(), ssound5, 'normal')
    ssound6 = ['ሦ','ሶ']
    candidateList = candidateList + substitute(candidate['root'].strip(), ssound6, 'normal')
    ssound7 = ['ሤ','ሴ']
    candidateList = candidateList + substitute(candidate['root'].strip(), ssound7, 'normal')
    
    emphaticT1 = ['ጸ', 'ፀ']
    candidateList = candidateList + substitute(candidate['root'].strip(), emphaticT1, 'normal')
    emphaticT2 = ['ጹ', 'ፁ']
    candidateList = candidateList + substitute(candidate['root'].strip(), emphaticT2, 'normal')
    emphaticT3 = ['ጺ', 'ፂ']
    candidateList = candidateList + substitute(candidate['root'].strip(), emphaticT3, 'normal')
    emphaticT4 = ['ጻ', 'ፃ']
    candidateList = candidateList + substitute(candidate['root'].strip(), emphaticT4, 'normal')
    emphaticT5 = ['ጼ', 'ፄ']
    candidateList = candidateList + substitute(candidate['root'].strip(), emphaticT5, 'normal')
    emphaticT6 = ['ጽ', 'ፅ']
    candidateList = candidateList + substitute(candidate['root'].strip(), emphaticT6, 'normal')
    emphaticT7 = ['ጾ', 'ፆ']
    candidateList = candidateList + substitute(candidate['root'].strip(), emphaticT7, 'normal')
    
    asounds14 = ['አ', 'ዐ', 'ኣ', 'ዓ']
    candidateList = candidateList + substitute(candidate['root'].strip(), asounds14, 'normal')
    
    asounds2 = ['ኡ', 'ዑ']
    candidateList = candidateList + substitute(candidate['root'].strip(), asounds2, 'normal')
    asounds3 = ['ኢ', 'ዒ']
    candidateList = candidateList + substitute(candidate['root'].strip(), asounds3, 'normal')
    asounds5 = ['ኤ', 'ዔ']
    candidateList = candidateList + substitute(candidate['root'].strip(), asounds5, 'normal')
    asounds6 = ['እ', 'ዕ']
    candidateList = candidateList + substitute(candidate['root'].strip(), asounds6, 'normal')
    asounds7 = ['ኦ', 'ዖ']
    candidateList = candidateList + substitute(candidate['root'].strip(), asounds7, 'normal')
    
    candidateList = list(set(candidateList))
    
    return candidateList

# Adds all possible substitutions to candidates
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

# If mode is ws removes the substitute, otherwise return all possible substitutions (through recursion)
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

# Avoids duplicates
def appendResult(result: list, candidate: str, newCandidate: str, children: list):
    if candidate not in result:
        result = result + [candidate]
    if newCandidate not in result:
        result = result + [newCandidate]
    for child in children:
        if child not in result:
            result = result + [child]
    return result