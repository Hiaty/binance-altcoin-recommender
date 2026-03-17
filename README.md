# 🚀 币安山寨币智能推荐系统

<p align="center">
  <img src="images/binance_logo.jpg" width="80" alt="币安Logo">
</p>

<p align="center">
  <strong>基于币安Web3 API的智能加密货币分析工具</strong>
</p>

<p align="center">
  <a href="#功能特性">功能特性</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#使用指南">使用指南</a> •
  <a href="#技术架构">技术架构</a> •
  <a href="#免责声明">免责声明</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-lightgrey.svg" alt="Platform">
</p>

---

## 📖 项目简介

币安山寨币智能推荐系统是一个基于**K线形态分析**、**庄家识别算法**和**多维度技术指标**的加密货币智能分析工具。系统通过实时抓取币安Web3 API数据，对市值3000万以上的活跃山寨币进行深度分析，帮助投资者发现潜在的价值币种。

### ✨ 核心优势

- 🤖 **AI智能筛选** - 自动识别优质币种，过滤垃圾项目
- 📊 **K线形态分析** - 日线/周线技术分析，识别买卖信号
- 🎯 **庄家识别** - 检测持仓集中度、异常换手等控盘特征
- 📈 **多维评分** - 综合8项指标，给出科学的投资建议
- 🎨 **可视化UI** - 美观的Web界面，支持交互式操作

---

## 🛠️ 功能特性

### 1. 智能数据抓取
- ✅ 自动筛选市值3000万+的活跃币种
- ✅ 实时获取价格、交易量、持仓分布等数据
- ✅ 支持日线/周线K线数据获取

### 2. 深度技术分析
| 指标 | 说明 | 应用价值 |
|------|------|----------|
| **历史最大回调** | 从最高点下跌幅度 | 判断入场时机，回调越大机会越好 |
| **底部最大反弹** | 从最低点上涨幅度 | 评估反弹力度和潜力 |
| **换手率** | 24h交易量/市值 | 5-50%为健康区间，过高可能是出货信号 |
| **本周/本月反弹** | 7天/30天涨跌幅 | 反映短期和中期趋势 |
| **持仓集中度** | 前10大持有者占比 | >80%为高度控盘，风险较高 |
| **资金净流入** | 买入量-卖出量 | 判断资金流向和市场情绪 |

### 3. K线形态识别
- 📈 均线金叉/死叉识别
- 🚀 突破新高/跌破新低检测
- 📊 三连阳/三连阴形态
- 💹 放量/缩量分析

### 4. 智能推荐系统
基于多维度算法评分：
- **推荐** (40+分) - 综合指标优秀，建议关注
- **观望** (20-40分) - 部分指标良好，需进一步观察
- **不推荐** (<20分) - 风险较高，建议回避

---

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Windows/Linux/MacOS

### 安装步骤

#### 1. 克隆仓库
```bash
git clone https://github.com/guiguzibeneben/binance-altcoin-recommender.git
cd binance-altcoin-recommender
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 运行数据抓取
```bash
python src/fetch_top20_altcoins.py
```

#### 4. 执行分析
```bash
python src/analyze_altcoins.py
```

#### 5. 生成图表
```bash
python src/generate_recommendation_chart.py
```

#### 6. 打开UI界面
双击打开 `altcoin_recommender_ui.html` 或在浏览器中访问。

---

## 📖 使用指南

### UI界面操作

1. **设置筛选参数**
   - 筛选数量：选择要分析的币种数量（默认20个）
   - 最小市值：设置筛选的最小市值（默认3000万）
   - 排序方式：支持按市值、推荐评分、本周涨幅、换手率排序

2. **执行分析**
   - 点击「🔄 重新分析」按钮
   - 等待3-5分钟获取数据和分析结果

3. **查看结果**
   - 统计卡片：查看推荐/观望/不推荐/强庄币数量
   - 数据表格：查看每个币种的详细分析指标
   - 指标说明：了解各项指标的含义和应用

### 命令行使用

```bash
# 抓取数据
python src/fetch_top20_altcoins.py

# 分析币种
python src/analyze_altcoins.py

# 生成图表
python src/generate_recommendation_chart.py
```

---

## 🏗️ 技术架构

```
binance-altcoin-recommender/
├── 📁 src/                          # 源代码目录
│   ├── 📄 fetch_top20_altcoins.py   # 数据抓取模块
│   ├── 📄 analyze_altcoins.py       # 数据分析模块
│   └── 📄 generate_recommendation_chart.py  # 图表生成模块
├── 📁 data/                         # 数据存储目录
├── 📁 images/                       # 图片资源目录
│   └── 🖼️ binance_logo.jpg         # 币安Logo
├── 📁 docs/                         # 文档目录
├── 🌐 altcoin_recommender_ui.html  # Web界面
├── 📋 requirements.txt              # 依赖列表
└── 📖 README.md                     # 项目说明
```

### 技术栈
- **Python** - 核心开发语言
- **Requests** - HTTP数据抓取
- **Pillow** - 图像生成
- **NumPy** - 数值计算
- **HTML/CSS/JavaScript** - 前端界面

---

## 📊 分析示例

### 推荐币种特征
- ✅ 日线/周线形态良好（金叉、突破）
- ✅ 历史回调充分（>50%）
- ✅ 换手率健康（5-50%）
- ✅ 持仓集中度适中（<70%）
- ✅ 资金净流入为正

### 风险币种特征
- ⚠️ 持仓高度集中（>90%）
- ⚠️ 换手率异常（>100%）
- ⚠️ 月涨幅过大（>200%）
- ⚠️ 资金持续流出

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 提交Issue
- 🐛 Bug反馈
- 💡 功能建议
- 📖 文档改进

### 提交PR
1. Fork本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

---

## 📜 免责声明

⚠️ **重要提示**

1. **投资风险**：加密货币投资具有高风险，价格波动剧烈，可能导致本金损失。
2. **仅供参考**：本分析仅供参考，不构成任何投资建议或承诺。
3. **独立判断**：请根据自身风险承受能力独立做出投资决策。
4. **数据准确性**：虽然我们会尽力确保数据准确性，但不保证实时性和完整性。
5. **技术风险**：系统可能存在技术故障或延迟，使用风险自负。

**使用本系统即表示您已阅读并同意以上免责声明。**

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

---

## 🙏 致谢

- [币安](https://www.binance.com/) - 提供Web3 API数据支持
- [OpenClaw](https://github.com/openclaw) - AI助手技术支持
- 所有贡献者和用户

---

<p align="center">
  <strong>⭐ Star 本项目如果它对你有帮助！</strong>
</p>

<p align="center">
  Made with ❤️ by <a href="https://github.com/guiguzibeneben">@guiguzibeneben</a>
</p>
