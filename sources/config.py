
def getWebConfig():
	return {
		"CurrencyQueryStartHour": "09:30",
		"CurrencyQueryFinishHour": "17:00",
		"CurrencyQueryPeriod": "4",
		"CurrencyQueryUrl": "http://127.0.0.1:8000/currentsituation",
		"ProjectPath": "C:\\Users\\hayri\\Desktop\\IOT\\ExchangeNotifier",
		"DebugSendSMS": False,
		"UseGoogleAppEngine": True,
		"GoogleAppDomain": "http://exchangenotifier.hayrihabip.com/",
		"GoogleAppAuthUri": "http://exchangenotifier.hayrihabip.com/auth",
		"LocalDomain": "http://127.0.0.1:8000/",
		"LocalAuthUri": "http://127.0.0.1:8000/auth",
		"ClientId": "181684175257-0r909pah1c6fksigrhif4rmm1l3kuqub.apps.googleusercontent.com",
		"ClientSecret": "gkX2H8W1WHrwuhK-P0Ag_st1",
		"RefreshToken": "1/zf85MxQqt0bnBs2012cm2WpyyS0aLIxnWf0y6R1rujk",
  		"DownloadUri": "https://www.googleapis.com/download/storage/v1/b/%s/o/%s?alt=media",
  		"BucketName": "exchangenotifier"
	}

def getSourceConfig():
	return {
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
			},
			"logs": {
				"path": "%ProjectTablesPath%",
				"name": "logs.json",
				"codeFormat": {
					"type": "id"
				},
				"title": "Loglar"
			}
		}
	}