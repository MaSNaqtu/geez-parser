#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 15:30:55 2024

@author: samuel
"""

import re

import constants
from modules.query.dillman import checkDill

namespace = {'fidal': 'http://fidal.parser'}
    
def execute(query, fidal, negative, quotative, interrogatives, transcription_type):
    for q in query:
        particles = get_all_particles(q, negative, quotative, interrogatives)
        nouns = formulas(q, 'noun', transcription_type)


def get_all_particles(candidate, negative, quotative, interrogatives):
    candidates = []
    # Get element with text matching candidate
    pronoun_matches = constants.PRONOUNS.xpath(f"//fidal:*[text()='{candidate}']", namespaces=namespace)
    for match in pronoun_matches:
        # Get root (full nominative, singular, masculine form of the group) by traversing group -> type -> num -> gender -> full
        root = match.xpath("ancestor::fidal:group/fidal:type[@name='nominative']/fidal:num[@type='Singular']/fidal:gender[@type='Masculine']/fidal:full", namespaces=namespace)[0]
        candidates = candidates + [{
            'solution': {
                'pos': 'pronoun',
                'group': match.xpath("ancestor::fidal:group/@name", namespaces=namespace)[0],
                'type': match.xpath("ancestor::fidal:type/@name", namespaces=namespace)[0],
                'forms': {
                    'desinence': {
                        'gender': match.xpath("ancestor::fidal:gender/@type", namespaces=namespace),
                        'number': match.xpath("ancestor::fidal:num/@type", namespaces=namespace)
                    }
                }
            },
            'root': root.text
        }]

    proclitic_matches = constants.PROCLITICS.xpath(f"//fidal:proclitic[text()='{candidate}']", namespaces=namespace)
    for proclitic in proclitic_matches:
        candidates = candidates + [{
            'solution': {
                'pos': 'proclitic'
                },
            'root': proclitic.text
            }]

    if candidate == negative:
        candidates = candidates + [{
            'solution': {
                'pos': 'proclitic',
                'type': 'negative'
                },
            'root': negative
            }]

    if candidate == quotative:
        candidates = candidates + [{
            'solution': {
                'pos': 'quotative particle',
                'type': 'quotative'
                },
            'root': quotative
            }]

    for interrogative in interrogatives:
        if candidate == interrogative:
            candidates = candidates + [{
                'solution': {
                    'pos': 'interrogative particle',
                    'type': 'interrogative'
                    },
                'root': interrogative
                }]

    particle_matches = constants.PARTICLES.xpath(f"//fidal:particle[text()='{candidate}']", namespaces=namespace)
    for particle in particle_matches:
        if particle.text == candidate:
            candidates = candidates + [{
                'solution': {
                    'pos': 'particle',
                    'type': particle.get('type')
                    },
                'root': particle.text
                }]

    number_matches = constants.NUMBERS.xpath(f"//fidal:num[text()='{candidate}']", namespaces=namespace)
    for number in number_matches:
        if number.text == candidate:
            candidates = candidates + [{
                'solution': {
                    'pos': 'numeral',
                    'type': number.get('val')
                    },
                'root': number.text
                }]

    # Access to online Dillmann taken down, so this will not access the dictionary
    return checkDill.checkDill(candidates)

def formulas(candidate, formula_type, transcription_type):
    cons_vowel = parse_chars(candidate, formula_type)
    possible_desinences = desinences(cons_vowel, formula_type, transcription_type)
    formula = get_formula(cons_vowel, transcription_type)
    return

def get_formula(consVowel, transcriptionType):
    formula = ''
    for i, conVowel in enumerate(consVowel):
        # Seperate in original, but seem identical
        if conVowel['name'] == 'prefix' or conVowel['name'] == 'suffix':
            transcriptions = constants.LETTERS.xpath('//vowel[parent::transcription[@type="{}"]]'.format(transcriptionType))
            formula = formula + conVowel['transcription']
            transcription = transcriptions[conVowel['order']].text
            # This seems weird, check
            if transcription is not None:
                formula = formula + transcription
        else:
            prefix_count = len([conVowel for conVowel in consVowel if conVowel['name'] == 'prefix'])
            transcriptions = constants.LETTERS.xpath('//vowel[parent::transcription[@type="{}"]]'.format(transcriptionType))
            formula = formula + str(conVowel['position'] - prefix_count)
            transcription = transcriptions[conVowel['order']].text
            # This seems weird
            if transcription is not None:
                formula = formula + transcription
            
    return formula

def parse_chars(candidate, formula_type):
    if formula_type == 'noun':
        return standard_noun(candidate)


def standard_noun(candidate):
    letters = []

    for i, char in enumerate(candidate):

        realizations = constants.LETTERS.xpath(
            f"//fidal:letter//fidal:realization[.='{char}']",
            namespaces=namespace
        )

        for realization in realizations:
            if i == 0 and len(candidate) > 4 and char in ('መ', 'ም'):
                first_order = realization.xpath("parent::fidal:realizations/fidal:realization[2]", namespaces=namespace)[0].text
                order = len(realization.xpath("preceding-sibling::fidal:realization", namespaces=namespace))
                transcription = realization.xpath("ancestor::fidal:letter/fidal:transcription", namespaces=namespace)[0].text

                letters.append({
                    'char': char,
                    'firstOrder': first_order,
                    'position': i,
                    'order': order,
                    'transcription': transcription,
                    'name': 'prefix'
                })
            else:
                for realization2 in realization.xpath("parent::fidal:realizations/fidal:realization[2]", namespaces=namespace):
                    first_order = realization2.text
                    order = len(realization.xpath("preceding-sibling::fidal:realization", namespaces=namespace))
                    transcription = realization.xpath("ancestor::fidal:letter/fidal:transcription", namespaces=namespace)[0].text

                    letters.append({
                        'char': char,
                        'firstOrder': first_order,
                        'position': i,
                        'order': order,
                        'transcription': transcription,
                        'name': 'syllab'
                    })

    return letters


def desinences(cons_vowel, formula_type, transcription_type):
    if formula_type == 'noun':
        target_patterns = constants.NOUN_SUFFIXES
    else:
        target_patterns = constants.CONJUGATION

    pseudo_trans = chars_to_pseudo_transcription(cons_vowel, formula_type, transcription_type)
    pseudo_trans_short = pseudo_trans[:-1]
    transcriptions = [pseudo_trans, pseudo_trans_short]

    desinences = []
    postfixes = target_patterns.xpath('.//fidal:affix[not(@type="pre")]', namespaces=namespace)
    for transcription in transcriptions:
        for postfix in postfixes:
            clean_affix = postfix.text.replace('kk', 'k').replace('tt', 't').replace('nn', 'n')

            if len(clean_affix) == 1:
                count_affix = 0
            else:
                affix_chars = transcription_to_chars(clean_affix, 0, 'BM')
                count_affix = len(affix_chars)
            if transcription.endswith(clean_affix):
                desinence_object = postfix_desinence(postfix)
                desinence_object['length'] = len(cons_vowel) - count_affix
                desinences.append(desinence_object)

    prefixes = target_patterns.xpath('.//fidal:affix[@type="pre"]', namespaces=namespace)
    for prefix in prefixes:
        if len(prefix.xpath('./following-sibling::fidal:affix', namespaces=namespace)) == 0:
            if pseudo_trans.startswith(prefix.text) and pseudo_trans.endswith('ǝ'):
                desinence_object = prefix_desinence(prefix)
                desinence_object['length'] = len(cons_vowel)
                desinences.append(desinence_object)
    return desinences
                    

# Don't undeerstand this one
def postfix_desinence(affix):
    desinence = {'affix': affix.text}
    if len(affix.xpath('./ancestor::fidal:pronouns', namespaces=namespace)) > 0:
        desinence['pronouns'] = {
                'gender': affix.xpath('./ancestor::fidal:gender', namespaces=namespace)[0].get('type'),
                'person': affix.xpath('./ancestor::fidal:person', namespaces=namespace)[0].get('type'),
                'number': affix.xpath('./ancestor::fidal:num', namespaces=namespace)[0].get('type')
                }
    desinence['gender'] = affix.xpath('./ancestor::fidal:gender', namespaces=namespace)[-1].get('type')
    desinence['person'] = affix.xpath('./ancestor::fidal:person', namespaces=namespace)[-1].get('type')
    desinence['number'] = affix.xpath('./ancestor::fidal:num', namespaces=namespace)[-1].get('type')
    desinence['mode'] = affix.xpath('./ancestor::fidal:type', namespaces=namespace)[-1].get('name')
    desinence['type'] = affix.xpath('./ancestor::fidal:group', namespaces=namespace)[-1].get('name')

    return desinence

def prefix_desinence(affix):
    return {
        'gender': affix.xpath('./ancestor::fidal:gender', namespaces=namespace)[-1].get('type'),
        'person': affix.xpath('./ancestor::fidal:person', namespaces=namespace)[-1].get('type'),
        'number': affix.xpath('./ancestor::fidal:num', namespaces=namespace)[-1].get('type'),
        'mode': affix.xpath('./ancestor::fidal:type', namespaces=namespace)[-1].get('name'),
        'type': affix.xpath('./ancestor::fidal:group', namespaces=namespace)[-1].get('name')
    }

def chars_to_pseudo_transcription(chars, formula_type, transcription_type):
    vowels = constants.LETTERS.xpath(f'//fidal:vowel[parent::fidal:transcription[@type="{transcription_type}"]]', namespaces=namespace)

    result = ''
    for char in chars:
        vowel_node = vowels[char['order']]
        vowel = vowel_node.text
        result += char['transcription']
        if vowel is not None:
            result += vowel

    return result
    
def transcription_to_chars(transcription, position, transcription_type):
    transcription_tag = [vowel.text for vowel in constants.LETTERS.xpath('//fidal:transcription[@type="BM"]/fidal:vowel', namespaces=namespace) if vowel.text is not None]
    vowels = ''.join(transcription_tag)
    # This matches text that starts with one consonant followed by any number of ʷ (including none) and then any number of the vowels in the chosen transcription (including none)
    regex = re.compile('(([ṭṗṣḍḫčḥśʿʾbcdfghlmnpqrstvzwyxk])(ʷ?[' + vowels +']?))')
    all_matches = regex.findall(transcription)
    
    chars = []
    for i, (full, consonant, vowel) in enumerate(all_matches):
        order = 0
        if len(vowel) != 0:
            order = len(constants.LETTERS.xpath(f'//fidal:transcription[@type="{transcription_type}"]/fidal:vowel[.="{vowel}"]/preceding-sibling::fidal:vowel', namespaces = namespace))
        # Gets realization of the same order
        fidal = constants.LETTERS.xpath(f'//fidal:transcription[.="{consonant}"]/following-sibling::fidal:realizations/fidal:realization', namespaces = namespace)[order].text
        first = constants.LETTERS.xpath(f'//fidal:transcription[.="{consonant}"]/following-sibling::fidal:realizations/fidal:realization', namespaces = namespace)[1].text
        chars = chars + [{
            'char': fidal,
            'firstOrder': first,
            'position': position + i,
            'order': order,
            'transcription': consonant
        }]
        
    return chars