# -*- coding: utf-8 -*-

from django.http import *
from random import randint

from sources.sourceDAL import *

def currentsituation(request):
    if not isAuthorized(request):
        request.session["RedirectUrl"] = "downloadTest"
        return HttpResponseRedirect(AuthUri)

    isSuccessful = False

    code = ""
    message = "successful"

    # try:
    sourceHelper = source(request = request)

    dailyRecordsTable = sourceHelper.getTable("dailyRecords")
    if not dailyRecordsTable["error"]:
        # region Get&Set Currencies
        currencies = getGarantiCurrencies(dailyRecordsTable["config"]["codeFormat"])

        code = currencies["code"] = sourceHelper.getNewCode(dailyRecordsTable) # gunluk tum datayi apiden okuyacak hale geldiginde dailyRecordsTable a kaydı kaldır

        dailyRecordsTable["rows"].append(currencies)
        sourceHelper.saveTable(dailyRecordsTable)
        # endregion

        # region Check Max&Min and Alarms
        maxMinRecords = getCurrentMaxMinRecords(request, currencies)

        usersTable = sourceHelper.getTable("users")
        userAlarmsTable = sourceHelper.getTable("userAlarms")

        for user in usersTable["rows"]:
            availableUserAlarms = getAvailableUserAlarms(request, dailyRecordsTable, userAlarmsTable, user["id"])
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

def auth(request):
    if "code" not in request.GET:
        if not "refresh_token" in request.COOKIES: # request for access_token
            scope = "https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform.read-only+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdevstorage.full_control+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdevstorage.read_only+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdevstorage.read_write"
            params = { "redirect_uri": AuthUri, "client_id": WebConfig["ClientId"] }

            return HttpResponseRedirect("https://accounts.google.com/o/oauth2/auth?response_type=code&approval_prompt=force&access_type=offline&" + urllib.urlencode(params) + "&scope=" + scope)
        else:
            data = authanticate("refresh_token", request.COOKIES["refresh_token"])
    else:
        data = authanticate("authorization_code", request.GET["code"])

    authResponse = json.loads(data)
    # return HttpResponse(data)

    response = HttpResponse("Authorized")
    if "RedirectUrl" in request.session:
        response = HttpResponseRedirect(Domain + request.session["RedirectUrl"])

    response.set_cookie("access_token_expired_date_total_seconds", (datetime.now() + timedelta(minutes = 50) - datetime(1970, 1, 1)).total_seconds())
    response.set_cookie("access_token", authResponse["access_token"])

    if "refresh_token" in authResponse:
        response.set_cookie("refresh_token", authResponse["refresh_token"])

    return response

def cloudstoragetest(request):
    if not isAuthorized(request):
        request.session["RedirectUrl"] = "downloadTest"
        return HttpResponseRedirect(AuthUri)

    credentials = AccessTokenCredentials(request.COOKIES["access_token"], "MyAgent/1.0", None)
    storage = discovery.build("storage", "v1", credentials = credentials)

    # storageResponse = storage.objects().list(bucket = WebConfig["BucketName"]).execute()
    # response = HttpResponse('<h3>Objects.list raw response:</h3><pre>{}</pre>'.format(json.dumps(storageResponse, sort_keys = True, indent = 2)))

    # Get Payload Data
    req = storage.objects().get(bucket = WebConfig["BucketName"], object = "test.txt", projection = "full")
    # The BytesIO object may be replaced with any io.Base instance.
    fh = io.BytesIO()
    downloader = http.MediaIoBaseDownload(fh, req, chunksize = 1024*1024)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    return HttpResponse(fh.getvalue())

def downloadTest(request):
    if not isAuthorized(request):
        request.session["RedirectUrl"] = "downloadTest"
        return HttpResponseRedirect(AuthUri)

    return HttpResponse(downloadStorageObject("test.txt", request))

def insertTest(request):
    if not isAuthorized(request):
        request.session["RedirectUrl"] = "insertTest"
        return HttpResponseRedirect(AuthUri)

    credentials = AccessTokenCredentials(request.COOKIES["access_token"], "MyAgent/1.0", None)
    storage = discovery.build("storage", "v1", credentials = credentials)

    # The BytesIO object may be replaced with any io.Base instance.
    media = http.MediaIoBaseUpload(io.BytesIO("Test ediyor. " + str(randint(0, 1000000))), 'text/plain')

    return HttpResponse(json.dumps(storage.objects().insert(bucket = WebConfig["BucketName"], name = "test.txt", media_body = media).execute(), indent = 2))
