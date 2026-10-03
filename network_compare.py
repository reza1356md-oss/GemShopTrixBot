import urllib.request
import time


def test_url(name, url):
    print(f"\n===== {name} =====")
    print(f"URL: {url}")

    try:
        start = time.time()

        with urllib.request.urlopen(url, timeout=15) as response:
            elapsed = time.time() - start
            print("HTTPS_OK")
            print("STATUS:", response.status)
            print("TIME:", round(elapsed, 2), "seconds")

    except Exception as e:
        print("HTTPS_FAILED")
        print(type(e).__name__)
        print(str(e))


test_url("PUBLIC TEST", "https://example.com")
test_url("RUBIKA TEST", "https://botapi.rubika.ir/v3")
