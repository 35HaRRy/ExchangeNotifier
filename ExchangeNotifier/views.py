# -*- coding: utf-8 -*-

from random import randint
from django.http import *
from django.template.context_processors import csrf

from sources.sourceDAL import *

def situation(request):
    code = ""
    isSuccessful = False
    message = "successful"

    auths = fillAuths(request)
    sourceHelper = source(auths = auths)

    try:
        dailyRecordsTable = sourceHelper.getTable("dailyRecords")
        if not dailyRecordsTable["error"]:
            # region Get&Set Currencies
            currencySource = "enpara"
            if "currencySource" in request.GET:
                currencySource = request.GET["currencySource"]

            currencies = {}
            if currencySource == "tcmb":
                currencies = getTcmbCurrencies(dailyRecordsTable["config"]["codeFormat"])
            elif currencySource == "garanti.doviz.com":
                currencies = getGarantiCurrencies(dailyRecordsTable["config"]["codeFormat"])
            elif currencySource == "enpara":
                currencies = getEnParaCurrencies(dailyRecordsTable["config"]["codeFormat"])

            code = currencies["code"]

            dailyRecordsTable["rows"].append(currencies)
            sourceHelper.saveTable(dailyRecordsTable)
            # endregion

            mode = "current"
            if "mode" in request.GET:
                mode = request.GET["mode"]

            if mode == "current": # region Check Max&Min and Alarms
                maxMinRecords = insertUpdateCurrentMaxMinRecords(auths, currencies)

                usersTable = sourceHelper.getTable("users")
                userAlarmsTable = sourceHelper.getTable("userAlarms")

                for user in usersTable["rows"]:
                    availableUserAlarms = getAvailableUserAlarms(auths, dailyRecordsTable, userAlarmsTable, user["id"])
                    for availableUserAlarm in availableUserAlarms:
                        messageText = getMessageText(availableUserAlarm, maxMinRecords, currencies)
                        notificationResult = str(sendNotification(availableUserAlarm["name"], messageText, user)).replace("'", "-").replace("\"", "-")

                        log = {"date": str(datetime.now(tz)), "description": str(user["name"]) + ": bildirim gonderme islemi", "error": notificationResult}
                        sourceHelper.insertTable("logs", log)
            elif mode == "notifieUser":
                maxMinRecords = insertUpdateCurrentMaxMinRecords(auths, currencies)

                users = sourceHelper.getRows(sourceHelper.getTable("users")["rows"], ["id"], [request.GET["id"]])
                if len(users) > 0:
                    userAlarms = sourceHelper.getRows(sourceHelper.getTable("userAlarms")["rows"], ["userId", "alarmId"], [users[0]["id"], "9"])
                    if len(userAlarms) > 0:
                        alarm = sourceHelper.getRows(sourceHelper.getTable("alarms")["rows"], ["id"], ["9"])[0]

                        notificationResult = sendNotification(alarm["name"], getMessageText(alarm, maxMinRecords, currencies), users[0])
                        log = {"date": str(datetime.now(tz)), "description": str(users[0]["name"]) + ": bildirim gonderme islemi", "error": str(notificationResult)}
                        sourceHelper.insertTable("logs", log)

            isSuccessful = True
        else:
            message = dailyRecordsTable["errorMessage"]
    except Exception as e:
        isSuccessful = False
        message = str(e)

        sourceHelper.insertTable("logs", {"date": str(datetime.now(tz)), "description": "situation error", "error": message.replace("'", "-").replace("\"", "-")})

    response = HttpResponse("Code \"{0}\" is {1} - {2}. Message: {3}".format(code, str(isSuccessful), datetime.now(tz), message))

    if isSuccessful:
        fillAuthResponse(auths, response)

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
    response = {}
    auths = fillAuths(request)

    if "FileName" in request.GET:
        s = template.Template(downloadStorageObject(auths, "templates/editor.html"))
        # s = get_template("editor.html")

        if "hfValue" in request.POST:
            data = { "data": unicodedata.normalize("NFKD", request.POST["hfValue"]).encode("ascii", "ignore") }
            insertStorageObject(auths, request.GET["FileName"], data["data"])
        else:
            data = { "data": downloadStorageObject(auths, request.GET["FileName"]) }

        # data.update(csrf(request))
        data["data"] = data["data"].replace("\"", "\\\"").replace("\r", "").replace("\n", "")

        response = HttpResponse(s.render(template.Context(data)))
    else:
        response = HttpResponse("File not found")

    fillAuthResponse(auths, response)

    return response

def logs(request):
    response = {}
    auths = fillAuths(request)
    sourceHelper = source(auths)

    rows = ""
    s = template.Template(downloadStorageObject(auths, "templates/logs.html"))

    logTable = sourceHelper.getTable("logs")
    for row in logTable["rows"]:
        rows += "<tr><td>" + str(row["id"]) + "</td>"
        rows += "<td>" + str(row["date"]) + "</td>"
        rows += "<td>" + str(row["description"]) + "</td>"
        rows += "<td>" + str(row["error"]) + "</td></tr>"

    response = HttpResponse(s.render(template.Context({ "data": rows })))
    fillAuthResponse(auths, response)

    return response

def dbRequest(request):
    response = {}
    auths = fillAuths(request)

    requestUser = {}
    if request.method == 'POST':
        if request.POST["FunctionName"] == "insertUpdateUser":
            if "email" in request.POST and "fcmRegistrationId" in request.POST:
                requestUser = { "email": request.POST["email"], "fcmRegistrationId": request.POST["fcmRegistrationId"] }
            else:
                response = HttpResponse(str({"messageType": 0, "message": "email or fcmRegistrationId parameters are missing"}))
        else:
            response = HttpResponse(str({"messageType": 0, "message": "Invalid function name"}))
    else:
        response = HttpResponse(str({ "messageType": 0, "message": "Request method must be POST" }))

    if response != {}:
        fillAuthResponse(auths, response)
        return response

    sourceHelper = source(auths)

    if request.POST["FunctionName"] == "insertUpdateUser":
        usersTable = sourceHelper.getTable("users")

        # if "id" in requestUser:
        #     sourceHelper.updateTable(usersTable, requestUser)

        users = sourceHelper.getRows(usersTable["rows"], ["email"], [requestUser["email"]])
        if len(users) > 0:
            user = users[0]
            user["fcmRegistrationId"] = requestUser["fcmRegistrationId"]
            sourceHelper.updateTable(usersTable, user)
        else:
            requestUser["id"] = str(getMaxId(usersTable["rows"]))
            requestUser["notificationMethods"] = "FCM"
            sourceHelper.insertTable("users", requestUser)

    response = HttpResponse(str({"messageType": 1, "message": "user '%s' was updated successfully" % requestUser["email"]}))
    fillAuthResponse(auths, response)

    return response

def downloadTest(request):
    response = HttpResponse(downloadStorageObject(fillAuths(request), "test.txt"))
    fillAuthResponse(auths, response)

    return response

def insertTest(request):
    auths = fillAuths(request)

    credentials = AccessTokenCredentials(auths["access_token"], "MyAgent/1.0", None)
    storage = discovery.build("storage", "v1", credentials = credentials)

    # The BytesIO object may be replaced with any io.Base instance.
    media = http.MediaIoBaseUpload(io.BytesIO("Test ediyor. " + str(randint(0, 1000000))), 'text/plain')

    response = HttpResponse(json.dumps(storage.objects().insert(bucket = WebConfig["BucketName"], name = "test.txt", media_body = media).execute(), indent = 2))
    fillAuthResponse(auths, response)

    return response

def fcmTest(request):
    fcmRegistrationId = request.POST["fcmRegistrationId"]
    title = request.POST["title"]
    messageText = request.POST["messageText"]

    return HttpResponse(str(sendFCM(fcmRegistrationId, title, messageText)))

def test(request):
    return HttpResponse(request.body)