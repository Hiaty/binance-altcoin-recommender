#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
币安山寨币智能推荐系统 - 启动器
一键启动前后端服务
"""

import subprocess
import sys
import os
import webbrowser
import time
from threading import Thread

def check_dependencies():
    """检查并安装依赖"""
    print("[1/4] 检查依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"])
        print("[✓] 依赖检查完成")
        return True
    except Exception as e:
        print(f"[✗] 依赖安装失败: {e}")
        return False

def start_backend():
    """启动后端服务"""
    print("[2/4] 启动后端服务...")
    try:
        # 使用subprocess启动Flask服务
        process = subprocess.Popen(
            [sys.executable, "src/app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务启动
        time.sleep(3)
        
        # 检查服务是否正常运行
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
    
    # 检查依赖
    if not check_dependencies():
        input("按回车键退出...")
        return
    
    print()
    
    # 启动后端
    backend_process = start_backend()
    if not backend_process:
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
    print("    GET  /api/chart    - 生成图表")
    print()
    print("  按 Ctrl+C 停止服务")
    print("=" * 60)
    print()
    
    # 在新线程中打开浏览器
    Thread(target=open_browser, daemon=True).start()
    
    try:
        # 等待后端服务结束
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        backend_process.terminate()
        print("服务已停止")

if __name__ == "__main__":
    main()
