# 币安山寨币智能推荐系统 - 完整版

## 项目结构

```
binance-altcoin-recommender/
├── backend/                    # 后端代码
│   ├── app.py                 # Flask主应用
│   ├── api/
│   │   ├── __init__.py
│   │   ├── analyze.py         # 分析接口
│   │   └── data.py            # 数据接口
│   ├── core/
│   │   ├── __init__.py
│   │   ├── fetcher.py         # 数据抓取
│   │   ├── analyzer.py        # 数据分析
│   │   └── chart.py           # 图表生成
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py         # 工具函数
│   ├── config.py              # 配置文件
│   └── requirements.txt       # 后端依赖
├── frontend/                   # 前端代码
│   ├── index.html             # 主页面
│   ├── css/
│   │   └── style.css          # 样式文件
│   ├── js/
│   │   ├── app.js             # 主应用逻辑
│   │   ├── api.js             # API调用
│   │   └── charts.js          # 图表组件
│   └── assets/
│       └── logo.png           # 资源文件
├── data/                       # 数据目录
├── docs/                       # 文档
├── tests/                      # 测试代码
├── README.md                   # 项目说明
├── LICENSE                     # 许可证
└── start.py                    # 一键启动脚本
```

## 快速开始

### 1. 安装依赖
```bash
pip install -r backend/requirements.txt
```

### 2. 启动服务
```bash
python start.py
```

### 3. 访问系统
浏览器打开: http://localhost:5000

## API文档

### 分析接口
- `POST /api/analyze` - 执行币种分析
- `GET /api/results` - 获取分析结果
- `GET /api/chart` - 生成分析图表

## 技术栈
- 后端: Flask + Python
- 前端: HTML5 + CSS3 + JavaScript
- 数据: 币安Web3 API

## 许可证
MIT License
