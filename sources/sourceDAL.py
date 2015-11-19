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

def getAvailableUserAlarms(dailyRecords, userAlarmsTable, userId):
    sourceHelper = source()
    now = datetime.now()

    currencies = dailyRecords["rows"][dailyRecords["rows"].length - 1]
    lastDayCloseCurrencies = dailyRecords["rows"][dailyRecords["rows"].length - 2]

    availableUserAlarms = []
    alarmsTable = sourceHelper.getTable("alarms")
    userAlarmWavePointsTable = sourceHelper.getTable("userAlarmWavePoints")

    userAlarms = sourceHelper.getRows(userAlarmsTable["rows"], ["userId", "startDate", "finishDate", "status"], [userId, now, now, 1], ["equal", "bigger", "smaller", "equal"])
    for userAlarm in userAlarms:
        alarm = sourceHelper.getRows(alarmsTable["rows"], ["id"], userAlarm["alarmId"])[0]
        if alarm["type"] == 1: # Belli saatlerde çalışan alarm
            hourItem = alarm["hour"].split(":")
            if now.hour == hourItem[0] and hourItem[1] - 1 <= now.minute <= hourItem[1] + 1:
                availableUserAlarms.append(alarm)
        elif alarm["type"] == 2: # Belli değeri geçince veya altında kalınca çalışan alarm
            for currencyCode in alarm["currencies"].split(","):
                if alarm["when"] == "bigger":
                    if currencies[currencyCode] >= alarm["value"]:
                        userAlarm["status"] = 0
                        availableUserAlarms.append(alarm)
                if alarm["when"] == "smaller":
                    if currencies[currencyCode] <= alarm["value"]:
                        userAlarm["status"] = 0
                        availableUserAlarms.append(alarm)
        elif alarm[0]["type"] == 3: # Belli miktarda dalgalanma olduğunda çalışan alarm
            userAlarmWavePoints = sourceHelper.getRows(userAlarmWavePointsTable["rows"], ["userAlarmId", "date"], [userAlarm["id"], now])
            if userAlarmWavePoints.length > 0:
                wavePoint = userAlarmWavePoints[0]["value"]
            else:


    sourceHelper.saveTable(userAlarmsTable) # çalışan type2 alarmları kaydet

    return availableUserAlarms
