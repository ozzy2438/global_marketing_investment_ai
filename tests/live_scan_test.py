import os, json, time, urllib.request, sys

# Read token from env so this script can be shared safely.
TOKEN = os.environ.get("APIFY_API_TOKEN", "").strip()
if not TOKEN:
    raise SystemExit("APIFY_API_TOKEN is required to run this live scan test.")
BASE  = "https://api.apify.com/v2"
ACTOR = "compass~crawler-google-places"

def start_scan(location, country, sector_kw="dental clinic"):
    payload = json.dumps({
        "searchStringsArray": [f"{sector_kw} in {location}"],
        "locationQuery": location,
        "maxCrawledPlacesPerSearch": 15,
        "language": "en",
        "countryCode": country.lower(),
        "maxImages": 0,
        "maxReviews": 0,
        "skipClosedPlaces": True,
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/acts/{ACTOR}/runs?token={TOKEN}",
        data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())["data"]
    return data["id"], data["defaultDatasetId"], data["status"]

def check(run_id):
    with urllib.request.urlopen(f"{BASE}/actor-runs/{run_id}?token={TOKEN}", timeout=15) as r:
        return json.loads(r.read())["data"]["status"]

def fetch(dataset_id):
    with urllib.request.urlopen(
        f"{BASE}/datasets/{dataset_id}/items?token={TOKEN}&format=json&limit=50", timeout=30
    ) as r:
        return json.loads(r.read())

def score_item(item):
    s = 0
    if item.get("website"):     s += 20
    if item.get("phone"):       s += 10
    if item.get("url"):         s +=  5
    rc = item.get("reviewsCount", 0) or 0
    rt = item.get("totalScore", 0) or 0
    if rc > 100:  s += 20
    elif rc > 30: s += 13
    elif rc > 5:  s +=  7
    if rt >= 4.5:  s += 15
    elif rt >= 4.0: s += 10
    elif rt >= 3.0: s +=  5
    if not item.get("website"): s += 15  # no website = huge AI opportunity
    return min(100, s)

# === Start scans ===
print("🚀 Taramalar başlatılıyor...")
scans = [
    ("Sydney CBD, Australia", "au", "dental clinic"),
    ("Beşiktaş, Istanbul", "tr", "diş kliniği"),
]

runs = []
for loc, cc, kw in scans:
    rid, did, st = start_scan(loc, cc, kw)
    runs.append((loc, cc, rid, did))
    print(f"  ✅ {loc} → run_id: {rid} [{st}]")

# === Poll for completion ===
print("\n⏳ Apify sonuçları bekleniyor...")
results = {}
pending = {rid: (loc, cc, did) for loc, cc, rid, did in runs}

for attempt in range(18):
    time.sleep(10)
    done = []
    for rid, (loc, cc, did) in list(pending.items()):
        st = check(rid)
        print(f"  [{(attempt+1)*10:3d}s] {loc[:30]:30s}: {st}")
        if st == "SUCCEEDED":
            items = fetch(did)
            results[loc] = {"items": items, "cc": cc}
            done.append(rid)
        elif st in ("FAILED", "ABORTED", "TIMED-OUT"):
            print(f"  ❌ Hata: {loc}")
            done.append(rid)
    for rid in done:
        del pending[rid]
    if not pending:
        break

# === Print results ===
print("\n" + "="*60)
print("📊 JARVIS CANLI TARAMA SONUÇLARI")
print("="*60)

for loc, data in results.items():
    items = data["items"]
    cc    = data["cc"]
    currency = {"au": "AUD", "tr": "TRY"}.get(cc, "USD")
    rates    = {"AUD": 1.55, "TRY": 38.5, "USD": 1.0}
    rate     = rates.get(currency, 1.0)
    pkg_usd  = {"Premium": 2500, "Professional": 1200, "Starter": 500}

    print(f"\n📍 {loc}")
    print(f"   Toplam bulunan: {len(items)} işletme")
    print("-"*60)

    scored = sorted([(score_item(it), i, it) for i, it in enumerate(items)], reverse=True)
    for sc, _, it in scored[:10]:
        pkg = ("Premium" if sc>=75 else "Professional" if sc>=55 else
               "Starter" if sc>=35 else "Nurture")
        monthly_local = round(pkg_usd.get(pkg, 500) * rate) if pkg != "Nurture" else 0
        web  = "🌐" if it.get("website") else "❌"
        name = (it.get("title") or "?")[:42]
        phone = it.get("phone") or "N/A"
        rating = it.get("totalScore") or 0
        reviews = it.get("reviewsCount") or 0
        print(f"\n  [{sc:3d}/100] {web} {name}")
        print(f"   📦 {pkg:12s} | 💰 {monthly_local:,} {currency}/ay")
        print(f"   📞 {phone}")
        print(f"   ⭐ {rating} yıldız ({reviews} yorum)")

print("\n" + "="*60)
print("✅ Tarama tamamlandı!")
