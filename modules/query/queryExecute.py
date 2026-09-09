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


def get_formula(cons_vowel, transcription_type):
    formula = ''
    for i, con_vowel in enumerate(cons_vowel):
        order = con_vowel['order']
        transcriptions = constants.LETTERS.xpath(f'//fidal:vowel[parent::fidal:transcription[@type="{transcription_type}"]]', namespaces=namespace)
        transcription = transcriptions[order].text
        # Seperate in original, but seem identical
        if con_vowel['name'] == 'prefix' or con_vowel['name'] == 'suffix':
            formula = formula + con_vowel['transcription']
            if transcription is not None:
                formula = formula + transcription
        else:
            prefix_count = len([conVowel for conVowel in cons_vowel if conVowel['name'] == 'prefix'])
            # +1 So it starts at 1 in the formula
            formula = formula + str(con_vowel['position'] - prefix_count + 1)
            if transcription is not None:
                formula = formula + transcription

    return formula


def parse_chars(candidate, formula_type):
    if formula_type == 'noun':
        return standard_noun(candidate)


def formulas(candidate, formula_type, transcription_type):
    cons_vowel = parse_chars(candidate, formula_type)
    possible_desinences = desinences(cons_vowel, formula_type, transcription_type)
    formula = get_formula(cons_vowel, transcription_type)

    if '4' in formula:
        short = formula[0 : formula.index('4')]
        if short.endswith('ǝ'):
            short = short.replace('ǝ', 'a')
    else:
        short = formula

    # I figured out from the paper that yǝ is a prefix, but I don't know why the others are equivalent
    if short.startswith('tǝ') and formula_type != 'noun':
        short = short.replace('tǝ', 'yǝ')
    if short.startswith('nǝ') and formula_type != 'noun':
        short = short.replace('nǝ', 'yǝ')
    if short.startswith('ya') and formula_type != 'noun':
        short = short.replace('ya', 'yǝ')

    # Don't know why doubled (will double each in a double, meaning there will be 4 instances)
    formula_gem = short.replace('2', '22')
    formula_gem_1 = short.replace('1', '11')
    formula_gem_1_and_2 = formula_gem_1.replace('2', '22')
    formula_gem_3 = short.replace('3', '33')

    formula_t = short
    # This seems to replace 1ǝ with t and then compensate the other numbers because one is missing
    if formula_t.startswith('yǝ1ǝ') and type != 'noun':
        formula_t = formula_t.replace('1ǝ', 't').replace('2', '1').replace('3', '2').replace('4', '3')
    formula_long_a = ''
    if formula_type != 'noun':
        formula_long_a = short.replace('ā', 'a')
    formula_u = ''
    if formula_type != 'noun':
        formula_u = short.replace('u', 'a')
    formula_i = ''
    if formula_type != 'noun':
        formula_i = short.replace('i', 'a')
    formula_short_w = short
    if '1' in short and formula_type != 'noun':
        formula_short_w = short.replace('1', 'y')

    # Schwacher Wechsel: A Vocal Shift "Schwacher Wechsel," meaning "weak alternation" in German,
    # describes a linguistic phenomenon specific to Germanic languages.
    # It involves the alternation of vowels in certain inflectional forms of verbs, adjectives, and nouns.
    # For instance, in German, the verb "geben" (to give) changes its vowel in the past tense to "gab" (gave).
    # This vowel alternation is a characteristic feature of Germanic languages, contributing to their unique sound patterns.
    # https://www.linguavoyage.org/ol/12025.html
    schwacher_formulas = []
    if formula_type == 'noun':
        schwacher_formulas = schwacher_formulas + schwacher(short, 'L')
    else:
        for letter in ['W', 'L', 'Y']:
            schwacher_formulas = schwacher_formulas + schwacher(short, letter)
    alternatives_1 = [form.replace('aL','ǝL') for form in schwacher_formulas]
    alternatives_2 = [form.replace('1ǝ','1a') for form in schwacher_formulas]

    formula_noun = ''
    if formula_type == 'noun':
        formula_noun = formula.replace('4', 'nn')
    formula_l_short = []
    if formula_type == 'noun':
        formula_l_short = [form[0:len(form) - 1] for form in schwacher_formulas]

    all_alternatives = []
    all_alternatives = (all_alternatives +
                        [formula_short_w] +
                        [formula] +
                        formula_l_short +
                        [formula_long_a] +
                        [formula_u] +
                        [formula_i] +
                        [formula_t] +
                        [formula_noun] +
                        [formula_gem] +
                        [formula_gem_1] +
                        [formula_gem_1_and_2] +
                        [formula_gem_3] +
                        schwacher_formulas +
                        alternatives_1 +
                        alternatives_2)

    #Don't know why we do that again, but this time  for all
    formula_l_short = [form.substring(len(form) - 1) for form in all_alternatives]
    all_formulas = [shva(form) for form in all_alternatives]
    return


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
                    

# Don't undeerstand this one
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

def schwacher(base, letter):
    formula_w_1 = base.replace('1', letter)
    formula_w_2 = base.replace('2', letter)
    formula_w_3 = base.replace('3', letter)

    formula_gem_w_1 = formula_w_1.replace('1', '11')
    formula_gem_w_2 = formula_w_2.replace('2', '22')
    # In the original this does the same thing as formula_gem_w_2 again, is that a mistake?
    formula_gem_w_3 = formula_w_3.replace('3', '33')

    gem = letter + letter
    formula_gem_1_and_2_w = formula_w_1.replace(letter, gem)
    return [
        formula_w_1,
        formula_w_2,
        formula_w_3,
        formula_gem_w_1,
        formula_gem_w_2,
        formula_gem_w_3,
        formula_gem_1_and_2_w
    ]


def shva(form):
    if 'ǝ' in form:
        homophones = ['', 'ǝ']
        shva_substitute(form, homophones, 'normal')


def shva_substitute(form, homophones, param):
    for homophone in homophones:
        pass