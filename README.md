# 🪙 币安山寨币智能推荐系统 v2.0
### Binance Altcoin AI Recommendation System

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white">
  <img alt="Flask" src="https://img.shields.io/badge/Flask-2.0+-000000?logo=flask">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green">
  <img alt="Free" src="https://img.shields.io/badge/API-Free%20%2F%20No%20Key-brightgreen">
</p>

<p align="center">
  <a href="#中文说明">中文</a> &nbsp;·&nbsp; <a href="#english">English</a>
</p>

---

## 中文说明

### 📖 简介

一个基于 **Binance Web3 API + 市场情绪 + Goal-Driven 回测框架** 的山寨币智能筛选工具。

无需任何 API Key，开箱即用。在原项目基础上进行了大幅优化：全量扫描、情绪过滤、K线智能选源、胜率回测。

### ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 🔍 **全量扫描** | 用 a-z 字母遍历 Binance Web3 API，覆盖 BSC / Base / Solana 全链代币，不再依赖关键词 |
| 📊 **多维度评分** | 历史回调、换手率、持仓集中度、K线形态、资金净流入综合打分 |
| 😱 **市场情绪过滤** | 实时接入 Fear & Greed Index + BTC 趋势，大盘暴跌时自动降级推荐 |
| 🔑 **K线智能选源** | Binance 现货有上市的代币优先用官方 API，链上代币用第三方数据源 |
| 📈 **Goal-Driven 回测** | 每次推荐自动记录价格快照，3日/7日后自动计算真实胜率 |
| 🐋 **庄家识别** | 识别高度控盘、放量拉升、深V反弹等强庄特征 |

### 🚀 快速开始

**环境要求：** Python 3.8+，无需任何 API Key

```bash
# 1. 克隆项目
git clone https://github.com/YOUR_USERNAME/binance-altcoin-recommender.git
cd binance-altcoin-recommender

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python start.py

# 4. 浏览器访问
open http://localhost:5001
```

> **macOS 注意**：5000 端口被 AirPlay 占用，项目默认使用 5001 端口。

### 📐 项目结构

```
├── backend/
│   ├── app.py              # Flask 主应用
│   ├── config.py           # 配置（端口、市值阈值等）
│   ├── api/
│   │   ├── analyze.py      # 分析 + 情绪 + 回测接口
│   │   └── data.py         # 数据接口
│   └── core/
│       ├── fetcher.py      # 数据抓取（全量扫描 + 智能K线）
│       ├── analyzer.py     # 评分分析（注入情绪因子）
│       ├── sentiment.py    # 市场情绪（F&G + BTC趋势）
│       └── backtest.py     # Goal-Driven 回测引擎
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── api.js
│       └── app.js
├── data/                   # 回测记录（运行后自动生成）
└── start.py                # 一键启动
```

### 📡 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/analyze` | 执行全量分析 |
| GET | `/api/sentiment` | 获取当前市场情绪 |
| GET | `/api/backtest` | 获取历史胜率统计 |
| GET | `/health` | 服务健康检查 |

### ⚙️ 评分规则

```
基础评分（满分 80）：
  +20  日线形态强势（strength > 60）
  +15  周线向好
  +15  历史回调充分（> 50%）且本周回升
  +10  换手率健康（5%–50%）
  +10  24h 资金净流入为正
  +10  筹码分散（前10持仓 < 70%）
  -15  涨幅过大（历史回调 < 20%）
  -20  高度控盘（前10持仓 > 90%）
  -15  换手过高（> 100%）

情绪叠加（-15 ~ +10）：
  BTC 跌超 5%  → -15 分
  BTC 涨超 5%  → +10 分
  极度恐惧（F&G ≤ 20）→ +10 分（可能是抄底时机）
  极度贪婪（F&G ≥ 80）→ -10 分（市场过热）

推荐阈值：≥ 40 推荐 | 20–39 观望 | < 20 不推荐
大盘暴跌（BTC 跌超 8%）时，所有「推荐」自动降为「观望」
```

### ⚠️ 免责声明

本项目仅供学习和技术研究，**不构成任何投资建议**。加密货币市场风险极高，请独立判断，自行承担风险。

---

## English

### 📖 Overview

An AI-powered altcoin screening tool built on **Binance Web3 API**, enriched with real-time **market sentiment** filtering and a **Goal-Driven backtesting framework**.

No API keys required. Significant improvements over the original project: full-market scanning, sentiment-aware scoring, smart K-line source selection, and win-rate tracking.

### ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Full Market Scan** | Iterates a–z keywords against Binance Web3 API, covering BSC / Base / Solana — no keyword dependency |
| 📊 **Multi-factor Scoring** | Scores on drawdown, turnover rate, holder concentration, K-line patterns, and net capital flow |
| 😱 **Sentiment Filter** | Live Fear & Greed Index + BTC trend; auto-demotes buy signals during market panic |
| 🔑 **Smart K-line Source** | Official Binance spot API for listed tokens; third-party on-chain source for DEX-only tokens |
| 📈 **Goal-Driven Backtest** | Snapshots every recommendation at entry price; auto-calculates real 3-day / 7-day win rates over time |
| 🐋 **Whale Detection** | Flags high holder concentration, volume pumps, and deep-V rebounds |

### 🚀 Quick Start

**Requirements:** Python 3.8+ · No API keys needed

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/binance-altcoin-recommender.git
cd binance-altcoin-recommender

# Install dependencies
pip install -r requirements.txt

# Run
python start.py

# Open browser
open http://localhost:5001
```

### 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/analyze` | Run full analysis |
| GET | `/api/sentiment` | Current market sentiment |
| GET | `/api/backtest` | Historical win rate stats |
| GET | `/health` | Health check |

### ⚙️ Scoring Logic

```
Base Score (max 80):
  +20  Strong daily K-line pattern (strength > 60)
  +15  Positive weekly trend
  +15  Deep drawdown (> 50%) with weekly recovery
  +10  Healthy turnover rate (5%–50%)
  +10  Positive 24h net capital inflow
  +10  Distributed holdings (top-10 < 70%)
  -15  Overbought (drawdown < 20%)
  -20  Highly concentrated (top-10 > 90%)
  -15  Excessive turnover (> 100%)

Sentiment Overlay (-15 to +10):
  BTC drops > 5%      → -15
  BTC gains > 5%      → +10
  Extreme Fear ≤ 20   → +10 (potential buy opportunity)
  Extreme Greed ≥ 80  → -10 (overheated market)

Thresholds: ≥ 40 → Buy | 20–39 → Watch | < 20 → Avoid
BTC crash > 8%: all "Buy" signals auto-downgraded to "Watch"
```

### ⚠️ Disclaimer

This project is for **educational and research purposes only**. Nothing here constitutes financial advice. Crypto markets are highly volatile — always do your own research.

---

### 🙏 Credits

- Original project: [guiguzibeneben/binance-altcoin-recommender](https://github.com/guiguzibeneben/binance-altcoin-recommender)
- Data sources: [Binance Web3 API](https://web3.binance.com) · [Binance Spot API](https://api.binance.com) · [alternative.me Fear & Greed](https://alternative.me/crypto/fear-and-greed-index/)
- Architecture inspiration: [Goal-Driven Framework](https://github.com/lidangzzz/goal-driven)

<p align="center">⭐ If this helps you, please give it a star!</p>
