import time
import requests
import simplejson as json

from datetime import datetime as dt

while True:
    webConfig = json.loads(open("C:\\Users\\hayri\\Desktop\\IOT\\ExchangeNotifier\\ExchangeNotifier\\webConfig.json").read())

    r = requests.get(webConfig["CurrencyQueryUrl"])
    print(r.text)

    now = dt.now()
    currencyQueryFinishHour = webConfig["CurrencyQueryFinishHour"].split(":")
    currencyQueryStartHour = webConfig["CurrencyQueryStartHour"].split(":")

    sleepTime = (int)(webConfig["CurrencyQueryPeriod"])
    if now.hour == (int)(currencyQueryFinishHour[0]) and (int)(currencyQueryFinishHour[0]) - 1 <= now <= (int)(currencyQueryFinishHour[0]) + 1:
        sleepTime = (24 + (int)(currencyQueryStartHour[0]) - now.hour) * 60 + (int)(currencyQueryStartHour[1]) - now.minute

    print(sleepTime.__str__() + " sn. uyku modunda")
    time.sleep(sleepTime)