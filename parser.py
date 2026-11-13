# -*- coding: utf-8 -*-
from modules.clean import qClean
from modules.query import queryExecute

import constants

namespace = {'fidal': 'http://fidal.parser'}
# Potentially add new attributes location of articulation, manner of articulation
# Current "type" attribute is a container mixing different linguistic meta-language levels, but is very pragmatic, since it's the traditional algorithm taught to beginners when learning to parse a complex semitic verbal form. 
#Load constansts.LETTERS file
# Get the first order of each laryngeal
laryngeals = constants.LETTERS.xpath('//fidal:letter[@type="laryngeal"]//fidal:realization[2]//text()', namespaces=namespace)
# All distinct laryngeals (a set has unique values, so converting to and from list removes duplicates)
laryngealsAll = list(set(constants.LETTERS.xpath('//fidal:letter[@type="laryngeal"]//fidal:realization/text()', namespaces=namespace)))
sibilants = constants.LETTERS.xpath('//fidal:letter[@type="sibilant"]//fidal:realization[2]//text()', namespaces=namespace)
dentals = constants.LETTERS.xpath('//fidal:letter[@type="dental"]//fidal:realization[2]//text()', namespaces=namespace)
yod = constants.LETTERS.xpath('//fidal:letter[@type="yod"]//fidal:realization[2]//text()', namespaces=namespace)
waw = constants.LETTERS.xpath('//fidal:letter[@type="waw"]//fidal:realization[2]//text()', namespaces=namespace)
# All realizations with type neg (just one, so no list)
neg = constants.LETTERS.xpath('//fidal:realization[@type="neg"]//text()', namespaces=namespace)[0]
quot = constants.LETTERS.xpath('//fidal:realization[@type="quot"]//text()', namespaces=namespace)[0]
# int is a protected keyword in python, that's why it's intList
interrogative = constants.LETTERS.xpath('//fidal:realization[@type="int"]//text()', namespaces=namespace)

def main():
    ## Nesina Collection
    #query = ['ሐካይ'] #Lösung: ḥakkay -> sollte auf ሀካይ, hakkāy, zurückgeführt werden: Vertauschung Laryngale
    #query = ['ቃሕሞ'] #Lösung: qāḥm -> kind of ant
    #query = ['እምኔሁ'] #Lösung: ʾǝmǝnne-hu  -> Langform der Präposition እም (ʾǝm, seit, von an, aus ...) mit Suffix-Pronomen 3.sg. m.
    #query = ['ወያስተዳሉ'] # Lösung: yāstadāllu / yāstadālu  (√ dlw II: Stamm Ast3, W3 [schwaches Verb, d.h. man sieht nicht alle Konsonanten]), hier als Imperfekt (zwei ll) oder Jussiv (ein l) interpretierbar (bereit machen, vorbereiten, einrichten, würdig machen) Ähnliche Formen existieren von derselben Wurzel im Stamm Ast 2, aber eben nicht genau diese Form.
    #query = ['ተመየጥ'] #  Lösung: tamayaṭ -> Imperativ sg.m., Stamm T1 des schwachen Verbes √ myṭ(Wende Dich zu! Wende Dich um! etc.)
    ## Samuel Collection
    #query =['ተወሰንክሙ'] #  Interesting to Nesina
    #query =['ዝንቱ']  # Has pronoun
    query = ['ዘኢወለደተኒ'] # Has proclitic
    #query = ['ይወልድ'] # Has prefix
    #query = ['አና']  # Has postfix
    #query = ['ወለደ']
    #query = ['ይዕቀብ']
    # Initialize default parameters
    transcription_type = 'BM'
    fidal = True
    fuzzy = True
    no_dil = False
    mismatch = False
    query = qClean.clean(query, fidal, transcription_type, neg, quot, interrogative)
    #print(f'After Clean: \n{query}')
    queryExecute.execute(query, fidal, neg, quot, interrogative, transcription_type)



if __name__ == "__main__":
    main()
