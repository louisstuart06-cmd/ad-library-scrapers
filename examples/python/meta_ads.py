"""Facebook & Instagram ads from the Meta Ad Library.

Actor: https://apify.com/stumadethat/meta-ads-library-monitor

    export APIFY_TOKEN=apify_api_xxx
    python meta_ads.py "nike" --country FR --max 50 --csv nike_meta_ads.csv
"""
import argparse
import csv
import os

from apify_client import ApifyClient

ACTOR_ID = "stumadethat/meta-ads-library-monitor"
COLUMNS = ["pageName", "isActive", "firstShown", "daysRunning", "platforms", "displayFormat",
           "bodyText", "title", "ctaText", "landingUrl", "adLibraryUrl"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("terms", nargs="+", help="Keywords or brand names")
    ap.add_argument("--country", default="ALL", help="ISO code such as FR or US, or ALL")
    ap.add_argument("--status", default="ACTIVE", choices=["ACTIVE", "INACTIVE", "ALL"])
    ap.add_argument("--max", type=int, default=50, help="Max ads per search term")
    ap.add_argument("--csv", help="Optional CSV output path")
    args = ap.parse_args()

    client = ApifyClient(os.environ["APIFY_TOKEN"])
    run = client.actor(ACTOR_ID).call(run_input={
        "searchTerms": args.terms,
        "country": args.country,
        "activeStatus": args.status,
        "maxAdsPerSearch": args.max,
    })
    dataset_id = getattr(run, "default_dataset_id", None) or run["defaultDatasetId"]
    ads = list(client.dataset(dataset_id).iterate_items())

    for ad in ads:
        text = (ad.get("bodyText") or "").replace("\n", " ")[:80]
        print(f"{ad['pageName']:<25} {ad.get('daysRunning') or '?':>4} d  {text}")
    print(f"\n{len(ads)} ads")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
            w.writeheader()
            for ad in ads:
                w.writerow({**ad, "platforms": ", ".join(ad.get("platforms") or [])})
        print(f"Saved to {args.csv}")


if __name__ == "__main__":
    main()
