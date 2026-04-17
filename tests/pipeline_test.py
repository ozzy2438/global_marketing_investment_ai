import json, time, urllib.request, os, sys

BASE = "http://localhost:8000"

def api(path, method="GET", body=None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        f"{BASE}{path}", data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method=method
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

# 1. Start Melbourne scan
print("🚀 Melbourne CBD — Restaurant scan başlatılıyor...")
res = api("/api/v1/scan/start", "POST", {
    "sector": "restaurant",
    "location": "Melbourne CBD, Australia",
    "country_code": "au",
    "language": "en",
    "max_results": 20,
    "wait_for_completion": False
})
scan_id = res["scan_id"]
print(f"✅ scan_id: {scan_id}")
print(f"   poll_url: {res['poll_url']}")

# 2. Poll until done
print("\n⏳ Polling for completion...")
for i in range(25):
    time.sleep(10)
    try:
        status = api(f"/api/v1/scan/status/{scan_id}")
        st = status.get("status", "?")
        print(f"  [{(i+1)*10}s] status: {st}")
        if st == "COMPLETED":
            print("  ✅ Scan COMPLETED!")
            break
        if st in ("FAILED", "TIMEOUT", "ABORTED", "TIMED-OUT"):
            print(f"  ❌ Scan failed: {st}")
            sys.exit(1)
    except Exception as e:
        print(f"  [{(i+1)*10}s] poll error: {e}")

# 3. Check memory results
print("\n📊 /api/v1/scan/results:")
try:
    results = api(f"/api/v1/scan/results/{scan_id}")
    total   = results.get("total_leads", results.get("total", "?"))
    saved   = results.get("saved_to_db", "?")
    print(f"  total_leads : {total}")
    print(f"  saved_to_db : {saved}")
    for l in results.get("leads", [])[:5]:
        print(f"  • [{l.get('score',0):3d}] {l.get('name','?')[:40]} | {l.get('phone','')}")
except Exception as e:
    print(f"  Error: {e}")

# 4. Confirm DB saved
print("\n🗄️  /api/leads (from SQLite):")
db = api("/api/leads?limit=10")
print(f"  count: {db.get('count', 0)}")
for l in db.get("leads", []):
    print(f"  • [{l.get('score',0):3d}] {l.get('business_name','?')[:40]} | {l.get('city','')}")

print("\n✅ Test complete!")
