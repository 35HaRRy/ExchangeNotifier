# -*- coding: utf-8 -*-

from django.http import *

from sources.source import *
from sources.sourceDAL import *
from sources.tools import *
 
def currentsituation(request):
    isSuccessful = False

    try:
        sourceHelper = source()
        dailyRecord = sourceHelper.getTable("dailyRecords")

        if not dailyRecord["error"]:
            currencies = getTcmbCurrencies()

            # format = { "template": "d.m.y h:m:s", "separators": { "date": ".", "hour": ":", "dateHour": " " } }
            format = { "template": "d.m.y.h.m", "separator": "." }
            code = currencies["code"] = getCurrentCode(format)

            dailyRecord["rows"].append(currencies)
            sourceHelper.saveTable(dailyRecord)

            isSuccessful = True
    except:
        isSuccessful = False

    return HttpResponse("Code \"{0}\" is {1} - {2}".format(code, str(isSuccessful), datetime.now()))