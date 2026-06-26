// ci_smoke.mjs — headless-Chromium boot smoke for the campaign tools.
//
// The dev sandbox can't launch Chromium (missing libs / no root), so this runs in
// CI, where a real browser is available. It serves the repo over http (mirroring the
// `python3 -m http.server` workflow — file:// breaks the sheet's fetch() of character
// JSON), boots each page, and FAILS only on an *uncaught* JS exception (`pageerror`)
// during load. console.error/warn is logged but does NOT fail the run — only logging
// can be intentional, a thrown-and-uncaught error never is. This catches the class
// `node --check` can't: scripts that parse fine but throw at runtime.
//
// To widen coverage, add files to PAGES. Keep this dependency-light and robust;
// a flaky smoke is worse than no smoke.

import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';
import { chromium } from 'playwright';

const ROOT  = process.cwd();
const PAGES = ['sheet.html']; // boot-smoke targets; add e.g. 'KOTOR_GM_Console_v4.html' once confirmed clean
const MIME  = {
  '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.json': 'application/json', '.css': 'text/css', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2',
};

// --- tiny static server (no deps) -----------------------------------------
const server = createServer(async (req, res) => {
  try {
    const url = decodeURIComponent((req.url || '/').split('?')[0]);
    const p = normalize(join(ROOT, url === '/' ? '/index.html' : url));
    if (!p.startsWith(ROOT)) { res.writeHead(403).end(); return; }     // no path escape
    const body = await readFile(p);
    res.writeHead(200, { 'content-type': MIME[extname(p)] || 'application/octet-stream' });
    res.end(body);
  } catch {
    res.writeHead(404).end();
  }
});

await new Promise((r) => server.listen(0, r));
const { port } = server.address();

// --- boot each page in a real browser -------------------------------------
const browser = await chromium.launch();
let failures = 0;

for (const page of PAGES) {
  const ctx = await browser.newContext();
  const pg  = await ctx.newPage();
  const errors = [];
  pg.on('pageerror', (e) => errors.push(String(e).split('\n')[0]));
  pg.on('console', (m) => { if (m.type() === 'error') console.log(`   [console.error] ${page}: ${m.text()}`); });

  try {
    // waitUntil:'load' (not 'networkidle') — firebase live-sync can hold a connection open.
    await pg.goto(`http://localhost:${port}/${page}`, { waitUntil: 'load', timeout: 30000 });
    await pg.waitForTimeout(1500); // let deferred init settle
  } catch (e) {
    errors.push('navigation: ' + String(e).split('\n')[0]);
  }

  if (errors.length) {
    failures++;
    console.error(`\u2717 ${page}: ${errors.length} uncaught error(s) during boot`);
    for (const e of errors) console.error('   ' + e);
  } else {
    console.log(`\u00b7 ${page}: booted clean (no uncaught exceptions)`);
  }
  await ctx.close();
}

await browser.close();
server.close();
process.exit(failures ? 1 : 0);
