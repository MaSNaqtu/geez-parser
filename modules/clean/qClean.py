#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 10:58:06 2024

@author: samuel
"""

import xml.etree.ElementTree as ET

def clean(query, fidal, transcriptionType, negative, quotative, interrogative):
    print('Processing Query' + str(query) + ':')
    proclitics = getProclitics()
    query = splitProclitics(proclitics, query)
    print(query)
    query = splitNegation(query, negative)
    print(query)
    query = splitQuotative(query, quotative)
    print(query)
    query = splitInterrogative(query, interrogative)
    print(query)
    query = splitSuffixes(query)
    print(query)
    query = splitAffixes(query)
    print(query)
    query = splitNumbers(query)
    print(query)
    query = removeColon(query)
    print(query)
    query = removeDuplicates(query)
    print(query)
    query.sort(key=sortQuery)
    print(query)
    print()
    return query

def splitProclitics(proclitics, query):
    for proclitic in proclitics:
        if query[0].startswith(proclitic.text):
            query = [query[0][0], query[0], query[0][1:]]
    return query

def splitNegation(query, negative):
    queryResult = []
    for q in query:
        if q[0] == negative['root']:
            queryResult = queryResult + [q[0], q, q[1:]]
        else:
            queryResult = queryResult + [q]
    return queryResult

def splitQuotative(query, quotative):
    queryResult = []
    for q in query:
        if q[-1] == quotative['root']:
            queryResult = queryResult + [q[0:-1], q[-1], q]
        else:
            queryResult = queryResult + [q]
    return queryResult

def splitInterrogative(query, interrogative):
    interrogativeValues = [value['root'] for value in interrogative]
    queryResult = []
    for q in query:
        if q[-1] in interrogativeValues:
            queryResult = queryResult + [q[0:-1], q[-1], q]
        else:
            queryResult = queryResult + [q]
    return queryResult

def splitSuffixes(query):
    tree = ET.parse('./in/morpho/particles.xml')
    root = tree.getroot()
    
    suf = []
    for particle in root.iter('{http://fidal.parser}particle'):
        if particle.attrib['position'] == 'suf':
            suf = suf + [particle.text]
            
    queryResult = []
    for q in query:
        if q[-1] in suf:
            queryResult = queryResult + [q[0:-1], q[-1], q]
        else:
            queryResult = queryResult + [q]
            
    return queryResult

def splitAffixes(query):
    tree = ET.parse('./in/morpho/particles.xml')
    root = tree.getroot()
    
    af = []
    for particle in root.iter('{http://fidal.parser}particle'):
        if particle.attrib['position'] == 'af':
            af = af + [particle.text]
            
    queryResult = []
    for q in query:
        if q[0] in af:
            queryResult = queryResult + [q[1:], q[0], q]
        else:
            queryResult = queryResult + [q]
            
    return queryResult

def splitNumbers(query):
    tree = ET.parse('./in/morpho/numbers.xml')
    root = tree.getroot()
    
    nums = []
    for number in root.iter('{http://fidal.parser}num'):
        nums = nums + [number.text]
    
    queryResult = []
    for q in query:
        if q[0] in nums:
            queryResult = queryResult + [q[1:], q[0], q]
        elif q[-1] in nums:
            queryResult = queryResult + [q[0:-1], q[-1], q]
        else:
            queryResult = queryResult + [q]
    return queryResult

def removeColon(query):
    queryResult = []
    for q in query:
        if q[-1] == ':':
            queryResult = queryResult + [q[0:-1]]
        else:
            queryResult = queryResult + [q]
    return queryResult

def removeDuplicates(query):
    queryResult = []
    for q in query:
        if q not in queryResult:
            queryResult = queryResult + [q]
    return queryResult
        

def getProclitics():
    proclitics = []
    tree = ET.parse('./in/morpho/proclitics.xml')
    root = tree.getroot()
    for proclitic in root.iter('{http://fidal.parser}proclitic'):
        proclitics = proclitics + [proclitic]
    tree = ET.parse('./in/morpho/pronouns.xml')
    root = tree.getroot()
    for proclitic in root.iter('{http://fidal.parser}proclitic'):
        proclitics = proclitics + [proclitic]
    return proclitics

def sortQuery(q):
    return len(q)