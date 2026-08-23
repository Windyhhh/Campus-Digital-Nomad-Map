#!/bin/bash

echo "========================================"
echo "校园数字游民活地图 - 快速启动"
echo "Campus Digital Nomad Live Map"
echo "========================================"
echo ""

# 检查是否已部署
if [ ! -d "venv" ]; then
    echo "[信息] 首次运行，开始自动部署..."
    python3 deploy.py
else
    echo "[信息] 环境已存在，直接启动应用..."
    echo ""
    echo "========================================"
    echo "应用启动中..."
    echo "访问地址: http://127.0.0.1:5000"
    echo "示例账户: admin / admin123"
    echo "按 Ctrl+C 停止应用"
    echo "========================================"
    echo ""
    venv/bin/python run.py
fi
