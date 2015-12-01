import time
import requests
import simplejson as json

from datetime import datetime as dt

webConfig = json.loads(open("C:\\Users\\hayri\\Desktop\\IOT\\ExchangeNotifier\\ExchangeNotifier\\webConfig.json").read())

currencyQueryStartHour = webConfig["CurrencyQueryStartHour"].split(":")
currencyQueryFinishHour = webConfig["CurrencyQueryFinishHour"].split(":")

for i in range(0, 1):
    currencyQueryStartHour[i] = (int)(currencyQueryStartHour[i])
    currencyQueryFinishHour[i] = (int)(currencyQueryFinishHour[i])

while True:
    now = dt.now()

    r = requests.get(webConfig["CurrencyQueryUrl"])
    print(r.text)

    sleepTime = (int)(webConfig["CurrencyQueryPeriod"])
    if now.hour == currencyQueryFinishHour[0] and currencyQueryFinishHour[1] - 1 <= now.minute <= currencyQueryFinishHour[1] + 1:
        sleepTime = (24 + currencyQueryStartHour[0] - now.hour) * 60 + currencyQueryStartHour[1] - now.minute

        if now.isocalendar()[2] - 1 == 5: # cuma gunu ise pazartesi acilisa kadar uyu
            sleepTime += 48

    print(sleepTime.__str__() + " sn. uyku modunda")
    time.sleep(sleepTime)