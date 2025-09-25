#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 10:58:06 2024

@author: samuel
"""

import constants

namespaces={'fidal':'http://fidal.parser'}

def clean(query, fidal, transcription_type, negation, quotation, interrogative):
    #TODO:check if it is really fidal
    print('Processing Query' + str(query) + ':')
    # Declares namespace and finds the text of all proclitics
    proclitic_list = constants.PROCLITICS.xpath('//fidal:proclitic/text()', namespaces=namespaces)
    proclitic_list = proclitic_list + constants.PRONOUNS.xpath('//fidal:proclitic/text()', namespaces=namespaces)
    query = split_proclitics(query, proclitic_list)
    print(query)
    query = split_negation(query, negation)
    print(query)
    query = split_quotation(query, quotation)
    print(query)
    query = split_interrogative(query, interrogative)
    print(query)
    query = split_suffixes(query)
    print(query)
    query = split_affixes(query)
    print(query)
    query = split_numbers(query)
    print(query)
    query = remove_colon(query)
    print(query)
    query = list(set(query))
    print(query)
    query.sort(key=sort_query)
    print(query)
    print()
    return query

# If query starts with proclitic expand to [proclitic, query, query without proclitic]
def split_proclitics(query, proclitics):
    for proclitic in proclitics:
        if query[0].startswith(proclitic):
            return [proclitic, query[0], query[0].replace(proclitic, '', 1)]
    return query

# If one part of the query starts with negation expand to [negation, query, query without negation]
def split_negation(query, negation):
    query_result = []
    for q in query:
        if q.startswith(negation):
            query_result = query_result + [negation, q, q.replace(negation, '', 1)]
        else:
            query_result = query_result + [q]
    return query_result

# If query ends with quotation expand to [query without quotation, quotation, query]
def split_quotation(query, quotation):
    query_result = []
    for q in query:
        if q.endswith(quotation):
            query_result = query_result + [q[0:-1], quotation, q]
        else:
            query_result = query_result + [q]
    return query_result

# If query ends with interrogation expand to [query without interrogation, interrogation, query]
def split_interrogative(query, interrogation):
    query_result = []
    for q in query:
        # Two interrogative particles, so we need to check if the last letter is in  the list.
        if q[-1] in interrogation:
            query_result = query_result + [q[0:-1], q[-1], q]
        else:
            query_result = query_result + [q]
    return query_result

# If query ends with suffix expand to [query without suffix, suffix, query]
def split_suffixes(query):
    #Find suffixes
    suf = constants.PARTICLES.xpath('//fidal:particle[@position="suf"]/text()', namespaces=namespaces)
            
    query_result = []
    for q in query:
        if q[-1] in suf:
            query_result = query_result + [q[0:-1], q[-1], q]
        else:
            query_result = query_result + [q]
            
    return query_result

# If query starts with affix expand to [query without affix, affix, query] (Not sure why ordering is different for other affixes like negation)
def split_affixes(query):
    af = constants.PARTICLES.xpath('//fidal:particle[@position="af"]/text()', namespaces=namespaces)
            
    query_result = []
    for q in query:
        if q[0] in af:
            query_result = query_result + [q[1:], q[0], q]
        else:
            query_result = query_result + [q]
            
    return query_result

# If query starts or ends with number expand to [query without number, number, query]
def split_numbers(query):
    nums = constants.NUMBERS.xpath('//fidal:num/text()', namespaces=namespaces)
    
    query_result = []
    for q in query:
        if q[0] in nums:
            query_result = query_result + [q[1:], q[0], q]
        elif q[-1] in nums:
            query_result = query_result + [q[0:-1], q[-1], q]
        else:
            query_result = query_result + [q]
    return query_result

# If there is a colon remove
def remove_colon(query):
    query_result = []
    for q in query:
        if q[-1] == ':':
            query_result = query_result + [q[0:-1]]
        else:
            query_result = query_result + [q]
    return query_result

def sort_query(q):
    return len(q)