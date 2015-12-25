
import io
import requests
import simplejson as json

from googleapiclient import http
from googleapiclient import discovery
from oauth2client.client import AccessTokenCredentials

from baseTools import *

def authorized(request):
    result = True

    if "access_token" not in request.COOKIES:
        result = False
    else:
        if (datetime.now() - datetime(1970, 1, 1)).total_seconds() >= float(request.COOKIES["access_token_expired_date_total_seconds"]):
            result = False

    return result

def downloadStorageObject(file, request):
    return requests.get(
        WebConfig["DownloadUri"] % (WebConfig["BucketName"], file.replace("/", "%2F")),
        headers = { "Authorization": "Bearer " + request.COOKIES["access_token"] }
    )

def insertStorageObject(request, table):
    credentials = AccessTokenCredentials(request.COOKIES["access_token"], "MyAgent/1.0", None)
    storage = discovery.build("storage", "v1", credentials = credentials)

    # The BytesIO object may be replaced with any io.Base instance.
    media = http.MediaIoBaseUpload(io.BytesIO(str(table["rows"]).replace("'", "\"").replace("u\"", "\"")), 'text/plain')
    storage.objects().insert(bucket = WebConfig["BucketName"], name = "test.txt", media_body = media).execute()
