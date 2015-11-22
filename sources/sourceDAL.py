﻿import requests
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
                if isThisRow(alarm["when"], alarm["value"], currencies[currencyCode]):
                    userAlarm["status"] = 0
                    availableUserAlarms.append(alarm)
        elif alarm["type"] == 3: # Belli miktarda dalgalanma olduğunda çalışan alarm
            for currencyCode in alarm["currencies"].split(","):
                wavePoint = { "userAlarmId": userAlarm["id"], "date": now, "value": "", "currency": currencyCode, "isReferencePoint": 1 }

                userAlarmWavePoints = sourceHelper.getRows(userAlarmWavePointsTable["rows"], ["userAlarmId", "date", "currency"], [userAlarm["id"], now, currencyCode])
                if userAlarmWavePoints.length == 0:
                    lastDayCloseRecords = sourceHelper.getTable("dailyRecords", { "options": getSortDateString(now + timedelta(days=-1)) })
                    wavePoint = lastDayCloseRecords["rows"][lastDayCloseRecords["rows"] - 1][currencyCode]
                    wavePoint["isReferencePoint"] = 0

                    userAlarmWavePoints.append(wavePoint)

                currentWave = (float)(currencies[currencyCode]) - (float)(wavePoint["value"])
                if alarm["when"] == "increase":
                    isWaving = isThisRow("biggerorequal", alarm["value"], currentWave)
                elif alarm["when"] == "decrease":
                    isWaving = isThisRow("smaller", 0, currentWave) and isThisRow("biggerorequal", alarm["value"], currentWave * -1)

                if isWaving:
                    availableUserAlarms.append(alarm)

                    if wavePoint["isReferencePoint"] == 0:
                        wavePoint["value"] = currencies[currencyCode]

                sourceHelper.saveTable(userAlarmWavePointsTable)

    sourceHelper.saveTable(userAlarmsTable) # çalışan type2 alarmları kaydet

    return availableUserAlarms
