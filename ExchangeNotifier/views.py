# -*- coding: utf-8 -*-

import urllib

from django.http import *

from sources.sourceDAL import *

from googleapiclient import http
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

BucketName = "exchangenotifier"

def auth(request):
    if "code" not in request.GET:
        if not "refresh_token" in request.COOKIES: # request for access_token
            scope = "https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform.read-only+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdevstorage.full_control+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdevstorage.read_only+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdevstorage.read_write"
            params = { "redirect_uri": WebConfig["AuthUri"], "client_id": WebConfig["ClientId"] }

            return HttpResponseRedirect("https://accounts.google.com/o/oauth2/auth?response_type=code&approval_prompt=force&access_type=offline&" + urllib.urlencode(params) + "&scope=" + scope)
        else: # refresh access_token
            params = { "client_id": WebConfig["ClientId"], "client_secret": WebConfig["ClientSecret"], "code":  request.COOKIES["code"] }
            r = requests.post(
                "https://www.googleapis.com/oauth2/v3/token?scope=&grant_type=authorization_code&" + urllib.urlencode(params),
                headers = { "Authorization": "Bearer " + request.COOKIES["refresh_token"] }
            )
    else: # get access_token
        code = request.GET["code"]

        params = { "redirect_uri": WebConfig["AuthUri"], "client_id": WebConfig["ClientId"], "client_secret": WebConfig["ClientSecret"], "code": code }
        r = requests.post("https://www.googleapis.com/oauth2/v3/token?scope=&grant_type=authorization_code&" + urllib.urlencode(params))

    authResponse = json.loads(r.text)

    response = HttpResponse("Authorized")
    if "RedirectUrl" in request.session:
        response = HttpResponseRedirect(WebConfig["Domain"] + request.session["RedirectUrl"])

    response.set_cookie("access_token_expired_date_total_seconds", (datetime.now() + timedelta(minutes = 50) - datetime(1970, 1, 1)).total_seconds())
    response.set_cookie("access_token", authResponse["access_token"])
    response.set_cookie("code", code)

    if "refresh_token" in authResponse:
        response.set_cookie("refresh_token", authResponse["refresh_token"])

    return response

def cloudstoragetest(request):
    authorized(request, "cloudstoragetest")

    credentials = AccessTokenCredentials(request.COOKIES["access_token"], "MyAgent/1.0", None)
    storage = discovery.build("storage", "v1", credentials = credentials)

    # storageResponse = storage.objects().list(bucket = BucketName).execute()
    # response = HttpResponse('<h3>Objects.list raw response:</h3><pre>{}</pre>'.format(json.dumps(storageResponse, sort_keys = True, indent = 2)))

    # Get Payload Data
    req = storage.objects().get(bucket = BucketName, object = "dailyRecords/temp.txt", projection = "full")
    # The BytesIO object may be replaced with any io.Base instance.
    fh = io.BytesIO()
    downloader = http.MediaIoBaseDownload(fh, req, chunksize = 1024*1024)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    return HttpResponse(fh.getvalue())

def downloadTest(request):
    authorized(request, "downloadTest")

    return HttpResponse(requests.get(WebConfig["DownloadUri"] % (BucketName, "dailyRecords%2Ftemp.txt"), headers = { "Authorization": "Bearer " + request.COOKIES["access_token"] }).text)

def insertTest(request):
    authorized(request, "insertTest")

    credentials = AccessTokenCredentials(request.COOKIES["access_token"], "MyAgent/1.0", None)
    storage = discovery.build("storage", "v1", credentials = credentials)

    # The BytesIO object may be replaced with any io.Base instance.
    media = http.MediaIoBaseUpload(io.BytesIO("test ediyor ahahahahahah"), 'text/plain')

    return HttpResponse(json.dumps(storage.objects().insert(bucket = BucketName, name = "test.txt", media_body = media).execute(), indent = 2))

def authorized(request, pageName):
    if "access_token" not in request.COOKIES:
        request.session["RedirectUrl"] = pageName
        return HttpResponseRedirect(WebConfig["AuthUri"])
    else:
        if (datetime.now() - datetime(1970, 1, 1)).total_seconds() >= float(request.COOKIES["access_token_expired_date_total_seconds"]):
            request.session["RedirectUrl"] = pageName
            return HttpResponseRedirect(WebConfig["AuthUri"])
