# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET

from modules.clean import qClean
from modules.query import queryExecute

def main():
    query =['ተወሰንክሙ']
    # Initialize default parameters
    transcriptionType = 'BM'
    fidal = True
    fuzzy = True
    noDil = False
    mismatch = False
    letters = getLetters()
    negationMarker = getLetter(letters, 'neg')
    quotationMarker = getLetter(letters, 'quot')
    interrogationMarker = getInterrogatives(letters)
    query = qClean.clean(query, fidal, transcriptionType, negationMarker, quotationMarker, interrogationMarker)
    query.sort(key=lengthSort)
    queryExecute.execute(query, fidal, negationMarker, quotationMarker, interrogationMarker)

def getLetters():
    #Load letters file
    tree = ET.parse('./in/morpho/letters.xml')
    #Root is <letters...>...</letters>
    root = tree.getroot()
    
    laryngeals = []
    
    laryngealsAll = []
    sibilants = []
    dentals = []
    yod = []
    waw = []
    neg = []
    quot = []
    #"int" is a keyword in python, so the variable is renamed to intList
    intList = []
    # Potentially add new attributes location of articulation, manner of articulation
    # Current "type" attribute is a container mixing different linguistic meta-language levels, but is very pragmatic, since it's the traditional algorithm taught to beginners when learning to parse a complex semitic verbal form.    
    #Find all "letter" tags and iterate through them
    for letter in root.iter('letter'):
        hasType = 'type' in letter.attrib
        
        realizations = letter.iter('realization')
        for realization in realizations:
            if 'type' in realization.attrib:
                rType = realization.attrib['type']
                if rType == 'neg':
                    neg = neg + [realization.text]
                elif rType == 'quot':
                    quot = quot + [realization.text]
                elif rType == 'int':
                    intList = intList + [realization.text]
        
        if not hasType:
            continue

        lType = letter.attrib['type']
        if lType == 'laryngeal':
            #Find all tags "realizations" directly under the the letter
            realizations = letter.findall('realizations')[0]
            #realization[1] Corresponds to first order (currently presumed)
            laryngeals = laryngeals + [realizations[1].text]
            #All other realizations go into laryngealsAll
            for realization in realizations:
                if realization.text not in laryngealsAll:
                    laryngealsAll = laryngealsAll + [realization.text]
                    
        if lType == 'sibilant':
            realizations = letter.findall('realizations')[0]
            sibilants = sibilants + [realizations[1].text]
            
        if lType == 'dental':
            realizations = letter.findall('realizations')[0]
            dentals = dentals + [realizations[1].text]
        
        if lType == 'yod':
            realizations = letter.findall('realizations')[0]
            yod = yod + [realizations[1].text]
            
        if lType == 'waw':
            realizations = letter.findall('realizations')[0]
            waw = waw + [realizations[1].text]
        
    return {
        'laryngeals': laryngeals,
        'laryngealsAll': laryngealsAll,
        'sibilants': sibilants,
        'dentals': dentals,
        'yod': yod,
        'waw': waw,
        'neg': neg,
        'quot': quot,
        'int': intList
        }

def getLetter(letters, letterType):
    return {
        'solution': {
            'pos': 'proclitics',
            'type': 'negative'
            },
        'root': letters[letterType][0]
        }

#TODO: All letters possible as multiple
def getInterrogatives(letters):
    interrogatives = []
    for interrogative in letters['int']:
        interrogatives = interrogatives + [{
            'solution': {
                'pos': 'interrrogative particle',
                'type': 'interrogative'
                },
            'root': interrogative
            }]
    return interrogatives

def lengthSort(e):
    return len(e)

if __name__ == "__main__":
    main()
