#!/bin/bash
# 盈米金融教学平台 - 启动脚本

echo "=========================================="
echo "  盈米金融教学平台 Web应用"
echo "  Finance Education Platform"
echo "=========================================="
echo ""

# 检查Python版本
python_version=$(python3 --version 2>&1)
echo "✓ Python版本: $python_version"
echo ""

# 检查依赖
echo "检查依赖包..."
pip3 list | grep -E "streamlit|pandas|plotly" || {
    echo "⚠️  缺少依赖包，正在安装..."
    pip3 install -r requirements.txt
}
echo ""

# 启动应用
echo "🚀 启动应用..."
echo "📱 浏览器将自动打开 http://localhost:8501"
echo ""
echo "提示: 按 Ctrl+C 停止应用"
echo "=========================================="
echo ""

streamlit run app.py
