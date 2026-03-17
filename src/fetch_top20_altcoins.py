import requests
import json
import time
from datetime import datetime, timedelta

# API端点
SEARCH_URL = "https://web3.binance.com/bapi/defi/v5/public/wallet-direct/buw/wallet/market/token/search"
DYNAMIC_URL = "https://web3.binance.com/bapi/defi/v4/public/wallet-direct/buw/wallet/market/token/dynamic/info"
KLINE_URL = "https://dquery.sintral.io/u-kline/v1/k-line/candles"

headers = {
    "Accept-Encoding": "identity",
    "User-Agent": "binance-web3/1.0 (Skill)"
}

def search_tokens(keyword="", chain_ids="56,8453,CT_501", order_by="volume24h"):
    params = {"keyword": keyword, "chainIds": chain_ids, "orderBy": order_by}
    try:
        response = requests.get(SEARCH_URL, params=params, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data"):
                return data["data"]
    except Exception as e:
        print(f"搜索失败: {e}")
    return []

def get_dynamic_data(chain_id, contract_address):
    params = {"chainId": chain_id, "contractAddress": contract_address}
    try:
        response = requests.get(DYNAMIC_URL, params=params, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data"):
                return data["data"]
    except Exception as e:
        print(f"获取动态数据失败: {e}")
    return None

def get_kline_data(address, platform, interval="1d", limit=200):
    params = {"address": address, "platform": platform, "interval": interval, "limit": limit}
    try:
        response = requests.get(KLINE_URL, params=params, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                return data["data"]
    except Exception as e:
        print(f"获取K线失败: {e}")
    return []

def get_platform(chain_id):
    mapping = {"56": "bsc", "8453": "base", "CT_501": "solana"}
    return mapping.get(chain_id, "bsc")

# 获取3000万以上的活跃代币
print("正在搜索市值3000万以上的活跃山寨币...")
all_tokens = []
keywords = ["ai", "meme", "game", "dao", "meta", "nft", "defi", "swap", "pepe", "doge", "elon", "shib", "cat", "frog"]

for kw in keywords:
    tokens = search_tokens(keyword=kw, order_by="marketCap")
    for token in tokens:
        market_cap_str = token.get("marketCap")
        if market_cap_str is None:
            continue
        try:
            market_cap = float(market_cap_str)
        except (ValueError, TypeError):
            continue
        
        volume_24h = float(token.get("volume24h") or 0)
        change_24h = float(token.get("percentChange24h") or 0)
        
        # 条件：市值3000万以上，24h交易量>50万，不是死币
        if market_cap >= 30000000 and volume_24h > 500000 and change_24h > -50:
            token_info = {
                "name": token.get("name"),
                "symbol": token.get("symbol"),
                "chainId": token.get("chainId"),
                "contractAddress": token.get("contractAddress"),
                "price": float(token.get("price") or 0),
                "marketCap": market_cap,
                "volume24h": volume_24h,
                "percentChange24h": change_24h,
                "holdersTop10Percent": float(token.get("holdersTop10Percent") or 0),
                "liquidity": float(token.get("liquidity") or 0)
            }
            if not any(t["contractAddress"] == token_info["contractAddress"] for t in all_tokens):
                all_tokens.append(token_info)
    time.sleep(0.2)

# 按市值排序，取最低的20个
all_tokens.sort(key=lambda x: x["marketCap"])
selected_tokens = all_tokens[:20]

print(f"\n找到 {len(selected_tokens)} 个符合条件的代币")
print("\n正在获取详细数据（包括K线分析）...")

# 获取每个代币的详细数据
results = []
for i, token in enumerate(selected_tokens, 1):
    print(f"[{i}/20] 分析 {token['symbol']} - 市值: ${token['marketCap']/10000:.1f}万")
    
    dynamic = get_dynamic_data(token["chainId"], token["contractAddress"])
    platform = get_platform(token["chainId"])
    
    # 获取日线和周线K线
    klines_daily = get_kline_data(token["contractAddress"], platform, interval="1d", limit=200)
    klines_weekly = get_kline_data(token["contractAddress"], platform, interval="1w", limit=50)
    
    result = {
        **token,
        "dynamic": dynamic,
        "klines_daily": klines_daily,
        "klines_weekly": klines_weekly
    }
    results.append(result)
    time.sleep(0.3)

# 保存数据
with open("top20_altcoins_data.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n[OK] 数据已保存到 top20_altcoins_data.json")
print(f"共分析 {len(results)} 个代币")
