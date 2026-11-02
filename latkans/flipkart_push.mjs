// Creates the priced Flipkart listings for the Atreya Ganesh lotus bell latkan via Listings API v3.
// Flipkart's API lists against an FSN. A brand new Atreya product gets its FSN from a catalog upload
// in Seller Hub first (Toran vertical); then pass the FSNs here.
//
//   node flipkart_push.mjs --fsn2 <FSN> --fsn4 <FSN>          -> prints the request, sends nothing
//   node flipkart_push.mjs --fsn2 <FSN> --fsn4 <FSN> --live   -> creates the listings
//
// Credentials from --env <path> (default E:/atreya/listing/atreya-aplus/.env):
// FLIPKART_APP_ID (or FK_APP_ID), FLIPKART_APP_SECRET (or FK_APP_SECRET), FLIPKART_LOCATION_ID (or FK_LOCATION_ID).
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const arg = (k) => (args.includes(k) ? args[args.indexOf(k) + 1] : undefined);
const LIVE = args.includes('--live');
const envPath = arg('--env') || 'E:/atreya/listing/atreya-aplus/.env';
import { existsSync } from 'node:fs';
for (const line of (existsSync(envPath) ? readFileSync(envPath, 'utf8') : '').split(/\r?\n/)) {
  const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*"?(.*?)"?\s*$/);
  if (m && !process.env[m[1]]) process.env[m[1]] = m[2];
}
const pick = (...ks) => ks.map((k) => process.env[k]).find(Boolean);
const APP_ID = pick('FLIPKART_APP_ID', 'FK_APP_ID', 'FLIPKART_CLIENT_ID');
const APP_SECRET = pick('FLIPKART_APP_SECRET', 'FK_APP_SECRET', 'FLIPKART_CLIENT_SECRET');
const LOCATION = pick('FLIPKART_LOCATION_ID', 'FK_LOCATION_ID');
const TAX_CODE = arg('--tax-code') || 'GST_5';

const L = JSON.parse(readFileSync(join(HERE, 'listing.json'), 'utf8'));
const fsn = { 2: arg('--fsn2'), 4: arg('--fsn4') };

const body = {};
for (const k of L.skus) {
  if (!fsn[k.number_of_items]) continue;
  const [len, wid, ht] = k.package_cm;
  body[k.sku] = {
    product_id: fsn[k.number_of_items],
    price: { mrp: k.mrp_inr, selling_price: k.price_inr, currency: 'INR' },
    tax: { hsn: L.shared.hsn_code, tax_code: TAX_CODE },
    listing_status: 'ACTIVE',
    shipping_fees: { local: 0, zonal: 0, national: 0, currency: 'INR' },
    fulfillment_profile: 'NON_FBF',
    // hours: the live ATR-GANESH-LOTUS-LATKAN-4, created with a 2-day SLA in Seller Hub, reads back as 48
    fulfillment: { dispatch_sla: 48, procurement_type: 'REGULAR' },
    packages: [{ name: 'package-1', dimensions: { length: len, breadth: wid, height: ht }, weight: k.package_weight_g / 1000, description: '', handling: { fragile: false } }],
    locations: [{ id: LOCATION, status: 'ENABLED', inventory: k.quantity }],
  };
}
if (!Object.keys(body).length) { console.log('Pass --fsn2 and/or --fsn4 (from Seller Hub after the catalog upload is approved).'); process.exit(1); }
if (!LIVE) { console.log(JSON.stringify(body, null, 2)); console.log('\nDry run. Add --live to send.'); process.exit(0); }
if (!APP_ID || !APP_SECRET || !LOCATION) throw new Error(`Missing Flipkart app id, secret or location id in ${envPath}`);

const tok = await fetch('https://api.flipkart.net/oauth-service/oauth/token?grant_type=client_credentials&scope=Seller_Api', {
  headers: { Authorization: 'Basic ' + Buffer.from(`${APP_ID}:${APP_SECRET}`).toString('base64') },
}).then((r) => r.json());
if (!tok.access_token) throw new Error('Flipkart token failed: ' + JSON.stringify(tok));

const r = await fetch('https://api.flipkart.net/sellers/listings/v3', {
  method: 'POST',
  headers: { Authorization: `Bearer ${tok.access_token}`, 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
});
console.log(r.status, JSON.stringify(await r.json(), null, 2));
