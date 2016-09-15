
import pytz
import urllib
import httplib
import requests
import unicodedata
import simplejson as json

from os import *
from datetime import *

from config import *

# region Project values
SourceConfig = getSourceConfig()
WebConfig = getWebConfig()

if WebConfig["UseProjectEngine"]:
    ProjectTablesPath = "tables/"
else:
    ProjectPath = getcwd()
    ProjectSourcePath = ProjectPath + "/sources/"
    ProjectTablesPath = ProjectSourcePath + "tables/"

tz = pytz.timezone('Europe/Istanbul')
# endregion

def getShortDateString():
    return getShortDateStringFromDate(datetime.now(tz))
def getShortDateStringFromDate(date):
    return "{0}-{1}-{2}".format(date.day, date.month, date.year)

def sendNotification(title, messageText, user):
    result = []

    notificationMethods = user["notificationMethods"];
    for notificationMethod in notificationMethods:
        if notificationMethod == "SMS":
            result.append(sendSms(user["phone"], messageText))
        elif notificationMethod == "FCM":
            result.append(sendFCM(user["fcmRegistrationId"], title, messageText))

    return result
def sendSms(phone, messageText):
    result = {}

    apiKey = "4df23cac-dbf4-42c1-9656-3a6736ca1a39"

    if not WebConfig["DebugSendSMS"]:
        params = {"from": "5514192308", "to": phone, "content": messageText}
        headers = {"Content-type": "application/x-www-form-urlencoded", "api_key": apiKey}

        conn = httplib.HTTPSConnection("api-gw.turkcell.com.tr")
        conn.request("POST", "/api/v1/sms", urllib.urlencode(params), headers)

        result = conn.getresponse().read()
        conn.close()

        result = json.loads(result)
        result["messageText"] = messageText
    else:
        result = {"messageText": messageText}

    return result
def sendFCM(fcmRegistrationId, title, messageText):
    params = {"to": fcmRegistrationId, "priority": "normal", "notification": {"title": title, "body": messageText, "sound": "cash-register-06"}, "data": {"body": messageText}}
    headers = {"Authorization": "key=" + WebConfig["FCMServerKey"]}

    response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, json=params)
    return json.loads(response.text);