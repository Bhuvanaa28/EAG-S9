import httpx
import json
import sys

session_id = sys.argv[1] if len(sys.argv) > 1 else None
url = "http://localhost:8109/v1/cost/by_agent"
if session_id:
    url += f"?session={session_id}"

r = httpx.get(url)
print(json.dumps(r.json(), indent=2))
