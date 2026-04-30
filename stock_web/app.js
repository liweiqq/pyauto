const stockDB = {
  "00700": { name: "腾讯控股", market: "HK", price: 352.2, changePct: 1.35, pe: 18.6, pb: 3.2, cap: "3.26T HKD" },
  "09988": { name: "阿里巴巴-SW", market: "HK", price: 78.4, changePct: -0.85, pe: 13.1, pb: 1.5, cap: "1.45T HKD" },
  "AAPL": { name: "Apple", market: "US", price: 197.6, changePct: 0.42, pe: 29.4, pb: 39.8, cap: "3.0T USD" },
  "TSLA": { name: "Tesla", market: "US", price: 168.9, changePct: -1.93, pe: 47.0, pb: 7.3, cap: "537B USD" }
};

const greyMarketDB = {
  "LAZY": { ipo: "蓝宇科技", issue: 28.0, grey: 31.8, premiumPct: 13.57, volume: "1280万股", broker: "富途暗盘" },
  "NOVA": { ipo: "Nova Med", issue: 12.5, grey: 11.9, premiumPct: -4.8, volume: "440万股", broker: "辉立暗盘" }
};

let current = "00700";
const quoteEl = document.getElementById("quote");
const greyEl = document.getElementById("grey");
const analysisEl = document.getElementById("analysis");
const historyEl = document.getElementById("history");
const watchlistEl = document.getElementById("watchlist");

function randomHistory(base, len = 10) {
  return Array.from({ length: len }).map((_, i) => {
    const delta = (Math.random() * 0.1 - 0.05) * base;
    const value = +(base + delta).toFixed(2);
    return { date: `2026-04-${String(20 + i).padStart(2, "0")}`, close: value };
  });
}

function renderQuote(stock) {
  const cls = stock.changePct >= 0 ? "up" : "down";
  quoteEl.innerHTML = `
    <h2>${stock.name} (${current})</h2>
    <div class="grid">
      <div class="kpi"><h4>最新价</h4><p>${stock.price}</p></div>
      <div class="kpi"><h4>涨跌幅</h4><p class="${cls}">${stock.changePct}%</p></div>
      <div class="kpi"><h4>市值</h4><p>${stock.cap}</p></div>
      <div class="kpi"><h4>市场</h4><p>${stock.market}</p></div>
    </div>`;
}

function renderGreyMarket() {
  const rows = Object.entries(greyMarketDB).map(([code, g]) => `
    <tr>
      <td>${code}</td><td>${g.ipo}</td><td>${g.issue}</td><td>${g.grey}</td>
      <td class="${g.premiumPct >= 0 ? "up" : "down"}">${g.premiumPct}%</td>
      <td>${g.volume}</td><td>${g.broker}</td>
    </tr>`).join("");
  greyEl.innerHTML = `<h2>今日暗盘信息</h2>
    <table>
      <thead><tr><th>代码</th><th>名称</th><th>发行价</th><th>暗盘价</th><th>溢价率</th><th>成交量</th><th>来源</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
}

function renderAnalysis(stock) {
  const score = +(70 + Math.random() * 25).toFixed(1);
  const signal = stock.changePct > 0 ? "偏强（短线多头）" : "震荡偏弱（关注支撑）";
  analysisEl.innerHTML = `
    <h2>个股分析</h2>
    <div class="grid">
      <div class="kpi"><h4>PE(TTM)</h4><p>${stock.pe}</p></div>
      <div class="kpi"><h4>PB</h4><p>${stock.pb}</p></div>
      <div class="kpi"><h4>综合评分</h4><p>${score}/100</p></div>
      <div class="kpi"><h4>趋势信号</h4><p>${signal}</p></div>
    </div>
    <p class="muted">分析维度：估值、动量、成交强弱（演示版）。</p>`;
}

function renderGreyHistory(stock) {
  const history = randomHistory(stock.price, 8);
  historyEl.innerHTML = `<h2>暗盘历史</h2>
    <table><thead><tr><th>日期</th><th>参考收盘</th><th>相对发行价</th></tr></thead><tbody>
    ${history.map(h => `<tr><td>${h.date}</td><td>${h.close}</td><td class="${h.close > stock.price ? "up" : "down"}">${(((h.close-stock.price)/stock.price)*100).toFixed(2)}%</td></tr>`).join("")}
    </tbody></table>`;
}

function loadWatchlist() {
  return JSON.parse(localStorage.getItem("watchlist") || "[]");
}
function saveWatchlist(data) {
  localStorage.setItem("watchlist", JSON.stringify(data));
}

function renderWatchlist() {
  const list = loadWatchlist();
  watchlistEl.innerHTML = `<h2>移动清单（Watchlist）</h2>
    <p class="muted">支持手机端浏览器，数据保存在本地 localStorage。</p>
    <button class="action-btn" id="addCurrentBtn">加入当前股票</button>
    <div id="watchRows"></div>`;
  const rows = document.getElementById("watchRows");
  if (!list.length) rows.innerHTML = `<p class="muted">暂无股票，请先添加。</p>`;
  rows.innerHTML += list.map((x, i) => `<div class="list-row"><span>${x.code} - ${x.name}</span><button data-i="${i}" class="remove">删除</button></div>`).join("");
  document.getElementById("addCurrentBtn").onclick = () => {
    const stock = stockDB[current];
    if (!list.some(x => x.code === current)) {
      list.push({ code: current, name: stock.name });
      saveWatchlist(list);
      renderWatchlist();
    }
  };
  rows.querySelectorAll(".remove").forEach(btn => {
    btn.onclick = () => {
      list.splice(+btn.dataset.i, 1);
      saveWatchlist(list);
      renderWatchlist();
    };
  });
}


function createSyntheticStock(code) {
  const seed = [...code].reduce((n, c) => n + c.charCodeAt(0), 0);
  const price = +(20 + (seed % 300) + ((seed % 17) / 10)).toFixed(2);
  const changePct = +((((seed % 15) - 7) / 3).toFixed(2));
  const market = /^\d{5,6}$/.test(code) ? "HK" : (/^[A-Z]{1,5}$/.test(code) ? "US" : "CN");
  return {
    name: `${code}（自动生成）`,
    market,
    price,
    changePct,
    pe: +(8 + (seed % 35)).toFixed(1),
    pb: +(0.8 + (seed % 60) / 10).toFixed(1),
    cap: "模拟数据"
  };
}

function renderAll() {
  const stock = stockDB[current];
  renderQuote(stock);
  renderGreyMarket();
  renderAnalysis(stock);
  renderGreyHistory(stock);
  renderWatchlist();
}

document.querySelectorAll(".tab").forEach(tab => {
  tab.onclick = () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(tab.dataset.tab).classList.add("active");
  };
});

document.getElementById("searchBtn").onclick = () => {
  const q = document.getElementById("stockInput").value.trim().toUpperCase();
  if (!q) return;
  const found = Object.entries(stockDB).find(([code, s]) => code === q || s.name.toUpperCase().includes(q));
  if (found) {
    current = found[0];
    renderAll();
    return;
  }

  if (!stockDB[q]) {
    stockDB[q] = createSyntheticStock(q);
  }
  current = q;
  renderAll();
  alert(`未收录 ${q} 的实时数据，已为你生成可浏览的模拟数据。你可以后续接入真实 API。`);
};

renderAll();
