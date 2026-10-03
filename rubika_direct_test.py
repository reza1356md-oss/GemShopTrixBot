import urllib.request
import urllib.error

url = "https://botapi.rubika.ir/v3"

print("=== RUBIKA DIRECT HTTPS TEST ===")
print("URL:", url)

try:
    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "User-Agent": "Railway-Rubika-Test"
        }
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        print("HTTPS_OK")
        print("STATUS:", response.status)
        print("HEADERS:", dict(response.headers))
        print("BODY:", response.read(500))

except urllib.error.HTTPError as e:
    print("HTTP_RESPONSE_RECEIVED")
    print("STATUS:", e.code)
    print("BODY:", e.read(500))

except Exception as e:
    print("HTTPS_FAILED")
    print(type(e).__name__)
    print(str(e))
