"""
币安山寨币智能推荐系统 - 分析模块 v2
改进：
  B. 加入市场情绪因子（BTC 趋势 + Fear & Greed）
"""

import numpy as np
from datetime import datetime


def analyze_kline_pattern(klines):
    """分析 K 线形态，返回 pattern/strength/trend/volume_ratio"""
    if not klines or len(klines) < 20:
        return {"pattern": "数据不足", "strength": 50, "trend": "未知", "volume_ratio": 1}

    closes  = [c[3] for c in klines]
    highs   = [c[1] for c in klines]
    lows    = [c[2] for c in klines]
    volumes = [c[4] for c in klines]

    ma5  = np.mean(closes[-5:])  if len(closes) >= 5  else closes[-1]
    ma10 = np.mean(closes[-10:]) if len(closes) >= 10 else closes[-1]
    ma20 = np.mean(closes[-20:]) if len(closes) >= 20 else closes[-1]

    trend = "上涨" if ma5 > ma10 > ma20 else "下跌" if ma5 < ma10 < ma20 else "震荡"

    patterns = []
    recent = closes[-3:]
    if len(recent) >= 3:
        if all(recent[i] > recent[i - 1] for i in range(1, len(recent))):
            patterns.append("三连阳")
        elif all(recent[i] < recent[i - 1] for i in range(1, len(recent))):
            patterns.append("三连阴")

    if ma5 > ma20:
        patterns.append("均线金叉")
    elif ma5 < ma20:
        patterns.append("均线死叉")

    recent_high = max(highs[-20:])
    recent_low  = min(lows[-20:])
    current     = closes[-1]

    if current > recent_high * 0.98:
        patterns.append("突破新高")
    elif current < recent_low * 1.02:
        patterns.append("跌破新低")

    recent_vol = np.mean(volumes[-5:])
    avg_vol    = np.mean(volumes[-20:])
    vol_ratio  = recent_vol / avg_vol if avg_vol > 0 else 1

    if vol_ratio > 2:
        patterns.append("放量")
    elif vol_ratio < 0.5:
        patterns.append("缩量")

    strength = 50
    if "三连阳" in patterns or "突破新高" in patterns:
        strength += 20
    if "均线金叉" in patterns:
        strength += 15
    if "放量" in patterns:
        strength += 10
    if "三连阴" in patterns or "跌破新低" in patterns:
        strength -= 20
    if "均线死叉" in patterns:
        strength -= 15

    return {
        "pattern": ", ".join(patterns) if patterns else trend,
        "strength": max(0, min(100, strength)),
        "trend": trend,
        "volume_ratio": vol_ratio,
    }


def analyze_token(token_data, sentiment=None):
    """
    分析单个代币
    sentiment: get_market_sentiment() 的返回值（可选）
    """
    symbol       = token_data.get("symbol", "Unknown")
    name         = token_data.get("name", "Unknown")
    price        = token_data.get("price", 0)
    market_cap   = token_data.get("market_cap") or token_data.get("marketCap", 0)
    volume_24h   = token_data.get("volume_24h") or token_data.get("volume24h", 0)
    change_24h   = token_data.get("change_24h") or token_data.get("percentChange24h", 0)
    holders_top10 = token_data.get("holders_top10") or token_data.get("holdersTop10Percent", 0)
    chain_id     = token_data.get("chain_id") or token_data.get("chainId", "")
    contract     = token_data.get("contract_address") or token_data.get("contractAddress", "")

    dynamic       = token_data.get("dynamic") or {}
    klines_daily  = token_data.get("klines_daily") or []
    klines_weekly = token_data.get("klines_weekly") or []

    turnover_rate  = (volume_24h / market_cap * 100) if market_cap > 0 else 0
    max_drawdown   = 0
    max_rebound    = 0
    price_chg_week = 0
    price_chg_month = 0

    if klines_daily and len(klines_daily) >= 30:
        closes = [c[3] for c in klines_daily]
        highs  = [c[1] for c in klines_daily]
        lows   = [c[2] for c in klines_daily]

        ath = max(highs)
        atl = min(lows)
        max_drawdown  = (ath - price) / ath * 100 if ath > 0 else 0
        max_rebound   = (price - atl) / atl * 100 if atl > 0 else 0

        if len(closes) >= 7:
            price_chg_week  = (closes[-1] - closes[-7])  / closes[-7]  * 100 if closes[-7]  > 0 else 0
        if len(closes) >= 30:
            price_chg_month = (closes[-1] - closes[-30]) / closes[-30] * 100 if closes[-30] > 0 else 0

    volume_buy  = float(dynamic.get("volume24hBuy",  0) or 0)
    volume_sell = float(dynamic.get("volume24hSell", 0) or 0)
    net_inflow  = volume_buy - volume_sell

    daily_pattern  = analyze_kline_pattern(klines_daily)
    weekly_pattern = analyze_kline_pattern(klines_weekly)

    # ── 强庄币识别 ──
    whale_signals = []
    if holders_top10 > 80:
        whale_signals.append("高度控盘")
    if turnover_rate > 50 and change_24h > 20:
        whale_signals.append("放量拉升")
    if max_drawdown > 70 and price_chg_week > 30:
        whale_signals.append("深V反弹")
    is_whale = len(whale_signals) >= 2

    # ── 基础评分 ──
    buy_score     = 0
    buy_reasons   = []
    not_buy_reasons = []

    if daily_pattern["strength"] > 60:
        buy_score += 20
        buy_reasons.append("日线强势")
    if weekly_pattern["strength"] > 60:
        buy_score += 15
        buy_reasons.append("周线向好")
    if max_drawdown > 50 and price_chg_week > 0:
        buy_score += 15
        buy_reasons.append("回调充分")
    if 5 < turnover_rate < 50:
        buy_score += 10
        buy_reasons.append("换手健康")
    if net_inflow > 0:
        buy_score += 10
        buy_reasons.append("资金流入")
    if holders_top10 < 70:
        buy_score += 10
        buy_reasons.append("筹码分散")

    if max_drawdown < 20:
        buy_score -= 15
        not_buy_reasons.append("涨幅过大")
    if holders_top10 > 90:
        buy_score -= 20
        not_buy_reasons.append("高度控盘")
    if turnover_rate > 100:
        buy_score -= 15
        not_buy_reasons.append("换手过高")

    # ── B. 市场情绪叠加 ──
    sentiment_note = ""
    if sentiment:
        adjust = sentiment.get("score_adjust", 0)
        buy_score += adjust

        btc = sentiment.get("btc", {})
        fg  = sentiment.get("fear_greed", {})
        btc_chg = btc.get("change_24h", 0)
        fg_val  = fg.get("value", 50)

        # 大盘暴跌时标记
        if btc_chg < -8:
            not_buy_reasons.append(f"BTC暴跌{btc_chg:.1f}%")
            sentiment_note = f"⚠️市场恐慌(BTC {btc_chg:.1f}%)"
        elif btc_chg < -2:
            sentiment_note = f"BTC偏弱({btc_chg:.1f}%)"
        elif btc_chg > 3:
            sentiment_note = f"BTC向好(+{btc_chg:.1f}%)"

        if fg_val <= 20:
            sentiment_note += f" | 极度恐惧({fg_val})"
        elif fg_val >= 80:
            sentiment_note += f" | 极度贪婪({fg_val})"

    buy_score = max(-30, min(80, buy_score))

    # ── 最终推荐 ──
    # 大盘暴跌时，把所有"推荐"降为"观望"
    market_ok = sentiment.get("market_ok", True) if sentiment else True

    if buy_score >= 40 and market_ok:
        recommendation = "推荐"
    elif buy_score >= 20:
        recommendation = "观望"
    else:
        recommendation = "不推荐"

    # ── 分析点评 ──
    analysis = f"【{daily_pattern['pattern']}】"
    if is_whale:
        analysis += f"强庄: {';'.join(whale_signals)}。"
    else:
        analysis += "暂无强庄迹象。"
    if buy_reasons:
        analysis += f"优势: {';'.join(buy_reasons[:2])}。"
    if not_buy_reasons:
        analysis += f"风险: {';'.join(not_buy_reasons[:1])}。"
    if sentiment_note:
        analysis += f" [{sentiment_note}]"

    return {
        "symbol":         symbol,
        "name":           name,
        "price":          price,
        "market_cap":     market_cap,
        "chain_id":       chain_id,
        "contract_address": contract,
        "max_drawdown":   round(max_drawdown, 1),
        "max_rebound":    round(max_rebound, 1),
        "turnover_rate":  round(turnover_rate, 2),
        "week_change":    round(price_chg_week, 1),
        "month_change":   round(price_chg_month, 1),
        "concentration":  round(holders_top10, 1),
        "net_inflow":     round(net_inflow, 2),
        "daily_pattern":  daily_pattern["pattern"],
        "weekly_pattern": weekly_pattern["pattern"],
        "pattern_strength": daily_pattern["strength"],
        "analysis":       analysis,
        "is_whale":       is_whale,
        "whale_signals":  whale_signals,
        "recommendation": recommendation,
        "buy_score":      buy_score,
        "kline_source":   token_data.get("kline_source", "sintral"),
    }


def analyze_all(tokens_data, sentiment=None):
    """分析所有代币，注入情绪因子"""
    results = []
    for token in tokens_data:
        result = analyze_token(token, sentiment)
        results.append(result)

    results.sort(key=lambda x: x["market_cap"])
    for i, item in enumerate(results, 1):
        item["rank"] = i

    return results
