"""
配置文件
"""

import os

class Config:
    """配置类"""
    # 服务配置
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = True
    
    # 币安API配置
    BINANCE_API_BASE = 'https://web3.binance.com'
    BINANCE_API_TIMEOUT = 30
    
    # 数据配置
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    MIN_MARKET_CAP = 30000000  # 最小市值3000万
    DEFAULT_COUNT = 20  # 默认分析数量
    
    # 分析配置
    MAX_DRAWDOWN_THRESHOLD = 50  # 最大回调阈值
    TURNOVER_MIN = 5  # 最小换手率
    TURNOVER_MAX = 50  # 最大换手率
    CONCENTRATION_THRESHOLD = 80  # 持仓集中度阈值
