"""
市场情绪模块
- Fear & Greed Index (alternative.me)
- BTC 24h 趋势 (Binance 官方 API)
"""

import requests

BINANCE_API = "https://api.binance.com/api/v3"
FEAR_GREED_API = "https://api.alternative.me/fng/"


def get_fear_greed():
    """获取 Fear & Greed Index (0=极度恐惧, 100=极度贪婪)"""
    try:
        resp = requests.get(FEAR_GREED_API, params={"limit": 1}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            item = data["data"][0]
            return {
                "value": int(item["value"]),
                "label": item["value_classification"],  # 英文标签
                "label_cn": _translate_fg(item["value_classification"]),
            }
    except Exception as e:
        print(f"Fear & Greed 获取失败: {e}")
    return {"value": 50, "label": "Neutral", "label_cn": "中性"}


def get_btc_trend():
    """获取 BTC 24h 涨跌幅及均线趋势"""
    try:
        # 24h ticker
        ticker = requests.get(
            f"{BINANCE_API}/ticker/24hr", params={"symbol": "BTCUSDT"}, timeout=10
        ).json()
        change_24h = float(ticker["priceChangePercent"])
        price = float(ticker["lastPrice"])

        # 近 7 天日线 K 线
        klines = requests.get(
            f"{BINANCE_API}/klines",
            params={"symbol": "BTCUSDT", "interval": "1d", "limit": 7},
            timeout=10,
        ).json()
        closes = [float(k[4]) for k in klines]
        ma7 = sum(closes) / len(closes) if closes else price
        trend = "up" if price > ma7 else "down"

        return {
            "price": price,
            "change_24h": change_24h,
            "ma7": ma7,
            "trend": trend,
        }
    except Exception as e:
        print(f"BTC 数据获取失败: {e}")
    return {"price": 0, "change_24h": 0, "ma7": 0, "trend": "unknown"}


def get_market_sentiment():
    """合并返回市场情绪数据"""
    fg = get_fear_greed()
    btc = get_btc_trend()

    # 情绪得分调整因子（-20 ~ +20），用于叠加到币种评分
    score_adjust = 0

    # BTC 当天跌超 5% → 整体扣分
    if btc["change_24h"] < -5:
        score_adjust -= 15
    elif btc["change_24h"] < -2:
        score_adjust -= 8
    elif btc["change_24h"] > 5:
        score_adjust += 10
    elif btc["change_24h"] > 2:
        score_adjust += 5

    # Fear & Greed 极端值调整
    if fg["value"] <= 20:   # 极度恐惧 → 可能是买入机会
        score_adjust += 10
    elif fg["value"] >= 80:  # 极度贪婪 → 风险高
        score_adjust -= 10

    return {
        "fear_greed": fg,
        "btc": btc,
        "score_adjust": score_adjust,
        "market_ok": btc["change_24h"] > -8,  # BTC 跌超 8% 时不建议任何买入
    }


def _translate_fg(label):
    mapping = {
        "Extreme Fear": "极度恐惧",
        "Fear": "恐惧",
        "Neutral": "中性",
        "Greed": "贪婪",
        "Extreme Greed": "极度贪婪",
    }
    return mapping.get(label, label)
