import json
import numpy as np
from datetime import datetime

# 读取数据
with open("top20_altcoins_data.json", "r", encoding="utf-8") as f:
    tokens = json.load(f)

def analyze_kline_pattern(klines):
    """分析K线形态"""
    if not klines or len(klines) < 20:
        return {"pattern": "数据不足", "strength": 0}
    
    closes = [c[3] for c in klines]
    highs = [c[1] for c in klines]
    lows = [c[2] for c in klines]
    volumes = [c[4] for c in klines]
    
    # 计算均线
    ma5 = np.mean(closes[-5:]) if len(closes) >= 5 else closes[-1]
    ma10 = np.mean(closes[-10:]) if len(closes) >= 10 else closes[-1]
    ma20 = np.mean(closes[-20:]) if len(closes) >= 20 else closes[-1]
    
    # 趋势判断
    trend = "上涨" if ma5 > ma10 > ma20 else "下跌" if ma5 < ma10 < ma20 else "震荡"
    
    # 形态识别
    patterns = []
    
    # 最近3根K线
    recent = closes[-3:]
    if len(recent) >= 3:
        # 三连阳
        if all(recent[i] > recent[i-1] for i in range(1, len(recent))):
            patterns.append("三连阳")
        # 三连阴
        elif all(recent[i] < recent[i-1] for i in range(1, len(recent))):
            patterns.append("三连阴")
    
    # 金叉/死叉
    if ma5 > ma20 and len(closes) > 5:
        patterns.append("均线金叉")
    elif ma5 < ma20:
        patterns.append("均线死叉")
    
    # 突破形态
    recent_high = max(highs[-20:])
    recent_low = min(lows[-20:])
    current = closes[-1]
    
    if current > recent_high * 0.98:
        patterns.append("突破新高")
    elif current < recent_low * 1.02:
        patterns.append("跌破新低")
    
    # 量能分析
    recent_volume = np.mean(volumes[-5:])
    avg_volume = np.mean(volumes[-20:])
    volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
    
    if volume_ratio > 2:
        patterns.append("放量")
    elif volume_ratio < 0.5:
        patterns.append("缩量")
    
    # 计算强度分数 (0-100)
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
    
    strength = max(0, min(100, strength))
    
    return {
        "pattern": ", ".join(patterns) if patterns else trend,
        "strength": strength,
        "trend": trend,
        "volume_ratio": volume_ratio
    }

# 分析每个代币
analysis_results = []

for token in tokens:
    symbol = token.get("symbol", "Unknown")
    name = token.get("name", "Unknown")
    price = token.get("price", 0)
    market_cap = token.get("marketCap", 0)
    volume_24h = token.get("volume24h", 0)
    change_24h = token.get("percentChange24h", 0)
    holders_top10 = token.get("holdersTop10Percent", 0)
    liquidity = token.get("liquidity", 0)
    
    dynamic = token.get("dynamic", {}) or {}
    klines_daily = token.get("klines_daily", []) or []
    klines_weekly = token.get("klines_weekly", []) or []
    
    # 1. 换手率
    turnover_rate = (volume_24h / market_cap * 100) if market_cap > 0 else 0
    
    # 2. 历史最大回调和底部反弹
    max_drawdown = 0
    max_rebound = 0
    price_change_week = 0
    price_change_month = 0
    
    if klines_daily and len(klines_daily) >= 30:
        closes = [c[3] for c in klines_daily]
        highs = [c[1] for c in klines_daily]
        lows = [c[2] for c in klines_daily]
        
        # 历史最高和最低
        all_time_high = max(highs)
        all_time_low = min(lows)
        
        # 从最高点回调
        max_drawdown = ((all_time_high - price) / all_time_high * 100) if all_time_high > 0 else 0
        
        # 从底部反弹
        max_rebound = ((price - all_time_low) / all_time_low * 100) if all_time_low > 0 else 0
        
        # 本周和本月涨跌
        if len(closes) >= 7:
            price_change_week = ((closes[-1] - closes[-7]) / closes[-7] * 100) if closes[-7] > 0 else 0
        if len(closes) >= 30:
            price_change_month = ((closes[-1] - closes[-30]) / closes[-30] * 100) if closes[-30] > 0 else 0
    
    # 3. 资金净流入
    volume_buy = float(dynamic.get("volume24hBuy", 0)) if dynamic else 0
    volume_sell = float(dynamic.get("volume24hSell", 0)) if dynamic else 0
    net_inflow = volume_buy - volume_sell
    
    # 4. K线形态分析
    daily_pattern = analyze_kline_pattern(klines_daily)
    weekly_pattern = analyze_kline_pattern(klines_weekly)
    
    # 5. 是否强庄币判断
    whale_signals = []
    if holders_top10 > 80:
        whale_signals.append("高度控盘")
    if turnover_rate > 50 and change_24h > 20:
        whale_signals.append("放量拉升")
    if max_drawdown > 70 and price_change_week > 30:
        whale_signals.append("深V反弹")
    if net_inflow > market_cap * 0.1:
        whale_signals.append("大额流入")
    
    is_whale_coin = len(whale_signals) >= 2
    
    # 6. 是否推荐购买
    buy_score = 0
    buy_reasons = []
    not_buy_reasons = []
    
    # 加分项
    if daily_pattern["strength"] > 60:
        buy_score += 20
        buy_reasons.append("日线强势")
    if weekly_pattern["strength"] > 60:
        buy_score += 15
        buy_reasons.append("周线向好")
    if max_drawdown > 50 and price_change_week > 0:
        buy_score += 15
        buy_reasons.append("回调充分")
    if turnover_rate > 5 and turnover_rate < 50:
        buy_score += 10
        buy_reasons.append("换手健康")
    if net_inflow > 0:
        buy_score += 10
        buy_reasons.append("资金流入")
    if holders_top10 < 70:
        buy_score += 10
        buy_reasons.append("筹码分散")
    
    # 减分项
    if max_drawdown < 20:
        buy_score -= 15
        not_buy_reasons.append("涨幅过大")
    if holders_top10 > 90:
        buy_score -= 20
        not_buy_reasons.append("高度控盘")
    if turnover_rate > 100:
        buy_score -= 15
        not_buy_reasons.append("换手过高")
    if daily_pattern["strength"] < 30:
        buy_score -= 20
        not_buy_reasons.append("趋势弱势")
    if price_change_month > 200:
        buy_score -= 15
        not_buy_reasons.append("月涨幅过大")
    
    # 最终推荐
    if buy_score >= 40:
        recommendation = "推荐"
        rec_color = "green"
    elif buy_score >= 20:
        recommendation = "观望"
        rec_color = "yellow"
    else:
        recommendation = "不推荐"
        rec_color = "red"
    
    # 7. 币种分析点评
    analysis_comment = f"【{daily_pattern['pattern']}】"
    if is_whale_coin:
        analysis_comment += f"强庄特征: {';'.join(whale_signals)}。"
    else:
        analysis_comment += "暂无强庄控盘迹象。"
    
    if buy_reasons:
        analysis_comment += f"优势: {';'.join(buy_reasons[:2])}。"
    if not_buy_reasons:
        analysis_comment += f"风险: {';'.join(not_buy_reasons[:2])}。"
    
    result = {
        "rank": 0,  # 稍后填充
        "symbol": symbol,
        "name": name,
        "market_cap": market_cap,
        "price": price,
        "max_drawdown": max_drawdown,
        "max_rebound": max_rebound,
        "turnover_rate": turnover_rate,
        "week_change": price_change_week,
        "month_change": price_change_month,
        "concentration": holders_top10,
        "net_inflow": net_inflow,
        "daily_pattern": daily_pattern["pattern"],
        "weekly_pattern": weekly_pattern["pattern"],
        "pattern_strength": daily_pattern["strength"],
        "analysis": analysis_comment,
        "is_whale": is_whale_coin,
        "whale_signals": whale_signals,
        "recommendation": recommendation,
        "rec_color": rec_color,
        "buy_score": buy_score
    }
    analysis_results.append(result)

# 按市值排序并填充排名
analysis_results.sort(key=lambda x: x["market_cap"])
for i, r in enumerate(analysis_results, 1):
    r["rank"] = i

# 保存分析结果
with open("altcoin_analysis_results.json", "w", encoding="utf-8") as f:
    json.dump(analysis_results, f, ensure_ascii=False, indent=2)

print(f"[OK] 分析完成，共 {len(analysis_results)} 个代币")
print("\n推荐分布:")
print(f"  推荐: {sum(1 for r in analysis_results if r['recommendation'] == '推荐')} 个")
print(f"  观望: {sum(1 for r in analysis_results if r['recommendation'] == '观望')} 个")
print(f"  不推荐: {sum(1 for r in analysis_results if r['recommendation'] == '不推荐')} 个")
