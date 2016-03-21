
import pytz
import urllib
import httplib
import unicodedata
import simplejson as json

from os import *
from datetime import *
# from twilio.rest import TwilioRestClient

from config import *

# region Project values
SourceConfig = getSourceConfig()
WebConfig = getWebConfig()

if WebConfig["UseGoogleAppEngine"]:
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

def sendSMS(messageText, user):
    # account_sid = "AC2841ace8649ed31da847b9ab29ae499f"
    # auth_token  = "6da7cfcbdc6855ae5cc927fd5701dd25"
    # client = TwilioRestClient(account_sid, auth_token)

    # if not WebConfig["DebugSendSMS"]:
        # return client.messages.create(body = messageText, to = user["phone"], from_ = "+15736256137")

    apiKey = "4df23cac-dbf4-42c1-9656-3a6736ca1a39"

    if not WebConfig["DebugSendSMS"]:
        params = { "from": "5514192308", "to": user["phone"], "content": messageText }
        headers = { "Content-type": "application/x-www-form-urlencoded", "api_key": apiKey }

        conn = httplib.HTTPSConnection("api-gw.turkcell.com.tr")
        conn.request("POST", "/api/v1/sms", urllib.urlencode(params), headers)

        data = conn.getresponse().read()
        conn.close()

        data = json.loads(data)
        data["messageText"] = messageText
        return data
    else:
        return { "messageText": messageText }