"""Stock Portfolio Tracker - a browser-based local Python project.

Run: python main.py
Then open: http://127.0.0.1:8765

Prices are fixed educational examples, not live market prices.
"""

import csv
import io
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import webbrowser

HOST = "127.0.0.1"
PORT = 8765

# Fixed educational sample prices (USD); no live market data is fetched.
STOCK_PRICES = {
    "AAPL": 180.00,
    "TSLA": 250.00,
    "GOOGL": 140.00,
    "MSFT": 420.00,
    "AMZN": 185.00,
}

STOCK_NAMES = {
    "AAPL": "Apple Inc.",
    "TSLA": "Tesla, Inc.",
    "GOOGL": "Alphabet Inc.",
    "MSFT": "Microsoft Corporation",
    "AMZN": "Amazon.com, Inc.",
}

STOCK_COLORS = {
    "AAPL": "#7c83ff",
    "TSLA": "#ff6b7a",
    "GOOGL": "#f7b955",
    "MSFT": "#36cfc9",
    "AMZN": "#8bdb8b",
}

# Starter data makes the dashboard useful on first launch. Reset Portfolio
# clears these holdings. All totals are recalculated from price x quantity.
PORTFOLIO = [
    {"symbol": "AAPL", "quantity": 5},
    {"symbol": "TSLA", "quantity": 2},
]


def calculate_investment(symbol, quantity):
    """Return the investment value for one stock holding."""
    return round(STOCK_PRICES[symbol] * quantity, 2)


def portfolio_snapshot():
    """Build portfolio data and calculate every total from source values."""
    holdings = []
    total_value = 0.0
    total_shares = 0

    for holding in PORTFOLIO:
        symbol = holding["symbol"]
        quantity = int(holding["quantity"])
        price = STOCK_PRICES[symbol]
        value = calculate_investment(symbol, quantity)
        holdings.append(
            {
                "symbol": symbol,
                "name": STOCK_NAMES[symbol],
                "price": price,
                "quantity": quantity,
                "total_value": value,
                "color": STOCK_COLORS[symbol],
            }
        )
        total_value += value
        total_shares += quantity

    # Return stable rounded totals for display and calculations.
    return {
        "stocks": STOCK_PRICES,
        "names": STOCK_NAMES,
        "colors": STOCK_COLORS,
        "portfolio": holdings,
        "total_value": round(total_value, 2),
        "total_shares": total_shares,
        "holding_count": len(holdings),
    }


HTML_PAGE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#0a1020">
<title>Northstar · Stock Portfolio Tracker</title>
<style>
  :root {
    color-scheme: dark;
    --bg: #080d1a;
    --panel: rgba(17, 26, 47, .82);
    --panel-solid: #111a2f;
    --panel-soft: #0c1427;
    --border: rgba(148, 163, 184, .16);
    --muted: #8f9bb4;
    --text: #edf2ff;
    --accent: #8b91ff;
    --green: #55e0b0;
    --red: #ff7887;
    --radius: 22px;
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0; min-height: 100vh; color: var(--text);
    background:
      radial-gradient(ellipse at 5% 0%, rgba(93, 95, 214, .20), transparent 33rem),
      radial-gradient(ellipse at 95% 15%, rgba(37, 190, 163, .10), transparent 28rem),
      var(--bg);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }
  button, input, select { font: inherit; }
  button { cursor: pointer; }
  button:focus-visible, input:focus-visible, select:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
  .shell { max-width: 1440px; padding: 26px; margin: 0 auto; }
  .topbar { display:flex; align-items:center; justify-content:space-between; gap:18px; margin-bottom:28px; }
  .brand { display:flex; align-items:center; gap:13px; min-width:0; }
  .brand-mark { width:46px; height:46px; display:grid; place-items:center; border-radius:15px; background:linear-gradient(135deg,#777cff,#41d9b5); color:#08101e; font-size:23px; font-weight:900; box-shadow:0 8px 28px #777cff32; }
  .eyebrow { color:var(--green); font-size:11px; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }
  h1 { font-size:clamp(22px,3vw,30px); line-height:1.15; margin:4px 0 0; letter-spacing:-.04em; }
  .top-actions { display:flex; align-items:center; gap:10px; }
  .status-pill { display:flex; align-items:center; gap:8px; border:1px solid var(--border); color:#c6d0e5; background:#101a2b99; border-radius:999px; padding:10px 14px; font-size:12px; white-space:nowrap; }
  .pulse { width:7px; height:7px; border-radius:50%; background:var(--green); box-shadow:0 0 12px #55e0b099; }
  .button { border:1px solid var(--border); border-radius:12px; padding:10px 14px; color:var(--text); background:#18233b; font-weight:700; font-size:13px; transition:transform .18s,background .18s,border-color .18s; }
  .button:hover { transform:translateY(-1px); border-color:#777cff88; background:#202d49; }
  .button.primary { color:#091322; background:linear-gradient(135deg,#a1a5ff,#65e5c1); border:0; box-shadow:0 8px 24px #65e5c11b; }
  .button.primary:hover { background:linear-gradient(135deg,#b8bbff,#8af1d3); }
  .button.danger { color:#ff9daa; background:#ff78870d; border-color:#ff78872b; }
  .hero { display:grid; grid-template-columns:minmax(0,1.5fr) minmax(280px,.8fr); gap:18px; margin-bottom:18px; }
  .hero-value, .hero-note, .panel, .metric { background:linear-gradient(145deg,rgba(20,31,55,.92),rgba(12,20,38,.88)); border:1px solid var(--border); border-radius:var(--radius); box-shadow:0 20px 60px #00000014; }
  .hero-value { padding:28px 30px; position:relative; overflow:hidden; }
  .hero-value:after { content:""; position:absolute; width:240px; height:240px; right:-60px; top:-110px; border-radius:50%; background:radial-gradient(circle,#8b91ff27,transparent 68%); pointer-events:none; }
  .section-label { color:var(--muted); font-size:12px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; }
  .value-line { display:flex; align-items:baseline; flex-wrap:wrap; gap:12px; margin-top:13px; }
  .big-total { font-size:clamp(34px,5vw,54px); line-height:1.1; letter-spacing:-.055em; font-weight:800; font-variant-numeric:tabular-nums; }
  .sample-tag { font-size:11px; color:#b6f5e2; background:#55e0b016; border:1px solid #55e0b02b; border-radius:999px; padding:6px 9px; }
  .hero-help { margin:13px 0 0; color:var(--muted); font-size:13px; line-height:1.65; max-width:620px; }
  .hero-note { padding:24px; display:flex; flex-direction:column; justify-content:space-between; gap:16px; }
  .note-top { display:flex; align-items:center; justify-content:space-between; gap:12px; }
  .note-icon { width:38px; height:38px; border-radius:13px; display:grid; place-items:center; background:#8b91ff18; color:#a9adff; font-size:19px; }
  .note-number { font-size:25px; font-weight:800; letter-spacing:-.04em; }
  .note-sub { color:var(--muted); font-size:12px; margin-top:4px; }
  .metrics { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; margin-bottom:24px; }
  .metric { padding:17px 20px; border-radius:17px; }
  .metric-label { color:var(--muted); font-size:12px; }
  .metric-value { font-size:22px; font-weight:800; letter-spacing:-.03em; margin-top:9px; font-variant-numeric:tabular-nums; }
  .section-heading { display:flex; justify-content:space-between; align-items:end; gap:16px; margin:25px 0 14px; }
  .section-heading h2 { margin:0; font-size:18px; letter-spacing:-.025em; }
  .section-heading p { margin:5px 0 0; font-size:12px; color:var(--muted); }
  .catalog { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:12px; }
  .stock-card { text-align:left; background:var(--panel); color:var(--text); border:1px solid var(--border); border-radius:17px; padding:17px; transition:transform .18s,border-color .18s,background .18s; min-width:0; }
  .stock-card:hover { transform:translateY(-3px); border-color:#8b91ff80; background:#172440; }
  .ticker-row { display:flex; justify-content:space-between; align-items:center; gap:8px; }
  .ticker { font-weight:850; font-size:15px; }
  .ticker-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
  .company { color:var(--muted); font-size:11px; margin-top:8px; min-height:28px; line-height:1.4; }
  .stock-price { font-size:18px; font-weight:800; margin-top:14px; font-variant-numeric:tabular-nums; }
  .click-hint { color:#9da8c1; font-size:10px; margin-top:6px; }
  .main-grid { display:grid; grid-template-columns:minmax(270px,.75fr) minmax(0,1.5fr); gap:18px; align-items:start; }
  .panel { padding:23px; min-width:0; }
  .panel-head { display:flex; justify-content:space-between; align-items:start; gap:12px; margin-bottom:20px; }
  .panel h3 { margin:0; font-size:16px; letter-spacing:-.02em; }
  .panel-desc { color:var(--muted); font-size:12px; margin-top:5px; line-height:1.5; }
  .step { width:28px; height:28px; border-radius:9px; display:grid; place-items:center; flex-shrink:0; font-weight:800; color:#b8baff; background:#8b91ff18; }
  .field { margin-bottom:16px; }
  .field label { display:block; font-size:12px; color:#c7d0e5; margin-bottom:8px; font-weight:650; }
  .field select, .field input { width:100%; border-radius:12px; background:#0a1223; color:var(--text); border:1px solid #293650; padding:13px 12px; outline:none; }
  .field select:focus, .field input:focus { border-color:#8b91ff99; box-shadow:0 0 0 3px #8b91ff14; }
  .estimate { display:flex; justify-content:space-between; align-items:center; gap:8px; background:#080f20b8; border:1px solid var(--border); border-radius:12px; padding:13px; margin:4px 0 16px; }
  .estimate span { font-size:12px; color:var(--muted); }
  .estimate strong { color:var(--green); font-size:16px; font-variant-numeric:tabular-nums; }
  .full { width:100%; }
  .message { min-height:20px; margin-top:12px; font-size:12px; line-height:1.5; color:var(--muted); }
  .message.success { color:var(--green); }
  .message.error { color:var(--red); }
  .helper { border-top:1px solid var(--border); margin-top:19px; padding-top:15px; color:var(--muted); font-size:11px; line-height:1.65; }
  .holdings-panel { padding-bottom:18px; }
  .holdings-actions { display:flex; align-items:center; gap:8px; flex-wrap:wrap; justify-content:flex-end; }
  .table-wrap { overflow-x:auto; width:100%; }
  table { width:100%; border-collapse:collapse; white-space:nowrap; }
  th { font-size:10px; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-weight:750; padding:0 12px 13px; text-align:right; }
  th:first-child, td:first-child { text-align:left; padding-left:3px; }
  td { padding:15px 12px; border-top:1px solid var(--border); text-align:right; font-size:13px; font-variant-numeric:tabular-nums; }
  td.value { font-weight:800; color:var(--green); }
  .symbol-cell { display:flex; align-items:center; gap:10px; }
  .symbol-badge { width:34px; height:34px; display:grid; place-items:center; border-radius:11px; background:#ffffff08; font-size:10px; font-weight:900; }
  .symbol-name strong { font-size:12px; display:block; }
  .symbol-name small { color:var(--muted); display:block; font-size:10px; margin-top:3px; }
  .remove-btn { color:#ff9ba7; background:transparent; border:1px solid #ff78872a; padding:6px 9px; border-radius:8px; font-size:11px; }
  .remove-btn:hover { background:#ff788712; }
  .empty { text-align:center; padding:36px 12px; color:var(--muted); }
  .empty-icon { width:46px; height:46px; border-radius:15px; margin:0 auto 12px; display:grid; place-items:center; background:#8b91ff15; font-size:22px; }
  .empty strong { color:var(--text); display:block; font-size:14px; }
  .empty p { font-size:12px; line-height:1.6; }
  .breakdown { margin-top:18px; padding-top:20px; border-top:1px solid var(--border); }
  .breakdown-title { font-size:12px; font-weight:800; margin-bottom:15px; }
  .bar-row { margin-top:13px; }
  .bar-label { display:flex; justify-content:space-between; gap:10px; color:#cbd5e8; font-size:11px; margin-bottom:7px; }
  .bar-label span:last-child { color:var(--muted); font-variant-numeric:tabular-nums; }
  .bar-track { background:#070d1a; border-radius:999px; height:7px; overflow:hidden; }
  .bar-fill { height:100%; border-radius:999px; transition:width .35s ease; }
  .footer { display:flex; justify-content:space-between; gap:16px; flex-wrap:wrap; color:#66728d; font-size:11px; padding:24px 2px 8px; }
  .toast { position:fixed; right:22px; bottom:22px; z-index:5; max-width:min(380px,calc(100vw - 32px)); border:1px solid var(--border); background:#182540; box-shadow:0 18px 55px #0008; color:var(--text); border-radius:14px; padding:13px 16px; font-size:13px; opacity:0; transform:translateY(8px); pointer-events:none; transition:.22s; }
  .toast.show { opacity:1; transform:translateY(0); }
  @media (max-width:1050px) { .catalog { grid-template-columns:repeat(3,minmax(0,1fr)); } .main-grid { grid-template-columns:1fr; } }
  @media (max-width:700px) { .shell { padding:16px; } .topbar { align-items:flex-start; } .top-actions { flex-direction:column; align-items:flex-end; } .status-pill { display:none; } .hero { grid-template-columns:1fr; } .hero-value,.hero-note { padding:22px; } .metrics { gap:8px; } .metric { padding:13px; } .metric-value { font-size:17px; } .catalog { grid-template-columns:repeat(2,minmax(0,1fr)); gap:9px; } .stock-card { padding:13px; } .stock-price { font-size:16px; } .panel { padding:17px; } .section-heading { align-items:start; flex-direction:column; } .holdings-actions { justify-content:flex-start; } }
  @media (max-width:390px) { .metrics { grid-template-columns:1fr; } .value-line { align-items:flex-start; flex-direction:column; gap:9px; } .catalog { grid-template-columns:1fr 1fr; } h1 { font-size:20px; } }
  @media (prefers-reduced-motion:reduce) { *,*::before,*::after { scroll-behavior:auto!important; transition:none!important; } }
</style>
</head>
<body>
<div class="shell">
  <header class="topbar">
    <div class="brand">
      <div class="brand-mark" aria-hidden="true">N</div>
      <div><div class="eyebrow">Personal finance workspace</div><h1>Stock Portfolio Tracker</h1></div>
    </div>
    <div class="top-actions">
      <div class="status-pill"><span class="pulse"></span> Local dashboard · Connected</div>
      <button class="button" id="exportTop" type="button">↓ Export CSV</button>
    </div>
  </header>

  <section class="hero" aria-label="Portfolio overview">
    <div class="hero-value">
      <div class="section-label">Total investment value</div>
      <div class="value-line"><div id="totalVal" class="big-total" aria-live="polite">Calculating…</div><span class="sample-tag">Fixed sample prices</span></div>
      <p class="hero-help">Your portfolio value is calculated from each holding's quantity multiplied by its predefined price. This demo does not use live stock market data.</p>
    </div>
    <div class="hero-note">
      <div class="note-top"><span class="section-label">Portfolio snapshot</span><div class="note-icon" aria-hidden="true">◈</div></div>
      <div><div class="note-number" id="heroHoldings">—</div><div class="note-sub">Different stock holdings</div></div>
      <div style="height:1px;background:var(--border)"></div>
      <div><div class="note-number" id="heroShares">—</div><div class="note-sub">Total shares owned</div></div>
    </div>
  </section>

  <section class="metrics" aria-label="Portfolio metrics">
    <div class="metric"><div class="metric-label">Total portfolio value</div><div class="metric-value" id="metricTotal">—</div></div>
    <div class="metric"><div class="metric-label">Stocks in portfolio</div><div class="metric-value" id="metricHoldings">—</div></div>
    <div class="metric"><div class="metric-label">Total shares</div><div class="metric-value" id="metricShares">—</div></div>
  </section>

  <section aria-labelledby="catalogTitle">
    <div class="section-heading"><div><h2 id="catalogTitle">Explore stock catalogue</h2><p>Select any card to prefill the holding form.</p></div><div class="section-label">5 sample stocks</div></div>
    <div id="catalogCards" class="catalog"></div>
  </section>

  <div class="section-heading"><div><h2>Your portfolio</h2><p>Manage positions and review their investment values.</p></div></div>
  <main class="main-grid">
    <section class="panel" aria-labelledby="addTitle">
      <div class="panel-head"><div><h3 id="addTitle">Add a holding</h3><div class="panel-desc">Choose a stock and enter the number of shares.</div></div><span class="step">01</span></div>
      <form id="addForm">
        <div class="field"><label for="symInput">Stock symbol</label><select id="symInput" required></select></div>
        <div class="field"><label for="qtyInput">Share quantity</label><input id="qtyInput" type="number" inputmode="numeric" min="1" step="1" value="5" placeholder="e.g. 5" required></div>
        <div class="estimate"><span>Estimated holding value</span><strong id="estimateVal">$900.00</strong></div>
        <button class="button primary full" id="addButton" type="submit">＋ Add to portfolio</button>
        <div id="msgBox" class="message" role="status" aria-live="polite">Existing stock positions will have their share quantities combined.</div>
      </form>
      <div class="helper">Prices are hardcoded example values for this assignment. They are not live quotes, financial advice, or a recommendation to buy or sell.</div>
    </section>

    <section class="panel holdings-panel" aria-labelledby="holdingsTitle">
      <div class="panel-head">
        <div><h3 id="holdingsTitle">Holdings breakdown</h3><div class="panel-desc" id="tableSubtitle">Calculated values for your current portfolio.</div></div>
        <div class="holdings-actions"><button class="button" type="button" id="exportButton">Export CSV</button><button class="button danger" type="button" id="clearButton">Reset</button></div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th scope="col">Stock</th><th scope="col">Price</th><th scope="col">Shares</th><th scope="col">Investment value</th><th scope="col">Action</th></tr></thead>
          <tbody id="tableBody"></tbody>
        </table>
        <div id="emptyState" class="empty" hidden><div class="empty-icon">◌</div><strong>Your portfolio is empty</strong><p>Add a stock using the form to calculate your total investment.</p></div>
      </div>
      <div class="breakdown"><div class="breakdown-title">Portfolio allocation</div><div id="chartBars"><div class="panel-desc">Add holdings to see the value breakdown.</div></div></div>
    </section>
  </main>
  <footer class="footer"><span>Northstar · Stock Portfolio Tracker</span><span>Built with Python's standard library · Sample prices only</span></footer>
</div>
<div id="toast" class="toast" role="status" aria-live="polite"></div>

<script>
'use strict';
const money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
let appData = null;
let toastTimer = null;

function showToast(message) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2600);
}
function setMessage(message, type = '') {
  const el = document.getElementById('msgBox');
  el.textContent = message;
  el.className = 'message' + (type ? ' ' + type : '');
}
async function api(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }
  });
  let data;
  try { data = await response.json(); }
  catch (_) { throw new Error('The server returned an unreadable response. Restart the app and try again.'); }
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status}).`);
  return data;
}
function renderCatalog(data) {
  const cards = document.getElementById('catalogCards');
  const select = document.getElementById('symInput');
  cards.replaceChildren();
  select.replaceChildren();
  Object.entries(data.stocks).forEach(([symbol, price]) => {
    const option = document.createElement('option');
    option.value = symbol;
    option.textContent = `${symbol} — ${data.names[symbol]} (${money.format(price)})`;
    select.appendChild(option);

    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'stock-card';
    card.setAttribute('aria-label', `Select ${symbol}, ${data.names[symbol]}, ${money.format(price)} per share`);
    card.innerHTML = `<div class="ticker-row"><span class="ticker"></span><span class="ticker-dot"></span></div><div class="company"></div><div class="stock-price"></div><div class="click-hint">Click to select ↗</div>`;
    card.querySelector('.ticker').textContent = symbol;
    card.querySelector('.ticker-dot').style.background = data.colors[symbol];
    card.querySelector('.company').textContent = data.names[symbol];
    card.querySelector('.stock-price').textContent = money.format(price);
    card.addEventListener('click', () => {
      select.value = symbol;
      updateEstimate();
      document.getElementById('qtyInput').focus();
      setMessage(`${symbol} selected at ${money.format(price)} per share.`);
    });
    cards.appendChild(card);
  });
}
function renderPortfolio(data) {
  appData = data;
  const total = Number(data.total_value) || 0;
  const shares = Number(data.total_shares) || 0;
  const holdings = data.portfolio || [];
  document.getElementById('totalVal').textContent = money.format(total);
  document.getElementById('metricTotal').textContent = money.format(total);
  document.getElementById('heroHoldings').textContent = String(holdings.length);
  document.getElementById('metricHoldings').textContent = String(holdings.length);
  document.getElementById('heroShares').textContent = shares.toLocaleString('en-US');
  document.getElementById('metricShares').textContent = shares.toLocaleString('en-US');
  document.getElementById('tableSubtitle').textContent = holdings.length
    ? `${holdings.length} holding${holdings.length === 1 ? '' : 's'} · ${shares.toLocaleString('en-US')} total shares`
    : 'No holdings yet. Add a stock to get started.';

  const tbody = document.getElementById('tableBody');
  tbody.replaceChildren();
  document.getElementById('emptyState').hidden = holdings.length !== 0;
  document.querySelector('table').hidden = holdings.length === 0;

  holdings.forEach(item => {
    const tr = document.createElement('tr');
    const symbolCell = document.createElement('td');
    const badge = document.createElement('div'); badge.className = 'symbol-badge';
    badge.style.color = item.color; badge.style.border = `1px solid ${item.color}35`; badge.textContent = item.symbol;
    const nameWrap = document.createElement('div'); nameWrap.className = 'symbol-name';
    const symbolName = document.createElement('strong'); symbolName.textContent = item.symbol;
    const companyName = document.createElement('small'); companyName.textContent = item.name;
    nameWrap.append(symbolName, companyName);
    const symbolWrap = document.createElement('div'); symbolWrap.className = 'symbol-cell'; symbolWrap.append(badge, nameWrap); symbolCell.appendChild(symbolWrap);
    tr.appendChild(symbolCell);
    const priceCell = document.createElement('td'); priceCell.textContent = money.format(item.price); tr.appendChild(priceCell);
    const quantityCell = document.createElement('td'); quantityCell.textContent = Number(item.quantity).toLocaleString('en-US'); tr.appendChild(quantityCell);
    const valueCell = document.createElement('td'); valueCell.className = 'value'; valueCell.textContent = money.format(item.total_value); tr.appendChild(valueCell);
    const actionCell = document.createElement('td');
    const remove = document.createElement('button'); remove.type = 'button'; remove.className = 'remove-btn'; remove.textContent = 'Remove';
    remove.setAttribute('aria-label', `Remove ${item.symbol} from portfolio`);
    remove.addEventListener('click', async () => {
      try { await api('/api/remove', { method: 'POST', body: JSON.stringify({ symbol: item.symbol }) }); await loadData(); showToast(`${item.symbol} removed.`); }
      catch (error) { showToast(error.message); }
    });
    actionCell.appendChild(remove); tr.appendChild(actionCell);
    tbody.appendChild(tr);
  });
  renderBars(holdings, total);
  updateEstimate();
}
function renderBars(holdings, total) {
  const holder = document.getElementById('chartBars');
  holder.replaceChildren();
  if (!holdings.length || total <= 0) {
    const text = document.createElement('div'); text.className = 'panel-desc'; text.textContent = 'Add holdings to see the value breakdown.'; holder.appendChild(text); return;
  }
  holdings.forEach(item => {
    const pct = total > 0 ? (item.total_value / total) * 100 : 0;
    const row = document.createElement('div'); row.className = 'bar-row';
    const label = document.createElement('div'); label.className = 'bar-label';
    const left = document.createElement('span'); left.textContent = `${item.symbol} · ${pct.toFixed(1)}%`;
    const right = document.createElement('span'); right.textContent = money.format(item.total_value);
    label.append(left, right);
    const track = document.createElement('div'); track.className = 'bar-track';
    const fill = document.createElement('div'); fill.className = 'bar-fill'; fill.style.width = `${Math.min(100, Math.max(0, pct))}%`; fill.style.background = item.color;
    track.appendChild(fill); row.append(label, track); holder.appendChild(row);
  });
}
function updateEstimate() {
  if (!appData) return;
  const symbol = document.getElementById('symInput').value;
  const quantity = Number(document.getElementById('qtyInput').value);
  const price = Number(appData.stocks[symbol] || 0);
  document.getElementById('estimateVal').textContent = money.format(price * (Number.isFinite(quantity) && quantity > 0 ? Math.floor(quantity) : 0));
}
async function loadData() {
  try {
    const data = await api('/api/portfolio');
    if (!appData) renderCatalog(data);
    renderPortfolio(data);
  } catch (error) {
    document.getElementById('totalVal').textContent = 'Unavailable';
    setMessage(error.message, 'error');
    showToast(error.message);
  }
}
document.getElementById('addForm').addEventListener('submit', async event => {
  event.preventDefault();
  const symbol = document.getElementById('symInput').value;
  const quantity = document.getElementById('qtyInput').value;
  const button = document.getElementById('addButton');
  button.disabled = true; button.textContent = 'Adding…';
  try {
    const result = await api('/api/add', { method: 'POST', body: JSON.stringify({ symbol, quantity }) });
    await loadData();
    setMessage(result.message, 'success');
    showToast(result.message);
  } catch (error) {
    setMessage(error.message, 'error');
  } finally {
    button.disabled = false; button.textContent = '＋ Add to portfolio';
  }
});
document.getElementById('symInput').addEventListener('change', updateEstimate);
document.getElementById('qtyInput').addEventListener('input', updateEstimate);
function exportCsv() {
  if (!appData) { showToast('Portfolio data has not loaded yet.'); return; }
  const rows = [['Stock Symbol', 'Company', 'Price Per Share (USD)', 'Quantity', 'Investment Value (USD)']];
  appData.portfolio.forEach(item => rows.push([item.symbol, item.name, item.price.toFixed(2), item.quantity, item.total_value.toFixed(2)]));
  rows.push([]);
  rows.push(['TOTAL INVESTMENT', '', '', '', Number(appData.total_value).toFixed(2)]);
  const csv = rows.map(row => row.map(value => `"${String(value).replaceAll('"', '""')}"`).join(',')).join('\r\n');
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a'); link.href = url; link.download = 'stock_portfolio.csv';
  document.body.appendChild(link); link.click(); link.remove(); URL.revokeObjectURL(url);
  showToast('Portfolio CSV exported.');
}
document.getElementById('exportButton').addEventListener('click', exportCsv);
document.getElementById('exportTop').addEventListener('click', exportCsv);
document.getElementById('clearButton').addEventListener('click', async () => {
  if (!confirm('Reset the portfolio and remove all current holdings?')) return;
  try { await api('/api/clear', { method: 'POST', body: '{}' }); await loadData(); setMessage('Portfolio reset. Total investment is now $0.00.', 'success'); showToast('Portfolio reset.'); }
  catch (error) { showToast(error.message); }
});
loadData();
</script>
</body>
</html>'''


class PortfolioHandler(BaseHTTPRequestHandler):
    """Serve the dashboard and a small JSON API from the Python standard library."""

    def log_message(self, format_string, *args):
        # Keep the console readable; server errors are still surfaced by Python.
        return

    def send_bytes(self, body, content_type="text/plain; charset=utf-8", status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, data, status=200):
        payload = json.dumps(data).encode("utf-8")
        self.send_bytes(payload, "application/json; charset=utf-8", status)

    def read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 0 or length > 1_000_000:
                raise ValueError("Request body is too large.")
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object.")
            return data
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Invalid request data. Please try again.") from exc

    def do_GET(self):
        if self.path == "/api/portfolio":
            self.send_json(portfolio_snapshot())
        elif self.path in ("/", "/index.html"):
            self.send_bytes(HTML_PAGE.encode("utf-8"), "text/html; charset=utf-8")
        elif self.path == "/favicon.ico":
            self.send_bytes(b"", "image/x-icon", 204)
        else:
            self.send_json({"error": "Route not found."}, 404)

    def do_POST(self):
        try:
            data = self.read_json()
        except ValueError as exc:
            self.send_json({"error": str(exc)}, 400)
            return

        if self.path == "/api/add":
            symbol = str(data.get("symbol", "")).strip().upper()
            if symbol not in STOCK_PRICES:
                self.send_json({"error": "Please choose a valid stock: AAPL, TSLA, GOOGL, MSFT, or AMZN."}, 400)
                return
            quantity_raw = data.get("quantity", "")
            try:
                # Reject decimals, zero, negatives, booleans, and non-numeric text.
                quantity_text = str(quantity_raw).strip()
                if not quantity_text or not quantity_text.isdigit():
                    raise ValueError
                quantity = int(quantity_text)
                if quantity < 1 or quantity > 1_000_000_000:
                    raise ValueError
            except (TypeError, ValueError):
                self.send_json({"error": "Quantity must be a positive whole number."}, 400)
                return

            for holding in PORTFOLIO:
                if holding["symbol"] == symbol:
                    holding["quantity"] += quantity
                    break
            else:
                PORTFOLIO.append({"symbol": symbol, "quantity": quantity})

            snapshot = portfolio_snapshot()
            self.send_json({"ok": True, "message": f"Added {quantity} share(s) of {symbol}.", "total_value": snapshot["total_value"]})
            return

        if self.path == "/api/remove":
            symbol = str(data.get("symbol", "")).strip().upper()
            before = len(PORTFOLIO)
            PORTFOLIO[:] = [holding for holding in PORTFOLIO if holding["symbol"] != symbol]
            if len(PORTFOLIO) == before:
                self.send_json({"error": "That stock is not in the current portfolio."}, 404)
                return
            self.send_json({"ok": True, "message": f"Removed {symbol} from the portfolio."})
            return

        if self.path == "/api/clear":
            PORTFOLIO.clear()
            self.send_json({"ok": True, "message": "Portfolio cleared."})
            return

        self.send_json({"error": "Route not found."}, 404)


def main():
    """Start the localhost dashboard and open it in the default browser."""
    try:
        server = ThreadingHTTPServer((HOST, PORT), PortfolioHandler)
    except OSError as exc:
        print(f"Could not start the local server on {HOST}:{PORT}: {exc}")
        print(f"Close any other app using port {PORT}, or change PORT near the top of main.py.")
        return

    url = f"http://{HOST}:{PORT}"
    print("=" * 62)
    print("  STOCK PORTFOLIO TRACKER")
    print("=" * 62)
    print(f"Dashboard: {url}")
    print("Press Ctrl+C in this terminal to stop the server.")
    print("Prices are fixed educational sample prices, not live quotes.")
    try:
        webbrowser.open(url)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Stock Portfolio Tracker...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
