# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET

from modules.clean import qClean
from modules.query import queryExecute

def main():
    query =['ዝንቱ']
    letters = getLetters()
    negative = getLetter(letters, 'neg')
    quotative = getLetter(letters, 'quot')
    interrogatives = getInterrogatives(letters)
    qClean.clean(query, True, 'BM', negative, quotative, interrogatives)
    queryExecute.execute(query, True, negative, quotative, interrogatives)

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
    
    #Find all "letter" tags and iterate through them
    for letter in root.iter('{http://fidal.parser}letter'):
        hasType = 'type' in letter.attrib
        
        realizations = letter.iter('{http://fidal.parser}realization')
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
            realizations = letter.findall('{http://fidal.parser}realizations')[0]
            #TODO: Ask if someone might now, why the magic number 2
            laryngeals = laryngeals + [realizations[2].text]
            #All other realizations go into laryngealsAll
            for realization in realizations:
                if realization.text not in laryngealsAll:
                    laryngealsAll = laryngealsAll + [realization.text]
                    
        if lType == 'sibilant':
            realizations = letter.findall('{http://fidal.parser}realizations')[0]
            sibilants = sibilants + [realizations[2].text]
            
        if lType == 'dental':
            realizations = letter.findall('{http://fidal.parser}realizations')[0]
            dentals = dentals + [realizations[2].text]
        
        if lType == 'yod':
            realizations = letter.findall('{http://fidal.parser}realizations')[0]
            yod = yod + [realizations[2].text]
            
        if lType == 'waw':
            realizations = letter.findall('{http://fidal.parser}realizations')[0]
            waw = waw + [realizations[2].text]
        
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

if __name__ == "__main__":
    main()
