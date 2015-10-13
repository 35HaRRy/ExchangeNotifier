import datetime
import requests
import xml.etree.ElementTree as xmlParser

def getTcmbCurrencies():
    r = requests.get('http://www.tcmb.gov.tr/kurlar/today.xml')
    tempCurrencies = xmlParser.fromstring(r.text.encode('utf-8')).findall('Currency')

    currencies = {}
    for currency in tempCurrencies:
        currencies[currency.attrib["CurrencyCode"]] = currency.find("ForexSelling").text

    return currencies

def getSortDateString():
    now = datetime.now()

    return "{0}-{1}-{2}".format(now.day, now.month, now.year)

def getTextFromNode(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)

    return ''.join(rc)