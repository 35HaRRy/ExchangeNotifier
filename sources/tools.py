# -*- coding: utf-8 -*-

import os

from django import template
from django.template.loader import get_template

from appEngineTools import *

# region Table
def getCodeFromDate(now, format):
    nowIso = now.isocalendar()

    dateItems = { "d": now.day, "m": now.month, "y": now.year, "h": now.hour, "mn": now.minute, "s": now.second, "wy": nowIso[1], "dw": nowIso[2] }

    code = []
    for templateItem in format["template"].split(format["separator"]):
       code.append(str(dateItems[templateItem]))

    return ".".join(code)
def getMaxId(rows):
    maxId = 0
    for row in rows:
        if int(row["id"]) > maxId:
            maxId = int(row["id"])

    return maxId

def isThisRow(clause, rowValue, value):
    if int == type(value):
        rowValue = int(rowValue)
    elif float == type(value):
        rowValue = float(rowValue)
    elif datetime == type(value):
        rowValue = datetime.strptime(str(rowValue).split(" ")[0], "%Y-%m-%d")
        value = datetime.strptime(str(value).split(" ")[0], "%Y-%m-%d")

    if clause == "equal":
        return rowValue == value
    elif clause == "bigger":
        return rowValue < value
    elif clause == "biggerorequal":
        return rowValue <= value
    elif clause == "smaller":
        return rowValue > value
    elif clause == "smallerorequal":
        return rowValue >= value
    else:
       raise ValueError("clause cumlesi hatali")

def getMessageText(availableUserAlarm, maxMinRecordTables, currencies):
    message = availableUserAlarm["name"] + ": "

    for currencyCode in availableUserAlarm["currencies"].split(","):
        message += " " + currencyCode + " " + str(round(float(currencies[currencyCode]), 3))

    maxMins = ["max", "min"]

    for maxMinTable in maxMinRecordTables:
        message += " " + maxMinTable["config"]["title"].replace(" Max-Min Degerler", "") +  "("

        row = maxMinTable["rows"][len(maxMinTable["rows"]) - 1]

        currencyMaxMins = []
        for currencyCode in availableUserAlarm["currencies"].split(","):
            tempItems = []
            for maxMin in maxMins:
                tempItems.append(str(round(float(row[maxMin][currencyCode]), 3)))

            currencyMaxMins.append(currencyCode + " " + "/".join(tempItems))
        message += " ".join(currencyMaxMins) + ")"

    return message
# endregion

# region File
def getFileContent(auths, fileFullPath):
    content = "[]"

    if WebConfig["UseGoogleAppEngine"]:
        content = downloadStorageObject(auths, fileFullPath)
    else:
        fileFullPath = fileFullPath.replace("/", "\\")
        if path.isfile(fileFullPath):
            content = open(fileFullPath).read()
            if not content:
                content = "[]"
        else:
            open(fileFullPath, 'a')

    return content
# endregion
