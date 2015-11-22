import os
import simplejson as json

from twilio.rest import TwilioRestClient

from datetime import *

def getWebConfig():
    return json.loads(open(os.path.dirname(__file__).replace("sources", "") + "webConfig.json").read())

def getSortDateString():
    return getSortDateString(datetime.now())
def getSortDateString(date):
    return "{0}-{1}-{2}".format(date.day, date.month, date.year)

def getCode(format):
    return  getCode(datetime.now(), format)

def getCode(now, format):
    nowIso = now.isocalendar()

    dateItems = { "d": now.day, "m": now.month, "y": now.year, "h": now.hour, "m": now.minute,"s": now.second, "wy": nowIso[1], "dw": nowIso[2] }

    code = []
    for templateItem in format["template"].split(format["separator"]):
       code.append(str(dateItems[templateItem]))

    return ".".join(code)

def isThisRow(clause, rowValue, value):
    rowValue = type(value)(rowValue)

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
       raise ValueError("clause cümlesi hatal?")

def getMessageText(messageTemplate, datas):
    message = messageTemplate

    for data in datas:
        for (key, value) in data.iterItems():
            message = message.replace("#" + key + "#", value)

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
