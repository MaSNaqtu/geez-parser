#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 15:30:55 2024

@author: samuel
"""

import xml.etree.ElementTree as ET
import re
from modules.query.dillman import checkDill

namespace = {'fidal': 'http://fidal.parser'}
    
def execute(query, fidal, negative, quotative, interrogatives, transcriptionType):
    for q in query:
        particles = getAllParticles(q, negative, quotative, interrogatives)
        nouns = formulas(q, 'noun', transcriptionType)

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

def formulas(candidate, formulaType, transcriptionType):
    lettersRoot = ET.parse('./in/morpho/letters.xml')
    consVowel = parseChars(candidate, formulaType, lettersRoot)
    possibleDesinences = desinences(consVowel, formulaType, lettersRoot, transcriptionType)
    formula1 = formula(consVowel, transcriptionType, lettersRoot)
    return

def formula(consVowel, transcriptionType, lettersRoot):
    formula = ''
    for i, conVowel in enumerate(consVowel):
        # TODO: Check if this is correct, original goes through letters again, not sure why
        formula = formula + str(conVowel['position']) + conVowel['transcription']
    return formula
    
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

def parseChars(candidate, formulaType, lettersRoot):
    if formulaType == 'noun':
        return standardNoun(candidate, lettersRoot)
        

def standardNoun(candidate, lettersRoot):
    letters = []
    
    for i, char in enumerate(candidate):
        # Find realization with text equal to character
        realization = lettersRoot.find(".//realization[. = '{}']".format(char), namespace)
        # Find realization and move up 2 levels to get letter
        letter = lettersRoot.find(".//realization[. = '{}']....".format(char), namespace)
        #I don't quite understandd what this means yet
        if (i == 0 and len(candidate) > 4 and (realization.text == 'መ' or realization.text == 'ም')):
            realizations = letter.find('realizations', namespace).findall('realization', namespace)
            first = realizations[1]
            transcription = letter.find('transcription', namespace).text
            for j, currentRealization in enumerate(realizations):
                if realization.text == currentRealization.text:
                    break
            letters.append({'char': char, 'firstOrder': first.text, 'order': j, 'transcription': transcription, 'name': 'prefix'})
        else:
            realizations = letter.find('realizations', namespace).findall('realization', namespace)
            first = realizations[1]
            transcription = letter.find('transcription', namespace).text
            for j, currentRealization in enumerate(realizations):
                if realization.text == currentRealization.text:
                    break
            letters.append({'char': char, 'firstOrder': first.text, 'position': i, 'order': j, 'transcription': transcription, 'name': 'syllab'})
    return letters

def desinences(consVowel, formulaType, lettersRoot, transcriptionType):
    if formulaType == 'noun':
        targetPatterns = ET.parse('./in/morpho/nounssuffixes.xml')
    else:
        targetPatterns = ET.parse('./in/morpho/conjugation.xml')
    pseudoTrans = charsToPseudoTranscription(consVowel, formulaType, lettersRoot, transcriptionType)
    desinences = []
    for transcription in pseudoTrans:
        affixes = [pattern.text for pattern in targetPatterns.findall('.//{http://fidal.parser}affix')]
        for affix in affixes:
            cleanAffix = affix.replace('kk', 'k').replace('tt', 't').replace('nn', 'n')
            if len(cleanAffix) == 1:
                countAffix = 0
            else:
                affixChars = transcriptionToChars(cleanAffix, 0, 'BM', lettersRoot)
                countAffix = len(affixChars)
                if (transcription.endswith(cleanAffix)):
                    desinenceObject = desinence(targetPatterns, affix)
                    desinenceObject['length'] = len(consVowel) - countAffix
                    desinences = desinences + [desinenceObject]
                # What does this mean?
                if (transcription.endswith('ǝ') and transcription.startswith('^')):
                    desinenceObject = desinence(targetPatterns, affix)
                    desinenceObject['length'] = len(consVowel)
                    desinences = desinences + [desinenceObject]
    return desinences
                    

def desinence(targetPatterns, affix):
    affixPattern = ".//{http://fidal.parser}affix[. = '" + affix +"']"
    # Not sure why last in code, results in all the same thing, wrong understanding maybe?
    # gender = targetPatterns.find(affixPattern + "......").findall("{http://fidal.parser}gender")[-1].attrib['type']
    # person = targetPatterns.find(affixPattern + "........").findall("{http://fidal.parser}person")[-1].attrib['type']
    # number = targetPatterns.find(affixPattern + "..........").findall("{http://fidal.parser}num")[-1].attrib['type']
    # mode = targetPatterns.find(affixPattern + "............").findall("{http://fidal.parser}type")[-1].attrib['name']
    # affixType = targetPatterns.find(affixPattern + "..............").findall("{http://fidal.parser}group")[-1].attrib['name']
    
    # Use info of current one because of above confusion
    gender = targetPatterns.find(affixPattern + "....").attrib['type']
    person = targetPatterns.find(affixPattern + "......").attrib['type']
    number = targetPatterns.find(affixPattern + "........").attrib['type']
    mode = targetPatterns.find(affixPattern + "..........").attrib['name']
    affixType = targetPatterns.find(affixPattern + "............").attrib['name']
    
    return {
        'gender': gender,
        'person': person,
        'number': number,
        'mode': mode,
        'type': affixType
    }

def charsToPseudoTranscription(chars, formulaType, lettersRoot, transcriptionType):
    result = []
    for char in chars:
        partOne = char['transcription']
        transcription = lettersRoot.find('transcription[@type="{}"]'.format(transcriptionType), namespace)
        vowel = transcription.findall('vowel', namespace)[char['order'] + 1].text
        charTranscription = char['transcription']
        result = result + [charTranscription + vowel]
    return result
    
def transcriptionToChars(transcription, position, transcriptionType, lettersRoot):
    transcriptionTag = lettersRoot.find('transcription[@type="{}"]'.format(transcriptionType), namespace)
    vowelTags = transcriptionTag.findall('vowel')
    vowels = ''
    for vowel in vowelTags:
        if vowel.text is not None:
            vowels = vowels + vowel.text
    # This matches text that starts with one consonant followed by any number of ʷ (including none) and then any number of the vowels in the chosen transcription (including none)
    regex = re.compile('(([ṭṗṣḍḫčḥśʿʾbcdfghlmnpqrstvzwyxk])(ʷ?[' + vowels +']?))')
    allMatches = regex.findall(transcription)
    
    chars = []
    for full, consonant, vowel in allMatches:
        for i, vowelTag in enumerate(vowelTags):
            if vowelTag.text is not None and vowelTag.text == vowel:
                order = i
                fidal = vowelTag.text
                first = vowelTags[1]
                chars = chars + [{
                    'char': fidal,
                    'firstOrder': first,
                    'position': position,
                    'order': order,
                    'transcription': vowel
                }]
        
    return chars