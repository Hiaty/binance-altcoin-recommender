#!/usr/bin/env python3
"""
币安山寨币智能推荐系统 - 简化版启动器
确保能正常运行
"""

import subprocess
import sys
import os
import webbrowser
import time

def main():
    print("=" * 60)
    print("  币安山寨币智能推荐系统")
    print("=" * 60)
    print()
    
    # 检查Python
    print("[1/3] 检查Python...")
    try:
        import flask
        print("  Python已就绪")
    except ImportError:
        print("  正在安装依赖...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-cors", "requests", "-q"])
        print("  依赖安装完成")
    
    print()
    print("[2/3] 启动服务...")
    print("  服务地址: http://localhost:5000")
    print()
    
    # 启动后端
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_path = os.path.join(base_dir, 'backend', 'app.py')
    
    # 打开浏览器
    time.sleep(2)
    webbrowser.open("http://localhost:5000")
    
    print("[3/3] 浏览器已打开，请使用系统")
    print("  按Ctrl+C停止服务")
    print()
    
    # 运行后端
    subprocess.call([sys.executable, backend_path])

if __name__ == "__main__":
    main()
