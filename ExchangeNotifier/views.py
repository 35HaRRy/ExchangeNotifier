# -*- coding: utf-8 -*-

import urllib
import settings

from django.http import *

from sources.sourceDAL import *
from sources.tools import *

from googleapiclient import discovery
from oauth2client.client import AccessTokenCredentials

def currentsituation(request):
    isSuccessful = False

    code = ""
    message = "successful"

    # try:
    sourceHelper = source()

    dailyRecordsTable = sourceHelper.getTable("dailyRecords")
    if not dailyRecordsTable["error"]:
        # region Get&Set Currencies
        currencies = getGarantiCurrencies(dailyRecordsTable["config"]["codeFormat"])

        code = currencies["code"] = sourceHelper.getNewCode(dailyRecordsTable) # gunluk tum datayi apiden okuyacak hale geldiginde dailyRecordsTable a kaydı kaldır

        dailyRecordsTable["rows"].append(currencies)
        sourceHelper.saveTable(dailyRecordsTable)
        # endregion

        # region Check Max&Min and Alarms
        maxMinRecords = getCurrentMaxMinRecords(currencies)

        usersTable = sourceHelper.getTable("users")
        userAlarmsTable = sourceHelper.getTable("userAlarms")

        for user in usersTable["rows"]:
            availableUserAlarms = getAvailableUserAlarms(dailyRecordsTable, userAlarmsTable, user["id"])
            for availableUserAlarm in availableUserAlarms:
                messageText = getMessageText(availableUserAlarm, maxMinRecords, currencies)

                sendSMS(messageText, user)
        # endregion

        isSuccessful = True
    else:
        message = dailyRecordsTable["errorMessage"]
    # except Exception as e:
    #     isSuccessful = False
    #     message = e

    return HttpResponse("Code \"{0}\" is {1} - {2}. Message: {3}".format(code, str(isSuccessful), datetime.now(), message))

CLIENT_ID = "181684175257-0r909pah1c6fksigrhif4rmm1l3kuqub.apps.googleusercontent.com"
CLIENT_SECRET = "gkX2H8W1WHrwuhK-P0Ag_st1"
BUCKET_NAME = APPLICATION_NAME = "exchangenotifier"
AUTH_URI = "http://127.0.0.1:8000/auth"

def auth(request):
    if "code" not in request.GET:
        if not request.COOKIES.has_key("refresh_token"):
            scope = "https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform.read-only+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdevstorage.full_control+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdevstorage.read_only+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdevstorage.read_write"
            params = { "redirect_uri": AUTH_URI, "client_id": CLIENT_ID }

            return HttpResponseRedirect("https://accounts.google.com/o/oauth2/auth?response_type=code&approval_prompt=force&access_type=offline&" + urllib.urlencode(params) + "&scope=" + scope)
        else:
            params = { "refresh_token": request.COOKIES["refresh_token"], "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET }
            r = requests.post("https://www.googleapis.com/oauth2/v3/token?scope=&grant_type=authorization_code&" + urllib.urlencode(params))

    else:
        params = { "redirect_uri": AUTH_URI, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "code": request.GET["code"] }
        r = requests.post("https://www.googleapis.com/oauth2/v3/token?scope=&grant_type=authorization_code&" + urllib.urlencode(params))
        authResponse = json.loads(r.text)

        response = HttpResponse("Authorized")
        if request.session.has_key("RedirectUrl"):
            response = HttpResponseRedirect(request.session["RedirectUrl"])

        set_cookie(response, "access_token", authResponse["access_token"])
        set_cookie(response, "refresh_token", authResponse["refresh_token"])

        return response

def cloudstoragetest(request):
    if request.COOKIES.has_key("access_token"):
        credentials = AccessTokenCredentials(request.COOKIES["access_token"], "MyAgent/1.0", None)
        storage = discovery.build("storage", "v1", credentials = credentials)

        storageResponse = storage.objects().list(bucket = BUCKET_NAME).execute()
        response = HttpResponse('<h3>Objects.list raw response:</h3><pre>{}</pre>'.format(json.dumps(storageResponse, sort_keys = True, indent = 2)))
    else:
        request.session["RedirectUrl"] + "cloudstoragetest"
        response = HttpResponseRedirect(AUTH_URI)

    return  response


def set_cookie(response, key, value):
  max_age = int(WebConfig["CookieTime"])

  expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
  response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)