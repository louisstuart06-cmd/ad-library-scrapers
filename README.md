# Ad Library Scrapers: Facebook (Meta), TikTok & Google Ads Transparency

Scrape the three public ad libraries from Python, Node.js, cURL, n8n, Make, Zapier or an AI agent, and get clean JSON/CSV:

- **[Facebook Ad Library scraper](https://apify.com/stumadethat/meta-ads-library-monitor)** (Meta Ad Library: Facebook, Instagram, Messenger, Audience Network)
- **[TikTok Ad Library scraper / API](https://apify.com/stumadethat/tiktok-ads-library-monitor)** (TikTok Commercial Content Library, ads shown in Europe)
- **[Google Ads Transparency Center scraper](https://apify.com/stumadethat/google-ads-transparency-monitor)** (Search, YouTube, Shopping, Maps and Play ads)

This repository holds **ready-to-run examples**. The scrapers themselves run as hosted [Apify](https://apify.com) Actors, so you don't maintain browsers, proxies or anti-bot workarounds. Each one has a **monitoring mode** (only ads that are new since the last run), a **per-advertiser summary** and a shareable **HTML report**.

> Use case: *"Show me every ad my competitors launched this week, on Facebook, Instagram, TikTok, YouTube and Google Search, in one spreadsheet."* See [`examples/monitor_competitors.py`](examples/monitor_competitors.py).

## The three scrapers

| Library | What you get | Price (pay per result) | Link |
|---|---|---|---|
| **Meta Ad Library** (Facebook & Instagram) | Ad copy, title, CTA, landing page, images, videos, platforms, start date, days running, active status, page likes, similar-ads count | **$0.80 / 1,000 ads**, plus $0.01 per search for the summary and report | [meta-ads-library-monitor](https://apify.com/stumadethat/meta-ads-library-monitor) |
| **TikTok Ad Library** | Video URL, cover, dates, days running, unique users reached. With details: who paid, TikTok account, landing page, targeting (age, gender, country, interests, OS), impressions per country | **$1 / 1,000 ads**, plus $3 / 1,000 ads with details | [tiktok-ads-library-monitor](https://apify.com/stumadethat/tiktok-ads-library-monitor) |
| **Google Ads Transparency Center** | Advertiser, format (text, image, video), first and last shown, days running, image URL. With details: ad text, YouTube video, landing URLs, platforms, countries, impressions range per country | **$1.20 / 1,000 ads**, plus $2.50 / 1,000 ads with details | [google-ads-transparency-monitor](https://apify.com/stumadethat/google-ads-transparency-monitor) |

New Apify accounts get free monthly credits, enough for thousands of ads. You can set a maximum cost per run, and the Actor stops cleanly when it reaches it.

## Quick start (Python)

1. Create a free Apify account and copy your API token from **Console → Settings → API & Integrations**.
2. Run:

```bash
pip install -r examples/python/requirements.txt
export APIFY_TOKEN=apify_api_xxx
python examples/python/meta_ads.py "nike" --country FR --max 50
```

```python
import os
from apify_client import ApifyClient

client = ApifyClient(os.environ["APIFY_TOKEN"])
run = client.actor("stumadethat/meta-ads-library-monitor").call(run_input={
    "searchTerms": ["nike"],
    "country": "FR",
    "activeStatus": "ACTIVE",
    "maxAdsPerSearch": 50,
})
for ad in client.dataset(run.default_dataset_id).iterate_items():
    print(ad["pageName"], ad["daysRunning"], ad["landingUrl"])
```

The same pattern works for the other two Actors: [`tiktok_ads.py`](examples/python/tiktok_ads.py) and [`google_ads.py`](examples/python/google_ads.py). There is also an example for [Node.js](examples/node/meta_ads.mjs) and one for [cURL, a single HTTP call](examples/curl.md).

## Inputs

| Actor | Main inputs |
|---|---|
| Meta | `searchTerms` (keywords or brand names), `pageIds` (Facebook page IDs or Ad Library URLs), `country` (`FR`, `US`… or `ALL`), `activeStatus` (`ACTIVE`, `INACTIVE`, `ALL`), `mediaType` (`ALL`, `IMAGE`, `VIDEO`, `MEME`), `maxAdsPerSearch`, `onlyNewAds` |
| TikTok | `searchTerms`, `advertiserIds`, `countries` (`["FR","DE"]`, or empty for all), `lastDays` or `startDate`/`endDate`, `sortBy` (`LAST_SHOWN`, `NEWEST`, `MOST_SEEN`), `maxAdsPerSearch`, `includeDetails`, `onlyNewAds` |
| Google | `domains` (e.g. `nike.com`), `advertisers` (names or `AR…` IDs), `advertiserNameMatch`, `region` (`US`, `FR`… or `anywhere`), `platform` (`ALL`, `GOOGLE_SEARCH`, `YOUTUBE`, `GOOGLE_SHOPPING`, `GOOGLE_MAPS`, `GOOGLE_PLAY`), `adFormat` (`ALL`, `TEXT`, `IMAGE`, `VIDEO`), `maxAdsPerTarget`, `lastSeenWithinDays`, `firstSeenWithinDays`, `includeDetails`, `onlyNewAds` |

> **Tip (Meta):** `searchTerms` works like the Ad Library search box. It returns every ad that *mentions* the keyword, for example resellers advertising Nike products. To get only one brand's own ads, pass its Facebook page ID or its Ad Library URL (`...view_all_page_id=...`) in `pageIds`.

## Output samples

The values below are illustrative, but the field names are the real ones.

**Meta (Facebook / Instagram) ad**

```json
{
  "adId": "1234567890123456",
  "pageName": "Nike",
  "pageId": "123456789012345",
  "pageLikes": 39000000,
  "isActive": true,
  "firstShown": "2026-11-02",
  "lastShown": "2026-11-18",
  "daysRunning": 17,
  "platforms": ["FACEBOOK", "INSTAGRAM"],
  "displayFormat": "VIDEO",
  "bodyText": "Just do it. New collection out now.",
  "title": "Shop the new collection",
  "ctaText": "Shop now",
  "landingUrl": "https://www.nike.com/…",
  "imageUrls": ["https://scontent…"],
  "videoUrls": ["https://video…"],
  "similarAdsCount": 4,
  "adLibraryUrl": "https://www.facebook.com/ads/library/?id=1234567890123456",
  "searchTerm": "nike",
  "country": "FR"
}
```

**TikTok ad** (the fields after `adLibraryUrl` come with `includeDetails: true`)

```json
{
  "adId": "1790000000000000",
  "advertiserName": "Decathlon",
  "format": "VIDEO",
  "firstShown": "2026-10-28",
  "lastShown": "2026-11-17",
  "daysRunning": 21,
  "isActive": true,
  "uniqueUsersSeen": "100K-1M",
  "videoUrl": "https://library.tiktok.com/…",
  "coverImageUrl": "https://…",
  "adLibraryUrl": "https://library.tiktok.com/ads/detail/?ad_id=1790000000000000",
  "paidBy": "Decathlon SE",
  "tiktokUsername": "decathlon",
  "landingUrl": "https://www.decathlon.fr/…",
  "targetCountries": ["FR"],
  "targetAges": ["18-24", "25-34"],
  "targetGenders": ["female", "male", "unknown"],
  "totalImpressions": "100K-1M",
  "impressionsByCountry": [{"country": "FR", "impressions": "100K-1M", "breakdown": []}]
}
```

**Google ad** (the fields after `transparencyUrl` come with `includeDetails: true`)

```json
{
  "advertiserId": "AR00000000000000000000",
  "advertiserName": "Nike, Inc.",
  "domain": "nike.com",
  "creativeId": "CR00000000000000000000",
  "format": "VIDEO",
  "firstShown": "2026-09-30T00:00:00+00:00",
  "lastShown": "2026-11-17T00:00:00+00:00",
  "daysRunning": 49,
  "isActive": true,
  "transparencyUrl": "https://adstransparency.google.com/advertiser/AR…/creative/CR…",
  "adTexts": ["Just Do It", "Shop the new collection"],
  "youtubeUrl": "https://www.youtube.com/watch?v=…",
  "landingUrls": ["https://www.nike.com/…"],
  "impressionsMin": 100000,
  "impressionsMax": 125000,
  "platforms": ["YOUTUBE"],
  "countries": ["US", "CA"],
  "regionStats": [{"country": "US", "impressionsMin": 90000, "impressionsMax": 100000, "firstShown": "2026-09-30", "lastShown": "2026-11-17", "platforms": [{"platform": "YOUTUBE", "impressionsMin": 90000, "impressionsMax": 100000}]}]
}
```

Each run also saves `SUMMARY` (JSON: ads per advertiser, active ads, new ads in the last 7 and 30 days, longest-running ad, top landing domains…) and `REPORT` (HTML) in the run's key-value store.

## Monitor competitors every day

[`examples/monitor_competitors.py`](examples/monitor_competitors.py) runs the three scrapers for a list of brands with `onlyNewAds: true`, then appends the new ads to one CSV file with the columns `date, platform, brand, advertiser, ad_id, first_shown, days_running, text, landing_url, ad_url`.

```bash
python examples/monitor_competitors.py --brands examples/brands.example.json --out new_ads.csv
```

To run it every morning, use cron (`0 8 * * * …`), or skip the script and create an **Apify Schedule** on each Actor with `onlyNewAds: true`. You can then send the results to Slack, Google Sheets or email with Apify integrations.

## FAQ

**Why not use the official APIs?**
- The **Meta Ad Library API** only returns political and social-issue ads, except for ads shown in the EU. It also needs a verified developer identity. The website shows all ads, which is what the Meta scraper reads.
- **TikTok's Commercial Content API** needs an approved research or business application.
- **Google Ads Transparency Center** has no official API for searching ads by advertiser or domain.

**Is it legal to scrape ad libraries?**
These libraries are public transparency tools, which the EU Digital Services Act (Article 39) requires platforms to publish. The scrapers collect only publicly displayed ad data, with no logins and no personal user data. You remain responsible for how you use the data, for example GDPR if you process personal data, and the platforms' terms. This is not legal advice.

**What are the limits?**
- **TikTok:** the library only covers ads shown in the EU/EEA, UK and Switzerland.
- **Meta:** outside the EU, inactive non-political ads are not public. Spend and reach are mostly given for EU and political ads.
- **Google:** shows impression ranges, not exact numbers.
- **Search results:** the libraries throttle heavy users, so very large searches may return fewer ads. The Actors save everything collected before a block.

**How does monitoring mode work?**
With `onlyNewAds: true`, the Actor remembers the ad IDs it has already returned for the same search, in a named key-value store, and outputs only new ones. Schedule it daily and you get a feed of new competitor ads.

**Can I use it with n8n, Make, Zapier or AI agents?**
- **n8n, Make and Zapier:** each has an official Apify module. Pick "Run Actor" and use the Actor ID, e.g. `stumadethat/meta-ads-library-monitor`.
- **AI agents (Claude, ChatGPT, Cursor…):** add the [Apify MCP server](https://mcp.apify.com) and ask, for example: *"Use stumadethat/tiktok-ads-library-monitor to list Decathlon's TikTok ads in France this month."*

**What does it cost to run daily?**
Monitoring 5 brands on the 3 platforms usually means a few dozen new ads a day, which comes to cents per day.

## License

The examples are MIT-licensed (see [LICENSE](LICENSE)). The Actors are hosted services on Apify, billed per result.
