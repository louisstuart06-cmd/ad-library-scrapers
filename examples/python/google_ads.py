"""Google ads (Search, YouTube, Shopping, Maps, Play) from the Google Ads Transparency Center.

Actor: https://apify.com/stumadethat/google-ads-transparency-monitor

    export APIFY_TOKEN=apify_api_xxx
    python google_ads.py nike.com --region US --platform YOUTUBE --details
"""
import argparse
import os

from apify_client import ApifyClient

ACTOR_ID = "stumadethat/google-ads-transparency-monitor"
PLATFORMS = ["ALL", "GOOGLE_SEARCH", "YOUTUBE", "GOOGLE_SHOPPING", "GOOGLE_MAPS", "GOOGLE_PLAY"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("domains", nargs="+", help="Advertiser websites, e.g. nike.com")
    ap.add_argument("--region", default="anywhere", help="ISO code such as US or FR, or 'anywhere'")
    ap.add_argument("--platform", default="ALL", choices=PLATFORMS)
    ap.add_argument("--format", default="ALL", choices=["ALL", "TEXT", "IMAGE", "VIDEO"])
    ap.add_argument("--last-seen-days", type=int, default=0, help="Only ads shown in the last N days (0 = all)")
    ap.add_argument("--max", type=int, default=50, help="Max ads per domain")
    ap.add_argument("--details", action="store_true", help="Add ad text, YouTube video, impressions, countries")
    args = ap.parse_args()

    client = ApifyClient(os.environ["APIFY_TOKEN"])
    run = client.actor(ACTOR_ID).call(run_input={
        "domains": args.domains,
        "region": args.region,
        "platform": args.platform,
        "adFormat": args.format,
        "lastSeenWithinDays": args.last_seen_days,
        "maxAdsPerTarget": args.max,
        "includeDetails": args.details,
    })
    dataset_id = getattr(run, "default_dataset_id", None) or run["defaultDatasetId"]

    n = 0
    for ad in client.dataset(dataset_id).iterate_items():
        n += 1
        line = f"{ad['advertiserName']:<25} {ad['format']:<6} {ad.get('daysRunning') or '?':>4} d"
        if args.details:
            text = " | ".join(ad.get("adTexts") or [])[:80]
            line += f"  {ad.get('impressionsMin')}-{ad.get('impressionsMax')} impr.  {text}"
        print(line)
        print(f"    {ad['transparencyUrl']}")
    print(f"\n{n} ads")


if __name__ == "__main__":
    main()
