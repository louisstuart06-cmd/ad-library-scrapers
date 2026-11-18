"""TikTok ads from the TikTok Ad Library (ads shown in the EU/EEA, UK, Switzerland, Turkey).

Actor: https://apify.com/stumadethat/tiktok-ads-library-monitor

    export APIFY_TOKEN=apify_api_xxx
    python tiktok_ads.py "decathlon" --countries FR DE --days 30 --details
"""
import argparse
import os

from apify_client import ApifyClient

ACTOR_ID = "stumadethat/tiktok-ads-library-monitor"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("terms", nargs="+", help="Brand names or keywords")
    ap.add_argument("--countries", nargs="*", default=["FR"], help="ISO codes; pass nothing for all countries")
    ap.add_argument("--days", type=int, default=30, help="Ads shown in the last N days")
    ap.add_argument("--sort", default="LAST_SHOWN", choices=["LAST_SHOWN", "NEWEST", "MOST_SEEN"])
    ap.add_argument("--max", type=int, default=50, help="Max ads per search term")
    ap.add_argument("--details", action="store_true", help="Add payer, landing page, targeting, impressions")
    args = ap.parse_args()

    client = ApifyClient(os.environ["APIFY_TOKEN"])
    run = client.actor(ACTOR_ID).call(run_input={
        "searchTerms": args.terms,
        "countries": args.countries,
        "lastDays": args.days,
        "sortBy": args.sort,
        "maxAdsPerSearch": args.max,
        "includeDetails": args.details,
    })
    dataset_id = getattr(run, "default_dataset_id", None) or run["defaultDatasetId"]

    n = 0
    for ad in client.dataset(dataset_id).iterate_items():
        n += 1
        line = f"{ad['advertiserName']:<25} {ad['firstShown']} {ad.get('daysRunning') or '?':>4} d  reach {ad.get('uniqueUsersSeen') or '?':<10}"
        if args.details:
            line += f" ages {','.join(ad.get('targetAges') or [])}  -> {ad.get('landingUrl') or ''}"
        print(line)
        print(f"    {ad['adLibraryUrl']}")
    print(f"\n{n} ads")


if __name__ == "__main__":
    main()
