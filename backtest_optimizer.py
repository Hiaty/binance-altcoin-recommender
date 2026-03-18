"""
Goal-Driven 权重优化器
======================
Goal    : 「推荐」组 3日胜率 ≥ 50%，且样本数 ≥ 5
Criteria: 在过去 30/20/10 天三个时间点的平均胜率
Subagent: run_backtest(weights) → win_rate
Master  : 随机搜索 + 爬山优化，不断迭代直到目标达成

新增：相对强弱过滤（RS Filter）
  只推荐「比 BTC 同期表现更强」的代币
"""

import requests
import numpy as np
import json, os, time, random
from datetime import datetime
from copy import deepcopy

SPOT_API = "https://api.binance.com/api/v3"
WEIGHTS_FILE = "data/best_weights.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

EXCLUDE = {
    "BTC","ETH","BNB","SOL","XRP","ADA","DOGE","MATIC","DOT","AVAX",
    "LINK","UNI","ATOM","LTC","BCH","ETC","SHIB","TRX","NEAR","APT",
    "USDT","USDC","BUSD","DAI","TUSD","FDUSD","USDP",
}

# ── 默认权重（与 analyzer.py 对齐）────────────────────────────────
DEFAULT_WEIGHTS = {
    "w_pattern":    20,   # 日线 K 线形态强度
    "w_weekly":     15,   # 周线方向
    "w_drawdown":   15,   # 历史回调充分+本周回升
    "w_turnover":   10,   # 换手健康
    "w_rs":         15,   # 相对强弱 vs BTC（新增）
    "w_overbought": -15,  # 涨幅过大惩罚
    "w_overtrade":  -15,  # 换手过高惩罚
    "thresh_rec":   40,   # 推荐阈值
    "thresh_watch": 20,   # 观望阈值
    "rs_min":       -5,   # 最低相对强弱（相对 BTC，低于此不推荐）
}

# ── 数据缓存（跑优化时复用，减少 API 调用）─────────────────────────
_cache = {}


def _fetch_klines(pair, limit=60):
    if pair in _cache:
        return _cache[pair]
    try:
        resp = requests.get(
            f"{SPOT_API}/klines",
            params={"symbol": pair, "interval": "1d", "limit": limit},
            headers=HEADERS, timeout=15,
        )
        if resp.status_code == 200:
            raw = resp.json()
            result = [[int(k[0]), float(k[1]), float(k[2]),
                       float(k[3]), float(k[4]), float(k[5])] for k in raw]
            _cache[pair] = result
            return result
    except Exception:
        pass
    return []


def _load_pairs():
    """获取活跃 USDT 交易对（带缓存）"""
    if "pairs" in _cache:
        return _cache["pairs"]
    resp = requests.get(f"{SPOT_API}/ticker/24hr", headers=HEADERS, timeout=30)
    pairs = []
    for t in resp.json():
        sym = t["symbol"]
        if not sym.endswith("USDT"):
            continue
        base = sym[:-4]
        if base in EXCLUDE:
            continue
        vol = float(t["quoteVolume"])
        if not (100_000 <= vol <= 500_000_000):
            continue
        pairs.append({"symbol": base, "pair": sym, "volume_usdt": vol})
    pairs.sort(key=lambda x: x["volume_usdt"], reverse=True)
    pairs = pairs[:150]
    _cache["pairs"] = pairs
    return pairs


# ── 评分函数（权重参数化）─────────────────────────────────────────

def score_token(history, btc_ret_3d, weights):
    """
    用历史 K 线 + BTC 同期收益率计算评分
    history: list of [ts,open,high,low,close,vol]，长度 ≥ 30
    btc_ret_3d: 同时段 BTC 3日涨幅（用于相对强弱）
    返回 (score, recommendation)
    """
    if len(history) < 30:
        return None, None

    closes  = [k[4] for k in history]
    highs   = [k[2] for k in history]
    lows    = [k[3] for k in history]
    volumes = [k[5] for k in history]
    price   = closes[-1]

    ma5  = np.mean(closes[-5:])
    ma20 = np.mean(closes[-20:])

    # K 线形态强度
    strength = 50
    recent = closes[-3:]
    if recent[0] < recent[1] < recent[2]:
        strength += 20
    elif recent[0] > recent[1] > recent[2]:
        strength -= 20
    if ma5 > ma20:
        strength += 15
    else:
        strength -= 15
    recent_high = max(highs[-20:])
    recent_low  = min(lows[-20:])
    if price > recent_high * 0.98:
        strength += 20
    elif price < recent_low * 1.02:
        strength -= 20
    vol_ratio = np.mean(volumes[-5:]) / (np.mean(volumes[-20:]) or 1)
    if vol_ratio > 2: strength += 10
    elif vol_ratio < 0.5: strength -= 10
    strength = max(0, min(100, strength))

    # 相对强弱：过去 7 天本币 vs BTC
    token_ret_7d = (closes[-1] - closes[-7]) / closes[-7] * 100 if len(closes) >= 7 and closes[-7] > 0 else 0
    rs = token_ret_7d - btc_ret_3d   # 相对收益

    # 历史回调
    ath = max(highs)
    drawdown = (ath - price) / ath * 100 if ath > 0 else 0
    chg_week = (closes[-1] - closes[-7]) / closes[-7] * 100 if len(closes) >= 7 and closes[-7] > 0 else 0

    # ── 评分计算 ──
    score = 0

    if strength > 60:
        score += weights["w_pattern"]
    if ma5 > ma20:
        score += weights["w_weekly"]
    if drawdown > 50 and chg_week > 0:
        score += weights["w_drawdown"]
    if 0.5 < vol_ratio < 3:
        score += weights["w_turnover"]

    # 相对强弱加分
    if rs > weights["rs_min"]:
        score += weights["w_rs"] * min(rs / 20, 1)   # 线性映射，最多满分
    else:
        score += weights["w_rs"] * (rs / 20)          # 可能为负

    # 惩罚
    if drawdown < 20:
        score += weights["w_overbought"]   # 负值
    if vol_ratio > 5:
        score += weights["w_overtrade"]    # 负值

    if score >= weights["thresh_rec"]:
        return score, "推荐"
    elif score >= weights["thresh_watch"]:
        return score, "观望"
    else:
        return score, "不推荐"


# ── 单次回测（给定权重，给定时间点）──────────────────────────────────

def run_backtest(weights, test_days_ago=30, verbose=False):
    """
    返回 {winrate_3d, winrate_7d, n_rec, avg_ret_3d, avg_ret_7d}
    """
    pairs   = _load_pairs()
    btc_kl  = _fetch_klines("BTCUSDT", 60)

    if len(btc_kl) < test_days_ago + 8:
        return None

    idx = len(btc_kl) - test_days_ago
    btc_price_then = btc_kl[idx - 1][4]
    btc_price_7d   = btc_kl[min(idx + 6, len(btc_kl) - 1)][4]
    btc_ret_7d     = (btc_price_7d - btc_price_then) / btc_price_then * 100

    results = []
    for p in pairs:
        klines = _fetch_klines(p["pair"], 60)
        if len(klines) < test_days_ago + 8:
            continue

        idx = len(klines) - test_days_ago
        if idx <= 0 or idx >= len(klines):
            continue

        history = klines[:idx]
        score, rec = score_token(history, btc_ret_7d, weights)
        if rec is None:
            continue

        price_then = klines[idx - 1][4]
        price_3d   = klines[min(idx + 2, len(klines) - 1)][4]
        price_7d   = klines[min(idx + 6, len(klines) - 1)][4]
        ret_3d = (price_3d - price_then) / price_then * 100 if price_then > 0 else 0
        ret_7d = (price_7d - price_then) / price_then * 100 if price_then > 0 else 0

        results.append({"rec": rec, "ret_3d": ret_3d, "ret_7d": ret_7d})

    rec_group = [r for r in results if r["rec"] == "推荐"]
    if len(rec_group) < 3:
        return {"winrate_3d": 0, "winrate_7d": 0, "n_rec": len(rec_group),
                "avg_ret_3d": 0, "avg_ret_7d": 0}

    win3 = sum(1 for r in rec_group if r["ret_3d"] > 0)
    win7 = sum(1 for r in rec_group if r["ret_7d"] > 0)
    wr3  = win3 / len(rec_group) * 100
    wr7  = win7 / len(rec_group) * 100
    avg3 = np.mean([r["ret_3d"] for r in rec_group])
    avg7 = np.mean([r["ret_7d"] for r in rec_group])

    if verbose:
        print(f"    推荐 {len(rec_group)} 只  3日胜率={wr3:.1f}%({win3}/{len(rec_group)})  "
              f"avg={avg3:+.2f}%  7日胜率={wr7:.1f}%  avg={avg7:+.2f}%")

    return {"winrate_3d": wr3, "winrate_7d": wr7, "n_rec": len(rec_group),
            "avg_ret_3d": avg3, "avg_ret_7d": avg7}


def multi_point_score(weights):
    """
    在 10/20/30 天三个时间点各跑一次回测，取平均胜率作为优化目标
    （Goal-Driven Criteria：平均 3日胜率）
    """
    total, count = 0, 0
    for days in [10, 20, 30]:
        r = run_backtest(weights, test_days_ago=days)
        if r and r["n_rec"] >= 3:
            total += r["winrate_3d"]
            count += 1
    return total / count if count > 0 else 0


# ── Goal-Driven 优化主循环 ─────────────────────────────────────────

def mutate(weights, scale=0.3):
    """随机扰动权重"""
    w = deepcopy(weights)
    key = random.choice([
        "w_pattern","w_weekly","w_drawdown","w_turnover",
        "w_rs","w_overbought","w_overtrade","thresh_rec","rs_min"
    ])
    if key in ("thresh_rec",):
        w[key] = int(np.clip(w[key] + random.randint(-8, 8), 20, 60))
    elif key in ("rs_min",):
        w[key] = round(w[key] + random.uniform(-5, 5), 1)
    elif key in ("w_overbought","w_overtrade"):
        w[key] = int(np.clip(w[key] + random.randint(-5, 5), -30, 0))
    else:
        w[key] = int(np.clip(w[key] + random.randint(-8, 8), 0, 30))
    return w


def optimize(goal_winrate=50, max_iterations=60):
    os.makedirs("data", exist_ok=True)
    print(f"\n{'='*60}")
    print(f"  Goal-Driven 权重优化器")
    print(f"  Goal    : 推荐组 3日平均胜率 ≥ {goal_winrate}%")
    print(f"  Criteria: 在 10/20/30 天三个时间点的平均胜率")
    print(f"  Max Iter: {max_iterations}")
    print(f"{'='*60}\n")

    print("[预热] 加载市场数据（约30秒）...")
    _load_pairs()
    _fetch_klines("BTCUSDT", 60)
    pairs = _cache["pairs"]
    for i, p in enumerate(pairs, 1):
        _fetch_klines(p["pair"], 60)
        if i % 30 == 0:
            print(f"  缓存 {i}/{len(pairs)} 条K线...")
        time.sleep(0.04)
    print(f"  数据缓存完毕，共 {len(_cache)-2} 只币\n")

    # ── 初始评估 ──
    best_weights = deepcopy(DEFAULT_WEIGHTS)
    best_score   = multi_point_score(best_weights)
    print(f"[初始权重] 平均胜率 = {best_score:.1f}%")
    print(f"  weights = {best_weights}\n")

    history_log = [{"iter": 0, "winrate": best_score, "weights": deepcopy(best_weights)}]

    # ── Master 监督循环 ──
    for i in range(1, max_iterations + 1):
        # 每 10 轮做一次大幅随机扰动（跳出局部最优）
        if i % 10 == 0:
            candidate = deepcopy(DEFAULT_WEIGHTS)
            for _ in range(4):
                candidate = mutate(candidate, scale=0.5)
            label = "🌊随机跳跃"
        else:
            candidate = mutate(best_weights)
            label = "🔧爬山"

        score = multi_point_score(candidate)

        improved = score > best_score
        if improved:
            best_score   = score
            best_weights = deepcopy(candidate)

        mark = "✅" if improved else "  "
        print(f"[{i:3d}/{max_iterations}] {label}  胜率={score:.1f}%  最佳={best_score:.1f}%  "
              f"推荐阈值={candidate['thresh_rec']}  RS权重={candidate['w_rs']}  {mark}")

        history_log.append({"iter": i, "winrate": score, "weights": deepcopy(candidate)})

        # ── Criteria 检查 ──
        if best_score >= goal_winrate:
            print(f"\n🎯 目标达成！平均胜率 {best_score:.1f}% ≥ {goal_winrate}%")
            break

        time.sleep(0.1)

    # ── 输出最终结果 ──
    print(f"\n{'='*60}")
    print(f"  优化完成  最终平均胜率: {best_score:.1f}%")
    print(f"{'='*60}")
    print("\n最优权重：")
    for k, v in best_weights.items():
        orig = DEFAULT_WEIGHTS[k]
        diff = v - orig
        arrow = f"  ({'+' if diff>=0 else ''}{diff})" if diff != 0 else ""
        print(f"  {k:20s}: {v}{arrow}")

    # ── 详细回测报告 ──
    print("\n最优权重详细验证：")
    for days in [10, 20, 30]:
        r = run_backtest(best_weights, test_days_ago=days, verbose=False)
        if r:
            print(f"  {days}天前: 推荐{r['n_rec']}只  "
                  f"3日胜率={r['winrate_3d']:.1f}%({r['avg_ret_3d']:+.2f}%)  "
                  f"7日胜率={r['winrate_7d']:.1f}%({r['avg_ret_7d']:+.2f}%)")

    # ── 保存最优权重 ──
    output = {
        "optimized_at": datetime.now().isoformat(),
        "best_winrate": round(best_score, 2),
        "goal_winrate": goal_winrate,
        "iterations":   len(history_log),
        "weights":      best_weights,
        "history":      history_log[-20:],   # 保留最后20条
    }
    with open(WEIGHTS_FILE, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 最优权重已保存到 {WEIGHTS_FILE}")
    print("   analyzer.py 将在下次分析时自动加载这些权重\n")

    return best_weights, best_score


if __name__ == "__main__":
    optimize(goal_winrate=50, max_iterations=60)
