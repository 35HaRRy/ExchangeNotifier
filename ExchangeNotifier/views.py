# -*- coding: utf-8 -*-

from django.http import *
from random import randint

from sources.sourceDAL import *

def currentsituation(request):
    if not isAuthorized(request):
        if "IsCronJob" not in request.GET:
            request.session["RedirectUrl"] = "currentsituation"
            return HttpResponseRedirect(AuthUri)
        else:
            auths = json.loads(authanticate("refresh_token", WebConfig["RefreshToken"]))
            auths["refresh_token"] = WebConfig["RefreshToken"]
            auths["access_token_expired_date_total_seconds"] = (datetime.now() + timedelta(minutes = 50) - datetime(1970, 1, 1)).total_seconds()
    else:
        auths = { "refresh_token": request.COOKIES["refresh_token"], "access_token": request.COOKIES["access_token"], "access_token_expired_date_total_seconds": request.COOKIES["access_token_expired_date_total_seconds"] }

    isSuccessful = False

    code = ""
    message = "successful"

    try:
        sourceHelper = source(auths = auths)

        dailyRecordsTable = sourceHelper.getTable("dailyRecords")
        if not dailyRecordsTable["error"]:
            # region Get&Set Currencies
            currencies = getGarantiCurrencies(dailyRecordsTable["config"]["codeFormat"])

            code = currencies["code"] = sourceHelper.getNewCode(dailyRecordsTable) # gunluk tum datayi apiden okuyacak hale geldiginde dailyRecordsTable a kaydı kaldır

            dailyRecordsTable["rows"].append(currencies)
            sourceHelper.saveTable(dailyRecordsTable)
            # endregion

            # region Check Max&Min and Alarms
            maxMinRecords = getCurrentMaxMinRecords(auths, currencies)

            usersTable = sourceHelper.getTable("users")
            userAlarmsTable = sourceHelper.getTable("userAlarms")

            for user in usersTable["rows"]:
                availableUserAlarms = getAvailableUserAlarms(auths, dailyRecordsTable, userAlarmsTable, user["id"])
                for availableUserAlarm in availableUserAlarms:
                    messageText = getMessageText(availableUserAlarm, maxMinRecords, currencies)

                    sendSMS(messageText, user)
            # endregion

            isSuccessful = True
        else:
            message = dailyRecordsTable["errorMessage"]
    except Exception as e:
        isSuccessful = False
        message = e

    response = HttpResponse("Code \"{0}\" is {1} - {2}. Message: {3}".format(code, str(isSuccessful), datetime.now(), message))
    if "IsCronJob" in request.GET:
        response.set_cookie("access_token_expired_date_total_seconds", auths["access_token_expired_date_total_seconds"])
        response.set_cookie("access_token", auths["access_token"])
        response.set_cookie("refresh_token", auths["refresh_token"])

    return  response

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

    response = HttpResponse("Authorized")
    if "RedirectUrl" in request.session:
        response = HttpResponseRedirect(Domain + request.session["RedirectUrl"])

    response.set_cookie("access_token_expired_date_total_seconds", (datetime.now() + timedelta(minutes = 50) - datetime(1970, 1, 1)).total_seconds())
    response.set_cookie("access_token", authResponse["access_token"])

    if "refresh_token" in authResponse:
        response.set_cookie("refresh_token", authResponse["refresh_token"])

    return response

def editorTest(request):
    if not isAuthorized(request):
        request.session["RedirectUrl"] = "editorTest"
        return HttpResponseRedirect(AuthUri)

    if "FileName" in request.GET:
        # template.Template("")
        b = template.Context({ "data": downloadStorageObject(request.GET["FileName"], request).replace("\"", "\\\"") })
        return HttpResponse(get_template("editor.html").render(b))
    else:
        return HttpResponse("File not found")

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

