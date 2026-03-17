"""
币安山寨币智能推荐系统 - 后端服务
Flask REST API
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.analyze import analyze_bp
from api.data import data_bp
from config import Config

def create_app():
    """创建Flask应用"""
    app = Flask(__name__, 
                static_folder='../frontend',
                static_url_path='')
    
    # 配置
    app.config.from_object(Config)
    
    # 启用CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # 注册蓝图
    app.register_blueprint(analyze_bp, url_prefix='/api')
    app.register_blueprint(data_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        """首页"""
        return send_from_directory('../frontend', 'index.html')
    
    @app.route('/health')
    def health():
        """健康检查"""
        return jsonify({
            'status': 'ok',
            'service': 'binance-altcoin-recommender',
            'version': '1.0.0'
        })
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print("币安山寨币智能推荐系统 - 后端服务")
    print("=" * 60)
    print(f"服务地址: http://{Config.HOST}:{Config.PORT}")
    print(f"API文档: http://{Config.HOST}:{Config.PORT}/api/docs")
    print("=" * 60)
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
