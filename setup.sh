#!/bin/bash

# 创建数据目录
mkdir -p data

# 创建.streamlit配置目录
mkdir -p ~/.streamlit/

# 创建Streamlit配置文件
echo "\
[general]\n\
email = \"support@example.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = $PORT\n\
\n\
[theme]\n\
primaryColor = \"#1f77b4\"\n\
backgroundColor = \"#ffffff\"\n\
secondaryBackgroundColor = \"#f0f2f6\"\n\
textColor = \"#262730\"\n\
font = \"sans serif\"\n\
" > ~/.streamlit/config.toml
