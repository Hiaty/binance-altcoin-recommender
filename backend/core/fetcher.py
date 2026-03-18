"""
币安山寨币智能推荐系统 - 数据抓取模块 v2
改进：
  A. 全量扫描：放弃关键词循环，改用空关键词 + 多排序维度 + 多链覆盖
  B. K线数据：优先使用 Binance 官方现货 API，链上代币降级使用 sintral.io
"""

import requests
import time

BINANCE_WEB3 = "https://web3.binance.com"
BINANCE_SPOT = "https://api.binance.com/api/v3"

HEADERS = {
    "Accept-Encoding": "identity",
    "User-Agent": "Mozilla/5.0 (compatible; binance-altcoin-recommender/2.0)",
}

CHAINS = ["56", "8453", "CT_501"]          # BSC / Base / Solana
CHAIN_STR = ",".join(CHAINS)

# 单字母 a-z + 常见词根，覆盖率远高于原来的关键词列表
# API 空关键词返回 success=False，必须有非空 keyword
_KEYWORDS = list("abcdefghijklmnopqrstuvwxyz") + [
    "ai", "meme", "pepe", "doge", "cat", "shib", "moon", "baby",
    "inu", "elon", "btc", "eth", "sol", "bnb", "dao", "nft", "defi",
]


# ──────────────────────────────────────────────────────────────────
# A. 全量扫描（单字母遍历，覆盖所有代币名称）
# ──────────────────────────────────────────────────────────────────

def _fetch_by_keyword(keyword, min_market_cap, max_market_cap, collected):
    """用单个关键词查询，把符合条件的代币合并进 collected（按 contractAddress 去重）"""
    url = f"{BINANCE_WEB3}/bapi/defi/v5/public/wallet-direct/buw/wallet/market/token/search"
    try:
        resp = requests.get(
            url,
            params={"keyword": keyword, "chainIds": CHAIN_STR, "orderBy": "volume24h"},
            headers=HEADERS,
            timeout=20,
        )
        if resp.status_code != 200:
            return
        data = resp.json()
        if not data.get("success"):
            return
        tokens = data.get("data") or []
    except Exception as e:
        print(f"  keyword={repr(keyword)} 失败: {e}")
        return

    for token in tokens:
        try:
            market_cap = float(token.get("marketCap") or 0)
            volume_24h = float(token.get("volume24h") or 0)
            change_24h = float(token.get("percentChange24h") or 0)
            liquidity  = float(token.get("liquidity") or 0)
        except (ValueError, TypeError):
            continue

        if not (min_market_cap <= market_cap <= max_market_cap):
            continue
        if volume_24h < 100_000:
            continue
        if liquidity < 50_000:
            continue
        if not (-95 <= change_24h <= 2000):
            continue

        addr = token.get("contractAddress", "")
        if addr and addr not in collected:
            collected[addr] = {
                "name":             token.get("name", ""),
                "symbol":           token.get("symbol", ""),
                "chain_id":         token.get("chainId", ""),
                "contract_address": addr,
                "price":            float(token.get("price") or 0),
                "market_cap":       market_cap,
                "volume_24h":       volume_24h,
                "change_24h":       change_24h,
                "holders_top10":    float(token.get("holdersTop10Percent") or 0),
                "liquidity":        liquidity,
            }


# ──────────────────────────────────────────────────────────────────
# B. K 线数据（Binance 官方优先，回退 sintral.io）
# ──────────────────────────────────────────────────────────────────

def _kline_binance_spot(symbol, interval="1d", limit=200):
    """从 Binance 现货 API 取 K 线（格式：[ts, open, high, low, close, volume]）"""
    try:
        resp = requests.get(
            f"{BINANCE_SPOT}/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit},
            headers=HEADERS,
            timeout=15,
        )
        if resp.status_code == 200:
            raw = resp.json()
            # Binance 格式转 [ts, high, low, close, volume]
            return [[k[0], float(k[2]), float(k[3]), float(k[4]), float(k[5])] for k in raw]
    except Exception:
        pass
    return []


def _kline_sintral(address, platform, interval="1d", limit=200):
    """从 sintral.io 取链上 K 线（原有逻辑）"""
    try:
        resp = requests.get(
            "https://dquery.sintral.io/u-kline/v1/k-line/candles",
            params={"address": address, "platform": platform, "interval": interval, "limit": limit},
            headers=HEADERS,
            timeout=20,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("data") or []
    except Exception:
        pass
    return []


def _listed_on_spot(symbol):
    """检查该代币是否在 Binance 现货有 USDT 交易对"""
    try:
        resp = requests.get(
            f"{BINANCE_SPOT}/ticker/price",
            params={"symbol": f"{symbol}USDT"},
            timeout=8,
        )
        return resp.status_code == 200
    except Exception:
        return False


_CHAIN_PLATFORM = {"56": "bsc", "8453": "base", "CT_501": "solana"}


def _get_klines(symbol, chain_id, address, interval, limit):
    """智能选择 K 线数据源：Binance 现货优先，否则 sintral.io"""
    # 先尝试 Binance 现货
    if _listed_on_spot(symbol):
        klines = _kline_binance_spot(f"{symbol}USDT", interval, limit)
        if klines:
            return klines, "binance"

    # 回退到 sintral.io
    platform = _CHAIN_PLATFORM.get(chain_id, "bsc")
    klines = _kline_sintral(address, platform, interval, limit)
    return klines, "sintral"


# ──────────────────────────────────────────────────────────────────
# 动态数据（买卖量、净流入）
# ──────────────────────────────────────────────────────────────────

def _get_dynamic(chain_id, address):
    try:
        resp = requests.get(
            f"{BINANCE_WEB3}/bapi/defi/v4/public/wallet-direct/buw/wallet/market/token/dynamic/info",
            params={"chainId": chain_id, "contractAddress": address},
            headers=HEADERS,
            timeout=20,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") and data.get("data"):
                return data["data"]
    except Exception:
        pass
    return None


# ──────────────────────────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────────────────────────

def fetch_altcoins(min_market_cap=30_000_000, count=20):
    """
    抓取山寨币完整数据
    Args:
        min_market_cap: 最小市值（默认 3000 万）
        count: 最终分析数量
    """
    max_market_cap = 1_000_000_000  # 10 亿上限

    print(f"[A] 全量扫描中（市值 {min_market_cap/10000:.0f}万 ~ 10亿）...")
    all_tokens: dict = {}

    for kw in _KEYWORDS:
        _fetch_by_keyword(kw, min_market_cap, max_market_cap, all_tokens)
        time.sleep(0.15)

    print(f"    扫描完成，累计 {len(all_tokens)} 个唯一代币")

    token_list = sorted(all_tokens.values(), key=lambda x: x["market_cap"])
    selected = token_list[:count]
    print(f"[A] 共找到 {len(all_tokens)} 个代币，分析前 {len(selected)} 个\n")

    results = []
    for i, token in enumerate(selected, 1):
        sym   = token["symbol"]
        chain = token["chain_id"]
        addr  = token["contract_address"]
        print(f"[{i}/{len(selected)}] {sym} | 抓取 K 线 & 动态数据...")

        daily_klines, src_d  = _get_klines(sym, chain, addr, "1d", 200)
        weekly_klines, src_w = _get_klines(sym, chain, addr, "1w", 50)
        dynamic = _get_dynamic(chain, addr)

        token["dynamic"]       = dynamic
        token["klines_daily"]  = daily_klines
        token["klines_weekly"] = weekly_klines
        token["kline_source"]  = src_d
        results.append(token)

        time.sleep(0.3)

    return results
