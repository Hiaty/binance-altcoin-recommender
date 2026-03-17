from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import subprocess
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 配置
DATA_DIR = 'data'
RESULTS_FILE = os.path.join(DATA_DIR, 'analysis_results.json')

@app.route('/')
def index():
    """主页 - 返回UI界面"""
    return app.send_static_file('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """执行分析"""
    try:
        data = request.json
        count = data.get('count', 20)
        min_cap = data.get('minCap', 3000)
        sort_by = data.get('sortBy', 'marketCap')
        
        # 运行数据抓取
        result = subprocess.run(
            ['python', 'src/fetch_top20_altcoins.py', 
             '--count', str(count),
             '--min-cap', str(min_cap)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            return jsonify({'error': '数据抓取失败', 'details': result.stderr}), 500
        
        # 运行分析
        result = subprocess.run(
            ['python', 'src/analyze_altcoins.py'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            return jsonify({'error': '分析失败', 'details': result.stderr}), 500
        
        # 读取结果
        with open('altcoin_analysis_results.json', 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # 根据排序方式排序
        if sort_by == 'buyScore':
            analysis_data.sort(key=lambda x: x.get('buy_score', 0), reverse=True)
        elif sort_by == 'weekChange':
            analysis_data.sort(key=lambda x: x.get('week_change', 0), reverse=True)
        elif sort_by == 'turnover':
            analysis_data.sort(key=lambda x: x.get('turnover_rate', 0), reverse=True)
        else:  # marketCap
            analysis_data.sort(key=lambda x: x.get('market_cap', 0))
        
        # 更新排名
        for i, item in enumerate(analysis_data, 1):
            item['rank'] = i
        
        return jsonify({
            'success': True,
            'data': analysis_data,
            'timestamp': datetime.now().isoformat(),
            'stats': {
                'total': len(analysis_data),
                'recommend': sum(1 for x in analysis_data if x.get('recommendation') == '推荐'),
                'watch': sum(1 for x in analysis_data if x.get('recommendation') == '观望'),
                'avoid': sum(1 for x in analysis_data if x.get('recommendation') == '不推荐'),
                'whale': sum(1 for x in analysis_data if x.get('is_whale', False))
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/results', methods=['GET'])
def get_results():
    """获取最新分析结果"""
    try:
        if os.path.exists('altcoin_analysis_results.json'):
            with open('altcoin_analysis_results.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify({'success': True, 'data': data})
        else:
            return jsonify({'error': '暂无分析结果'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart', methods=['GET'])
def generate_chart():
    """生成分析图表"""
    try:
        result = subprocess.run(
            ['python', 'src/generate_recommendation_chart.py'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return jsonify({'success': True, 'message': '图表生成成功'})
        else:
            return jsonify({'error': '图表生成失败', 'details': result.stderr}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print("=" * 60)
    print("币安山寨币智能推荐系统 - 后台服务")
    print("=" * 60)
    print("服务地址: http://localhost:5000")
    print("API文档:")
    print("  POST /api/analyze    - 执行分析")
    print("  GET  /api/results    - 获取结果")
    print("  GET  /api/chart      - 生成图表")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
