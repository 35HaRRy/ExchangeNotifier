import requests
import xml.etree.ElementTree as xmlParser

from source import *
from tools import *

def getTcmbCurrencies():
    r = requests.get('http://www.tcmb.gov.tr/kurlar/today.xml')
    tempCurrencies = xmlParser.fromstring(r.text.encode('utf-8')).findall('Currency')

    currencies = {}
    for currency in tempCurrencies:
        if currency.find("ForexSelling").text:
            currencies[currency.attrib["CurrencyCode"]] = currency.find("ForexSelling").text

    return currencies

def getCurrentMaxMinRecords(dailyCurrencies):
    maxMinRecordTables = []
    sourceHelper = source()

    maxMinRecordTableNames = ["dailyMaxMinRecords", "weeklyMaxMinRecords", "monthlyMaxMinRecords"]
    for maxMinRecordTableName in maxMinRecordTableNames:
        maxMinRecordTable = sourceHelper.getTable(maxMinRecordTableName)

        currentRecord = sourceHelper.getRows(maxMinRecordTable["rows"], ["code"], [maxMinRecordTable["newCode"]])
        if len(currentRecord) == 0: # kayıt var mı kontrol et
            currentRecord = {}
            currentRecord["code"] = maxMinRecordTable["code"]
            currentRecord["min"] = currentRecord["max"] = dailyCurrencies

            maxMinRecordTable["rows"].append(currentRecord)
        else:
            currentRecord = currentRecord[0]

            for key, value in dailyCurrencies.iterItems():
                if value >= currentRecord["max"][key]:
                    currentRecord["max"][key] = value

                if value <= currentRecord["min"][key]:
                    currentRecord["min"][key] = value

        sourceHelper.saveTable(maxMinRecordTable)
        maxMinRecordTables.append(maxMinRecordTable)

    return  maxMinRecordTables