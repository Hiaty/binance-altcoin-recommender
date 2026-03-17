"""
币安山寨币智能推荐系统 - 后端服务
Flask REST API
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import sys

# 获取基础路径（兼容打包后的路径）
if os.environ.get('BASE_DIR'):
    # 从环境变量获取（打包后）
    BASE_DIR = os.environ.get('BASE_DIR')
elif getattr(sys, 'frozen', False):
    # PyInstaller打包后的路径
    BASE_DIR = sys._MEIPASS
else:
    # 开发环境路径
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 添加项目路径
sys.path.append(os.path.join(BASE_DIR, 'backend'))

try:
    from api.analyze import analyze_bp
    from api.data import data_bp
    from config import Config
except ImportError:
    # 如果导入失败，尝试直接导入
    from backend.api.analyze import analyze_bp
    from backend.api.data import data_bp
    from backend.config import Config

def create_app():
    """创建Flask应用"""
    frontend_dir = os.path.join(BASE_DIR, 'frontend')
    
    app = Flask(__name__, 
                static_folder=frontend_dir,
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
        index_file = os.path.join(frontend_dir, 'index.html')
        if os.path.exists(index_file):
            return send_file(index_file)
        else:
            # 如果找不到文件，返回错误信息
            return jsonify({
                'error': 'Frontend not found',
                'frontend_dir': frontend_dir,
                'base_dir': BASE_DIR,
                'exists': os.path.exists(frontend_dir),
                'files': os.listdir(BASE_DIR) if os.path.exists(BASE_DIR) else 'N/A'
            }), 404
    
    @app.route('/health')
    def health():
        """健康检查"""
        return jsonify({
            'status': 'ok',
            'service': 'binance-altcoin-recommender',
            'version': '1.0.0',
            'base_dir': BASE_DIR,
            'frontend_dir': frontend_dir
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
    print(f"基础目录: {BASE_DIR}")
    print("=" * 60)
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
