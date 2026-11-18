"""Daily cross-platform competitor ad monitor: new Facebook/Instagram, TikTok and Google ads -> one CSV.

Each brand in the JSON file can have a Meta search term, a TikTok search term and a Google domain:

    [
      {"brand": "Decathlon", "meta": "decathlon", "tiktok": "decathlon", "google": "decathlon.fr"},
      {"brand": "Nike", "meta": "nike", "google": "nike.com"}
    ]

The Actors run with `onlyNewAds: true`, so each run returns only the ads that are new since the previous run.
The first run returns the current ads (the baseline). Schedule it daily with cron:

    0 8 * * *  APIFY_TOKEN=apify_api_xxx python monitor_competitors.py --brands brands.json --out new_ads.csv
"""
import argparse
import csv
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

from apify_client import ApifyClient

COLUMNS = ["date", "platform", "brand", "advertiser", "ad_id", "first_shown", "days_running", "text", "landing_url", "ad_url"]


def run_actor(client: ApifyClient, actor_id: str, run_input: dict) -> list[dict]:
    run = client.actor(actor_id).call(run_input=run_input)
    if run is None:
        return []
    dataset_id = getattr(run, "default_dataset_id", None) or run["defaultDatasetId"]
    return list(client.dataset(dataset_id).iterate_items())


def _domain(s: str) -> str:
    """Same normalisation as the Actor's searchTarget label: bare host, no scheme, no www."""
    return s.strip().lower().split("://")[-1].split("/")[0].split("?")[0].removeprefix("www.")


def meta_job(client, brands, args):
    terms = {b["meta"]: b["brand"] for b in brands if b.get("meta")}
    if not terms:
        return []
    ads = run_actor(client, "stumadethat/meta-ads-library-monitor", {
        "searchTerms": list(terms), "country": args.country, "maxAdsPerSearch": args.max,
        "onlyNewAds": True, "monitorStoreName": f"{args.store_prefix}-meta",
    })
    return [{
        "platform": "Meta", "brand": terms.get(a.get("searchTerm"), a.get("searchTerm")),
        "advertiser": a.get("pageName"), "ad_id": a.get("adId"), "first_shown": a.get("firstShown"),
        "days_running": a.get("daysRunning"), "text": a.get("bodyText") or a.get("title"),
        "landing_url": a.get("landingUrl"), "ad_url": a.get("adLibraryUrl"),
    } for a in ads]


def tiktok_job(client, brands, args):
    terms = {b["tiktok"]: b["brand"] for b in brands if b.get("tiktok")}
    if not terms:
        return []
    ads = run_actor(client, "stumadethat/tiktok-ads-library-monitor", {
        "searchTerms": list(terms), "countries": [args.country] if args.country != "ALL" else [],
        "lastDays": 30, "sortBy": "NEWEST", "maxAdsPerSearch": args.max,
        "onlyNewAds": True, "monitorStoreName": f"{args.store_prefix}-tiktok",
    })
    return [{
        "platform": "TikTok", "brand": terms.get(a.get("searchTerm"), a.get("searchTerm")),
        "advertiser": a.get("advertiserName"), "ad_id": a.get("adId"), "first_shown": a.get("firstShown"),
        "days_running": a.get("daysRunning"), "text": a.get("title"),
        "landing_url": a.get("landingUrl"), "ad_url": a.get("adLibraryUrl"),
    } for a in ads]


def google_job(client, brands, args):
    domains = {_domain(b["google"]): b["brand"] for b in brands if b.get("google")}
    if not domains:
        return []
    ads = run_actor(client, "stumadethat/google-ads-transparency-monitor", {
        "domains": list(domains), "region": args.country if args.country != "ALL" else "anywhere",
        "maxAdsPerTarget": args.max, "includeDetails": True,
        "onlyNewAds": True, "monitorStoreName": f"{args.store_prefix}-google",
    })
    return [{
        "platform": "Google", "brand": domains.get(a.get("searchTarget"), a.get("advertiserName")),
        "advertiser": a.get("advertiserName"), "ad_id": a.get("creativeId"), "first_shown": (a.get("firstShown") or "")[:10],
        "days_running": a.get("daysRunning"), "text": " | ".join(a.get("adTexts") or []),
        "landing_url": (a.get("landingUrls") or [None])[0], "ad_url": a.get("transparencyUrl"),
    } for a in ads]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brands", required=True, help="JSON file with the brands to watch")
    ap.add_argument("--out", default="new_ads.csv", help="CSV file; new rows are appended")
    ap.add_argument("--country", default="FR", help="ISO code, or ALL")
    ap.add_argument("--max", type=int, default=50, help="Max new ads per brand and platform")
    ap.add_argument("--store-prefix", default="competitor-monitor", help="Name of the Apify stores that remember seen ads")
    args = ap.parse_args()
    args.country = args.country.upper()

    brands = json.loads(Path(args.brands).read_text(encoding="utf-8"))
    client = ApifyClient(os.environ["APIFY_TOKEN"])
    with ThreadPoolExecutor(max_workers=3) as pool:
        jobs = [pool.submit(job, client, brands, args) for job in (meta_job, tiktok_job, google_job)]
        rows = [row for j in jobs for row in j.result()]

    out = Path(args.out)
    new_file = not out.exists()
    with out.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        if new_file:
            w.writeheader()
        for r in rows:
            r["text"] = (r.get("text") or "").replace("\n", " ")[:500]
            w.writerow({"date": date.today().isoformat(), **r})

    by_platform = {p: sum(1 for r in rows if r["platform"] == p) for p in ("Meta", "TikTok", "Google")}
    print(f"{len(rows)} new ads {by_platform} -> {out}")


if __name__ == "__main__":
    main()
