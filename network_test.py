import socket
import urllib.request

host = "botapi.rubika.ir"

print("DNS TEST")

try:
    ip = socket.gethostbyname(host)
    print("DNS_OK")
    print("IP:", ip)
except Exception as e:
    print("DNS_FAILED")
    print(type(e).__name__)
    print(str(e))

print("HTTPS TEST")

try:
    response = urllib.request.urlopen(
        "https://botapi.rubika.ir/v3",
        timeout=10
    )
    print("HTTPS_OK")
    print("STATUS:", response.status)
except Exception as e:
    print("HTTPS_FAILED")
    print(type(e).__name__)
    print(str(e))
