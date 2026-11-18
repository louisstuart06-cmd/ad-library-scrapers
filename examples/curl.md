# One HTTP call per library (cURL)

`run-sync-get-dataset-items` starts the Actor, waits for it to finish (up to 300 seconds) and returns the ads as JSON. Add `&format=csv` to the URL to get a CSV file instead. For long runs, use the asynchronous `/runs` endpoint and fetch the dataset afterwards.

```bash
export APIFY_TOKEN=apify_api_xxx
```

## Facebook & Instagram (Meta Ad Library)

```bash
curl -s -X POST "https://api.apify.com/v2/acts/stumadethat~meta-ads-library-monitor/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" \
  -d '{"searchTerms": ["nike"], "country": "FR", "activeStatus": "ACTIVE", "maxAdsPerSearch": 20}'
```

## TikTok Ad Library

```bash
curl -s -X POST "https://api.apify.com/v2/acts/stumadethat~tiktok-ads-library-monitor/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" \
  -d '{"searchTerms": ["decathlon"], "countries": ["FR"], "lastDays": 30, "maxAdsPerSearch": 20}'
```

## Google Ads Transparency Center

```bash
curl -s -X POST "https://api.apify.com/v2/acts/stumadethat~google-ads-transparency-monitor/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" \
  -d '{"domains": ["nike.com"], "region": "US", "platform": "YOUTUBE", "maxAdsPerTarget": 20, "includeDetails": true}'
```

## Only new ads since the last call

Add `"onlyNewAds": true` to any input. Each call then returns only the ads that the previous calls with the same search did not return.
