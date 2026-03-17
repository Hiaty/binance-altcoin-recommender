"""
分析接口 - 真实数据版本
"""

from flask import Blueprint, request, jsonify
import sys
import os

# 添加core到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.fetcher import fetch_altcoins
from core.analyzer import analyze_all
from datetime import datetime

analyze_bp = Blueprint('analyze', __name__)

# 缓存数据
cached_data = None
cached_time = None

@analyze_bp.route('/analyze', methods=['POST'])
def analyze():
    """执行分析"""
    try:
        data = request.get_json()
        count = data.get('count', 20)
        min_cap = data.get('minCap', 3000)
        sort_by = data.get('sortBy', 'marketCap')
        
        print(f"开始分析: {count}个币, 最小市值{min_cap}万")
        
        # 抓取数据
        tokens_data = fetch_altcoins(
            min_market_cap=min_cap * 10000,  # 转换为实际数值
            count=count
        )
        
        if not tokens_data:
            return jsonify({
                'success': False,
                'error': '数据抓取失败，请检查网络连接'
            }), 500
        
        # 分析数据
        analysis_results = analyze_all(tokens_data)
        
        # 根据排序方式排序
        if sort_by == 'buyScore':
            analysis_results.sort(key=lambda x: x.get('buy_score', 0), reverse=True)
        elif sort_by == 'weekChange':
            analysis_results.sort(key=lambda x: x.get('week_change', 0), reverse=True)
        elif sort_by == 'turnover':
            analysis_results.sort(key=lambda x: x.get('turnover_rate', 0), reverse=True)
        
        # 更新排名
        for i, item in enumerate(analysis_results, 1):
            item['rank'] = i
        
        # 统计
        stats = {
            'total': len(analysis_results),
            'recommend': sum(1 for r in analysis_results if r.get('recommendation') == '推荐'),
            'watch': sum(1 for r in analysis_results if r.get('recommendation') == '观望'),
            'avoid': sum(1 for r in analysis_results if r.get('recommendation') == '不推荐'),
            'whale': sum(1 for r in analysis_results if r.get('is_whale', False))
        }
        
        return jsonify({
            'success': True,
            'data': analysis_results,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        import traceback
        print(f"分析失败: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analyze_bp.route('/results', methods=['GET'])
def get_results():
    """获取最新分析结果"""
    # 这里应该从缓存或数据库读取
    return jsonify({
        'success': True,
        'message': '请使用POST /analyze接口获取实时数据'
    })

@analyze_bp.route('/chart', methods=['GET'])
def generate_chart():
    """生成图表"""
    try:
        # 这里可以调用生成图表的函数
        return jsonify({
            'success': True,
            'message': '图表功能开发中'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
