"""
回测模块 (Goal-Driven 框架)
- 保存每次推荐快照（代币、价格、时间）
- 定期检查推荐后 3/7 天的价格表现
- 计算胜率并输出报告
"""

import json
import os
import time
import requests
from datetime import datetime, timedelta

RECORD_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "backtest_records.json")
BINANCE_WEB3 = "https://web3.binance.com/bapi/defi/v4/public/wallet-direct/buw/wallet/market/token/dynamic/info"


def _ensure_data_dir():
    os.makedirs(os.path.dirname(RECORD_FILE), exist_ok=True)


def load_records():
    _ensure_data_dir()
    if not os.path.exists(RECORD_FILE):
        return []
    try:
        with open(RECORD_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_records(records):
    _ensure_data_dir()
    with open(RECORD_FILE, "w") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def record_recommendations(analysis_results):
    """把本次推荐快照追加到记录文件"""
    records = load_records()
    now = datetime.now().isoformat()

    for item in analysis_results:
        if item.get("recommendation") in ("推荐", "观望"):
            record = {
                "id": f"{item['symbol']}_{int(time.time())}",
                "symbol": item["symbol"],
                "name": item["name"],
                "chain_id": item.get("chain_id", ""),
                "contract": item.get("contract_address", ""),
                "price_at_rec": item.get("price", 0),
                "recommendation": item["recommendation"],
                "buy_score": item.get("buy_score", 0),
                "recorded_at": now,
                "checked_3d": False,
                "checked_7d": False,
                "return_3d": None,
                "return_7d": None,
            }
            records.append(record)

    save_records(records)
    return len(records)


def _get_current_price(chain_id, contract):
    """从 Binance Web3 API 取当前价格"""
    if not chain_id or not contract:
        return None
    try:
        resp = requests.get(
            BINANCE_WEB3,
            params={"chainId": chain_id, "contractAddress": contract},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") and data.get("data"):
                return float(data["data"].get("price", 0) or 0)
    except Exception:
        pass
    return None


def run_backtest_check():
    """检查到期记录的实际涨跌幅，更新文件，返回统计结果"""
    records = load_records()
    now = datetime.now()
    updated = 0

    for rec in records:
        try:
            rec_time = datetime.fromisoformat(rec["recorded_at"])
        except Exception:
            continue

        age_days = (now - rec_time).total_seconds() / 86400
        price_at_rec = rec.get("price_at_rec", 0)

        if price_at_rec <= 0:
            continue

        # 3 天检查
        if age_days >= 3 and not rec.get("checked_3d"):
            current = _get_current_price(rec.get("chain_id"), rec.get("contract"))
            if current and current > 0:
                rec["return_3d"] = round((current - price_at_rec) / price_at_rec * 100, 2)
                rec["checked_3d"] = True
                updated += 1

        # 7 天检查
        if age_days >= 7 and not rec.get("checked_7d"):
            current = _get_current_price(rec.get("chain_id"), rec.get("contract"))
            if current and current > 0:
                rec["return_7d"] = round((current - price_at_rec) / price_at_rec * 100, 2)
                rec["checked_7d"] = True
                updated += 1

    if updated > 0:
        save_records(records)

    return compute_stats(records)


def compute_stats(records=None):
    """计算胜率统计"""
    if records is None:
        records = load_records()

    stats = {
        "total_records": len(records),
        "recommend_count": 0,
        "watch_count": 0,
        # 3 天胜率
        "win_3d": 0, "lose_3d": 0, "winrate_3d": None,
        "avg_return_3d": None,
        # 7 天胜率
        "win_7d": 0, "lose_7d": 0, "winrate_7d": None,
        "avg_return_7d": None,
        "records": records[-50:],  # 最近 50 条
    }

    returns_3d, returns_7d = [], []

    for rec in records:
        if rec.get("recommendation") == "推荐":
            stats["recommend_count"] += 1
        elif rec.get("recommendation") == "观望":
            stats["watch_count"] += 1

        if rec.get("checked_3d") and rec.get("return_3d") is not None:
            r = rec["return_3d"]
            returns_3d.append(r)
            if r > 0:
                stats["win_3d"] += 1
            else:
                stats["lose_3d"] += 1

        if rec.get("checked_7d") and rec.get("return_7d") is not None:
            r = rec["return_7d"]
            returns_7d.append(r)
            if r > 0:
                stats["win_7d"] += 1
            else:
                stats["lose_7d"] += 1

    total_3d = stats["win_3d"] + stats["lose_3d"]
    total_7d = stats["win_7d"] + stats["lose_7d"]

    if total_3d > 0:
        stats["winrate_3d"] = round(stats["win_3d"] / total_3d * 100, 1)
        stats["avg_return_3d"] = round(sum(returns_3d) / len(returns_3d), 2)

    if total_7d > 0:
        stats["winrate_7d"] = round(stats["win_7d"] / total_7d * 100, 1)
        stats["avg_return_7d"] = round(sum(returns_7d) / len(returns_7d), 2)

    return stats
