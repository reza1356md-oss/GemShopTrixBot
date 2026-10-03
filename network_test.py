import urllib.request

url = "https://botapi.rubika.ir/v3"

try:
    response = urllib.request.urlopen(url, timeout=15)
    print("RUBIKA_API_CONNECTION_OK")
    print("STATUS:", response.status)
except Exception as e:
    print("RUBIKA_API_CONNECTION_FAILED")
    print(type(e).__name__)
    print(str(e))
