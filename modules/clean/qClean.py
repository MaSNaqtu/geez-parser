#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 10:58:06 2024

@author: samuel
"""

from lxml import etree

namespaces={'fidal':'http://fidal.parser'}

def clean(query, fidal, transcriptionType, negation, quotation, interrogation):
    #TODO:check if it is really fidal
    print('Processing Query' + str(query) + ':')
    proclitics = etree.parse('./in/morpho/proclitics.xml')
    pronouns = etree.parse('./in/morpho/pronouns.xml')
    # Declares namespace and finds the text of all proclitics
    procliticList = proclitics.xpath('//fidal:proclitic/text()', namespaces=namespaces)
    procliticList = procliticList + pronouns.xpath('//fidal:proclitic/text()', namespaces=namespaces)
    query = splitProclitics(procliticList, query)
    print(query)
    query = splitNegation(query, negation)
    print(query)
    query = splitQuotation(query, quotation)
    print(query)
    query = splitInterrogation(query, interrogation)
    print(query)
    query = splitSuffixes(query)
    print(query)
    query = splitAffixes(query)
    print(query)
    query = splitNumbers(query)
    print(query)
    query = removeColon(query)
    print(query)
    query = list(set(query))
    print(query)
    query.sort(key=sortQuery)
    print(query)
    print()
    return query

# If query starts with proclitic expand to [proclitic, query, query without proclitic]
def splitProclitics(proclitics, query):
    for proclitic in proclitics:
        if query[0].startswith(proclitic):
            query = [query[0][:len(proclitic)], query[0], query[0][len(proclitic):]]
    return query

# If query starts with negation expand to [negation, query, query without negation]
def splitNegation(query, negation):
    queryResult = []
    for q in query:
        if q[0] == negation:
            queryResult = queryResult + [q[0], q, q[1:]]
        else:
            queryResult = queryResult + [q]
    return queryResult

# If query ends with quotation expand to [query without quotation, quotation, query]
def splitQuotation(query, quotation):
    queryResult = []
    for q in query:
        if q[-1] == quotation:
            queryResult = queryResult + [q[0:-1], q[-1], q]
        else:
            queryResult = queryResult + [q]
    return queryResult

# If query ends with interrogation expand to [query without interrogation, interrogation, query]
def splitInterrogation(query, interrogation):
    queryResult = []
    for q in query:
        if q[-1] in interrogation:
            queryResult = queryResult + [q[0:-1], q[-1], q]
        else:
            queryResult = queryResult + [q]
    return queryResult

# If query ends with suffix expand to [query without suffix, suffix, query]
def splitSuffixes(query):
    particles = etree.parse('./in/morpho/particles.xml')
    
    
    #Find suffixes
    suf = particles.xpath('//fidal:particle[@position="suf"]/text()', namespaces=namespaces)
            
    queryResult = []
    for q in query:
        if q[-1] in suf:
            queryResult = queryResult + [q[0:-1], q[-1], q]
        else:
            queryResult = queryResult + [q]
            
    return queryResult

# If query starts with affix expand to [query without affix, affix, query] (Not sure why ordering is different for other affixes like negation)
def splitAffixes(query):
    particles = etree.parse('./in/morpho/particles.xml')
    
    
    af = particles.xpath('//fidal:particle[@position="suf"]/text()', namespaces=namespaces)
            
    queryResult = []
    for q in query:
        if q[0] in af:
            queryResult = queryResult + [q[1:], q[0], q]
        else:
            queryResult = queryResult + [q]
            
    return queryResult

# If query starts or ends with number expand to [query without number, number, query]
def splitNumbers(query):
    numbers = etree.parse('./in/morpho/numbers.xml')
    
    
    nums = numbers.xpath('//fidal:num/text()', namespaces=namespaces)
    
    queryResult = []
    for q in query:
        if q[0] in nums:
            queryResult = queryResult + [q[1:], q[0], q]
        elif q[-1] in nums:
            queryResult = queryResult + [q[0:-1], q[-1], q]
        else:
            queryResult = queryResult + [q]
    return queryResult

# If there is a colon remove
def removeColon(query):
    queryResult = []
    for q in query:
        if q[-1] == ':':
            queryResult = queryResult + [q[0:-1]]
        else:
            queryResult = queryResult + [q]
    return queryResult

def sortQuery(q):
    return len(q)