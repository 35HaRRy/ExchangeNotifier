# -*- coding: utf-8 -*-

from django.http import *

from sources.sourceDAL import *
from sources.tools import *
 
def currentsituation(request):
    isSuccessful = False

    try:
        sourceHelper = source()
        dailyRecords = sourceHelper.getTable("dailyRecords")

        if not dailyRecords["error"]:
            # region Get&Set Currencies
            currencies = getTcmbCurrencies()

            code = currencies["code"] = dailyRecords["config"]["newCode"]

            dailyRecords["rows"].append(currencies)
            sourceHelper.saveTable(dailyRecords)
            # endregion

            # region Check Max&Min and Alarms
            maxMinRecords = getCurrentMaxMinRecords(currencies)
            # alarmları kontrol et
            usersTable = sourceHelper.getTable("users")
            userAlarmsTable = sourceHelper.getTable("userAlarms")
            alarmTypesTable = sourceHelper.getTable("alarmTypes")

            for user in usersTable["rows"]:
                availableUserAlarms = getAvailableUserAlarms(dailyRecords, userAlarmsTable, user["id"])
                for availableUserAlarm in availableUserAlarms:
                    alarmType = sourceHelper.getRows(alarmTypesTable["rows"], ["id"], [availableUserAlarm["type"]])[0]
                    messageText = getMessageText(alarmType["messageTemplate"], [availableUserAlarm, maxMinRecords])

                    sendSMS(messageText, user)
            # endregion

            isSuccessful = True
    except:
        isSuccessful = False

    return HttpResponse("Code \"{0}\" is {1} - {2}".format(code, str(isSuccessful), datetime.now()))