# 币安山寨币智能推荐系统

![币安Logo](images/binance_logo.jpg)

基于币安Web3 API的智能山寨币分析推荐系统，通过K线形态分析、庄家识别、技术指标等多维度评估，帮助用户发现价值币种。

## 🌟 核心功能

- **智能筛选**: 自动筛选市值3000万+的活跃山寨币
- **K线形态分析**: 日线/周线技术分析，识别金叉、突破等信号
- **庄家识别**: 检测持仓集中度、异常换手等强庄币特征
- **综合评分**: 多维度算法评分，给出推荐/观望/不投资建议
- **可视化UI**: 美观的Web界面，支持交互式筛选和排序

## 📊 分析指标

| 指标 | 说明 |
|------|------|
| 历史最大回调 | 从最高点下跌幅度，越大说明回调越充分 |
| 底部最大反弹 | 从最低点上涨幅度，反映反弹力度 |
| 换手率 | 24h交易量/市值，5-50%为健康区间 |
| 本周/本月反弹 | 7天/30天涨跌幅，反映短中期趋势 |
| 持仓集中度 | 前10大持有者占比，>80%为高度控盘 |
| 日线/周线形态 | K线技术分析，识别买卖信号 |
| 是否强庄币 | 判断庄家控盘迹象 |

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests pillow numpy
```

### 2. 运行数据抓取

```bash
python src/fetch_top20_altcoins.py
```

### 3. 运行分析

```bash
python src/analyze_altcoins.py
```

### 4. 生成图表

```bash
python src/generate_recommendation_chart.py
```

### 5. 打开UI界面

双击打开 `altcoin_recommender_ui.html` 或在浏览器中访问。

## 📁 项目结构

```
binance-altcoin-recommender/
├── src/                          # 源代码
│   ├── fetch_top20_altcoins.py   # 数据抓取
│   ├── analyze_altcoins.py       # 数据分析
│   └── generate_recommendation_chart.py  # 图表生成
├── data/                         # 数据文件
├── images/                       # 图片资源
│   └── binance_logo.jpg         # 币安Logo
├── docs/                         # 文档
├── altcoin_recommender_ui.html  # UI界面
└── README.md                     # 项目说明
```

## 🎯 使用流程

1. **设置参数**: 在UI界面设置筛选数量、最小市值、排序方式
2. **执行分析**: 运行Python脚本获取数据并分析
3. **查看结果**: 在UI界面查看分析结果和推荐评级
4. **生成报告**: 自动生成图表和分析报告

## ⚠️ 风险提示

- 本分析仅供参考，不构成投资建议
- 加密货币投资有风险，入市需谨慎
- 请根据自身风险承受能力做出投资决策

## 📄 数据来源

- 币安Web3 API
- 实时市场数据

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📜 许可证

MIT License

## 👨‍💻 作者

Created with ❤️ by OpenClaw AI Assistant

---

**免责声明**: 本项目仅用于学习和研究目的，不构成任何投资建议。投资有风险，入市需谨慎。
