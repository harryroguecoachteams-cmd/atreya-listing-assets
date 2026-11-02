// Fills a fresh Flipkart Seller Hub catalog template (Toran vertical) for the two Ganesh lotus bell
// latkan SKUs, from listing.json. Same field choices as the live ATR-GANESH-LOTUS-LATKAN-4 toran
// (FSN TRNHRFNVVUATPMSH): HSN 6702, GST_18, Atreya packer/manufacturer address, Suitable For Door.
//
//   node flipkart_catalog.cjs <path to the C_toran_*.xls downloaded from Seller Hub>
//   -> flipkart/<same file name>  (upload it with the name unchanged, then Send to QC)
const fs = require('fs');
const path = require('path');
const XLSX = require('E:/atreya/listing/atreya-aplus/node_modules/xlsx');

const templatePath = process.argv[2];
if (!templatePath) throw new Error('template path required');
const L = JSON.parse(fs.readFileSync(path.join(__dirname, 'listing.json'), 'utf8'));
const S = L.shared, F = L.flipkart;
const SEP = '::';
const col = (n) => { let s = ''; while (n > 0) { const m = (n - 1) % 26; s = String.fromCharCode(65 + m) + s; n = Math.floor((n - 1) / 26); } return s; };
const keywords = (t, max = 20) => [...new Set(String(t).toLowerCase().split(/[\s,]+/).filter(Boolean))].slice(0, max).join(SEP);

const rowsFor = (k) => {
  const n = k.number_of_items;
  const img = (f) => `${L.image_base_url}/${k.sku}/${f}`;
  const [len, wid, ht] = k.package_cm;
  return {
    'Seller SKU ID': k.sku,
    'Listing Status': 'Active',
    'MRP (INR)': k.mrp_inr,
    'Your selling price (INR)': k.price_inr,
    'Fullfilment by': 'Seller',
    'Procurement type': 'instock',
    'Procurement SLA (DAY)': 2,
    'Stock': k.quantity,
    'Shipping provider': 'Flipkart',
    'Local handling fee (INR)': 0, 'Zonal handling fee (INR)': 0, 'National handling fee (INR)': 0,
    'Length (CM)': len, 'Breadth (CM)': wid, 'Height (CM)': ht,
    'Weight (KG)': k.package_weight_g / 1000,
    'HSN': S.hsn_code,
    'Luxury Cess': 0,
    'Country Of Origin': 'India',
    'Manufacturer Details': S.contact,
    'Packer Details': S.contact,
    'Tax Code': 'GST_18',
    'Minimum Order Quantity (MinOQ)': 1,
    'Brand': L.brand,
    'Model Number': k.part_number,
    'Length (ft)': Math.round(S.strand_length_cm / 30.48 * 10) / 10,
    'Items Included': F[`sales_package_${n}`],
    'Main Image URL': img(k.images[0]),
    'Other Image URL 1': img(k.images[1]), 'Other Image URL 2': img(k.images[2]),
    'Other Image URL 3': img(k.images[3]), 'Other Image URL 4': img(k.images[4]),
    'Description': S.description,
    'Search Keywords': keywords(S.backend_search_terms),
    'Key Features': F.key_features.join(SEP),
    // Flipkart builds the title as brand + model name + "Toran", so this gives title_2 / title_4
    'Model Name': F[`title_${n}`].replace(/^Atreya\s+/, '').replace(/\s+Toran$/, ''),
    'Material': 'Fabric::Wood::Plastic',
    'Style': S.style,
    'Color': 'Multicolor',
    'Suitable For': 'Door',
    'Weight (g)': k.item_weight_g,
    'Warranty Summary': 'No warranty', 'Warranty Service Type': 'No warranty',
    'Covered in Warranty': 'No warranty', 'Not Covered in Warranty': 'No warranty',
    'Pack of': n,
  };
};

const wb = XLSX.readFile(templatePath, { cellStyles: true });
const ws = wb.Sheets[F.vertical];
if (!ws) throw new Error(`${F.vertical} sheet not found in ${templatePath}`);
const grid = XLSX.utils.sheet_to_json(ws, { header: 1 });
const headers = grid[0].map((h) => String(h || '').split('\n')[0].trim());
const FORBIDDEN = /amazon|meesho|indiamart|alibaba|supplier|competitor|craftvatika/i;
const INV = require('E:/atreya/listing/atreya-aplus/flipkart_templates_2109.json')[F.vertical];
const MANDATORY = INV.cols.filter((c) => c && /8DB4E2|CC99FF/.test(c.fill)).map((c) => c.h)
  .filter((h) => !/Flipkart Serial|Catalog QC|QC Failed|Product Link|Product Data Status|Disapproval|Importer/.test(h));
let row = 5;                                  // rows 1-4: header, example, description, blank
for (const k of L.skus) {
  const values = rowsFor(k);
  for (const [name, value] of Object.entries(values)) {
    const targets = headers.map((h, i) => (h === name ? i + 1 : null)).filter(Boolean);
    if (!targets.length) { console.log(`  (no column "${name}")`); continue; }
    if (typeof value === 'string' && FORBIDDEN.test(value) && !/Image URL/.test(name)) throw new Error(`${k.sku} ${name}: forbidden reference`);
    for (const t of targets) ws[`${col(t)}${row}`] = typeof value === 'number' ? { t: 'n', v: value } : { t: 's', v: String(value) };
  }
  // every blue (8DB4E2) or purple (CC99FF) column is mandatory (colours from the saved 21 Sep toran template)
  const missing = MANDATORY.filter((h) => { const i = headers.indexOf(h); return i >= 0 && !ws[`${col(i + 1)}${row}`]; });
  console.log(`${k.sku} -> row ${row} | ${values['Model Name']} | Rs ${values['Your selling price (INR)']} / MRP ${values['MRP (INR)']} | stock ${values.Stock}${missing.length ? ' | MISSING: ' + missing.join(', ') : ''}`);
  row++;
}
const out = path.join(__dirname, 'flipkart', path.basename(templatePath));
fs.mkdirSync(path.dirname(out), { recursive: true });
XLSX.writeFile(wb, out, { bookType: 'biff8', bookSST: true });   // bookSST: Label cells cut at 255 chars
console.log('wrote', out);
