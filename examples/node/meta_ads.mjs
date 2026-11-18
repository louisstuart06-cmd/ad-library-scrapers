// Facebook & Instagram ads from the Meta Ad Library, in Node.js.
// Actor: https://apify.com/stumadethat/meta-ads-library-monitor
//
//   npm install apify-client
//   APIFY_TOKEN=apify_api_xxx node meta_ads.mjs nike FR
import { ApifyClient } from 'apify-client';

const [term = 'nike', country = 'ALL'] = process.argv.slice(2);
const client = new ApifyClient({ token: process.env.APIFY_TOKEN });

const run = await client.actor('stumadethat/meta-ads-library-monitor').call({
    searchTerms: [term],
    country,
    activeStatus: 'ACTIVE',
    maxAdsPerSearch: 50,
});

const { items } = await client.dataset(run.defaultDatasetId).listItems();
for (const ad of items) {
    console.log(`${ad.pageName} | ${ad.daysRunning ?? '?'} d | ${(ad.bodyText ?? '').slice(0, 80)} | ${ad.landingUrl ?? ''}`);
}
console.log(`\n${items.length} ads`);

// Advertiser summary (JSON) and HTML report from the run's key-value store
const summary = await client.keyValueStore(run.defaultKeyValueStoreId).getRecord('SUMMARY');
console.log(summary?.value?.slice(0, 3));
