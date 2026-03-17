#!/usr/bin/env python3
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
    print("[1/3] 检查依赖...")
    try:
        # 使用内嵌方式安装
        import requests
        import flask
        import flask_cors
        import numpy
        from PIL import Image
        print("[✓] 依赖已就绪")
        return True
    except ImportError:
        print("[✗] 缺少依赖，正在安装...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "requests", "flask", "flask-cors", "numpy", "pillow",
                "-q", "--user"
            ])
            print("[✓] 依赖安装完成")
            return True
        except Exception as e:
            print(f"[✗] 安装失败: {e}")
            return False

def start_server():
    """启动服务器"""
    print("[2/3] 启动服务...")
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
            print("[✓] 服务已启动")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"[✗] 启动失败: {stderr}")
            return None
    except Exception as e:
        print(f"[✗] 错误: {e}")
        return None

def open_browser():
    """打开浏览器"""
    time.sleep(4)
    print("[4/4] 打开浏览器...")
    webbrowser.open("http://localhost:5000")

def main():
    print("=" * 60)
    print("  币安山寨币智能推荐系统")
    print("=" * 60)
    print()
    
    if not check_and_install():
        input("按回车键退出...")
        return
    
    print()
    
    server = start_server()
    if not server:
        input("按回车键退出...")
        return
    
    print()
    print("[3/4] 启动成功!")
    print()
    print("=" * 60)
    print("  访问地址: http://localhost:5000")
    print("=" * 60)
    print()
    print("  按 Ctrl+C 停止服务")
    print("=" * 60)
    print()
    
    Thread(target=open_browser, daemon=True).start()
    
    try:
        server.wait()
    except KeyboardInterrupt:
        print("\n正在停止...")
        server.terminate()
        print("已停止")

if __name__ == "__main__":
    main()
