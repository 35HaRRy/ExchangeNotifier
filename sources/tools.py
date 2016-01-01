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
        if (int)(row["id"]) > maxId:
            maxId = (int)(row["id"])

    return maxId

def isThisRow(clause, rowValue, value):
    if int == type(value):
        rowValue = (int)(rowValue)
    elif datetime == type(value):
        rowValue = datetime.strptime(rowValue.__str__().split(" ")[0], "%Y-%m-%d")
        value = datetime.strptime(value.__str__().split(" ")[0], "%Y-%m-%d")

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
       raise ValueError("clause cumlesi hatal?")

def getMessageText(availableUserAlarm, maxMinRecordTables, currencies):
    message = availableUserAlarm["name"] + " - Anlik kur. USD: #USD#, EURO: #EUR#, GBP: #GBP#"

    for currencyCode in availableUserAlarm["currencies"].split(","):
        message = message.replace("#" + currencyCode + "#", str(currencies[currencyCode]))

    for maxminTable in maxMinRecordTables:
        message += " " + maxminTable["config"]["title"] +  "("

        row = maxminTable["rows"][len(maxminTable["rows"]) - 1]
        maxmins = ["max", "min"]
        for maxmin in maxmins:
            message += " " + maxmin + ": "

            maxminMessageItems = []
            for currencyCode in availableUserAlarm["currencies"].split(","):
                maxminMessageItems.append(currencyCode + " " + str(row[maxmin][currencyCode]))

            message += ", ".join(maxminMessageItems)
        message += " )"

    return message
# endregion

# region File
def getFileContent(auths, fileFullPath):
    content = "[]"

    if WebConfig["UseGoogleAppEngine"]:
        content = downloadStorageObject(auths, fileFullPath)
    else:
        if path.isfile(fileFullPath):
            content = open(fileFullPath).read()
            if not content:
                content = "[]"
        else:
            open(fileFullPath, 'a')

    return content
# endregion
