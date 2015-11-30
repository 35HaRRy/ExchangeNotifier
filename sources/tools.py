# -*- coding: utf-8 -*-

import os
import simplejson as json

from twilio.rest import TwilioRestClient

from datetime import *

# region Project values
ProjectSourcePath = os.path.dirname(__file__) + "\\"
ProjectTablesPath = ProjectSourcePath + "\\tables\\"
ProjectPath = ProjectSourcePath.replace("sources", "ExchangeNotifier")

SourceConfig = json.loads(open(ProjectSourcePath + "sourceConfig.json").read())["sourceConfig"]
WebConfig = json.loads(open(ProjectPath + "webConfig.json").read())
# endregion

def getShortDateString():
    return getShortDateStringFromDate(datetime.now())
def getShortDateStringFromDate(date):
    return "{0}-{1}-{2}".format(date.day, date.month, date.year)

def getCodeFromDate(now, format):
    nowIso = now.isocalendar()

    dateItems = { "d": now.day, "m": now.month, "y": now.year, "h": now.hour, "mn": now.minute, "s": now.second, "wy": nowIso[1], "dw": nowIso[2] }

    code = []
    for templateItem in format["template"].split(format["separator"]):
       code.append(str(dateItems[templateItem]))

    return ".".join(code)
def getMaxId(rows):
    maxId = 1
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
        message = message.replace("#" + currencyCode + "#", currencies[currencyCode])

    for maxminTable in maxMinRecordTables:
        message += " " + maxminTable["config"]["title"] +  "("

        row = maxminTable["rows"][len(maxminTable["rows"]) - 1]
        maxmins = ["max", "min"]
        for maxmin in maxmins:
            message += " " + maxmin + ": "

            maxminMessageItems = []
            for currencyCode in availableUserAlarm["currencies"].split(","):
                maxminMessageItems.append(currencyCode + " " + row[maxmin][currencyCode])

            message += ", ".join(maxminMessageItems)
        message += " )"

    return message

def sendSMS(messageText, user):
    account_sid = "AC2841ace8649ed31da847b9ab29ae499f"
    auth_token  = "6da7cfcbdc6855ae5cc927fd5701dd25"
    client = TwilioRestClient(account_sid, auth_token)

    message = client.messages.create(
        body= messageText,
        to= user["phone"],
        from_="+15736256137")

    return message
