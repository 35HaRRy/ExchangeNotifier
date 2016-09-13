
import io
import urllib2

from googleapiclient import http
from googleapiclient import discovery
from oauth2client.client import AccessTokenCredentials

from baseTools import *

Domain = WebConfig[WebConfig["Location"] + "Domain"]
AuthUri = WebConfig[WebConfig["Location"] + "AuthUri"]

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
        if (datetime.now(tz) - datetime(1970, 1, 1).replace(tzinfo = tz)).total_seconds() >= float(request.COOKIES["access_token_expired_date_total_seconds"]):
            result = False

    return result

def downloadStorageObject(auths, file):
    try:
        req = urllib2.Request(WebConfig["StoreageApiDownloadUri"] % (WebConfig["BucketName"], file.replace("/", "%2F")))
        req.add_header("Authorization", "Bearer " + auths["access_token"])

        content = urllib2.urlopen(req).read()
    except StandardError:
        content = "[]"

    return content

def insertStorageTable(auths, table):
    return insertStorageObject(auths, table["config"]["tableFileFullPath"], str(table["rows"]))

def insertStorageObject(auths, file, data):
    credentials = AccessTokenCredentials(auths["access_token"], "MyAgent/1.0", None)
    storage = discovery.build("storage", "v1", credentials = credentials)

    # The BytesIO object may be replaced with any io.Base instance.
    media = http.MediaIoBaseUpload(io.BytesIO(data.replace("'", "\"").replace("u\"", "\"")), "text/plain")
    return json.dumps(storage.objects().insert(bucket = WebConfig["BucketName"], name = file, media_body = media).execute(), indent = 2)
