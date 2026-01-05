#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
盈米金融教学平台 - Web应用主入口
Finance Education Platform - Streamlit Web App

Version: 1.0.0
Author: AI Assistant
Date: 2026-01-05
"""

import streamlit as st
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from finance_education_platform import FinanceEducationPlatform
from utils.auth import get_auth_manager, show_login_page, logout_user
from utils.database import get_db_manager
from utils.mcp_client import get_mcp_client
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# 页面配置
st.set_page_config(
    page_title="金融教学平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
def load_custom_css():
    st.markdown("""
        <style>
        /* 主题色 */
        :root {
            --primary-color: #1f77b4;
            --secondary-color: #ff7f0e;
            --success-color: #2ca02c;
            --danger-color: #d62728;
        }

        /* 标题样式 */
        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
            padding: 1rem;
            background: linear-gradient(120deg, #f6f9fc 0%, #e9f0f7 100%);
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* 卡片样式 */
        .info-card {
            padding: 1.5rem;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
            border-left: 4px solid #1f77b4;
        }

        .metric-card {
            padding: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        /* 按钮样式 */
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            border: none;
            background: linear-gradient(120deg, #1f77b4 0%, #2ca02c 100%);
            color: white;
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(31, 119, 180, 0.4);
        }

        /* 侧边栏样式 */
        .css-1d391kg {
            background-color: #f8f9fa;
        }

        /* 进度条样式 */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #1f77b4 0%, #2ca02c 100%);
        }

        /* 标签页样式 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
            background-color: #f0f2f6;
        }

        .stTabs [aria-selected="true"] {
            background-color: #1f77b4;
            color: white;
        }

        /* 数据表格样式 */
        .dataframe {
            font-size: 0.9rem;
        }

        /* 提示框样式 */
        .stAlert {
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

# 初始化session state
def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'platform' not in st.session_state:
        st.session_state.platform = FinanceEducationPlatform()
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = get_db_manager()
    if 'mcp_client' not in st.session_state:
        st.session_state.mcp_client = get_mcp_client()
    if 'current_module' not in st.session_state:
        st.session_state.current_module = None
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []

# 主页面
def main_page():
    # 加载自定义CSS
    load_custom_css()

    # 标题
    st.markdown('<h1 class="main-title">📊 金融教学平台</h1>', unsafe_allow_html=True)

    # 欢迎信息
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("""
        🎓 **欢迎来到金融教学平台**

        基于54个专业MCP工具，提供真实的金融数据和实战操作环境。
        从基金入门到投资组合构建，循序渐进掌握金融投资技能。
        """)

    st.markdown("---")

    # 功能模块展示
    st.subheader("🎯 核心功能模块")

    # 创建3列展示6个模块
    col1, col2, col3 = st.columns(3)

    modules = [
        {"icon": "📊", "name": "基金投资入门", "desc": "学习基金基础知识", "color": "#1f77b4"},
        {"icon": "🎯", "name": "投资组合构建", "desc": "构建个人投资组合", "color": "#ff7f0e"},
        {"icon": "⚠️", "name": "风险管理", "desc": "评估和控制风险", "color": "#2ca02c"},
        {"icon": "📰", "name": "市场分析", "desc": "追踪市场动态", "color": "#d62728"},
        {"icon": "💰", "name": "财务规划", "desc": "家庭财务管理", "color": "#9467bd"},
        {"icon": "📈", "name": "策略研究", "desc": "研究投资策略", "color": "#8c564b"}
    ]

    for i, module in enumerate(modules):
        col = [col1, col2, col3][i % 3]
        with col:
            st.markdown(f"""
                <div class="info-card">
                    <h3>{module['icon']} {module['name']}</h3>
                    <p style="color: #666;">{module['desc']}</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # 平台统计数据
    st.subheader("📊 平台数据")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <h2>54</h2>
                <p>专业工具</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <h2>6</h2>
                <p>教学模块</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <h2>30+</h2>
                <p>实战案例</p>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <h2>12周</h2>
                <p>学习周期</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 快速开始
    st.subheader("🚀 快速开始")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🎓 学生用户

        1. 选择左侧菜单的学习模块
        2. 按照课程顺序学习
        3. 完成实战练习
        4. 查看学习进度

        **推荐路径**: 基金入门 → 组合构建 → 风险管理
        """)

    with col2:
        st.markdown("""
        ### 👨‍🏫 教师用户

        1. 使用教学案例进行演示
        2. 布置实战作业
        3. 跟踪学生进度
        4. 查看学习报告

        **教学指南**: 查看教师使用手册
        """)

    # 页脚
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 2rem;">
            <p>📧 support@example.com</p>
            <p style="font-size: 0.8rem;">© 2026 金融教学平台 | Version 2.0.0</p>
        </div>
    """, unsafe_allow_html=True)

# 运行应用
def main():
    init_session_state()

    # 侧边栏
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1f77b4/ffffff?text=金融教学平台", use_container_width=True)
        st.markdown("---")

        # 用户信息
        if st.session_state.authenticated and st.session_state.user:
            user = st.session_state.user
            st.markdown("### 👤 用户信息")
            st.markdown(f"""
                **用户名**: {user.get('username', 'N/A')}
                **姓名**: {user.get('full_name', 'N/A')}
                **角色**: {user.get('role', 'student')}
            """)

            if st.button("🚪 退出登录", use_container_width=True):
                logout_user()
        else:
            st.warning("请先登录")

        st.markdown("---")

        # 导航菜单
        st.markdown("### 📚 功能导航")

        page = st.radio(
            "选择功能",
            ["🏠 首页", "📊 基金分析", "🎯 组合构建", "📈 学习进度", "💡 教学案例", "⚙️ 设置"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        # 学习进度概览（仅登录用户可见）
        if st.session_state.authenticated:
            st.markdown("### 📊 学习进度")
            user_id = st.session_state.user.get('id')
            db = st.session_state.db_manager
            progress_data = db.get_user_progress(user_id)

            if progress_data:
                total_lessons = len(progress_data)
                completed = sum(1 for p in progress_data if p['status'] == 'completed')
                progress_pct = (completed / total_lessons * 100) if total_lessons > 0 else 0

                st.progress(progress_pct / 100)
                st.caption(f"已完成 {completed}/{total_lessons} 课")

                # 显示平均分
                scores = [p['score'] for p in progress_data if p['score'] is not None]
                if scores:
                    avg_score = sum(scores) / len(scores)
                    st.caption(f"平均分: {avg_score:.1f}")
            else:
                st.info("暂无学习记录")

            st.markdown("---")

        # 快捷操作
        st.markdown("### ⚡ 快捷操作")
        if st.button("🔍 搜索基金", use_container_width=True):
            st.session_state.quick_action = "search_fund"
        if st.button("📊 查看报告", use_container_width=True):
            st.session_state.quick_action = "view_report"

    # 检查用户认证状态
    if not st.session_state.authenticated:
        load_custom_css()
        show_login_page()
        return

    # 主内容区（仅登录用户可见）
    if page == "🏠 首页":
        main_page()
    elif page == "📊 基金分析":
        from pages import fund_analysis
        fund_analysis.show()
    elif page == "🎯 组合构建":
        from pages import portfolio_builder
        portfolio_builder.show()
    elif page == "📈 学习进度":
        from pages import progress_tracker
        progress_tracker.show()
    elif page == "💡 教学案例":
        from pages import teaching_cases
        teaching_cases.show()
    elif page == "⚙️ 设置":
        from pages import settings
        settings.show()

if __name__ == "__main__":
    main()
