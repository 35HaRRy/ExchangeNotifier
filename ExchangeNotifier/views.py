# -*- coding: utf-8 -*-

from django.http import *

from sources.sourceDAL import *
from sources.tools import *
 
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