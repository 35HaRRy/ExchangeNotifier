
import io
import urllib
import urllib2
import httplib
import simplejson as json

from googleapiclient import http
from googleapiclient import discovery
from oauth2client.client import AccessTokenCredentials

from baseTools import *

Domain = WebConfig["GoogleAppDomain"]
AuthUri = WebConfig["GoogleAppAuthUri"]

# Domain = WebConfig["LocalDomain"]
# AuthUri = WebConfig["LocalAuthUri"]

def authanticate(grant_type, code):
    params = { "grant_type": grant_type, "redirect_uri": AuthUri, "client_id": WebConfig["ClientId"], "client_secret": WebConfig["ClientSecret"], "scope": "" }
    headers = { "Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain" }

    if grant_type == "refresh_token":
        # headers["Authorization"] = "Bearer " + code
        params["refresh_token"] = code
    else:
        params["code"] = code

    conn = httplib.HTTPSConnection("www.googleapis.com")
    conn.request("POST", "/oauth2/v3/token", urllib.urlencode(params), headers)

    data = conn.getresponse().read()
    conn.close()

    return data

def isAuthorized(request):
    result = True

    if "access_token" not in request.COOKIES:
        result = False
    else:
        if (datetime.now() - datetime(1970, 1, 1)).total_seconds() >= float(request.COOKIES["access_token_expired_date_total_seconds"]):
            result = False

    return result

def downloadStorageObject(file, request):
    try:
        req = urllib2.Request(WebConfig["DownloadUri"] % (WebConfig["BucketName"], file.replace("/", "%2F")))
        req.add_header("Authorization", "Bearer " + request.COOKIES["access_token"])
        content = urllib2.urlopen(req).read()
    except StandardError as se:
        content = "[]"

    return content

def insertStorageObject(request, table):
    credentials = AccessTokenCredentials(request.COOKIES["access_token"], "MyAgent/1.0", None)
    storage = discovery.build("storage", "v1", credentials = credentials)

    # The BytesIO object may be replaced with any io.Base instance.
    media = http.MediaIoBaseUpload(io.BytesIO(str(table["rows"]).replace("'", "\"").replace("u\"", "\"")), 'text/plain')
    storage.objects().insert(bucket = WebConfig["BucketName"], name = table["config"]["tableFileFullPath"], media_body = media).execute()
