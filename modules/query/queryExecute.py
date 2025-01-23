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
    for q in query:
        particles = getAllParticles(q, negative, quotative, interrogatives)
        nouns = formulas(q, 'noun')

def getAllParticles(candidate, negative, quotative, interrogatives):
    candidates = []
    if candidate == negative['root']:
        candidates = candidates + negative['root']
    if candidate == quotative['root']:
        candidates = candidates + quotative['root']

    for pronoun in getPronouns(candidate):
        candidates = candidates + [pronoun['root']]
    for proclitic in getProclitic(candidate):
        candidates = candidates + [proclitic['root']]
    for interrogative in interrogatives:
        if candidate == interrogative['root']:
            candidates = candidates + [interrogative['root']]
    for particle in getParticles(candidate):
        candidates = candidates + [particle['root']]

    #Unused?
    numbers = getNumbers()
    return checkDill.checkDill(candidates)

def formulas(candidate, formulaType):
    consVowel = parseChars(candidate, formulaType)
    possibleDesiences = desiences(consVowel, formulaType)
    return

# Get pronouns with info group name (e.g. demonstrative), type (e.g. nominative) and their forms
def getPronouns(candidate):
    tree = ET.parse('./in/morpho/pronouns.xml')
    root = tree.getroot()
    
    return getPronoun(candidate, root)

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

def getProclitic(candidate):
    tree = ET.parse('./in/morpho/proclitics.xml')
    root = tree.getroot()
    results = []
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

def getParticles(candidate):
    tree = ET.parse('./in/morpho/particles.xml')
    root = tree.getroot()
    particles = []
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

def parseChars(candidate, formulaType):
    if formulaType == 'noun':
        return standardNoun(candidate)
        

def standardNoun(candidate):
    tree = ET.parse('./in/morpho/letters.xml')
    nouns = []
    
    for i, char in enumerate(candidate):
        realization = tree.find(".//realization[. = '{}']".format(char), namespace)
        letter = tree.find(".//realization[. = '{}']....".format(char), namespace)
        if (i == 1 and len(candidate) > 4 and (realization.text == 'መ' or realization.text == 'ም')):
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
    