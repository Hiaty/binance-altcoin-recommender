#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
币安山寨币智能推荐系统 - 启动器
兼容打包版本
"""

import subprocess
import sys
import os
import webbrowser
import time
import socket
from threading import Thread

def get_resource_path(relative_path):
    """获取资源文件路径（兼容开发和打包环境）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的路径
        base_path = sys._MEIPASS
    else:
        # 开发环境路径
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def check_port(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def wait_for_server(port, timeout=30):
    """等待服务器启动"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_port(port):
            return True
        time.sleep(1)
    return False

def open_browser_once():
    """只打开一次浏览器"""
    time.sleep(3)
    if not hasattr(open_browser_once, 'opened'):
        open_browser_once.opened = True
        print("[OK] Opening browser...")
        webbrowser.open("http://localhost:5000", new=2)

def main():
    print("=" * 60)
    print("  Binance Altcoin Recommender System")
    print("=" * 60)
    print()
    
    # 检查端口是否已被占用
    if check_port(5000):
        print("[INFO] Server already running at http://localhost:5000")
        webbrowser.open("http://localhost:5000", new=2)
        return
    
    print("[1/3] Checking dependencies...")
    try:
        import flask
        import requests
        import numpy
        from PIL import Image
        print("[OK] Dependencies ready")
    except ImportError:
        print("[WARNING] Installing dependencies...")
        try:
            backend_req = get_resource_path('backend/requirements.txt')
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "-r", backend_req, "-q"
            ])
            print("[OK] Dependencies installed")
        except Exception as e:
            print(f"[ERROR] Failed: {e}")
            input("Press Enter to exit...")
            return
    
    print()
    print("[2/3] Starting server...")
    
    # 获取后端路径
    backend_path = get_resource_path('backend/app.py')
    base_path = get_resource_path('.')
    
    # 设置环境变量，让后端能找到资源
    os.environ['BASE_DIR'] = base_path
    
    # 启动服务器
    try:
        process = subprocess.Popen(
            [sys.executable, backend_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=base_path,
            env=os.environ
        )
        
        # 等待服务器启动
        if wait_for_server(5000):
            print("[OK] Server started")
        else:
            print("[ERROR] Server failed to start")
            stdout, stderr = process.communicate(timeout=1)
            if stderr:
                print(f"Error: {stderr}")
            process.terminate()
            input("Press Enter to exit...")
            return
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        return
    
    print()
    print("[3/3] Ready!")
    print()
    print("=" * 60)
    print("  Access: http://localhost:5000")
    print("=" * 60)
    print()
    print("  Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    # 只打开一次浏览器
    Thread(target=open_browser_once, daemon=True).start()
    
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nStopping...")
        process.terminate()
        print("Stopped")

if __name__ == "__main__":
    main()
