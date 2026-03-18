/**
 * 主应用逻辑 v2
 * 新增：情绪面板、回测面板
 */

let currentData = [];
let currentPage = 1;
const itemsPerPage = 5;

// ─── 开始分析 ──────────────────────────────────────────────────────
async function startAnalysis() {
    const btn     = document.querySelector(".btn-primary");
    const loading = document.getElementById("loading");
    const btnText = document.getElementById("btnText");
    const status  = document.getElementById("statusMessage");

    loading.style.display = "inline";
    btnText.textContent   = "分析中...";
    btn.disabled          = true;
    if (status) { status.textContent = "正在分析，请稍候..."; status.style.color = "#d29922"; }

    try {
        const params = {
            count:  parseInt(document.getElementById("count").value),
            minCap: parseInt(document.getElementById("minCap").value),
            sortBy: document.getElementById("sortBy").value,
        };

        const result = await api.analyze(params);

        if (result.success) {
            currentData = result.data;
            currentPage = 1;

            updateStats(result.stats);
            updateTableWithPagination(currentData);
            document.getElementById("updateTime").textContent = new Date().toLocaleString();

            // B. 渲染情绪面板
            if (result.sentiment) renderSentiment(result.sentiment);

            // C. 加载回测面板（异步，不阻塞主流程）
            loadBacktest();

            if (status) { status.textContent = `分析完成！共 ${currentData.length} 个币种`; status.style.color = "#238636"; }
        } else {
            if (status) { status.textContent = "分析失败: " + result.error; status.style.color = "#da3633"; }
        }
    } catch (err) {
        console.error(err);
        if (status) { status.textContent = "请求失败，请检查后端是否启动"; status.style.color = "#da3633"; }
    } finally {
        loading.style.display = "none";
        btnText.textContent   = "🔄 开始分析";
        btn.disabled          = false;
    }
}

// ─── 统计卡片 ──────────────────────────────────────────────────────
function updateStats(stats) {
    document.getElementById("statRecommend").textContent = stats.recommend;
    document.getElementById("statWatch").textContent     = stats.watch;
    document.getElementById("statAvoid").textContent     = stats.avoid;
    document.getElementById("statWhale").textContent     = stats.whale;
}

// ─── B. 情绪面板 ──────────────────────────────────────────────────
function renderSentiment(s) {
    const panel = document.getElementById("sentimentPanel");
    panel.style.display = "grid";

    const fg  = s.fear_greed;
    const btc = s.btc;

    // 恐贪指数颜色
    const fgEl = document.getElementById("sFG");
    fgEl.textContent = `${fg.value} · ${fg.label_cn}`;
    fgEl.style.color = fg.value <= 25 ? "#ff6b6b" : fg.value >= 75 ? "#51cf66" : "#ffd43b";

    // BTC 涨跌
    const btcEl = document.getElementById("sBTC");
    const btcChg = btc.change_24h.toFixed(2);
    btcEl.textContent = `${btcChg > 0 ? "+" : ""}${btcChg}%`;
    btcEl.style.color = btc.change_24h >= 0 ? "#51cf66" : "#ff6b6b";

    // 情绪调分
    const adjEl = document.getElementById("sAdj");
    const adj   = s.score_adjust;
    adjEl.textContent = `${adj > 0 ? "+" : ""}${adj} 分`;
    adjEl.style.color = adj >= 0 ? "#51cf66" : "#ff6b6b";

    // 大盘状态
    const mktEl = document.getElementById("sMarket");
    if (s.market_ok) {
        mktEl.textContent = "✅ 正常";
        mktEl.style.color = "#51cf66";
    } else {
        mktEl.textContent = "⚠️ 暴跌预警";
        mktEl.style.color = "#ff6b6b";
    }
}

// ─── C. 回测面板 ──────────────────────────────────────────────────
async function loadBacktest() {
    try {
        const result = await api.getBacktest();
        if (!result.success) return;
        const d = result.data;

        document.getElementById("backtestPanel").style.display = "block";

        const fmt = (v, suffix) => v !== null && v !== undefined ? `${v}${suffix}` : "暂无数据";

        document.getElementById("btWR3").textContent   = fmt(d.winrate_3d,    "%");
        document.getElementById("btAvg3").textContent  = fmt(d.avg_return_3d !== null ? (d.avg_return_3d > 0 ? "+" : "") + d.avg_return_3d : null, "%");
        document.getElementById("btWR7").textContent   = fmt(d.winrate_7d,    "%");
        document.getElementById("btAvg7").textContent  = fmt(d.avg_return_7d !== null ? (d.avg_return_7d > 0 ? "+" : "") + d.avg_return_7d : null, "%");
        document.getElementById("btTotal").textContent = d.total_records;

        // 颜色
        colorVal("btWR3",  d.winrate_3d,    50);
        colorVal("btAvg3", d.avg_return_3d, 0);
        colorVal("btWR7",  d.winrate_7d,    50);
        colorVal("btAvg7", d.avg_return_7d, 0);
    } catch (e) {
        console.warn("回测加载失败", e);
    }
}

function colorVal(id, val, threshold) {
    const el = document.getElementById(id);
    if (val === null || val === undefined) return;
    el.style.color = val >= threshold ? "#51cf66" : "#ff6b6b";
}

// ─── 表格渲染 ──────────────────────────────────────────────────────
function updateTableWithPagination(data) {
    const start    = (currentPage - 1) * itemsPerPage;
    const pageData = data.slice(start, start + itemsPerPage);
    updateTable(pageData);
    updatePagination(data.length);
}

function updateTable(data) {
    const tbody = document.getElementById("tableBody");
    tbody.innerHTML = "";

    if (!data.length) {
        tbody.innerHTML = '<tr><td colspan="14" class="empty">暂无数据</td></tr>';
        return;
    }

    data.forEach(item => {
        const row       = document.createElement("tr");
        const badgeCls  = item.recommendation === "推荐"  ? "badge-recommend"
                        : item.recommendation === "观望"  ? "badge-watch"
                        : "badge-avoid";
        const srcBadge  = item.kline_source === "binance"
            ? '<span style="color:#f0b90b;font-size:10px">●官方</span>'
            : '<span style="color:#888;font-size:10px">●链上</span>';

        row.innerHTML = `
            <td>${item.rank}</td>
            <td><strong>${item.symbol}</strong><br><small>${item.name}</small><br>${srcBadge}</td>
            <td>${(item.market_cap / 10000).toFixed(0)}</td>
            <td class="${item.max_drawdown > 50 ? "positive" : ""}">${item.max_drawdown}%</td>
            <td class="positive">${item.max_rebound}%</td>
            <td>${item.turnover_rate.toFixed(1)}%</td>
            <td class="${item.week_change > 0 ? "positive" : "negative"}">${item.week_change > 0 ? "+" : ""}${item.week_change}%</td>
            <td class="${item.month_change > 0 ? "positive" : "negative"}">${item.month_change > 0 ? "+" : ""}${item.month_change}%</td>
            <td class="${item.concentration > 80 ? "negative" : ""}">${item.concentration}%</td>
            <td>${item.daily_pattern}</td>
            <td class="analysis-text">${item.analysis}</td>
            <td>${item.is_whale ? "是" : "否"}</td>
            <td><span class="badge ${badgeCls}">${item.recommendation}</span><br><small>${item.buy_score}分</small></td>
        `;
        tbody.appendChild(row);
    });
}

function updatePagination(total) {
    const totalPages = Math.ceil(total / itemsPerPage);
    const div = document.getElementById("pagination");
    if (!div) return;

    let html = `<div class="pagination-info">第 ${currentPage} / ${totalPages} 页，共 ${total} 条</div><div class="pagination-buttons">`;
    if (currentPage > 1)
        html += `<button onclick="goToPage(${currentPage - 1})" class="btn-page">上一页</button>`;
    for (let i = 1; i <= totalPages; i++)
        html += `<button onclick="goToPage(${i})" class="btn-page${i === currentPage ? " active" : ""}">${i}</button>`;
    if (currentPage < totalPages)
        html += `<button onclick="goToPage(${currentPage + 1})" class="btn-page">下一页</button>`;
    html += "</div>";
    div.innerHTML = html;
}

window.goToPage = function (page) {
    currentPage = page;
    updateTableWithPagination(currentData);
};

// ─── 初始化 ────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    // 状态消息
    const controls = document.querySelector(".controls");
    if (controls) {
        const s = document.createElement("div");
        s.id = "statusMessage";
        s.style.cssText = "margin-top:10px;text-align:center;font-weight:bold;";
        controls.appendChild(s);
    }

    // 分页容器
    const tbl = document.querySelector(".table-container");
    if (tbl) {
        const p = document.createElement("div");
        p.id = "pagination";
        p.className = "pagination";
        tbl.after(p);
    }

    // 页面加载时立即拉一次情绪 + 回测
    api.getSentiment().then(r => { if (r.success) renderSentiment(r.data); }).catch(() => {});
    loadBacktest();

    fetch("/health").then(r => r.json()).then(d => console.log("后端状态:", d)).catch(() => {});
});
