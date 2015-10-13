# -*- coding: utf-8 -*-

from django.http import *

from sources.source import *
from sources.tools import *
 
def currentsituation(request):
    '''temp = source()
    table = temp.getTable("dailyRecords")

    return HttpResponse(table["error"])'''

    currencies = getTcmbCurrencies()

    return HttpResponse(currencies["USD"])