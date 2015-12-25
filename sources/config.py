
def getWebConfig():
	return {
		"CurrencyQueryStartHour": "09:30",
		"CurrencyQueryFinishHour": "17:00",
		"CurrencyQueryPeriod": "4",
		"CurrencyQueryUrl": "http://127.0.0.1:8000/currentsituation",
		"ProjectPath": "C:\\Users\\hayri\\Desktop\\IOT\\ExchangeNotifier",
		"GoogleApplicationCredentials": "ExchangeNotifier-b2901101963f.json",
		"Domain": "http://127.0.0.1:8000/",
		"AuthUri": "http://127.0.0.1:8000/auth",
		"ClientId": "181684175257-0r909pah1c6fksigrhif4rmm1l3kuqub.apps.googleusercontent.com",
		"ClientSecret": "gkX2H8W1WHrwuhK-P0Ag_st1",
  		"DownloadUri": "https://www.googleapis.com/download/storage/v1/b/%s/o/%s?alt=media"
	}

def getSourceConfig():
	return {
		"sourceConfig": {
			"tables": {
				"alarms": {
					"path": "%ProjectTablesPath%",
					"name": "alarms.json",
					"codeFormat": {
						"type": "id"
					},
					"title": "Alarmlar"
				},
				"users": {
					"path": "%ProjectTablesPath%",
					"name": "users.json",
					"codeFormat": {
						"type": "id"
					},
					"title": "Kullanicilar"
				},
				"userAlarms": {
					"path": "%ProjectTablesPath%",
					"name": "userAlarms.json",
					"codeFormat": {
						"type": "id"
					},
					"title": "Kullanici Alarmlari"
				},
				"userAlarmWavePoints": {
					"path": "%ProjectTablesPath%",
					"name": "userAlarmWavePoints.json",
					"codeFormat": {
						"type": "id"
					},
					"title": "Dalgalanma Noktalari"
				},
				"dailyRecords": {
					"path": "%ProjectTablesPath%dailyRecords/",
					"name": "%SortDateTimeString%.json",
					"codeFormat": {
						"template": "d.m.y.h.mn",
						"separator": ".",
						"type": "code"
					},
					"title": "Gunluk Kayitlar"
				},
				"dailyMaxMinRecords": {
					"path": "%ProjectTablesPath%maxMinRecords/",
					"name": "daily.json",
					"codeFormat": {
						"template": "d.m.y",
						"separator": ".",
						"type": "code"
					},
					"title": "Gunluk Max-Min Degerler"
				},
				"weeklyMaxMinRecords": {
					"path": "%ProjectTablesPath%maxMinRecords/",
					"name": "weekly.json",
					"codeFormat": {
						"template": "wy.y",
						"separator": ".",
						"type": "code"
					},
					"title": "Haftalik Max-Min Degerler"
				},
				"monthlyMaxMinRecords": {
					"path": "%ProjectTablesPath%maxMinRecords/",
					"name": "monthly.json",
					"codeFormat": {
						"template": "m.y",
						"separator": ".",
						"type": "code"
					},
					"title": "Aylik Max-Min Degerler"
				}
			}
		}
	}