
import requests
import xml.etree.ElementTree as xmlParser

from pyquery import PyQuery as pq

from source import *

def getTcmbCurrencies(format):
    r = requests.get('http://www.tcmb.gov.tr/kurlar/today.xml')
    tempCurrencies = xmlParser.fromstring(r.text.encode('utf-8')).findall('Currency')

    currencies = {}
    for currency in tempCurrencies:
        if currency.find("ForexSelling").text:
            currencies[currency.attrib["CurrencyCode"]] = currency.find("ForexSelling").text

    currency["code"] = getCodeFromDate(datetime.now(), format)
    currency["currencySource"] = "tcmb"

    return currencies

def getGarantiCurrencies(format):
    # r = requests.post("http://www.doviz.com/api/v1/currencies/all/latest/garanti")
    # tempCurrencies = json.loads(r.text)

    try:
        page = urllib2.urlopen("http://www.doviz.com/api/v1/currencies/all/latest/garanti").read()
    except httplib.IncompleteRead, e:
        page = e.partial
    tempCurrencies = json.loads(page)

    currencies = { "code": getCodeFromDate(datetime.fromtimestamp(int(tempCurrencies[0]["update_date"])), format), "currencySource": "Garanti - doviz.com api" }
    for currency in tempCurrencies:
        currencies[currency["code"]] = currency["selling"]

    return currencies
def getGarantiDailyValuesByCurrencyCode(currencyCode, format):
    r = requests.post("http://www.doviz.com/api/v1/currencies/" + currencyCode + "/daily/garanti")
    tempCurrencyValues = json.loads(r.text)

    currencyValues = []
    for tempCurrencyValeu in tempCurrencyValues:
        currencyValeu = { "value": float(tempCurrencyValeu["selling"]) }
        currencyValeu["code"] = getCodeFromDate(datetime.fromtimestamp(int(tempCurrencyValeu["update_date"])), format)

        currencyValues.append(currencyValeu)

    return currencyValues

def getEnParaCurrencies(format):
    dom = pq(url = "http://www.finansbank.enpara.com/doviz-kur-bilgileri/doviz-altin-kurlari.aspx")
    usd = float(dom(".dlCont:eq(2) span").html().replace("TL", "").strip().replace(",", "."))
    euro = float(dom(".dlCont:eq(5) span").html().replace("TL", "").strip().replace(",", "."))

    return { "code": getCodeFromDate(datetime.now(), format), "currencySource": "enpara", "USD": usd, "EUR": euro, "GBP": 0 }

def getCurrentMaxMinRecords(auths, dailyCurrencies):
    maxMinRecordTables = []
    sourceHelper = source(auths)

    maxMinRecordTableNames = ["dailyMaxMinRecords", "weeklyMaxMinRecords", "monthlyMaxMinRecords"]
    for maxMinRecordTableName in maxMinRecordTableNames:
        maxMinRecordTable = sourceHelper.getTable(maxMinRecordTableName)
        maxMinRecordNewCode = sourceHelper.getNewCode(maxMinRecordTable)

        currentRecord = sourceHelper.getRows(maxMinRecordTable["rows"], ["code"], [maxMinRecordNewCode])
        if len(currentRecord) == 0:
            currentRecord = {"code": maxMinRecordNewCode, "min": dailyCurrencies, "max": dailyCurrencies }
            maxMinRecordTable["rows"].append(currentRecord)
            sourceHelper.saveTable(maxMinRecordTable)
        else:
            currentRecord = currentRecord[0]

            for key, value in dailyCurrencies.items():
                if key not in ("code", "currencySource"):
                    if value >= currentRecord["max"][key]:
                        currentRecord["max"][key] = value

                    if value <= currentRecord["min"][key]:
                        currentRecord["min"][key] = value

            sourceHelper.updateTable(maxMinRecordTable, currentRecord)

        maxMinRecordTables.append(maxMinRecordTable)
    return  maxMinRecordTables

def getAvailableUserAlarms(auths, dailyRecordsTable, userAlarmsTable, userId):
    sourceHelper = source(auths)
    now = datetime.now(tz)

    currencies = dailyRecordsTable["rows"][len(dailyRecordsTable["rows"]) - 1]
    availableUserAlarms = []
    alarmsTable = sourceHelper.getTable("alarms")
    userAlarmWavePointsTable = sourceHelper.getTable("userAlarmWavePoints")

    userAlarms = sourceHelper.getRowsByClause(userAlarmsTable["rows"], ["userId", "startDate", "finishDate", "status"], [userId, now, now, "1"], ["equal", "biggerorequal", "smallerorequal", "equal"])
    for userAlarm in userAlarms:
        alarm = sourceHelper.getRows(alarmsTable["rows"], ["id"], userAlarm["alarmId"])[0]

        if alarm["type"] == "1": # Belli saatlerde calisan alarm
            hourItem = alarm["hour"].split(":")
            if now.hour == int(hourItem[0]) and int(hourItem[1]) - 2 <= now.minute <= int(hourItem[1]) + 2:
                availableUserAlarms.append(alarm)
        elif alarm["type"] == "2": # Belli degeri gecince veya altinda kalinca calisan alarm
            for currencyCode in alarm["currencies"].split(","):
                if isThisRow(alarm["when"], alarm["value"], currencies[currencyCode]):
                    availableUserAlarms.append(alarm)

                    userAlarm["status"] = "0"
                    sourceHelper.updateTable(userAlarmsTable, userAlarm)
        elif alarm["type"] == "3": # Belli miktarda dalgalanma oldugunda calisan alarm
            for currencyCode in alarm["currencies"].split(","):
                wavePoint = { "userAlarmId": userAlarm["id"], "date": str(now), "value": "", "currency": currencyCode, "isReferencePoint": "1" }

                userAlarmWavePoints = sourceHelper.getRows(userAlarmWavePointsTable["rows"], ["userAlarmId", "date", "currency"], [userAlarm["id"], now, currencyCode])
                if len(userAlarmWavePoints) == 0:
                    lastDayLastWavePoint = sourceHelper.getRows(userAlarmWavePointsTable["rows"], ["userAlarmId", "date", "currency"], [userAlarm["id"], now + timedelta(days = -1), currencyCode])
                    if len(lastDayLastWavePoint) > 0:
                        wavePoint["value"] = lastDayLastWavePoint[0]["value"]
                    else:
                        wavePoint["value"] = currencies[currencyCode]

                    wavePoint["id"] = sourceHelper.getNewCode(userAlarmWavePointsTable)
                    wavePoint["isReferencePoint"] = "0"

                    userAlarmWavePointsTable["rows"].append(wavePoint)
                    sourceHelper.saveTable(userAlarmWavePointsTable)
                else:
                    wavePoint = userAlarmWavePoints[0]

                currentWave = float(currencies[currencyCode]) - float(wavePoint["value"])
                if alarm["when"] == "increase":
                    isWaving = isThisRow("biggerorequal", alarm["value"], currentWave)
                elif alarm["when"] == "decrease":
                    isWaving = isThisRow("smaller", 0, currentWave) and isThisRow("biggerorequal", alarm["value"], currentWave * -1)

                if isWaving:
                    availableUserAlarms.append(alarm)

                    if wavePoint["isReferencePoint"] == "0":
                        wavePoint["value"] = currencies[currencyCode]
                        wavePoint["date"] = str(now)
                        sourceHelper.updateTable(userAlarmWavePointsTable, wavePoint)

    return availableUserAlarms
