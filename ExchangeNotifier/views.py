# -*- coding: utf-8 -*-

import io
import urllib

from django.http import *

from googleapiclient import discovery
from googleapiclient.http import MediaIoBaseDownload

from oauth2client.client import AccessTokenCredentials

from sources.sourceDAL import *

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

BUCKET_NAME = "exchangenotifier"

def auth(request):
    if "code" not in request.GET:
        if not request.session.has_key("refresh_token"): # request for access_token
            scope = "https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform.read-only+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdevstorage.full_control+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdevstorage.read_only+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdevstorage.read_write"
            params = { "redirect_uri": WebConfig["AuthUri"], "client_id": WebConfig["ClientId"] }

            return HttpResponseRedirect("https://accounts.google.com/o/oauth2/auth?response_type=code&approval_prompt=force&access_type=offline&" + urllib.urlencode(params) + "&scope=" + scope)
        else: # refresh access_token
            params = { "refresh_token": request.session["refresh_token"], "client_id": WebConfig["ClientId"], "client_secret": WebConfig["ClientSecret"] }
            r = requests.post("https://www.googleapis.com/oauth2/v3/token?scope=&grant_type=authorization_code&" + urllib.urlencode(params))
    else: # get access_token
        params = { "redirect_uri": WebConfig["AuthUri"], "client_id": WebConfig["ClientId"], "client_secret": WebConfig["ClientSecret"], "code": request.GET["code"] }
        r = requests.post("https://www.googleapis.com/oauth2/v3/token?scope=&grant_type=authorization_code&" + urllib.urlencode(params))

    authResponse = json.loads(r.text)

    response = HttpResponse("Authorized")
    if request.session.has_key("RedirectUrl"):
        response = HttpResponseRedirect(WebConfig["Domain"] + request.session["RedirectUrl"])

    request.session["access_token"] = authResponse["access_token"]

    if authResponse.has_key("refresh_token"):
        request.session["refresh_token"] = authResponse["refresh_token"]

    return response

def cloudstoragetest(request):
    if request.session.has_key("access_token"):
        credentials = AccessTokenCredentials(request.session["access_token"], "MyAgent/1.0", None)
        storage = discovery.build("storage", "v1", credentials = credentials)

        # storageResponse = storage.objects().list(bucket = BUCKET_NAME).execute()
        # response = HttpResponse('<h3>Objects.list raw response:</h3><pre>{}</pre>'.format(json.dumps(storageResponse, sort_keys = True, indent = 2)))

        # Get Payload Data
        req = storage.objects().get(bucket = BUCKET_NAME, object = "dailyRecords/temp.txt")
        # The BytesIO object may be replaced with any io.Base instance.
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, req, chunksize = 1024*1024)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        return HttpResponse(fh.getvalue())
    else:
        request.session["RedirectUrl"] = "cloudstoragetest"
        response = HttpResponseRedirect(WebConfig["AuthUri"])

    return  response

def test(request):
    if request.session.has_key("access_token"):
        credentials = AccessTokenCredentials(request.session["access_token"], "MyAgent/1.0", None)
        storage = discovery.build("storage", "v1", credentials = credentials)

        req = requests.get(
            "https://www.googleapis.com/download/storage/v1/b/exchangenotifier/o/dailyRecords%2Ftemp.txt?generation=1450910006218000&alt=media",
            headers = { "Authorization": "Bearer " + request.session["access_token"] }
        )
        return HttpResponse(json.dumps(req.text, indent = 2))
    else:
        request.session["RedirectUrl"] = "test"
        return HttpResponseRedirect(WebConfig["AuthUri"])
