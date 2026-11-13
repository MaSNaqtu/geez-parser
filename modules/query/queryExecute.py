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
    results = []
    for q in query:
        particles = get_all_particles(q, negative, quotative, interrogatives)

        #print(f'All particles:\n{particles}')

        nouns = formulas(q, 'noun', transcription_type)
        if len(nouns) > 0:
            print('Noun Matches: ' + str(nouns))
        verbs = formulas(q, 'verb', transcription_type)
        if len(verbs) > 0:
            print('Verb Matches: ' + str(nouns))

        results.append({
            "query": q,
            "particles": particles,
            "nouns": nouns,
            "verbs": verbs
        })
    return results



def get_all_particles(candidate, negative, quotative, interrogatives):
    candidates = []
    # Get element with text matching candidate
    pronoun_matches = constants.PRONOUNS.xpath(f"//fidal:*[text()='{candidate}']", namespaces=namespace)
    for match in pronoun_matches:
        # Get root (full nominative, singular, masculine form of the group) by traversing group -> type -> num -> gender -> full
        root = match.xpath("ancestor::fidal:group/fidal:type[@name='nominative']/fidal:num[@type='Singular']/fidal:gender[@type='Masculine']/fidal:full", namespaces=namespace)[0]
        candidates = candidates + [{
            "solution": {
                "pos": 'pronoun',
                "group": match.xpath("ancestor::fidal:group/@name", namespaces=namespace)[0],
                "type": match.xpath("ancestor::fidal:type/@name", namespaces=namespace)[0],
                "forms": {
                    "desinence": {
                        "gender": match.xpath("ancestor::fidal:gender/@type", namespaces=namespace),
                        "number": match.xpath("ancestor::fidal:num/@type", namespaces=namespace)
                    }
                }
            },
            "root": root.text
        }]

    #print(f'Candidates after pronoun: \n{candidates}')

    proclitic_matches = constants.PROCLITICS.xpath(f"//fidal:proclitic[text()='{candidate}']", namespaces=namespace)
    for proclitic in proclitic_matches:
        candidates = candidates + [{
            "solution": {
                "pos": 'proclitic'
                },
            "root": proclitic.text
            }]

    #print(f'Candidates after proclitic: \n{candidates}')

    if candidate == negative:
        candidates = candidates + [{
            "solution": {
                "pos": 'proclitic',
                "type": 'negative'
                },
            "root": negative
            }]

    #print(f'Candidates after negative: \n{candidates}')

    if candidate == quotative:
        candidates = candidates + [{
            "solution": {
                "pos": 'quotative particle',
                "type": 'quotative'
                },
            "root": quotative
            }]

    #print(f'Candidates after quotative: \n{candidates}')

    for interrogative in interrogatives:
        if candidate == interrogative:
            candidates = candidates + [{
                "solution": {
                    "pos": 'interrogative particle',
                    "type": 'interrogative'
                    },
                "root": interrogative
                }]

    #print(f'Candidates after interrogative: \n{candidates}')

    particle_matches = constants.PARTICLES.xpath(f"//fidal:particle[text()='{candidate}']", namespaces=namespace)
    for particle in particle_matches:
        if particle.text == candidate:
            candidates = candidates + [{
                "solution": {
                    "pos": 'particle',
                    "type": particle.get('type')
                    },
                "root": particle.text
                }]

    #print(f'Candidates after particles: \n{candidates}')

    number_matches = constants.NUMBERS.xpath(f"//fidal:num[text()='{candidate}']", namespaces=namespace)
    for number in number_matches:
        if number.text == candidate:
            candidates = candidates + [{
                "solution": {
                    "pos": 'numeral',
                    "type": number.get('val')
                    },
                "root": number.text
                }]

    #print(f'Candidates after numbers: \n{candidates}\n\n')

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
    elif len(candidate) >= 6 and (candidate.startswith('አስተ') or candidate.startswith('ያስተ')):
        return ast_form(candidate)
    elif len(candidate) < 3 and formula_type != 'regular' and formula_type != 'fuzzy':
        match formula_type:
            case 'w2':
                w_position = 2
            case 'w3':
                w_position = 3
            case _:
                w_position = 1
        return short(candidate, w_position)
    elif len(candidate) == 3 and formula_type != 'regular' and formula_type != 'fuzzy':
        return standard_short(candidate)
    else:
        return standard(candidate)


def formulas(candidate, formula_type, transcription_type):
    cons_vowel = parse_chars(candidate, formula_type)

    if not cons_vowel:
        return []

    #print(f'Parsed Chars:\n{cons_vowel}')

    possible_desinences = desinences(cons_vowel, formula_type, transcription_type)

    #print(f'Possible Desinences:\n{possible_desinences}')

    formula = get_formula(cons_vowel, transcription_type)

    #print(f'Initial Formula: {formula}')

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
    all_alternatives = list(set(all_alternatives))

    #Don't know why we do that again, but this time  for all
    formula_l_short = [form[0:(len(form) - 1)] for form in all_alternatives if form != '']
    nested_formulas = [shva(form) for form in all_alternatives]

    all_formulas = []
    for formula in nested_formulas:
        for nest in formula:
            if nest not in all_formulas:
                all_formulas.append(nest)
    long_and_short = all_formulas + formula_l_short
    # Remove duplicates
    long_and_short = list(set(long_and_short))
    long_and_short_final = [formula for formula in long_and_short if formula != '']

    #print(f'Long and Short:\n{long_and_short}')

    if formula_type == 'noun':
        print_matches = matches_nouns(long_and_short_final, transcription_type, cons_vowel, formula_type, possible_desinences)
        return print_matches
    else:
        return matches(long_and_short, transcription_type, cons_vowel, formula_type, possible_desinences)


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

                letters.append(prefix_char(char, first_order, order, transcription))
            else:
                for realization2 in realization.xpath("parent::fidal:realizations/fidal:realization[2]", namespaces=namespace):
                    first_order = realization2.text
                    order = len(realization.xpath("preceding-sibling::fidal:realization", namespaces=namespace))
                    transcription = realization.xpath("ancestor::fidal:letter/fidal:transcription", namespaces=namespace)[0].text

                    letters.append(syllable_char(char, first_order, i, order, transcription))

    #print(f'After standardNoun:\n{letters}')

    return letters


def ast_form(candidate):
    letters = []
    # Don't know why it replaces the beginning with ያ/አስተ
    if candidate[0] == 'ያ':
        letters.append(prefix_char('ያ', 'የ', 4, 'y'))
    else:
        letters.append(prefix_char('አ', 'አ', 1, 't'))

    letters.append(prefix_char('ስ','ሰ',6,'s'))
    letters.append(prefix_char('ተ','ተ',1,'t'))

    for i, letter in enumerate(candidate[3:]):
        position = i + 3
        realizations = constants.LETTERS.xpath(f'//fidal:realization[.="{letter}"]', namespaces=namespace)
        for realization in realizations:
            first_order = realization.xpath("parent::fidal:realizations/fidal:realization[2]", namespaces=namespace)[0].text
            order = len(realization.xpath("preceding-sibling::fidal:realization", namespaces=namespace))
            transcription = realization.xpath("ancestor::fidal:letter/fidal:transcription", namespaces=namespace)[0].text

            char = syllable_char(letter, first_order, position, order, transcription)
            if i == len(candidate) - 1 and candidate[-1] == 'ት':
                char['name'] = 'suffix'
            letters.append(char)

    return letters



def short(candidate, w_position):
    letters = []
    for i, letter in enumerate(candidate):
        pos_inc = 0
        if w_position == 1:
            pos_inc = i + w_position
        elif w_position == 2:
            match i:
                case 0:
                    pos_inc = 0
                case 1:
                    pos_inc = 2
                case _:
                    pos_inc = i
        elif w_position == 3:
            match i:
                case 0:
                    pos_inc = 0
                case 2:
                    pos_inc = 1
                case _:
                    pos_inc = i
        else:
            continue

        realizations = constants.LETTERS.xpath(f'//fidal:realization[.="{letter}"]', namespaces=namespace)
        for realization in realizations:
            first_order = realization.xpath("parent::fidal:realizations/fidal:realization[2]", namespaces=namespace)[0].text
            order = len(realization.xpath("preceding-sibling::fidal:realization", namespaces=namespace))
            transcription = realization.xpath("ancestor::fidal:letter/fidal:transcription", namespaces=namespace)[0].text

            letters.append(syllable_char(letter, first_order, pos_inc, order, transcription))

    return letters


def standard_short(candidate):
    letters = []
    for i, letter in enumerate(candidate):
        realizations = constants.LETTERS.xpath(f'//fidal:realization[.="{letter}"]', namespaces=namespace)
        for realization in realizations:
            first_order = realization.xpath("parent::fidal:realizations/fidal:realization[2]", namespaces=namespace)[0].text
            order = len(realization.xpath("preceding-sibling::fidal:realization", namespaces=namespace))
            transcription = realization.xpath("ancestor::fidal:letter/fidal:transcription", namespaces=namespace)[0].text

            if i == 0 and (letter == 'ይ' or letter == 'ያ' or letter == 'አ' or letter == 'ት' or letter == 'ተ' or letter == 'ን'):
                letters.append(prefix_char(letter, first_order, order, transcription))
            elif i == len(candidate) - 1 and letter == 'ት':
                char = syllable_char(letter, first_order, i, order, transcription)
                char['name'] = 'suffix'
                letters.append(char)
            else:
                letters.append(syllable_char(letter, first_order, i, order, transcription))

    return letters

def standard(candidate):
    letters = []
    for i, letter in enumerate(candidate):
        realizations = constants.LETTERS.xpath(f'//fidal:realization[.="{letter}"]', namespaces=namespace)
        for realization in realizations:
            first_order = realization.xpath("parent::fidal:realizations/fidal:realization[2]", namespaces=namespace)[0].text
            order = len(realization.xpath("preceding-sibling::fidal:realization", namespaces=namespace))
            transcription = realization.xpath("ancestor::fidal:letter/fidal:transcription", namespaces=namespace)[0].text

            if i < 2 and len(candidate) > 4 and candidate.startswith('ይት'):
                letters.append(prefix_char(letter, first_order, order, transcription))
            else:
                if i < 2 and len(candidate) > 3 and (letter == 'ይ' or letter == 'ያ' or letter == 'አ' or letter == 'ት' or letter == 'ተ' or letter == 'ን'):
                    letters.append(prefix_char(letter, first_order, order, transcription))
                else:
                    letters.append(syllable_char(letter, first_order, i, order, transcription))

    return letters

# The original has a branch which checks for candidate longer than 5. This can never be reached, since the length is checked
def prefix_char(char, first_order, order, transcription):
    return {
        "char": char,
        "firstOrder": first_order,
        "order": order,
        "transcription": transcription,
        "name": 'prefix'
    }

def syllable_char(char, first_order, position, order, transcription):
    return {
        "char": char,
        "firstOrder": first_order,
        "position": position,
        "order": order,
        "transcription": transcription,
        "name": 'syllab'
    }



def desinences(cons_vowel, formula_type, transcription_type):
    if cons_vowel is None:
        return []
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
    groups = affix.xpath('./ancestor::fidal:group', namespaces=namespace)
    if groups:
        desinence['type'] = groups[-1].get('name')

    return desinence


def prefix_desinence(affix):
    return {
        "gender": affix.xpath('./ancestor::fidal:gender', namespaces=namespace)[-1].get('type'),
        "person": affix.xpath('./ancestor::fidal:person', namespaces=namespace)[-1].get('type'),
        "number": affix.xpath('./ancestor::fidal:num', namespaces=namespace)[-1].get('type'),
        "mode": affix.xpath('./ancestor::fidal:type', namespaces=namespace)[-1].get('name'),
        "type": affix.xpath('./ancestor::fidal:group', namespaces=namespace)[-1].get('name')
    }


def chars_to_pseudo_transcription(chars, formula_type, transcription_type):
    vowels = constants.LETTERS.xpath(f'//fidal:vowel[parent::fidal:transcription[@type="{transcription_type}"]]', namespaces=namespace)

    result = ''
    if chars:
        for char in chars:
            vowel_node = vowels[char['order']]
            vowel = vowel_node.text
            result += char['transcription']
            if vowel is not None:
                result += vowel

    return result
                    

# Don't understand this one
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
            "char": fidal,
            "firstOrder": first,
            "position": position + i,
            "order": order,
            "transcription": consonant
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
        #Separate definition in original, reuse seems sensible though
        return checkDill.substitute(form, homophones, 'normal')
    return [form]


def matches_nouns(all_forms, transcription_type, cons_vowel, formula_type, possible_desinences):
    # TODO: fuzzy
    final_result = []
    for formula in all_forms:
        candidates = []
        matchings = constants.NOMINAL.xpath(f'//fidal:formula[.="{formula}"]', namespaces = namespace)
        #print(formula)
        for match in matchings:
            match_type = ''
            if match.text.endswith('i'):
                match_type = 'i'
            elif match.text.endswith('e'):
                match_type = 'e'
            else:
                match_type = 'consonant'

            pattern_type = 'regular'
            if 'type' in match.attrib:
                pattern_type = match.attrib['type']

            # Not 100% sure two last is correct
            main_root = ''
            for letter in cons_vowel[:2]:
                main_root = main_root + letter['char']

            second_position = cons_vowel[1]['firstOrder']
            # Gets all realizations of that letter
            second_position_realizations = constants.LETTERS.xpath(f'//fidal:realization[.="{second_position}"]/parent::fidal:realizations/fidal:realization', namespaces = namespace)
            second_position_sixth_order = second_position_realizations[0]

            third_position = cons_vowel[2]['firstOrder']
            third_position_realizations = constants.LETTERS.xpath(f'//fidal:realization[.="{third_position}"]/parent::fidal:realizations/fidal:realization', namespaces = namespace)
            third_position_sixth_order = third_position_realizations[0]

            last_sixth = cons_vowel[0]['char'] + third_position_sixth_order.text

            # I think that's the intention
            beginning = ''
            for letter in cons_vowel[:2]:
                beginning = beginning + letter['firstOrder']
            last_sixth_2 = beginning + third_position_sixth_order.text

            # Also not sure on this one
            last_sixth_and_second_last = cons_vowel[0]['firstOrder'] + second_position_sixth_order.text + third_position_sixth_order.text

            other_root = ''
            for letter in cons_vowel:
                other_root = other_root + letter['firstOrder']
            option_without_last = other_root[:-1]

            # Checks for waw, yod, and laryngeal. If less than two on them, returns 'regular' else returns the list of matches.
            main_root_types = root_type(main_root)

            # I think this is done in the original because it was copied from the other matches, and it never shows up for nouns.
            #mode = match.xpath(f'./ancestor::fidal:pattern/@name', namespaces=namespace)[0]
            mode = ''

            # I think this is done in the original because it was copied from the other matches, and it never shows up for nouns.
            #pattern = match.attrib['attested'] + formula if 'attested' in match.attrib else 'yes'
            pattern = formula

            main_root_type_results = []
            if main_root_types == 'regular':
                main_root_type_results.append('regular')
            else:
                for main_root_type in main_root_types:
                    if main_root_type.startswith('w') or main_root_type.startswith('y'):
                        main_root_type_results.append('regular')
                    else:
                        main_root_type_results.append(main_root_type)

            forms = []
            for form in possible_desinences:
                # Don't know why it has to be length 3
                if form['type'] == match_type and form['length'] == 3:
                    desinence_length = form['affix']
            forms.sort(key=lambda inner_form: inner_form['length'])

            solution = {
                "pos": match.xpath(f'./ancestor::fidal:pos/@name', namespaces=namespace),
                "group": match.xpath(f'./ancestor::fidal:group/@name', namespaces=namespace),
                "type": match.xpath(f'./ancestor::fidal:type/@name', namespaces=namespace),
                "mode": mode,
                "forms": forms
            }

            roots = {
                "mainRoot" : main_root,
                "otherRoots": [other_root, option_without_last, last_sixth, last_sixth_2, last_sixth_and_second_last]
            }
            candidates.append({
                "pattern": pattern,
                "patternType": pattern_type,
                "mainRootTypes": main_root_type_results,
                "solution": solution,
                "roots": roots
            })
        #TODO: There is a dillman check here (see it being offline), but it's still just for links, no other info
        for candidate in candidates:
            final_result.append(check_mismatches(candidate))
    return final_result

def matches(all_forms, transcription_type, cons_vowel, formula_type, possible_desinences):
    # TODO: fuzzy
    final_result = []
    for formula in all_forms:
        candidates = []
        matchings = constants.PATTERNS.xpath(f'//fidal:formula[.="{formula}"]', namespaces = namespace)

        verb_types = []
        for index, letter in enumerate(['w', 'y', 'l']):
            verb_types.append(letter + str(index))

        for match in matchings:
            verb_type = match.attrib['type'] if 'type' in match.attrib else 'regular'
            match_type = match.xpath(f'./parent::fidal:pattern/parent::fidal:type', namespaces = namespace)[0].attrib['name']
            match_type = '1a' if match_type == '2' or match_type == '3' else match_type
            roots = list_roots(match, verb_type, cons_vowel, transcription_type, match_type, formula)
            #if roots is not None and len(roots['mainRoots']['roots']) > 0:
                #print('Verb Roots: ' + str(roots))
            if roots == None:
                continue
            root_length = 3 + len([letter for letter in cons_vowel if letter['name'] == 'prefix'])
            main_roots = roots['mainRoots']['roots']
            main_root_types = [root_type(main_root) for main_root in main_roots]

            pattern_type = 'regular'
            if 'type' in match.attrib:
                pattern_type = match.attrib['type']

            mode = match.xpath('./ancestor::fidal:pattern/@name', namespaces=namespace)[0]

            forms = []
            for form in possible_desinences:
                if form['mode'] == mode:
                    forms.append(form)

            solution = {
                "pos": match.xpath(f'./ancestor::fidal:pos/@name', namespaces=namespace),
                "group": match.xpath(f'./ancestor::fidal:group/@name', namespaces=namespace),
                "type": match.xpath(f'./ancestor::fidal:type/@name', namespaces=namespace),
                "mode": mode,
                "forms": forms
            }

            roots = {
                "mainRoot": main_roots,
                "otherRoots": roots['otherRoots']
            }
            candidates.append({
                "pattern": formula,
                "attested": match.attrib['attested'] if 'attested' in match.attrib else 'yes',
                "patternType": pattern_type,
                "mainRootTypes": main_root_types,
                "solution": solution,
                "roots": roots
            })
        #TODO: There is a dillman check here (see it being offline), but it's still just for links, no other info
        for candidate in candidates:
            final_result.append(check_mismatches(candidate))
    return final_result

def root_type(main_root):
    check = []
    for i, letter in enumerate(main_root):
        # yod
        if letter == 'የ':
            check.append('y' + str(i + 1))
        # waw
        elif letter == 'ወ':
            check.append('w' + str(i + 1))
        # laryngeal
        elif letter == 'ዐ':
            check.append('l' + str(i + 1))
    return 'regular' if len(check) < 2 else check

def check_mismatches(candidate):
    main_root_type = candidate['solution']['type']
    pattern_type = candidate['patternType']

    candidate['mismatch'] = pattern_type != main_root_type

    return candidate


def list_roots(match, verb_type, cons_vowel, transcription_type, match_type, formula):
    patterns = constants.PATTERNS.xpath(f'//fidal:pos[@name="verb"]/fidal:group[@name="I"]/fidal:type[@name="{match_type}"]/fidal:pattern[1]/fidal:formula', namespaces = namespace)
    is_regular_or_fuzzy = verb_type == 'regular' or verb_type == 'fuzzy'

    root_pattern = ''
    if is_regular_or_fuzzy:
        for pattern in patterns:
            if 'type' not in pattern.attrib:
                root_pattern = pattern
                # Only take the first one )in the original, this is not explicit, but afterwards it's treated as if it's not a list
                break
    else:
        for pattern in patterns:
            type_matches = 'type' in pattern.attrib and pattern.attrib['type'] == verb_type
            is_attested = 'attested' in pattern.attrib
            if  type_matches and is_attested:
                root_pattern = pattern
                # Only take the first one
                break
    if root_pattern == '':
        return None

    syllables = [letter for letter in cons_vowel if letter['name'] == 'syllab']

    prefix_length = 0
    for letter_2 in cons_vowel:
        if letter_2['name'] == 'prefix':
            prefix_length = prefix_length + 1

    main_roots = {
        'type': root_pattern.attrib['type'] if 'type' in root_pattern.attrib else '',
        'roots': []
    }

    if is_regular_or_fuzzy:

        if formula == '2a3':
            main_roots["roots"].append('ወ')
            for letter in syllables[:3]:
                main_roots["roots"].append(build_root(letter['position'] - prefix_length, letter, root_pattern.text, transcription_type))
        elif '1' not in formula:
            prefixes = [char for char in cons_vowel if char['name'] == 'prefix']
            main_roots["roots"].append(build_root(1, prefixes[-1], root_pattern.text, transcription_type))
            if formula != '2a3':
                for letter in syllables:
                    main_roots["roots"].append(build_root(letter['position'] - prefix_length, letter, root_pattern.text, transcription_type))
    else:
        letter = verb_type[0]
        position = verb_type[1]
        match letter:
            case 'w':
                letter_variants_from_pattern = constants.LETTERS.xpath('//fidal:letter[@type="waw"]//fidal:realization[2]//text()', namespaces=namespace)
            case 'l':
                letter_variants_from_pattern = list(set(constants.LETTERS.xpath('//fidal:letter[@type="laryngeal"]//fidal:realization/text()', namespaces=namespace)))
            case _:
                letter_variants_from_pattern = constants.LETTERS.xpath('//fidal:letter[@type="yod"]//fidal:realization[2]//text()', namespaces=namespace)
        first_orders = [first_order['firstOrder'] for first_order in cons_vowel]

        # TODO: Figure out what is happening here. I'm getting nothing in my testcases, which would result in no roots, but the test case I used is the one in the paper, which has roots. For now I will just use the first order letters for processing.
        letter_variants = []
        for first_order in first_orders:
            if first_order in letter_variants_from_pattern:
                letter_variants.append(first_order)

        match position:
            case '1':
                for first_order in first_orders:
                    root = first_order
                    for syllable in syllables[prefix_length: prefix_length + 3]:
                        root = root + build_root(syllable['position'] - prefix_length, syllable, root_pattern.text,transcription_type)
                    main_roots["roots"].append(root)
            case '2':
                for first_order in first_orders:
                    main_roots["roots"].append(
                        build_root(syllables[0]['position'] - prefix_length, syllables[0], root_pattern.text, transcription_type) +
                        first_order +
                        build_root(syllables[2]['position'] - prefix_length, syllables[2], root_pattern.text, transcription_type)
                    )
                if 'type' not in root_pattern.attrib:
                    for first_order in first_orders:
                        main_roots["roots"].append(
                            build_root(syllables[0]['position'] - prefix_length, syllables[0], root_pattern.xtree('//fidal:formula[not(@type)]', namespaces=namespace)[0].text, transcription_type) +
                            first_order +
                            build_root(syllables[2]['position'] - prefix_length, syllables[2], root_pattern.xtree('//fidal:formula[not(@type)]', namespaces=namespace)[0].text, transcription_type)
                        )
            case '3':
                for first_order in first_orders:
                    root = first_order
                    for syllable in syllables[:2]:
                        root = root + build_root(syllable['position'] - prefix_length, syllable, root_pattern.text, transcription_type)
                    main_roots["roots"].append(root)

    #print('Main Verb Roots: ' + str(main_roots))

    other_roots = []
    for main_root in main_roots['roots']:
        if is_regular_or_fuzzy:
            possible_patterns = constants.PATTERNS.xpath('//fidal:formula[not(@type)][parent::fidal:pattern[not(parent::fidal:type[@name="1a"])][not(ancestor::fidal:group[@name="I"])][not(preceding-sibling::fidal:pattern)]][not(@type)]', namespaces = namespace)
        else:
            possible_patterns = constants.PATTERNS.xpath(f'//fidal:formula[@type="{verb_type}"][parent::fidal:pattern[not(parent::fidal:type[@name="1a"])][not(ancestor::fidal:group[@name="I"])][not(preceding-sibling::fidal:pattern)]]', namespaces=namespace)

        for current in possible_patterns:
            other_roots.append(pattern_to_form(current.text, main_root))
    roots = {
        "mainRoots": main_roots,
        "otherRoots": other_roots
    }

    return roots


def build_root(relative_position, letter, root_pattern, transcription_type):
    substring = root_pattern[relative_position:]
    vowel = substring[0]
    if vowel.isdigit():
        vowel_position = 0
    else:
        vowel_position = len(constants.LETTERS.xpath(f'//fidal:vowel[.="{vowel}"][parent::fidal:transcription[@type="{transcription_type}"]]/preceding-sibling::fidal:vowel', namespaces=namespace))
    transcription = constants.LETTERS.xpath(f'//fidal:letter[fidal:transcription="{letter['transcription']}"]', namespaces=namespace)[0]
    return transcription.xpath(f'.//fidal:realization[position()=({vowel_position} + 1)]', namespaces=namespace)[0].text


def pattern_to_form(text, main_root):
    text = text.replace('12', '102')
    text = text.replace('23', '203')
    text = text.replace('2L', '20L')
    text = text.replace('2W', '20W')
    text = text.replace('2Y', '20Y')

    text = text.replace('11', '1')
    text = text.replace('22', '2')
    text = text.replace('33', '3')

    text = re.sub('3$', '30', text)
    text = re.sub('W$', 'W0', text)
    text = re.sub('Y$', 'Y0', text)
    text = re.sub('L$', 'L0', text)

    text = text.replace('Y', 'Y0')
    text = text.replace('L', 'L0')

    text = text.replace('WW', 'W')
    text = text.replace('YY', 'Y')
    text = text.replace('YY', 'Y')
    text = text.replace('SS', 'S')

    text = text.replace('S', '1')
    text = text.replace('DD', 'D')
    text = text.replace('D', '1')

    text = text.replace('W2', 'W02')
    text = text.replace('W3', 'W03')
    text = text.replace('Y2', 'Y02')
    text = text.replace('Y3', 'Y03')
    text = text.replace('L2', 'L02')
    text = text.replace('L3', 'L03')

    if text[-1].isnumeric():
        text = text + str(0)

    groups = re.search('([ʾaāǝyst]+)?([\\daeiouāǝWYLDS]{2})?([\\daeiouāǝWYLDS]{2})?([\\daeiouāǝWYLDS]{2})?(\\w+)?', text).groups()
    pre = groups[0]
    pre = pre.replace('ʾa', 'አ')
    pre = pre.replace('ya', 'የ')
    pre = pre.replace('yā', 'ያ')
    pre = pre.replace('yǝ', 'ይ')
    pre = pre.replace('s', 'ስ')
    pre = pre.replace('ta', 'ተ')

    transcriptions = constants.LETTERS.xpath('//fidal:letters/fidal:transcription[@type="BM"]', namespaces=namespace)[0]
    middle = ''
    for i, group in enumerate(groups[1:4]):
        if group is None:
            continue
        # Adjust position by one due to 0 indexing in Python
        position = int(group[0]) - 1 if group[0].isdigit() else i
        letter_position = main_root[int(position)]
        realization = constants.LETTERS.xpath(f'//fidal:realization[.="{letter_position}"]', namespaces=namespace)[0]

        order_vowel = 0
        if len(group) > 0:
            order = group[1]
            # TODO: islower is a workaround, the issue is sometimes the order gets messed up: ('ta', 'L0', 'a2', 'aW', 'a')
            if order.isalpha() and order.islower():
                vowel = transcriptions.xpath(f'./fidal:vowel[.="{order}"]', namespaces=namespace)[0]
                order_vowel = len(vowel.xpath(f'./preceding-sibling::fidal:vowel', namespaces=namespace))
        corrected_realization = realization.xpath(f'./parent::fidal:realizations/fidal:realization', namespaces=namespace)[order_vowel].text
        middle = middle + corrected_realization
    pattern = pre + middle
    if groups[4] is not None:
        pattern = pattern + groups[4]
    pattern = pattern.replace('t', 'ት')
    return pattern