# -*- coding: utf-8 -*-

from django.http import *

from sources.sourceDAL import *
from sources.tools import *
 
def currentsituation(request):
    isSuccessful = False

    code = ""
    message = "successful"

    try:
        sourceHelper = source()

        dailyRecordsTable = sourceHelper.getTable("dailyRecords")
        if not dailyRecordsTable["error"]:
            # region Get&Set Currencies
            currencies = getTcmbCurrencies()

            code = currencies["code"] = dailyRecordsTable["config"]["newCode"]

            dailyRecordsTable["rows"].append(currencies)
            sourceHelper.saveTable(dailyRecordsTable)
            # endregion

            # region Check Max&Min and Alarms
            maxMinRecords = getCurrentMaxMinRecords(currencies)
            # alarmlari kontrol et
            usersTable = sourceHelper.getTable("users")
            userAlarmsTable = sourceHelper.getTable("userAlarms")
            alarmTypesTable = sourceHelper.getTable("alarmTypes")

            for user in usersTable["rows"]:
                availableUserAlarms = getAvailableUserAlarms(dailyRecordsTable, userAlarmsTable, user["id"])
                for availableUserAlarm in availableUserAlarms:
                    alarmType = sourceHelper.getRows(alarmTypesTable["rows"], ["id"], [availableUserAlarm["type"]])[0]
                    messageText = getMessageText(alarmType["messageTemplate"], [availableUserAlarm, maxMinRecords])

                    sendSMS(messageText, user)
            # endregion

            isSuccessful = True
        else:
            message = dailyRecordsTable["errorMessage"]
    except Exception as e:
        isSuccessful = False
        message = e

    return HttpResponse("Code \"{0}\" is {1} - {2}. Message: {3}".format(code, str(isSuccessful), datetime.now(), message))