#!/usr/bin/env python3
"""
币安山寨币智能推荐系统 - 一键启动器
同时启动前端和后端服务
"""

import subprocess
import sys
import os
import webbrowser
import time
from threading import Thread

def install_dependencies():
    """安装依赖"""
    print("[1/4] 检查依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", "backend/requirements.txt"])
        print("[✓] 依赖检查完成")
        return True
    except Exception as e:
        print(f"[✗] 依赖安装失败: {e}")
        return False

def start_backend():
    """启动后端"""
    print("[2/4] 启动后端服务...")
    try:
        process = subprocess.Popen(
            [sys.executable, "backend/app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(3)
        
        if process.poll() is None:
            print("[✓] 后端服务已启动")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"[✗] 后端启动失败: {stderr}")
            return None
    except Exception as e:
        print(f"[✗] 启动失败: {e}")
        return None

def open_browser():
    """打开浏览器"""
    time.sleep(4)
    print("[4/4] 打开浏览器...")
    webbrowser.open("http://localhost:5000")

def main():
    """主函数"""
    print("=" * 60)
    print("  币安山寨币智能推荐系统")
    print("=" * 60)
    print()
    
    if not install_dependencies():
        input("按回车键退出...")
        return
    
    print()
    
    backend = start_backend()
    if not backend:
        input("按回车键退出...")
        return
    
    print()
    print("[3/4] 服务启动成功!")
    print()
    print("=" * 60)
    print("  访问地址: http://localhost:5000")
    print("=" * 60)
    print()
    print("  API接口:")
    print("    POST /api/analyze  - 执行分析")
    print("    GET  /api/results  - 获取结果")
    print("    GET  /api/coins    - 币种列表")
    print()
    print("  按 Ctrl+C 停止服务")
    print("=" * 60)
    print()
    
    Thread(target=open_browser, daemon=True).start()
    
    try:
        backend.wait()
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        backend.terminate()
        print("服务已停止")

if __name__ == "__main__":
    main()
