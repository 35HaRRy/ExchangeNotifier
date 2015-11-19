# -*- coding: utf-8 -*-

from django.http import *

from sources.source import *
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

            currencies["code"] = dailyRecords["config"]["newCode"]

            dailyRecords["rows"].append(currencies)
            sourceHelper.saveTable(dailyRecords)
            # endregion

            # region Check Max&Min and Alarms
            maxMinRecords = getCurrentMaxMinRecords(currencies)
            # alarmları kontrol et
            users = sourceHelper.getTable("users")
            userAlarms = sourceHelper.getTable("userAlarms")

            for user in users["rows"]:
                maxMinRecordsText = getMaxMinRecordsText(maxMinRecords)

            availableUserAlarms = getAvailableUserAlarms(dailyRecords, userAlarms, user["id"])
                for availableUserAlarm in availableUserAlarms:


            # endregion

            isSuccessful = True
    except:
        isSuccessful = False

    return HttpResponse("Code \"{0}\" is {1} - {2}".format(code, str(isSuccessful), datetime.now()))