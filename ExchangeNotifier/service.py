import time
import requests
import simplejson as json

while True:
    webConfig = json.loads(open("C:\\Users\\hayri\\Desktop\\IOT\\ExchangeNotifier\\ExchangeNotifier\\webConfig.json").read())

    r = requests.get(webConfig["CurrencyQueryUrl"])
    print(r.text)

    time.sleep(webConfig["CurrencyQueryPeriod"])