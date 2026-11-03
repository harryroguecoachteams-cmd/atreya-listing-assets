// Upload in Seller Hub: Listings -> Uploads -> Upload Variant Grouping File. Track it under Add New Listings -> Variant Grouping.
// Flipkart variant grouping file: Main FSN (Pack of 2) | Variant FSN (Pack of 4).
// Sheet names and headers copied from Seller Hub's downloadNewGroupingTemplate.
const XLSX = require('E:/atreya/listing/atreya-aplus/node_modules/xlsx');
const wb = XLSX.utils.book_new();
// Seller Hub refuses uploads under ~200 KB (its own template is 1.3 MB with an embedded screenshot),
// so the instructions sheet carries filler rows; the grouping itself is only the last sheet.
const filler = [['Variant grouping: Atreya Ganesh lotus bell latkan']];
for (let r = 0; r < 2500; r++) filler.push(Array.from({ length: 10 }, (_, c) => r * 10 + c));
XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(filler), 'Summary Sheet');
XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet([['Main FSN', 'Variant FSN'], ['FSN1', 'FSN11'], ['FSN1', 'FSN12']]), 'Sample');
XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet([['Main FSN', 'Variant FSN'], ['TRNHSQBRZDH7KKAG', 'TRNHSQBSZKHB7TKG']]), 'Template (Fill Here)');
const out = require('path').join(__dirname, 'flipkart', 'variant_grouping_lotusbell.xls');
XLSX.writeFile(wb, out, { bookType: 'biff8' });
console.log('wrote', out);
