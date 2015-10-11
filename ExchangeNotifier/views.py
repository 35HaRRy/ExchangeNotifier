# -*- coding: utf-8 -*-

import requests

from django.http import *
from pyquery import *
from xml.dom.minidom import parse, parseString

from sources.source import * 
 
def currentsituation(request):
    #file = getJsonFile()

    r = requests.get('http://www.tcmb.gov.tr/kurlar/today.xml')
    xmlDoc = parseString(r.text.encode('utf-8'))
    jq = PyQuery(r.text.encode('utf-8'))

    texts = []
    for currency in xmlDoc.getElementsByTagName('Currency') :
		#for currencyItem in currency.childNodes :
            #texts.append(getText(currencyItem.childNodes))
        texts.append(getText(currency.childNodes[3].childNodes))
        texts.append('<br>')

    temp = source()
    table = temp.getTable("dailyRecords")

    return HttpResponse(table["error"])
    #return HttpResponse(temp.test())
    #return HttpResponse(' '.join(texts))
    #return HttpResponse(r.text.encode('utf-8'))
    
def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)

    return ''.join(rc)