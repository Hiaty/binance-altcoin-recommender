#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
币安山寨币智能推荐系统 - 启动器
打包版本
"""

import subprocess
import sys
import os
import webbrowser
import time
from threading import Thread

def check_and_install():
    """检查并安装依赖"""
    print("[1/3] Checking dependencies...")
    try:
        # 使用内嵌方式安装
        import requests
        import flask
        import flask_cors
        import numpy
        from PIL import Image
        print("[OK] Dependencies ready")
        return True
    except ImportError:
        print("[WARNING] Missing dependencies, installing...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "requests", "flask", "flask-cors", "numpy", "pillow",
                "-q", "--user"
            ])
            print("[OK] Dependencies installed")
            return True
        except Exception as e:
            print(f"[ERROR] Installation failed: {e}")
            return False

def start_server():
    """启动服务器"""
    print("[2/3] Starting server...")
    try:
        # 获取当前目录
        if getattr(sys, 'frozen', False):
            # 打包后的路径
            base_path = os.path.dirname(sys.executable)
        else:
            # 开发环境路径
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        backend_path = os.path.join(base_path, 'backend', 'app.py')
        
        process = subprocess.Popen(
            [sys.executable, backend_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=base_path
        )
        
        time.sleep(3)
        
        if process.poll() is None:
            print("[OK] Server started")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"[ERROR] Failed to start: {stderr}")
            return None
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return None

def open_browser():
    """打开浏览器"""
    time.sleep(4)
    print("[4/4] Opening browser...")
    webbrowser.open("http://localhost:5000")

def main():
    print("=" * 60)
    print("  Binance Altcoin Recommender System")
    print("=" * 60)
    print()
    
    if not check_and_install():
        input("Press Enter to exit...")
        return
    
    print()
    
    server = start_server()
    if not server:
        input("Press Enter to exit...")
        return
    
    print()
    print("[3/4] Started successfully!")
    print()
    print("=" * 60)
    print("  Access: http://localhost:5000")
    print("=" * 60)
    print()
    print("  Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    Thread(target=open_browser, daemon=True).start()
    
    try:
        server.wait()
    except KeyboardInterrupt:
        print("\nStopping...")
        server.terminate()
        print("Stopped")

if __name__ == "__main__":
    main()
