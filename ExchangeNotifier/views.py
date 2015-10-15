# -*- coding: utf-8 -*-

from django.http import *

from sources.source import *
from sources.sourceDAL import *
from sources.tools import *
 
def currentsituation(request):
    sourceHelper = source()
    currencies = getTcmbCurrencies()

    # format = { "template": "d.m.y h:m:s", "separators": { "date": ".", "hour": ":", "dateHour": " " } }
    format = { "template": "d.m.y.h.m", "separator": "." }
    currencies["code"] = getCurrentCode(format)

    dailyRecord = sourceHelper.getTable("dailyRecords")
    dailyRecord["rows"].append(currencies)

    sourceHelper.saveTable(dailyRecord)

    return HttpResponse(str(dailyRecord))