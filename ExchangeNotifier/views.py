# -*- coding: utf-8 -*-

from random import randint
from django.http import *
from django.template.context_processors import csrf

from sources.sourceDAL import *

def currentsituation(request):
    isSuccessful = False

    auths = {}
    code = ""
    message = "successful"

    sourceHelper = source(auths = auths)

    if WebConfig["UseGoogleAppEngine"]:
        if not isAuthorized(request):
            if "IsCronJob" not in request.GET:
                request.session["RedirectUrl"] = "currentsituation"
                return HttpResponseRedirect(AuthUri)
            else:
                auths = json.loads(authanticate("refresh_token", WebConfig["RefreshToken"]))
                auths["refresh_token"] = WebConfig["RefreshToken"]
                auths["access_token_expired_date_total_seconds"] = (datetime.now(tz) + timedelta(minutes = 50) - datetime(1970, 1, 1).replace(tzinfo = tz)).total_seconds()
        else:
            auths = request.COOKIES

    try:
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

                    smsResult = sendSMS(messageText, user)
                    log = { "date": str(datetime.now(tz)), "description": str(user["name"]) + ": " + messageText, "error": str(smsResult) }
                    sourceHelper.insertTable("logs", log)
            # endregion

            isSuccessful = True
        else:
            message = dailyRecordsTable["errorMessage"]
    except Exception as e:
        isSuccessful = False
        message = e
        log = { "date": str(datetime.now(tz)), "description": "currentsituation error", "error": str(e) }
        sourceHelper.insertTable("logs", log)

    response = HttpResponse("Code \"{0}\" is {1} - {2}. Message: {3}".format(code, str(isSuccessful), datetime.now(tz), message))
    if WebConfig["UseGoogleAppEngine"] and "IsCronJob" in request.GET:
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

    response.set_cookie("access_token_expired_date_total_seconds", (datetime.now(tz) + timedelta(minutes = 50) - datetime(1970, 1, 1).replace(tzinfo = tz)).total_seconds())
    response.set_cookie("access_token", authResponse["access_token"])

    if "refresh_token" in authResponse:
        response.set_cookie("refresh_token", authResponse["refresh_token"])

    return response

def editor(request):
    if not isAuthorized(request):
        request.session["RedirectUrl"] = "editor/"
        if "FileName" in request.GET:
            request.session["RedirectUrl"] = "editor/?FileName=" + request.GET["FileName"]

        return HttpResponseRedirect(AuthUri)

    auths = request.COOKIES

    if "FileName" in request.GET:
        s = template.Template(downloadStorageObject(auths, "templates/editor.html"))
        # s = get_template("editor.html")

        if "hfValue" in request.POST:
            # data = { "data": request.POST["hfValue"].replace("\"", "\\\"").replace("\r", "").replace("\n", "") }
            data = { "data": unicodedata.normalize('NFKD', request.POST["hfValue"]).encode('ascii','ignore') }
            insertStorageObject(auths, request.GET["FileName"], data["data"])
        else:
            data = { "data": downloadStorageObject(auths, request.GET["FileName"]) }

        data.update(csrf(request))
        data["data"] = data["data"].replace("\"", "\\\"").replace("\r", "").replace("\n", "")

        return HttpResponse(s.render(template.Context(data)))
    else:
        return HttpResponse("File not found")

def logs(request):
    if not isAuthorized(request):
        request.session["RedirectUrl"] = "logs"
        return HttpResponseRedirect(AuthUri)

    auths = request.COOKIES
    sourceHelper = source(auths)

    s = template.Template(downloadStorageObject(auths, "templates/logs.html"))
    # s = get_template("logs.html")

    rows = ""
    for row in sourceHelper.getTable("logs")["rows"]:
        rows += "<tr><td>" + str(row["id"]) + "</td>"
        rows += "<td>" + str(row["date"]) + "</td>"
        rows += "<td>" + str(row["description"]) + "</td>"
        rows += "<td>" + str(row["error"]) + "</td></tr>"

    return HttpResponse(s.render(template.Context({ "data": rows })))

def downloadTest(request):
    if not isAuthorized(request):
        request.session["RedirectUrl"] = "downloadTest"
        return HttpResponseRedirect(AuthUri)

    return HttpResponse(downloadStorageObject(request.COOKIES, "test.txt"))

def insertTest(request):
    if not isAuthorized(request):
        request.session["RedirectUrl"] = "insertTest"
        return HttpResponseRedirect(AuthUri)

    credentials = AccessTokenCredentials(request.COOKIES["access_token"], "MyAgent/1.0", None)
    storage = discovery.build("storage", "v1", credentials = credentials)

    # The BytesIO object may be replaced with any io.Base instance.
    media = http.MediaIoBaseUpload(io.BytesIO("Test ediyor. " + str(randint(0, 1000000))), 'text/plain')

    return HttpResponse(json.dumps(storage.objects().insert(bucket = WebConfig["BucketName"], name = "test.txt", media_body = media).execute(), indent = 2))
