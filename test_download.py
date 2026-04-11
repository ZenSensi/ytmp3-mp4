import urllib.request
import urllib.parse

test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
encoded = urllib.parse.quote(test_url, safe="")
api = f"http://localhost:8000/api/download?url={encoded}&format=mp4"
print("Testing MP4 download...")

try:
    r = urllib.request.urlopen(api, timeout=120)
    content = r.read()
    ct = r.headers.get("content-type", "")
    cd = r.headers.get("content-disposition", "")
    print(f"SUCCESS: {len(content)} bytes")
    print(f"Content-Type: {ct}")
    print(f"Content-Disposition: {cd}")
except Exception as e:
    print(f"ERROR: {e}")
