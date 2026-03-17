"""
数据接口
"""

from flask import Blueprint, jsonify
from datetime import datetime

data_bp = Blueprint('data', __name__)

@data_bp.route('/coins', methods=['GET'])
def get_coins():
    """获取币种列表"""
    coins = [
        {'symbol': 'POPCAT', 'name': 'Popcat', 'market_cap': 57194150},
        {'symbol': 'BabyDoge', 'name': 'Baby Doge Coin', 'market_cap': 90318640},
        {'symbol': 'DOGE', 'name': 'Dogecoin', 'market_cap': 258347100}
    ]
    return jsonify({
        'success': True,
        'data': coins,
        'timestamp': datetime.now().isoformat()
    })

@data_bp.route('/market', methods=['GET'])
def get_market_data():
    """获取市场数据"""
    return jsonify({
        'success': True,
        'data': {
            'total_market_cap': 1000000000000,
            'total_volume_24h': 50000000000,
            'btc_dominance': 45.5
        }
    })
