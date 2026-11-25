// build_crawler_xml port: byte-for-byte against the Python builder. Usage: node parity_xml.mjs WORK
import fs from 'fs'; import { buildCrawlerXml } from '../web/crawler_xml.js';
const W = process.argv[2], C = JSON.parse(fs.readFileSync(`${W}/xml_cases.json`)); let bad = 0;
for (const c of C) { const kw = { ...c.kw }; if (kw.objects) kw.objects = kw.objects.map(o => o.map(Number)); if (buildCrawlerXml(kw) !== c.xml) bad++; }
const res = { identical: C.length - bad, total: C.length };
console.log(`build_crawler_xml port: ${res.identical}/${res.total} byte-identical`);
fs.writeFileSync(`${W}/parity_xml.json`, JSON.stringify(res)); if (bad) process.exit(1);
