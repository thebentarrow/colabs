/**
 * Options Chain Fetcher
 * ---------------------
 * Fetches the full options chain for a given stock ticker every 15 minutes
 * using the Polygon.io API, and saves each snapshot to a timestamped JSON file.
 *
 * Setup:
 *   1. npm install node-fetch
 *   2. Set your API key: export POLYGON_API_KEY=your_key_here
 *   3. Run: node options-chain-fetcher.js AAPL
 *
 * Polygon.io free tier supports delayed data.
 * Upgrade to Stocks Starter or higher for real-time options data.
 */

const fs = require("fs");
const path = require("path");

// ── Config ────────────────────────────────────────────────────────────────────
const TICKER        = process.argv[2] || "AAPL";      // e.g.  node script.js TSLA
const API_KEY       = process.env.POLYGON_API_KEY || "YOUR_API_KEY_HERE";
const INTERVAL_MS   = 15 * 60 * 1000;                 // 15 minutes
const OUTPUT_DIR    = "./options_data";                // folder for saved snapshots
const LIMIT         = 250;                             // max contracts per page (Polygon max)

// Market hours (Eastern Time) — skip fetching outside trading hours
const MARKET_OPEN_ET  = { hour: 9,  minute: 30 };
const MARKET_CLOSE_ET = { hour: 16, minute: 0  };

// ── Helpers ───────────────────────────────────────────────────────────────────

/**
 * Returns true if the current time (ET) is within regular market hours.
 * Adjust or remove this check if you need pre/post-market data.
 */
function isMarketOpen() {
  const now = new Date();
  const etString = now.toLocaleString("en-US", { timeZone: "America/New_York" });
  const et = new Date(etString);
  const minutes = et.getHours() * 60 + et.getMinutes();
  const open    = MARKET_OPEN_ET.hour  * 60 + MARKET_OPEN_ET.minute;
  const close   = MARKET_CLOSE_ET.hour * 60 + MARKET_CLOSE_ET.minute;
  const dayOfWeek = et.getDay(); // 0 = Sunday, 6 = Saturday
  return dayOfWeek >= 1 && dayOfWeek <= 5 && minutes >= open && minutes < close;
}

/** Formats a Date as  YYYY-MM-DD_HH-MM  for use in filenames. */
function formatTimestamp(date) {
  return date.toISOString().replace(/:/g, "-").slice(0, 16);
}

/** Ensures the output directory exists. */
function ensureOutputDir() {
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    console.log(`[init] Created output directory: ${OUTPUT_DIR}`);
  }
}

// ── Polygon.io Fetcher ────────────────────────────────────────────────────────

/**
 * Fetches ALL pages of options contracts for the given ticker.
 * Polygon paginates via a `next_url` field in the response.
 *
 * Docs: https://polygon.io/docs/options/get_v3_snapshot_options__underlyingasset
 */
async function fetchOptionsChain(ticker) {
  // Lazy-load node-fetch (works with both CommonJS and ESM builds)
  const { default: fetch } = await import("node-fetch");

  const contracts = [];
  let url =
    `https://api.polygon.io/v3/snapshot/options/${ticker}` +
    `?limit=${LIMIT}&apiKey=${API_KEY}`;

  let page = 0;
  while (url) {
    page++;
    console.log(`  [fetch] Page ${page} — ${url.split("?")[0]}`);

    const res = await fetch(url);
    if (!res.ok) {
      const body = await res.text();
      throw new Error(`HTTP ${res.status}: ${body}`);
    }

    const json = await res.json();

    if (json.status === "ERROR" || json.status === "NOT_AUTHORIZED") {
      throw new Error(`Polygon error: ${json.error || json.message}`);
    }

    const results = json.results || [];
    contracts.push(...results);
    console.log(`  [fetch] Got ${results.length} contracts (total so far: ${contracts.length})`);

    // Follow pagination cursor if present
    url = json.next_url ? `${json.next_url}&apiKey=${API_KEY}` : null;
  }

  return contracts;
}

// ── Save Snapshot ─────────────────────────────────────────────────────────────

function saveSnapshot(ticker, contracts) {
  const timestamp = formatTimestamp(new Date());
  const filename  = `${ticker}_options_${timestamp}.json`;
  const filepath  = path.join(OUTPUT_DIR, filename);

  const snapshot = {
    ticker,
    fetchedAt: new Date().toISOString(),
    contractCount: contracts.length,
    contracts,
  };

  fs.writeFileSync(filepath, JSON.stringify(snapshot, null, 2));
  console.log(`[save] Wrote ${contracts.length} contracts → ${filepath}`);
  return filepath;
}

// ── Summary Logger ────────────────────────────────────────────────────────────

/**
 * Prints a brief summary: count of calls vs puts, and the spread of expiries.
 */
function logSummary(contracts) {
  const calls = contracts.filter(c => c.details?.contract_type === "call").length;
  const puts  = contracts.filter(c => c.details?.contract_type === "put").length;

  const expiries = [...new Set(
    contracts.map(c => c.details?.expiration_date).filter(Boolean)
  )].sort();

  console.log(`[summary] Calls: ${calls} | Puts: ${puts} | Expiries: ${expiries.length}`);
  if (expiries.length) {
    console.log(`[summary] Earliest: ${expiries[0]}  |  Latest: ${expiries[expiries.length - 1]}`);
  }
}

// ── Main Loop ─────────────────────────────────────────────────────────────────

async function run() {
  ensureOutputDir();
  console.log(`\n${"─".repeat(60)}`);
  console.log(` Options Chain Fetcher  |  Ticker: ${TICKER}`);
  console.log(` Interval : every 15 minutes (market hours only)`);
  console.log(` Output   : ${path.resolve(OUTPUT_DIR)}`);
  console.log(`${"─".repeat(60)}\n`);

  if (!API_KEY || API_KEY === "YOUR_API_KEY_HERE") {
    console.error("[error] No API key found. Set POLYGON_API_KEY environment variable.");
    process.exit(1);
  }

  // Run immediately on start, then on each interval
  await tick();
  setInterval(tick, INTERVAL_MS);
}

async function tick() {
  const now = new Date().toLocaleTimeString("en-US", { timeZone: "America/New_York" });

  if (!isMarketOpen()) {
    console.log(`[${now} ET] Market is closed — skipping fetch.`);
    return;
  }

  console.log(`[${now} ET] Fetching options chain for ${TICKER}…`);
  try {
    const contracts = await fetchOptionsChain(TICKER);
    logSummary(contracts);
    saveSnapshot(TICKER, contracts);
  } catch (err) {
    console.error(`[error] Failed to fetch options chain: ${err.message}`);
  }
}

run();