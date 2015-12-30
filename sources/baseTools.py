
from os import *

from datetime import *
from twilio.rest import TwilioRestClient

from config import *

# region Project values
SourceConfig = getSourceConfig()
WebConfig = getWebConfig()

if WebConfig["UseGoogleAppEngine"]:
    ProjectTablesPath = "tables/"
else:
    ProjectSourcePath = path.dirname(__file__) + "/"
    ProjectTablesPath = ProjectSourcePath + "tables/"
    ProjectPath = ProjectSourcePath.replace("sources", "ExchangeNotifier")
# endregion

def getShortDateString():
    return getShortDateStringFromDate(datetime.now())
def getShortDateStringFromDate(date):
    return "{0}-{1}-{2}".format(date.day, date.month, date.year)

def sendSMS(messageText, user):
    account_sid = "AC2841ace8649ed31da847b9ab29ae499f"
    auth_token  = "6da7cfcbdc6855ae5cc927fd5701dd25"
    client = TwilioRestClient(account_sid, auth_token)

    return client.messages.create(body = messageText, to = user["phone"], from_ = "+15736256137")