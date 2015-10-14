import requests
import xml.etree.ElementTree as xmlParser

from datetime import *

def getTcmbCurrencies():
    r = requests.get('http://www.tcmb.gov.tr/kurlar/today.xml')
    tempCurrencies = xmlParser.fromstring(r.text.encode('utf-8')).findall('Currency')

    currencies = {}
    for currency in tempCurrencies:
        if currency.find("ForexSelling").text:
            currencies[currency.attrib["CurrencyCode"]] = currency.find("ForexSelling").text

    return currencies

def getSortDateString():
    now = datetime.now()

    return "{0}-{1}-{2}".format(now.day, now.month, now.year)

def getCurrentCode(format):
    now = datetime.now()
    timetuple = now.timetuple()
    dateItems = { "d": now.day, "m": now.month, "y": now.year, "h": now.hour, "m": now.minute,"s": now.second, "wd": timetuple.tm_wday + 1 }

    code = []
    for templateItem in format["template"].split(format["separator"]):
       code.append(str(dateItems[templateItem]))

    return ".".join(code)
