# -*- coding: utf-8 -*-
from modules.clean import qClean
from modules.query import queryExecute
from lxml import etree

# Potentially add new attributes location of articulation, manner of articulation
# Current "type" attribute is a container mixing different linguistic meta-language levels, but is very pragmatic, since it's the traditional algorithm taught to beginners when learning to parse a complex semitic verbal form. 
#Load letters file
letters = etree.parse('./in/morpho/letters.xml')
# Get the first order of each laryngeal
laryngeals = letters.xpath('//letter[@type="laryngeal"]//realization[2]//text()')
# All distinct laryngeals (a set has unique values, so converting to and from list removes duplicates)
laryngealsAll = list(set(letters.xpath('//letter[@type="laryngeal"]//realization/text()')))
sibilants = letters.xpath('//letter[@type="sibilant"]//realization[2]//text()')
dentals = letters.xpath('//letter[@type="dental"]//realization[2]//text()')
yod = letters.xpath('//letter[@type="yod"]//realization[2]//text()')
waw = letters.xpath('//letter[@type="waw"]//realization[2]//text()')
# All realizations with type neg (just one, so no list)
neg = letters.xpath('//realization[@type="neg"]//text()')[0]
quot = letters.xpath('//realization[@type="quot"]//text()')[0]
# int is a protected keyword in python, that's why it's intList
intList = letters.xpath('//realization[@type="int"]//text()')

def main():
    query =['ተወሰንክሙ'] #  Interesting to Nesina
    # query =['ዝንቱ']  # Has pronoun
    # Initialize default parameters
    transcriptionType = 'BM'
    fidal = True
    fuzzy = True
    noDil = False
    mismatch = False
    query = qClean.clean(query, fidal, transcriptionType, neg, quot, intList)
    queryExecute.execute(query, fidal, neg, quot, intList, transcriptionType)



if __name__ == "__main__":
    main()
