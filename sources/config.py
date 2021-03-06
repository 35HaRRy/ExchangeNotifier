
def getWebConfig():
	return {
		"Location": "Project",
		# "Location": "Local",
		"DebugSendSMS": False,
		"UseProjectEngine": True,

		"ProjectPath": "C:\\Users\\hayri\\Desktop\\IOT\\ExchangeNotifier",

		"FCMServerKey": "AIzaSyANLzHDxRVLxRY3HYE7YYFoXyZNipPMqcI",
		"ClientSecret": "gkX2H8W1WHrwuhK-P0Ag_st1",
		"ClientId": "181684175257-0r909pah1c6fksigrhif4rmm1l3kuqub.apps.googleusercontent.com",
		"RefreshToken": "1/zf85MxQqt0bnBs2012cm2WpyyS0aLIxnWf0y6R1rujk",
  		"BucketName": "exchangenotifier",

		"LocalDomain": "http://127.0.0.1:8000/",
		"LocalAuthUri": "http://127.0.0.1:8000/auth",
		# "ProjectDomain": "http://exchangenotifier.appspot.com/",
		# "ProjectAuthUri": "http://exchangenotifier.appspot.com/auth",
		"ProjectDomain": "http://exchangenotifier.hayrihabip.com/",
		"ProjectAuthUri": "http://exchangenotifier.hayrihabip.com/auth",

  		"StoreageApiDownloadUri": "https://www.googleapis.com/download/storage/v1/b/%s/o/%s?alt=media",

		"HourFixer": -1
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