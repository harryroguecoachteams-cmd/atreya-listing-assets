// Creates the two Atreya Ganesh lotus bell latkan listings on Amazon.in and their A+ content.
// Reads everything from listing.json next to this file. Node 18+, no npm installs.
//
//   node amazon_push.mjs listings           -> VALIDATION_PREVIEW only, prints Amazon's issues
//   node amazon_push.mjs listings --live    -> creates the listings
//   node amazon_push.mjs status             -> shows ASIN + status per SKU once Amazon assigns them
//   node amazon_push.mjs aplus              -> uploads images, creates the A+ draft, validates against the ASINs
//   node amazon_push.mjs aplus --live       -> same, then attaches ASINs and submits for approval
//
// Credentials: --env <path> (default E:/atreya/listing/atreya-aplus/.env). Accepts LWA_CLIENT_ID or
// SP_API_CLIENT_ID / CLIENT_ID, LWA_CLIENT_SECRET or SP_API_CLIENT_SECRET / CLIENT_SECRET,
// LWA_REFRESH_TOKEN or SP_API_REFRESH_TOKEN / REFRESH_TOKEN, SELLER_ID, MARKETPLACE_ID.
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const cmd = args[0];
const LIVE = args.includes('--live');
const envPath = args.includes('--env') ? args[args.indexOf('--env') + 1] : 'E:/atreya/listing/atreya-aplus/.env';

import { existsSync } from 'node:fs';
for (const line of (existsSync(envPath) ? readFileSync(envPath, 'utf8') : '').split(/\r?\n/)) {
  const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*"?(.*?)"?\s*$/);
  if (m && !process.env[m[1]]) process.env[m[1]] = m[2];
}
const pick = (...ks) => ks.map((k) => process.env[k]).find(Boolean);
const CLIENT_ID = pick('LWA_CLIENT_ID', 'SP_API_CLIENT_ID', 'CLIENT_ID', 'LWA_APP_ID');
const CLIENT_SECRET = pick('LWA_CLIENT_SECRET', 'SP_API_CLIENT_SECRET', 'CLIENT_SECRET');
const REFRESH = pick('LWA_REFRESH_TOKEN', 'SP_API_REFRESH_TOKEN', 'REFRESH_TOKEN');
const SELLER = pick('SELLER_ID') || 'A2YEFZP86DTGZC';
const MP = pick('MARKETPLACE_ID') || 'A21TJRUUN4KGV';
const HOST = 'https://sellingpartnerapi-eu.amazon.com';
if (!CLIENT_ID || !CLIENT_SECRET || !REFRESH) throw new Error(`Missing LWA credentials in ${envPath}`);

const L = JSON.parse(readFileSync(join(HERE, 'listing.json'), 'utf8'));
const S = L.shared;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let token;
async function auth() {
  if (token) return token;
  const r = await fetch('https://api.amazon.com/auth/o2/token', {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ grant_type: 'refresh_token', refresh_token: REFRESH, client_id: CLIENT_ID, client_secret: CLIENT_SECRET }),
  });
  const j = await r.json();
  if (!j.access_token) throw new Error('LWA token failed: ' + JSON.stringify(j));
  return (token = j.access_token);
}
async function sp(method, path, body) {
  for (let attempt = 0; ; attempt++) {
    const r = await fetch(HOST + path, {
      method,
      headers: { 'x-amz-access-token': await auth(), 'content-type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (r.status === 429 && attempt < 5) { await sleep(2000 * 2 ** attempt); continue; }
    const text = await r.text();
    const j = text ? JSON.parse(text) : {};
    if (!r.ok) throw new Error(`${method} ${path} -> ${r.status}\n${JSON.stringify(j, null, 2)}`);
    return j;
  }
}

// ---------- Listings ----------
const v = (value) => [{ value, marketplace_id: MP }];
const t = (value) => [{ value, language_tag: 'en_IN', marketplace_id: MP }];

function attributesFor(k) {
  const img = (f) => `${L.image_base_url}/${k.sku}/${f}`;
  const bullets = S.bullets_template.map((b) =>
    b.replaceAll('{n}', k.number_of_items).replace('{pack_use}', k.pack_use).replace('{pack_where}', k.pack_where));
  const [len, wid, ht] = k.package_cm;
  const a = {
    item_name: t(k.title),
    brand: t(L.brand),
    manufacturer: t(L.brand),
    bullet_point: bullets.map((b) => ({ value: b, language_tag: 'en_IN', marketplace_id: MP })),
    product_description: t(S.description),
    generic_keyword: t(S.backend_search_terms),
    item_type_keyword: v(S.item_type_keyword),
    recommended_browse_nodes: v(S.browse_node),
    condition_type: v('new_new'),
    country_of_origin: v(S.country_of_origin),
    material: t(S.material),
    color: t(S.color),
    theme: t(S.theme),
    style: t(S.style),
    special_feature: t(S.special_feature),
    occasion_type: S.occasion_type.map((o) => ({ value: o, language_tag: 'en_IN', marketplace_id: MP })),
    number_of_items: v(k.number_of_items),
    unit_count: [{ value: k.number_of_items, type: { value: 'count', language_tag: 'en_IN' }, marketplace_id: MP }],
    included_components: t(`${k.number_of_items} Ganesh lotus latkans`),
    item_dimensions: [{ length: { value: S.strand_length_cm, unit: 'centimeters' }, width: { value: S.strand_width_cm, unit: 'centimeters' }, height: { value: 2, unit: 'centimeters' }, marketplace_id: MP }],
    item_weight: [{ value: k.item_weight_g, unit: 'grams', marketplace_id: MP }],
    size: t(k.size),
    item_type_name: t(S.item_type_name),
    model_number: v(k.model_number),
    part_number: v(k.part_number),
    packer_contact_information: t(S.contact),
    rtip_manufacturer_contact_information: v(S.contact),
    supplier_declared_has_product_identifier_exemption: v(true),
    item_package_dimensions: [{ length: { value: len, unit: 'centimeters' }, width: { value: wid, unit: 'centimeters' }, height: { value: ht, unit: 'centimeters' }, marketplace_id: MP }],
    item_package_weight: [{ value: k.package_weight_g, unit: 'grams', marketplace_id: MP }],
    batteries_required: v(false),
    supplier_declared_dg_hz_regulation: v('not_applicable'),
    product_tax_code: v('A_GEN_STANDARD'),
    external_product_information: [{ entity: 'HSN Code', value: S.hsn_code, marketplace_id: MP }],
    purchasable_offer: [{ currency: 'INR', audience: 'ALL', marketplace_id: MP, maximum_retail_price: [{ schedule: [{ value_with_tax: k.mrp_inr }] }], our_price: [{ schedule: [{ value_with_tax: k.price_inr }] }] }],
    fulfillment_availability: [{ fulfillment_channel_code: 'DEFAULT', quantity: k.quantity }],
    main_product_image_locator: [{ media_location: img(k.images[0]), marketplace_id: MP }],
  };
  k.images.slice(1).forEach((f, i) => { a[`other_product_image_locator_${i + 1}`] = [{ media_location: img(f), marketplace_id: MP }]; });
  return a;
}

async function schemaKeys() {
  const d = await sp('GET', `/definitions/2020-09-01/productTypes/${S.product_type}?marketplaceIds=${MP}&requirements=LISTING&locale=en_IN`);
  const schema = await (await fetch(d.schema.link.resource)).json();
  return new Set(Object.keys(schema.properties || {}));
}

async function listings() {
  const keys = await schemaKeys();
  const highlightKey = [...keys].find((k) => /highlight/i.test(k));
  for (const k of L.skus) {
    const attrs = attributesFor(k);
    if (highlightKey) attrs[highlightKey] = t(S.item_highlight);
    else console.log('  note: no Item Highlight attribute in this product type schema; add it in Seller Central');
    const dropped = Object.keys(attrs).filter((a) => !keys.has(a));
    dropped.forEach((a) => delete attrs[a]);
    if (dropped.length) console.log(`  ${k.sku}: not in ${S.product_type} schema, skipped: ${dropped.join(', ')}`);
    const mode = LIVE ? '' : '&mode=VALIDATION_PREVIEW';
    const res = await sp('PUT', `/listings/2021-08-01/items/${SELLER}/${encodeURIComponent(k.sku)}?marketplaceIds=${MP}&issueLocale=en_IN${mode}`,
      { productType: S.product_type, requirements: 'LISTING', attributes: attrs });
    console.log(`\n${k.sku}: ${res.status}${LIVE ? '' : ' (validation only)'}`);
    for (const i of res.issues || []) console.log(`  [${i.severity}] ${i.code} ${i.attributeNames?.join(',') || ''}: ${i.message}`);
  }
  if (!LIVE) console.log('\nNo errors above? Run again with --live.');
}

async function status() {
  const out = {};
  for (const k of L.skus) {
    const r = await sp('GET', `/listings/2021-08-01/items/${SELLER}/${encodeURIComponent(k.sku)}?marketplaceIds=${MP}&includedData=summaries,issues`);
    const s = r.summaries?.[0];
    out[k.sku] = s?.asin;
    console.log(`${k.sku}: ASIN ${s?.asin || '(not yet)'} | ${s?.status?.join(', ') || ''}`);
    for (const i of r.issues || []) console.log(`  [${i.severity}] ${i.code}: ${i.message}`);
  }
  return out;
}

// ---------- A+ ----------
async function upload(file) {
  const buf = readFileSync(join(HERE, file));
  const md5 = createHash('md5').update(buf).digest('base64');
  const r = await sp('POST', `/uploads/2020-11-01/uploadDestinations/aplus/2020-11-01/contentDocuments?marketplaceIds=${MP}&contentMD5=${encodeURIComponent(md5)}&contentType=image/jpeg`);
  const { uploadDestinationId, url } = r.payload;
  const headers = r.payload.headers || {};
  const u = new URL(url);
  let up;
  if (headers.key || headers.policy || headers.Policy || u.searchParams.has('key')) {   // S3 presigned POST form
    // amazon.in returns headers: null with the form fields in the URL query (same as publish-*-aplus.js)
    const form = new FormData();
    for (const [hk, hv] of [...u.searchParams.entries(), ...Object.entries(headers)]) form.append(hk, hv);
    form.append('file', new Blob([buf], { type: 'image/jpeg' }), file.split('/').pop());
    up = await fetch(`${u.protocol}//${u.host}${u.pathname}`, { method: 'POST', body: form });
  } else {                                                              // presigned PUT
    up = await fetch(url, { method: 'PUT', headers: { 'Content-Type': 'image/jpeg', 'Content-MD5': md5, ...headers }, body: buf });
  }
  if (!up.ok) throw new Error(`upload ${file} -> ${up.status} ${await up.text()}`);
  console.log(`  uploaded ${file}`);
  return uploadDestinationId;
}
function jpegSize(file) {
  const b = readFileSync(join(HERE, file));
  for (let i = 2; i < b.length;) {
    const marker = b[i + 1], len = b.readUInt16BE(i + 2);
    if (marker >= 0xc0 && marker <= 0xc3) return { h: b.readUInt16BE(i + 5), w: b.readUInt16BE(i + 7) };
    i += 2 + len;
  }
  throw new Error('no size in ' + file);
}
const txt = (value) => ({ value, decoratorSet: [] });
const para = (value) => ({ textList: [txt(value)] });
async function image(file, alt) {
  const { w, h } = jpegSize(file);
  const px = (n) => ({ value: n, units: 'pixels' });
  return { uploadDestinationId: await upload(file), altText: alt, imageCropSpecification: { size: { width: px(w), height: px(h) }, offset: { x: px(0), y: px(0) } } };
}

async function aplus() {
  const asins = Object.values(await status()).filter(Boolean);
  if (asins.length < L.skus.length) throw new Error('Both SKUs need ASINs first. Run "listings --live", wait 15-30 min, then retry.');
  const [m1, m2, m3] = L.aplus.modules;
  const modules = [
    { contentModuleType: m1.type, standardHeaderImageText: { headline: txt(m1.headline), block: { image: await image(m1.image, m1.alt), headline: txt(m1.headline), body: para(m1.body) } } },
    { contentModuleType: m2.type, standardThreeImageText: { headline: txt(m2.headline),
      ...Object.fromEntries(await Promise.all(m2.blocks.map(async (b, i) => [`block${i + 1}`, { image: await image(b.image, b.alt), headline: txt(b.headline), body: para(b.body) }]))) } },
    { contentModuleType: m3.type, standardSingleImageHighlights: {
      image: await image(m3.image, m3.alt), headline: txt(m3.headline),
      textBlock1: { headline: txt(m3.headline), body: para(m3.body) },
      bulletedListBlock: { headline: txt(m3.bullets_headline), block: { textList: m3.bullets.map((b, i) => ({ position: i + 1, text: txt(b) })) } } } },
  ];
  const doc = { contentDocument: { name: L.aplus.name, contentType: 'EBC', locale: 'en-IN', contentModuleList: modules } };
  const v1 = await sp('POST', `/aplus/2020-11-01/contentAsinValidations?marketplaceId=${MP}&asinSet=${asins.join(',')}`, doc);
  for (const e of v1.errors || []) console.log(`  [A+ ${e.code}] ${e.message}`);
  if (!LIVE) { console.log('\nA+ validated only. Run "aplus --live" to create and submit it.'); return; }
  // reuse the first draft of the same name, so a re-run (e.g. after a failed submit) never makes a duplicate.
  // 2 Nov 2026: a re-run made 66317d31-... before this existed; its ASINs were detached, fdd20ce1-... is the one.
  const list = await sp('GET', `/aplus/2020-11-01/contentDocuments?marketplaceId=${MP}`);
  const prev = (list.contentMetadataRecords || []).filter((d) => d.contentMetadata?.name === L.aplus.name && d.contentMetadata?.status === 'DRAFT')
    .find((d) => d.contentReferenceKey === 'fdd20ce1-b9d4-4320-9a2a-dc0853d5596e') || (list.contentMetadataRecords || [])
    .filter((d) => d.contentMetadata?.name === L.aplus.name && d.contentMetadata?.status === 'DRAFT')
    .sort((a, b) => String(a.contentMetadata.updateTime).localeCompare(b.contentMetadata.updateTime))[0];
  let contentReferenceKey = prev?.contentReferenceKey;
  if (contentReferenceKey) { await sp('POST', `/aplus/2020-11-01/contentDocuments/${contentReferenceKey}?marketplaceId=${MP}`, doc); console.log(`  updated existing draft ${contentReferenceKey}`); }
  else ({ contentReferenceKey } = await sp('POST', `/aplus/2020-11-01/contentDocuments?marketplaceId=${MP}`, doc));
  await sp('POST', `/aplus/2020-11-01/contentDocuments/${contentReferenceKey}/asins?marketplaceId=${MP}`, { asinSet: asins });
  await sp('POST', `/aplus/2020-11-01/contentDocuments/${contentReferenceKey}/approvalSubmissions?marketplaceId=${MP}`);
  console.log(`A+ ${contentReferenceKey} submitted for ${asins.join(', ')}. Approval usually takes up to 7 days.`);
}

const run = { listings, status, aplus }[cmd];
if (!run) { console.log('usage: node amazon_push.mjs listings|status|aplus [--live] [--env path]'); process.exit(1); }
await run();
