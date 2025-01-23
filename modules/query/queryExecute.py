#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 15:30:55 2024

@author: samuel
"""

import xml.etree.ElementTree as ET
from modules.query.dillman import checkDill

namespace = {'fidal': 'http://fidal.parser'}

def execute(query, fidal, negative, quotative, interrogatives):
    particles = getAllParticles(query, negative, quotative, interrogatives)
    nouns = formulas(query, 'noun')
    
def getAllParticles(query, negative, quotative, interrogatives):
    candidates = [negative['root'], quotative['root']]
    for pronoun in getPronouns(query):
        candidates = candidates + [pronoun['root']]
    for proclitic in getProclitic(query):
        candidates = candidates + [proclitic['root']]
    for interrogative in interrogatives:
        for candidate in query:
            if candidate == interrogative['root']:
                candidates = candidates + [interrogative['root']]
    for particle in getParticles(query):
        candidates = candidates + [particle['root']]

    #Unused?
    numbers = getNumbers()
    return checkDill.checkDill(candidates)

def formulas(query, formulaType):
    consVowel = parseChars(query, formulaType)
    possibleDesiences = desiences(consVowel, formulaType)
    return
    
# Get pronouns with info group name (e.g. demonstrative), type (e.g. nominative) and their forms
def getPronouns(query):
    tree = ET.parse('./in/morpho/pronouns.xml')
    root = tree.getroot()
    
    pronouns = []
    for candidate in query:
        matchingPronouns = getPronoun(candidate, root)
        pronouns = pronouns + matchingPronouns

    return pronouns

# Finds pronouns matching the candidate, finds its root, and returns group, type, forms, and the root
def getPronoun(candidate, root):
    pronouns = []
    for group in root:
        for pType in group:
            for num in pType:
                for gender in num:
                    for child in gender:
                        if child.text == candidate:
                            types = group.findall('{http://fidal.parser}type')
                            for rootType in types:
                                if rootType.attrib['name'] == 'nominative':
                                    root = getRoot(group)
                                    forms = getForms(group, pType)
                                    pronoun = {
                                        'solution': {
                                            'pos': 'pronoun',
                                            'group': group.attrib['name'],
                                            'type': pType.attrib['name'],
                                            'forms': forms
                                            },
                                        'root': root
                                        }
                                    pronouns = pronouns + [pronoun]
    return pronouns

# Gets the root (nominative, Singular, Masculine) of the pronoun
def getRoot(group):
    for pType in group:
        if pType.attrib['name'] == 'nominative':
            for num in pType:
                if num.attrib['type'] == 'Singular':
                    for gender in num:
                        if gender.attrib['type'] == 'Masculine':
                            return gender.find('{http://fidal.parser}full').text


 # Gets forms with infos type, gender, and number
def getForms(group, pType):
    forms = []
    for num in pType:
        for gender in num:
            form = {
                'desinence': {
                    'group': 'pronoun ' + group.attrib['name'],
                    'gender': gender.attrib['type'] if 'type' in gender.attrib else 'N/A',
                    'number': num.attrib['type']
                    }
                }
            forms = forms + [form]
    return forms

def getProclitic(query):
    tree = ET.parse('./in/morpho/proclitics.xml')
    root = tree.getroot()
    results = []
    for candidate in query:
        for child in root:
            if (child.text == candidate):
                result = {
                    'solution': {
                        'pos': 'proclitics',
                        },
                    'root': child.text
                    }
                results = results + [result]
    return results

def getParticles(query):
    tree = ET.parse('./in/morpho/particles.xml')
    root = tree.getroot()
    particles = []
    for candidate in query:
        for particle in root:
            if particle.text == candidate:
                particles = particles + [{
                    'solution': {
                        'pos': 'particle',
                        'type': particle.attrib['type']
                        },
                    'root': particle.text
                    }]
    return particles

def getNumbers():
    tree = ET.parse('./in/morpho/numbers.xml')
    root = tree.getroot()
    numbers = []
    
    for number in root:
        numbers = numbers + [{
            'solution': {
                'pos': 'numeral',
                'type': number.attrib['val']
                },
            'root': number.text
            }]
    return numbers

def parseChars(query, formulaType):
    if formulaType == 'noun':
        return standardNoun(query)

def standardNoun(query):
    tree = ET.parse('./in/morpho/letters.xml')
    nouns = []
    
    for i, char in enumerate(query[0]):
        realization = tree.find(".//realization[. = '{}']".format(char), namespace)
        letter = tree.find(".//realization[. = '{}']....".format(char), namespace)
        if (i == 1 and len(query[0]) > 4 and (realization == 'መ' or realization == 'ም')):
            realizations = letter.find('realizations', namespace).findall('realization', namespace)
            first = realizations[1]
            transcription = letter.find('transcription', namespace).text
            for j, currentRealization in enumerate(realizations):
                if realization.text == currentRealization.text:
                    break
            nouns.append({'char': char, 'firstOrder': first.text, 'order': j, 'transcription': transcription})
        else:
            realizations = letter.find('realizations', namespace).findall('realization', namespace)
            first = realizations[1]
            transcription = letter.find('transcription', namespace).text
            for j, currentRealization in enumerate(realizations):
                if realization.text == currentRealization.text:
                    break
            nouns.append({'char': char, 'firstOrder': first.text, 'position': i, 'order': j, 'transcription': transcription})
    return nouns

def desiences(consVowel, formulaType):
    if formulaType == 'noun':
        targetPatterns = ET.parse('./in/morpho/nounssuffixes.xml')
    else:
        targetPatterns = ET.parse('./in/morpho/conjugation.xml')
    pseudoTrans = charsToPseudoTranscription(consVowel, formulaType)
    for transcription in pseudoTrans:
        for affix in targetPatterns:
            cleanAffix = affix.replace('kk', 'k').replace('tt', 't').replace('nn', 'n')

def charsToPseudoTranscription(chars, formulaType):
    tree = ET.parse('./in/morpho/letters.xml')
    result = []
    for char in chars:
        partOne = char['transcription']
        transcription = tree.find('transcription[@type="BM"]', namespace)
        vowel = transcription.findall('vowel', namespace)[char['order'] + 1].text
        charTranscription = char['transcription']
        result = result + [charTranscription + vowel]
    return result
    