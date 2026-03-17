"""
分析接口
"""

from flask import Blueprint, request, jsonify
import json
import os
from datetime import datetime

analyze_bp = Blueprint('analyze', __name__)

# 模拟分析数据（实际应从core.analyzer导入）
def get_mock_analysis():
    return [
        {
            "rank": 1,
            "symbol": "POPCAT",
            "name": "Popcat",
            "market_cap": 57194150.0,
            "price": 0.05836510430818849,
            "max_drawdown": 81.1982183573407,
            "max_rebound": 45.41354645077212,
            "turnover_rate": 1.1390492272001882,
            "week_change": 14.760407448169227,
            "month_change": 9.20429020567846,
            "concentration": 42.20071828219829,
            "net_inflow": 29942.33253643976,
            "daily_pattern": "三连阳, 均线金叉",
            "weekly_pattern": "三连阳, 均线死叉, 缩量",
            "pattern_strength": 85,
            "analysis": "【三连阳, 均线金叉】暂无强庄控盘迹象。优势: 日线强势;回调充分。",
            "is_whale": False,
            "whale_signals": [],
            "recommendation": "推荐",
            "buy_score": 55
        },
        {
            "rank": 2,
            "symbol": "BabyDoge",
            "name": "Baby Doge Coin",
            "market_cap": 90318640.0,
            "price": 4.4575698432e-10,
            "max_drawdown": 69.71238197569922,
            "max_rebound": 26.422704508977834,
            "turnover_rate": 0.9113534489295229,
            "week_change": 10.037531203406456,
            "month_change": 9.839788746742865,
            "concentration": 25.138726771080844,
            "net_inflow": 13931.626603821933,
            "daily_pattern": "三连阳, 均线金叉",
            "weekly_pattern": "三连阳, 均线死叉",
            "pattern_strength": 85,
            "analysis": "【三连阳, 均线金叉】暂无强庄控盘迹象。优势: 日线强势;回调充分。",
            "is_whale": False,
            "whale_signals": [],
            "recommendation": "推荐",
            "buy_score": 55
        }
    ]

@analyze_bp.route('/analyze', methods=['POST'])
def analyze():
    """执行分析"""
    try:
        data = request.get_json()
        count = data.get('count', 20)
        min_cap = data.get('minCap', 3000)
        sort_by = data.get('sortBy', 'marketCap')
        
        # 获取分析结果（实际应调用core.analyzer）
        results = get_mock_analysis()
        
        # 统计
        stats = {
            'total': len(results),
            'recommend': sum(1 for r in results if r.get('recommendation') == '推荐'),
            'watch': sum(1 for r in results if r.get('recommendation') == '观望'),
            'avoid': sum(1 for r in results if r.get('recommendation') == '不推荐'),
            'whale': sum(1 for r in results if r.get('is_whale', False))
        }
        
        return jsonify({
            'success': True,
            'data': results,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analyze_bp.route('/results', methods=['GET'])
def get_results():
    """获取分析结果"""
    try:
        results = get_mock_analysis()
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analyze_bp.route('/chart', methods=['GET'])
def generate_chart():
    """生成图表"""
    try:
        return jsonify({
            'success': True,
            'message': '图表生成成功',
            'url': '/static/chart.png'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
