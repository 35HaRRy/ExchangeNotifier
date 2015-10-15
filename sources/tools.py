import os
import simplejson as json

from datetime import *

def getWebConfig():
    return json.loads(open(os.path.dirname(__file__).replace("sources", "") + "webConfig.json").read())

def getSortDateString():
    now = datetime.now()

    return "{0}-{1}-{2}".format(now.day, now.month, now.year)

def getCurrentCode(format):
    now = datetime.now()
    timetuple = now.timetuple()
    dateItems = { "d": now.day, "m": now.month, "y": now.year, "h": now.hour, "m": now.minute,"s": now.second, "wd": timetuple.tm_wday + 1 }

    code = []
    for templateItem in format["template"].split(format["separator"]):
       code.append(str(dateItems[templateItem]))

    return ".".join(code)
