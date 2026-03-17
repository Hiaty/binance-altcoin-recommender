"""
币安山寨币智能推荐系统 - 数据抓取模块
调用币安Web3 API获取实时数据
"""

import requests
import json
import time
from datetime import datetime

# API配置
BASE_URL = "https://web3.binance.com"
HEADERS = {
    "Accept-Encoding": "identity",
    "User-Agent": "binance-web3/1.0 (Skill)"
}

def search_tokens(keyword="", chain_ids="56,8453,CT_501", order_by="volume24h"):
    """搜索代币"""
    url = f"{BASE_URL}/bapi/defi/v5/public/wallet-direct/buw/wallet/market/token/search"
    params = {
        "keyword": keyword,
        "chainIds": chain_ids,
        "orderBy": order_by
    }
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data"):
                return data["data"]
    except Exception as e:
        print(f"搜索失败: {e}")
    
    return []

def get_dynamic_data(chain_id, contract_address):
    """获取代币动态数据"""
    url = f"{BASE_URL}/bapi/defi/v4/public/wallet-direct/buw/wallet/market/token/dynamic/info"
    params = {
        "chainId": chain_id,
        "contractAddress": contract_address
    }
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data"):
                return data["data"]
    except Exception as e:
        print(f"获取动态数据失败: {e}")
    
    return None

def get_kline_data(address, platform, interval="1d", limit=200):
    """获取K线数据"""
    url = "https://dquery.sintral.io/u-kline/v1/k-line/candles"
    params = {
        "address": address,
        "platform": platform,
        "interval": interval,
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                return data["data"]
    except Exception as e:
        print(f"获取K线失败: {e}")
    
    return []

def get_platform(chain_id):
    """链ID转平台名"""
    mapping = {
        "56": "bsc",
        "8453": "base",
        "CT_501": "solana"
    }
    return mapping.get(chain_id, "bsc")

def fetch_altcoins(min_market_cap=30000000, count=20):
    """
    抓取山寨币数据
    
    Args:
        min_market_cap: 最小市值（默认3000万）
        count: 返回数量（默认20个）
    
    Returns:
        list: 币种数据列表
    """
    print(f"正在抓取市值{min_market_cap/10000:.0f}万~10亿的活跃山寨币...")
    
    all_tokens = []
    keywords = ["ai", "meme", "game", "dao", "meta", "nft", "defi", "swap", "pepe", "doge", 
                "cat", "frog", "elon", "shib", "moon", "rocket", "baby", "fair", "safe",
                "token", "coin", "crypto", "web3", "chain", "finance", "money"]
    
    for kw in keywords:
        tokens = search_tokens(keyword=kw, order_by="volume24h")
        
        for token in tokens:
            market_cap_str = token.get("marketCap")
            if not market_cap_str:
                continue
            
            try:
                market_cap = float(market_cap_str)
            except:
                continue
            
            volume_24h = float(token.get("volume24h") or 0)
            change_24h = float(token.get("percentChange24h") or 0)
            liquidity = float(token.get("liquidity") or 0)
            
            # 筛选条件
            # 市值范围：min_market_cap 到 10亿（排除BTC、ETH等大市值币种）
            max_market_cap = 1000000000  # 10亿上限
            
            # 流动性筛选条件（排除死币）：
            # 1. 24h交易量 > 50万
            # 2. 流动性 > 10万
            # 3. 24h涨跌幅在 -90% ~ +1000% 之间（排除极端情况）
            min_volume = 500000  # 50万
            min_liquidity = 100000  # 10万
            
            is_active = (
                min_market_cap <= market_cap <= max_market_cap and
                volume_24h > min_volume and
                liquidity > min_liquidity and
                -90 <= change_24h <= 1000
            )
            
            if is_active:
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
                
                # 去重
                if not any(t["contractAddress"] == token_info["contractAddress"] for t in all_tokens):
                    all_tokens.append(token_info)
        
        time.sleep(0.2)
    
    # 先按市值排序，然后添加一些随机性，避免总是同样的币
    import random
    all_tokens.sort(key=lambda x: x["marketCap"])
    
    # 如果币种数量超过请求的count，随机选择一部分
    if len(all_tokens) > count:
        # 保留市值最小的前count*2个，然后从中随机选择
        candidates = all_tokens[:count*2]
        selected = random.sample(candidates, min(count, len(candidates)))
        # 再按市值排序
        selected.sort(key=lambda x: x["marketCap"])
    else:
        selected = all_tokens[:count]
    
    print(f"找到 {len(selected)} 个符合条件的代币")
    
    # 获取详细数据
    results = []
    for i, token in enumerate(selected, 1):
        print(f"[{i}/{len(selected)}] 获取 {token['symbol']} 的详细数据...")
        
        # 获取动态数据
        dynamic = get_dynamic_data(token["chainId"], token["contractAddress"])
        
        # 获取K线数据
        platform = get_platform(token["chainId"])
        klines_daily = get_kline_data(token["contractAddress"], platform, "1d", 200)
        klines_weekly = get_kline_data(token["contractAddress"], platform, "1w", 50)
        
        result = {
            **token,
            "dynamic": dynamic,
            "klines_daily": klines_daily,
            "klines_weekly": klines_weekly
        }
        results.append(result)
        time.sleep(0.3)
    
    return results

if __name__ == "__main__":
    # 测试
    data = fetch_altcoins(min_market_cap=30000000, count=10)
    print(f"\n共抓取 {len(data)} 个代币")
    for item in data:
        print(f"- {item['symbol']}: ${item['market_cap']/10000:.1f}万")
