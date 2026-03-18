"""
历史回测脚本
逻辑：
  1. 从 Binance Spot 获取所有活跃 USDT 交易对
  2. 过滤出符合市值代理条件的山寨币（排除 BTC/ETH/BNB 等大币）
  3. 拉取每只币 60 天日K线
  4. 在「30 天前」时间点，用当时已有数据跑评分算法
  5. 检查 3 天后、7 天后实际涨跌
  6. 统计「推荐」「观望」「不推荐」各组的真实胜率
"""

import requests
import numpy as np
import time
import json
from datetime import datetime, timedelta

SPOT_API = "https://api.binance.com/api/v3"

# ── 排除的大市值稳定币 / 主流币 ──────────────────────
EXCLUDE = {
    "BTC","ETH","BNB","SOL","XRP","ADA","DOGE","MATIC","DOT","AVAX",
    "LINK","UNI","ATOM","LTC","BCH","ETC","SHIB","TRX","NEAR","APT",
    "USDT","USDC","BUSD","DAI","TUSD","FDUSD","USDP",
}

HEADERS = {"User-Agent": "Mozilla/5.0"}


# ── 数据获取 ────────────────────────────────────────────────────────

def get_all_usdt_pairs():
    """获取 Binance 现货所有 USDT 交易对的 24h 统计"""
    resp = requests.get(f"{SPOT_API}/ticker/24hr", headers=HEADERS, timeout=30)
    all_tickers = resp.json()
    pairs = []
    for t in all_tickers:
        sym = t["symbol"]
        if not sym.endswith("USDT"):
            continue
        base = sym[:-4]
        if base in EXCLUDE:
            continue
        volume_usdt = float(t["quoteVolume"])   # USDT 成交额
        price = float(t["lastPrice"])
        if price <= 0:
            continue
        # 用成交额代理市值：保留 10万~5亿 USDT 成交量区间（粗筛中小市值）
        if not (100_000 <= volume_usdt <= 500_000_000):
            continue
        pairs.append({
            "symbol":       base,
            "pair":         sym,
            "price":        price,
            "volume_usdt":  volume_usdt,
            "change_24h":   float(t["priceChangePercent"]),
        })
    # 按成交量排序，取前 150 只（覆盖足够多但不至于太慢）
    pairs.sort(key=lambda x: x["volume_usdt"], reverse=True)
    return pairs[:150]


def get_klines(pair, limit=60):
    """获取日K线，返回 list of [ts, open, high, low, close, volume]"""
    try:
        resp = requests.get(
            f"{SPOT_API}/klines",
            params={"symbol": pair, "interval": "1d", "limit": limit},
            headers=HEADERS,
            timeout=15,
        )
        if resp.status_code != 200:
            return []
        raw = resp.json()
        return [[
            int(k[0]),
            float(k[1]), float(k[2]), float(k[3]),
            float(k[4]), float(k[5]),
        ] for k in raw]
    except Exception:
        return []


# ── 评分算法（与 analyzer.py 对齐）────────────────────────────────

def score_at_point(klines, idx):
    """
    用 klines[0:idx] 的数据（模拟 idx 时刻之前的历史）算评分
    idx 必须 >= 30
    返回 (score, recommendation)
    """
    history = klines[:idx]
    if len(history) < 30:
        return None, None

    closes  = [k[4] for k in history]
    highs   = [k[2] for k in history]
    lows    = [k[3] for k in history]
    volumes = [k[5] for k in history]

    price = closes[-1]

    # 均线
    ma5  = np.mean(closes[-5:])
    ma10 = np.mean(closes[-10:])
    ma20 = np.mean(closes[-20:])

    # K 线形态强度
    strength = 50
    recent = closes[-3:]
    if len(recent) == 3:
        if recent[0] < recent[1] < recent[2]:
            strength += 20   # 三连阳
        elif recent[0] > recent[1] > recent[2]:
            strength -= 20   # 三连阴
    if ma5 > ma20:
        strength += 15       # 均线金叉
    else:
        strength -= 15       # 均线死叉
    # 突破
    recent_high = max(highs[-20:])
    recent_low  = min(lows[-20:])
    if price > recent_high * 0.98:
        strength += 20
    elif price < recent_low * 1.02:
        strength -= 20
    # 量能
    vol_ratio = np.mean(volumes[-5:]) / np.mean(volumes[-20:]) if np.mean(volumes[-20:]) > 0 else 1
    if vol_ratio > 2:
        strength += 10
    elif vol_ratio < 0.5:
        strength -= 10
    strength = max(0, min(100, strength))

    # 历史回调
    ath = max(highs)
    atl = min(lows)
    max_drawdown = (ath - price) / ath * 100 if ath > 0 else 0
    price_chg_week = (closes[-1] - closes[-7]) / closes[-7] * 100 if len(closes) >= 7 and closes[-7] > 0 else 0

    # 换手率（用成交量 / 近20日均量代理，非真实市值）
    # 对现货来说用量比作为代理
    turnover_proxy = vol_ratio * 10  # 粗略映射

    # 评分
    score = 0
    if strength > 60:
        score += 20
    if max_drawdown > 50 and price_chg_week > 0:
        score += 15
    if 0.5 < vol_ratio < 3:
        score += 10   # 换手健康代理
    if max_drawdown < 20:
        score -= 15
    if vol_ratio > 5:
        score -= 15   # 换手过高代理

    if score >= 40:
        return score, "推荐"
    elif score >= 20:
        return score, "观望"
    else:
        return score, "不推荐"


# ── 主回测流程 ──────────────────────────────────────────────────────

def run_historical_backtest(test_days_ago=30):
    print(f"\n{'='*60}")
    print(f"  历史回测：模拟 {test_days_ago} 天前的推荐，检验实际涨跌")
    print(f"{'='*60}\n")

    print("[1/3] 获取活跃 USDT 交易对...")
    pairs = get_all_usdt_pairs()
    print(f"      筛选出 {len(pairs)} 个交易对\n")

    print("[2/3] 拉取 K 线并评分...")
    results = []

    for i, p in enumerate(pairs, 1):
        klines = get_klines(p["pair"], limit=60)
        if len(klines) < test_days_ago + 10:
            continue

        # idx = 60 - test_days_ago 表示「test_days_ago 天前」时刻
        idx = len(klines) - test_days_ago
        score, rec = score_at_point(klines, idx)
        if rec is None:
            continue

        price_then  = klines[idx - 1][4]   # 推荐时收盘价
        price_3d    = klines[min(idx + 2, len(klines) - 1)][4]  # 3天后
        price_7d    = klines[min(idx + 6, len(klines) - 1)][4]  # 7天后

        ret_3d = (price_3d - price_then) / price_then * 100 if price_then > 0 else 0
        ret_7d = (price_7d - price_then) / price_then * 100 if price_then > 0 else 0

        results.append({
            "symbol":     p["symbol"],
            "score":      score,
            "rec":        rec,
            "ret_3d":     round(ret_3d, 2),
            "ret_7d":     round(ret_7d, 2),
            "win_3d":     ret_3d > 0,
            "win_7d":     ret_7d > 0,
        })

        if i % 20 == 0:
            print(f"      已处理 {i}/{len(pairs)}...")
        time.sleep(0.05)

    print(f"\n[3/3] 计算胜率...\n")

    # ── 输出结果 ─────────────────────────────────────────────────
    for group in ["推荐", "观望", "不推荐"]:
        g = [r for r in results if r["rec"] == group]
        if not g:
            continue
        win3 = sum(1 for r in g if r["win_3d"])
        win7 = sum(1 for r in g if r["win_7d"])
        avg3 = np.mean([r["ret_3d"] for r in g])
        avg7 = np.mean([r["ret_7d"] for r in g])
        print(f"  【{group}】 共 {len(g)} 只")
        print(f"    3日胜率: {win3}/{len(g)} = {win3/len(g)*100:.1f}%   平均收益: {avg3:+.2f}%")
        print(f"    7日胜率: {win7}/{len(g)} = {win7/len(g)*100:.1f}%   平均收益: {avg7:+.2f}%")
        # 最佳 / 最差
        best3 = max(g, key=lambda r: r["ret_3d"])
        worst3 = min(g, key=lambda r: r["ret_3d"])
        print(f"    3日最佳: {best3['symbol']} {best3['ret_3d']:+.1f}%  最差: {worst3['symbol']} {worst3['ret_3d']:+.1f}%")
        print()

    # ── 对比基准（全部等权持仓）──────────────────────────────
    all_avg3 = np.mean([r["ret_3d"] for r in results])
    all_avg7 = np.mean([r["ret_7d"] for r in results])
    all_win3 = sum(1 for r in results if r["win_3d"]) / len(results) * 100
    print(f"  【市场基准（全持仓等权）】")
    print(f"    3日胜率: {all_win3:.1f}%   平均收益: {all_avg3:+.2f}%")
    print(f"    7日平均: {all_avg7:+.2f}%")
    print()

    # ── 保存详情 ─────────────────────────────────────────────
    out_path = "data/historical_backtest.json"
    import os; os.makedirs("data", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({
            "run_at": datetime.now().isoformat(),
            "test_days_ago": test_days_ago,
            "total": len(results),
            "results": sorted(results, key=lambda r: r["ret_3d"], reverse=True),
        }, f, ensure_ascii=False, indent=2)
    print(f"  详细结果已保存到 {out_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_historical_backtest(test_days_ago=30)
