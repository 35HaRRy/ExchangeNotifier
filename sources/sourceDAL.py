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
        maxMinRecordConfig = maxMinRecordTable["config"]

        currentRecord = sourceHelper.getRows(maxMinRecordTable["rows"], ["code"], [maxMinRecordConfig["newCode"]])
        if len(currentRecord) == 0:
            currentRecord = {"code": maxMinRecordConfig["newCode"], "min": dailyCurrencies, "max": dailyCurrencies }
            maxMinRecordTable["rows"].append(currentRecord)
        else:
            currentRecord = currentRecord[0]

            for key, value in dailyCurrencies.items():
                if value >= currentRecord["max"][key]:
                    currentRecord["max"][key] = value

                if value <= currentRecord["min"][key]:
                    currentRecord["min"][key] = value

        sourceHelper.saveTable(maxMinRecordTable)
        maxMinRecordTables.append(maxMinRecordTable)

    return  maxMinRecordTables

def getAvailableUserAlarms(dailyRecordsTable, userAlarmsTable, userId):
    sourceHelper = source()
    now = datetime.now()

    currencies = dailyRecordsTable["rows"][len(dailyRecordsTable["rows"]) - 1]
    availableUserAlarms = []
    alarmsTable = sourceHelper.getTable("alarms")
    userAlarmWavePointsTable = sourceHelper.getTable("userAlarmWavePoints")

    userAlarms = sourceHelper.getRowsByClause(userAlarmsTable["rows"], ["userId", "startDate", "finishDate", "status"], [userId, now, now, "1"], ["equal", "bigger", "smaller", "equal"])
    for userAlarm in userAlarms:
        alarm = sourceHelper.getRows(alarmsTable["rows"], ["id"], userAlarm["alarmId"])[0]

        if alarm["type"] == "1": # Belli saatlerde calisan alarm
            hourItem = alarm["hour"].split(":")
            if now.hour == hourItem[0] and hourItem[1] - 1 <= now.minute <= hourItem[1] + 1:
                availableUserAlarms.append(alarm)
        elif alarm["type"] == "2": # Belli degeri gecince veya altinda kalinca calisan alarm
            for currencyCode in alarm["currencies"].split(","):
                if isThisRow(alarm["when"], alarm["value"], currencies[currencyCode]):
                    userAlarm["status"] = "0"
                    availableUserAlarms.append(alarm)

            sourceHelper.saveTable(userAlarmsTable)
        elif alarm["type"] == "3": # Belli miktarda dalgalanma oldugunda calisan alarm
            for currencyCode in alarm["currencies"].split(","):
                wavePoint = { "userAlarmId": userAlarm["id"], "date": now, "value": "", "currency": currencyCode, "isReferencePoint": "1" }

                userAlarmWavePoints = sourceHelper.getRows(userAlarmWavePointsTable["rows"], ["userAlarmId", "date", "currency"], [userAlarm["id"], now, currencyCode])
                if len(userAlarmWavePoints) == 0:
                    lastDayCloseRecords = sourceHelper.getSourceTable("dailyRecords", { "ShortDateString": getShortDateStringFromDate(now + timedelta(days=-1)) })
                    wavePoint["value"] = lastDayCloseRecords["rows"][len(lastDayCloseRecords["rows"]) - 1][currencyCode]
                    wavePoint["isReferencePoint"] = "0"

                    userAlarmWavePointsTable["rows"].append(wavePoint)

                currentWave = (float)(currencies[currencyCode]) - (float)(wavePoint["value"])
                if alarm["when"] == "increase":
                    isWaving = isThisRow("biggerorequal", alarm["value"], currentWave)
                elif alarm["when"] == "decrease":
                    isWaving = isThisRow("smaller", 0, currentWave) and isThisRow("biggerorequal", alarm["value"], currentWave * -1)

                if isWaving:
                    availableUserAlarms.append(alarm)

                    if wavePoint["isReferencePoint"] == "0":
                        wavePoint["value"] = currencies[currencyCode]

                sourceHelper.saveTable(userAlarmWavePointsTable)

    return availableUserAlarms
