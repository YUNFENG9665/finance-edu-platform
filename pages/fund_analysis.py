"""
基金分析页面
Fund Analysis Page
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

def show():
    st.markdown('<h1 class="main-title">📊 基金分析工具</h1>', unsafe_allow_html=True)

    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 基金搜索", "📈 净值分析", "💼 持仓分析", "📊 综合诊断"])

    # 标签页1: 基金搜索
    with tab1:
        show_fund_search()

    # 标签页2: 净值分析
    with tab2:
        show_nav_analysis()

    # 标签页3: 持仓分析
    with tab3:
        show_holding_analysis()

    # 标签页4: 综合诊断
    with tab4:
        show_comprehensive_diagnosis()

def show_fund_search():
    st.subheader("🔍 搜索基金")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        keyword = st.text_input("输入基金名称或代码", placeholder="例如: 易方达")

    with col2:
        category = st.selectbox(
            "基金类型",
            ["全部", "偏股型", "债券型", "混合型", "指数型", "QDII型", "货币型"]
        )

    with col3:
        sort_by = st.selectbox(
            "排序方式",
            ["收益率", "成立日期", "基金规模"]
        )

    if st.button("🔍 搜索", type="primary", use_container_width=True):
        if not keyword:
            st.warning("请输入基金名称或代码")
            return

        with st.spinner("正在搜索基金..."):
            # 使用MCP API搜索基金
            mcp = st.session_state.mcp_client
            try:
                # 调用真实API
                api_results = mcp.search_funds(
                    keyword=keyword,
                    category=None if category == "全部" else category,
                    page=0,
                    size=20
                )

                # 如果API返回数据，使用真实数据
                if api_results and len(api_results) > 0:
                    results = api_results
                    st.info("✅ 使用真实MCP API数据")
                else:
                    # API没有返回数据，使用模拟数据作为演示
                    results = generate_mock_fund_list(keyword)
                    if results:
                        st.info("⚠️ API未返回数据，显示模拟数据供演示")
            except Exception as e:
                st.warning(f"API调用失败，使用模拟数据: {str(e)}")
                results = generate_mock_fund_list(keyword)

            if results:
                st.success(f"找到 {len(results)} 只基金")

                # 显示结果表格
                df = pd.DataFrame(results)

                # 格式化显示
                st.dataframe(
                    df,
                    column_config={
                        "fundCode": "基金代码",
                        "fundName": st.column_config.TextColumn("基金名称", width="large"),
                        "category": "类型",
                        "netValue": st.column_config.NumberColumn("最新净值", format="%.4f"),
                        "dayGrowth": st.column_config.NumberColumn("日涨跌", format="%.2f%%"),
                        "yearGrowth": st.column_config.NumberColumn("今年以来", format="%.2f%%"),
                        "riskLevel": st.column_config.ProgressColumn("风险等级", min_value=1, max_value=5)
                    },
                    hide_index=True,
                    use_container_width=True
                )

                # 选择基金查看详情
                st.markdown("---")
                selected_code = st.selectbox(
                    "选择一只基金查看详情",
                    options=df['fundCode'].tolist(),
                    format_func=lambda x: f"{x} - {df[df['fundCode']==x]['fundName'].values[0]}"
                )

                if st.button("查看详情", use_container_width=True):
                    st.session_state.selected_fund = selected_code
                    show_fund_detail(selected_code)
            else:
                st.warning("未找到相关基金，请调整搜索条件")

def show_fund_detail(fund_code):
    """显示基金详情"""
    st.markdown("---")
    st.subheader(f"基金详情: {fund_code}")

    # 基本信息
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("最新净值", "2.3456", "0.23%")
    with col2:
        st.metric("基金规模", "50.2亿", "-2.1亿")
    with col3:
        st.metric("成立日期", "2018-06-20")
    with col4:
        st.metric("风险等级", "中高风险")

    # 业绩表现
    st.markdown("### 📈 业绩表现")

    col1, col2, col3, col4, col5 = st.columns(5)

    metrics = [
        ("近1月", "+3.45%"),
        ("近3月", "+8.67%"),
        ("近6月", "+15.23%"),
        ("近1年", "+25.34%"),
        ("成立以来", "+134.56%")
    ]

    for col, (label, value) in zip([col1, col2, col3, col4, col5], metrics):
        with col:
            st.metric(label, value)

def show_nav_analysis():
    st.subheader("📈 净值走势分析")

    # 基金选择
    fund_code = st.text_input("基金代码", value="110022", key="nav_fund_code")

    col1, col2 = st.columns(2)

    with col1:
        time_range = st.selectbox(
            "时间范围",
            ["近1月", "近3月", "近6月", "近1年", "近3年", "成立以来"]
        )

    with col2:
        compare_index = st.selectbox(
            "对比基准",
            ["无", "沪深300", "中证500", "创业板指"]
        )

    if st.button("📊 分析", type="primary", use_container_width=True):
        # 生成模拟数据
        dates, nav_data = generate_mock_nav_data(time_range)

        # 创建图表
        fig = go.Figure()

        # 添加净值线
        fig.add_trace(go.Scatter(
            x=dates,
            y=nav_data,
            mode='lines',
            name='累计净值',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ))

        # 如果选择了对比基准
        if compare_index != "无":
            index_data = nav_data * np.random.uniform(0.95, 1.05, len(nav_data))
            fig.add_trace(go.Scatter(
                x=dates,
                y=index_data,
                mode='lines',
                name=compare_index,
                line=dict(color='#ff7f0e', width=2, dash='dash')
            ))

        fig.update_layout(
            title="净值走势图",
            xaxis_title="日期",
            yaxis_title="累计净值",
            hovermode='x unified',
            height=500,
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)

        # 统计指标
        st.markdown("### 📊 统计指标")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("区间收益率", "+25.34%")
        with col2:
            st.metric("年化收益率", "+18.76%")
        with col3:
            st.metric("最大回撤", "-23.45%")
        with col4:
            st.metric("波动率", "18.23%")

def show_holding_analysis():
    st.subheader("💼 持仓结构分析")

    fund_code = st.text_input("基金代码", value="110022", key="holding_fund_code")

    if st.button("📊 查看持仓", type="primary", use_container_width=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📈 十大重仓股")

            # 模拟十大重仓股数据
            holdings = pd.DataFrame({
                '股票代码': ['600519', '000858', '600036', '601318', '000333',
                           '002475', '600276', '603288', '000568', '002594'],
                '股票名称': ['贵州茅台', '五粮液', '招商银行', '中国平安', '美的集团',
                           '立讯精密', '恒瑞医药', '海天味业', '泸州老窖', '比亚迪'],
                '持仓占比': [8.45, 6.23, 5.67, 4.89, 4.32, 3.98, 3.76, 3.45, 3.21, 2.98],
                '较上期': [0.23, -0.15, 0.45, 0.12, -0.08, 0.34, -0.11, 0.19, 0.06, 0.28]
            })

            st.dataframe(
                holdings,
                column_config={
                    '持仓占比': st.column_config.ProgressColumn('持仓占比(%)', min_value=0, max_value=10),
                    '较上期': st.column_config.NumberColumn('较上期(%)', format="%.2f")
                },
                hide_index=True,
                use_container_width=True
            )

        with col2:
            st.markdown("#### 🏭 行业分布")

            # 行业分布饼图
            industries = pd.DataFrame({
                '行业': ['食品饮料', '金融', '医药', '电子', '家电', '其他'],
                '占比': [28.5, 22.3, 15.6, 12.4, 10.2, 11.0]
            })

            fig = px.pie(
                industries,
                values='占比',
                names='行业',
                title='行业分布',
                hole=0.4
            )

            fig.update_traces(
                textposition='inside',
                textinfo='percent+label'
            )

            st.plotly_chart(fig, use_container_width=True)

        # 资产配置
        st.markdown("#### 💰 资产配置")

        asset_allocation = pd.DataFrame({
            '资产类别': ['股票', '债券', '现金', '其他'],
            '占比': [92.5, 5.3, 1.8, 0.4]
        })

        fig = go.Figure(data=[
            go.Bar(
                x=asset_allocation['资产类别'],
                y=asset_allocation['占比'],
                text=asset_allocation['占比'].apply(lambda x: f'{x}%'),
                textposition='outside',
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            )
        ])

        fig.update_layout(
            title='资产配置比例',
            yaxis_title='占比(%)',
            height=400,
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)

def show_comprehensive_diagnosis():
    st.subheader("📊 综合诊断")

    fund_code = st.text_input("基金代码", value="110022", key="diag_fund_code")

    if st.button("🔍 开始诊断", type="primary", use_container_width=True):
        with st.spinner("正在分析..."):
            # 模拟诊断过程
            import time
            time.sleep(1)

            # 雷达图 - 多维度评分
            st.markdown("### 🎯 综合评分")

            categories = ['收益能力', '风险控制', '选股能力', '择时能力', '稳定性']
            scores = [85, 75, 80, 70, 78]

            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=scores,
                theta=categories,
                fill='toself',
                name='该基金',
                line_color='#1f77b4'
            ))

            fig.add_trace(go.Scatterpolar(
                r=[70, 70, 70, 70, 70],
                theta=categories,
                fill='toself',
                name='同类平均',
                line_color='#ff7f0e',
                opacity=0.5
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                showlegend=True,
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # 诊断结果
            st.markdown("### 📋 诊断结果")

            col1, col2 = st.columns(2)

            with col1:
                st.success("""
                **✅ 优势**
                - 长期业绩优秀，超越同类平均
                - 基金经理经验丰富，管理稳定
                - 持仓结构合理，行业分散充分
                - 费率合理，性价比高
                """)

            with col2:
                st.warning("""
                **⚠️ 风险提示**
                - 股票仓位较高，市场波动影响大
                - 重仓消费行业，行业风险需关注
                - 规模较大，灵活性受限
                - 短期回撤风险偏高
                """)

            # 投资建议
            st.markdown("### 💡 投资建议")

            st.info("""
            **适合人群**: 风险承受能力中高、投资期限3年以上的投资者

            **建议配置比例**: 30-50%（作为组合核心持仓）

            **投资方式**: 建议采用定投方式，平滑风险

            **持有建议**: 长期持有，定期再平衡

            **风险提示**: 市场有风险，投资需谨慎
            """)

# 辅助函数

def generate_mock_fund_list(keyword):
    """生成模拟基金列表"""
    funds = [
        {
            "fundCode": "110022",
            "fundName": "易方达消费行业股票",
            "category": "偏股型",
            "netValue": 4.2350,
            "dayGrowth": 1.23,
            "yearGrowth": 15.67,
            "riskLevel": 4
        },
        {
            "fundCode": "161725",
            "fundName": "招商中证白酒指数",
            "category": "指数型",
            "netValue": 1.2180,
            "dayGrowth": 0.89,
            "yearGrowth": 22.34,
            "riskLevel": 5
        },
        {
            "fundCode": "163406",
            "fundName": "兴全商业模式优选混合",
            "category": "混合型",
            "netValue": 3.5678,
            "dayGrowth": -0.45,
            "yearGrowth": 18.92,
            "riskLevel": 4
        },
        {
            "fundCode": "110008",
            "fundName": "易方达稳健收益债券",
            "category": "债券型",
            "netValue": 1.4567,
            "dayGrowth": 0.05,
            "yearGrowth": 4.23,
            "riskLevel": 2
        }
    ]

    if keyword:
        funds = [f for f in funds if keyword.lower() in f['fundName'].lower()]

    return funds

def generate_mock_nav_data(time_range):
    """生成模拟净值数据"""
    # 根据时间范围确定天数
    days_map = {
        "近1月": 30,
        "近3月": 90,
        "近6月": 180,
        "近1年": 365,
        "近3年": 1095,
        "成立以来": 2000
    }

    days = days_map.get(time_range, 365)

    # 生成日期序列
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i) for i in range(days, 0, -1)]

    # 生成模拟净值数据（随机游走）
    returns = np.random.normal(0.0005, 0.015, days)
    nav_data = 1.0 * np.exp(np.cumsum(returns))

    return dates, nav_data
