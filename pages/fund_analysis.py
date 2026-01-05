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

        with st.spinner("正在调用MCP API搜索基金..."):
            # 使用MCP API搜索基金
            mcp = st.session_state.mcp_client
            try:
                # 调用真实API
                results = mcp.search_funds(
                    keyword=keyword,
                    category=None if category == "全部" else category,
                    page=0,
                    size=20
                )

                # 检查API返回结果
                if not results or len(results) == 0:
                    st.warning(f"未找到与 '{keyword}' 相关的基金，请尝试其他关键词")
                    return

                st.success(f"✅ 从MCP API获取到 {len(results)} 只基金")

            except Exception as e:
                st.error(f"❌ MCP API调用失败: {str(e)}")
                st.info("请检查网络连接或API配置，稍后重试")
                return

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

def show_fund_detail(fund_code):
    """显示基金详情"""
    st.markdown("---")
    st.subheader(f"基金详情: {fund_code}")

    with st.spinner("正在从MCP API获取基金详情..."):
        mcp = st.session_state.mcp_client
        try:
            # 调用MCP API获取基金详细信息
            fund_info = mcp.get_fund_info(fund_code)

            if not fund_info:
                st.error(f"未找到基金 {fund_code} 的详细信息")
                return

            st.success("✅ 从MCP API获取基金详情成功")

            # 基本信息
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                nav = fund_info.get('netValue', 0)
                nav_change = fund_info.get('dayGrowth', 0)
                st.metric("最新净值", f"{nav:.4f}", f"{nav_change:+.2f}%")
            with col2:
                size = fund_info.get('fundSize', 0)
                st.metric("基金规模", f"{size:.1f}亿")
            with col3:
                establish_date = fund_info.get('establishDate', 'N/A')
                st.metric("成立日期", establish_date)
            with col4:
                risk_level = fund_info.get('riskLevel', 'N/A')
                st.metric("风险等级", risk_level)

            # 业绩表现
            st.markdown("### 📈 业绩表现")

            try:
                # 调用MCP API获取基金业绩
                performance = mcp.get_fund_returns(fund_code)

                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    st.metric("近1月", f"{performance.get('1m', 0):+.2f}%")
                with col2:
                    st.metric("近3月", f"{performance.get('3m', 0):+.2f}%")
                with col3:
                    st.metric("近6月", f"{performance.get('6m', 0):+.2f}%")
                with col4:
                    st.metric("近1年", f"{performance.get('1y', 0):+.2f}%")
                with col5:
                    st.metric("成立以来", f"{performance.get('since_inception', 0):+.2f}%")

            except Exception as e:
                st.warning(f"无法获取业绩数据: {str(e)}")

        except Exception as e:
            st.error(f"❌ MCP API调用失败: {str(e)}")
            st.info("请检查基金代码是否正确，或稍后重试")

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
        if not fund_code:
            st.warning("请输入基金代码")
            return

        with st.spinner("正在从MCP API获取净值数据..."):
            mcp = st.session_state.mcp_client
            try:
                # 调用MCP API获取基金净值历史
                nav_history = mcp.get_fund_nav_history(fund_code, time_range=time_range)

                if not nav_history or len(nav_history) == 0:
                    st.warning(f"未找到基金 {fund_code} 的净值数据")
                    return

                st.success(f"✅ 从MCP API获取到 {len(nav_history)} 条净值记录")

                # 提取日期和净值数据
                dates = [item['date'] for item in nav_history]
                nav_data = [item['nav'] for item in nav_history]

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

                # 如果选择了对比基准，获取基准数据
                if compare_index != "无":
                    try:
                        index_data = mcp.get_index_data(compare_index, time_range=time_range)
                        if index_data and len(index_data) > 0:
                            index_dates = [item['date'] for item in index_data]
                            index_values = [item['value'] for item in index_data]
                            fig.add_trace(go.Scatter(
                                x=index_dates,
                                y=index_values,
                                mode='lines',
                                name=compare_index,
                                line=dict(color='#ff7f0e', width=2, dash='dash')
                            ))
                    except Exception as e:
                        st.info(f"无法获取 {compare_index} 数据: {str(e)}")

                fig.update_layout(
                    title=f"{fund_code} 净值走势图",
                    xaxis_title="日期",
                    yaxis_title="累计净值",
                    hovermode='x unified',
                    height=500,
                    template="plotly_white"
                )

                st.plotly_chart(fig, use_container_width=True)

                # 获取统计指标
                st.markdown("### 📊 统计指标")

                try:
                    # 调用MCP API获取基金性能指标
                    metrics = mcp.get_fund_performance(fund_code, time_range=time_range)

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("区间收益率", f"{metrics.get('return', 0):.2f}%")
                    with col2:
                        st.metric("年化收益率", f"{metrics.get('annual_return', 0):.2f}%")
                    with col3:
                        st.metric("最大回撤", f"{metrics.get('max_drawdown', 0):.2f}%")
                    with col4:
                        st.metric("波动率", f"{metrics.get('volatility', 0):.2f}%")
                except Exception as e:
                    st.warning(f"无法获取性能指标: {str(e)}")

            except Exception as e:
                st.error(f"❌ MCP API调用失败: {str(e)}")
                st.info("请检查基金代码是否正确，或稍后重试")

def show_holding_analysis():
    st.subheader("💼 持仓结构分析")

    fund_code = st.text_input("基金代码", value="110022", key="holding_fund_code")

    if st.button("📊 查看持仓", type="primary", use_container_width=True):
        if not fund_code:
            st.warning("请输入基金代码")
            return

        with st.spinner("正在从MCP API获取持仓数据..."):
            mcp = st.session_state.mcp_client
            try:
                # 调用MCP API获取基金持仓
                holdings_data = mcp.get_fund_holdings(fund_code)

                if not holdings_data:
                    st.error(f"未找到基金 {fund_code} 的持仓数据")
                    return

                st.success("✅ 从MCP API获取持仓数据成功")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### 📈 十大重仓股")

                    # 从API数据构建DataFrame
                    top_holdings = holdings_data.get('top_holdings', [])
                    if top_holdings:
                        holdings_df = pd.DataFrame(top_holdings)
                        st.dataframe(
                            holdings_df,
                            column_config={
                                'ratio': st.column_config.ProgressColumn('持仓占比(%)', min_value=0, max_value=10),
                                'change': st.column_config.NumberColumn('较上期(%)', format="%.2f")
                            },
                            hide_index=True,
                            use_container_width=True
                        )
                    else:
                        st.info("暂无重仓股数据")

                with col2:
                    st.markdown("#### 🏭 行业分布")

                    # 从API数据获取行业分布
                    industry_dist = holdings_data.get('industry_distribution', [])
                    if industry_dist:
                        industries_df = pd.DataFrame(industry_dist)

                        fig = px.pie(
                            industries_df,
                            values='ratio',
                            names='industry',
                            title='行业分布',
                            hole=0.4
                        )

                        fig.update_traces(
                            textposition='inside',
                            textinfo='percent+label'
                        )

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("暂无行业分布数据")

                # 资产配置
                st.markdown("#### 💰 资产配置")

                asset_allocation = holdings_data.get('asset_allocation', [])
                if asset_allocation:
                    asset_df = pd.DataFrame(asset_allocation)

                    fig = go.Figure(data=[
                        go.Bar(
                            x=asset_df['asset_type'],
                            y=asset_df['ratio'],
                            text=asset_df['ratio'].apply(lambda x: f'{x:.1f}%'),
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
                else:
                    st.info("暂无资产配置数据")

            except Exception as e:
                st.error(f"❌ MCP API调用失败: {str(e)}")
                st.info("请检查基金代码是否正确，或稍后重试")

def show_comprehensive_diagnosis():
    st.subheader("📊 综合诊断")

    fund_code = st.text_input("基金代码", value="110022", key="diag_fund_code")

    if st.button("🔍 开始诊断", type="primary", use_container_width=True):
        if not fund_code:
            st.warning("请输入基金代码")
            return

        with st.spinner("正在从MCP API获取基金诊断数据..."):
            mcp = st.session_state.mcp_client
            try:
                # 调用MCP API获取基金诊断信息
                diagnosis = mcp.get_fund_diagnosis(fund_code)

                if not diagnosis:
                    st.error(f"未找到基金 {fund_code} 的诊断数据")
                    return

                st.success("✅ 从MCP API获取基金诊断数据成功")

                # 雷达图 - 多维度评分
                st.markdown("### 🎯 综合评分")

                # 从API获取评分数据
                ratings = diagnosis.get('ratings', {})
                categories = ['收益能力', '风险控制', '选股能力', '择时能力', '稳定性']
                scores = [
                    ratings.get('return_ability', 0),
                    ratings.get('risk_control', 0),
                    ratings.get('stock_picking', 0),
                    ratings.get('timing', 0),
                    ratings.get('stability', 0)
                ]

                # 获取同类平均
                peer_avg = diagnosis.get('peer_average', {})
                peer_scores = [
                    peer_avg.get('return_ability', 70),
                    peer_avg.get('risk_control', 70),
                    peer_avg.get('stock_picking', 70),
                    peer_avg.get('timing', 70),
                    peer_avg.get('stability', 70)
                ]

                fig = go.Figure()

                fig.add_trace(go.Scatterpolar(
                    r=scores,
                    theta=categories,
                    fill='toself',
                    name='该基金',
                    line_color='#1f77b4'
                ))

                fig.add_trace(go.Scatterpolar(
                    r=peer_scores,
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
                    # 从API获取优势
                    strengths = diagnosis.get('strengths', [])
                    if strengths:
                        strengths_text = "**✅ 优势**\n" + "\n".join([f"- {s}" for s in strengths])
                        st.success(strengths_text)
                    else:
                        st.info("暂无优势分析")

                with col2:
                    # 从API获取风险提示
                    risks = diagnosis.get('risks', [])
                    if risks:
                        risks_text = "**⚠️ 风险提示**\n" + "\n".join([f"- {r}" for r in risks])
                        st.warning(risks_text)
                    else:
                        st.info("暂无风险提示")

                # 投资建议
                st.markdown("### 💡 投资建议")

                suggestions = diagnosis.get('suggestions', {})
                if suggestions:
                    suggestion_text = f"""
                    **适合人群**: {suggestions.get('suitable_investors', 'N/A')}

                    **建议配置比例**: {suggestions.get('allocation_ratio', 'N/A')}

                    **投资方式**: {suggestions.get('investment_method', 'N/A')}

                    **持有建议**: {suggestions.get('holding_advice', 'N/A')}

                    **风险提示**: 市场有风险，投资需谨慎
                    """
                    st.info(suggestion_text)
                else:
                    st.info("**风险提示**: 市场有风险，投资需谨慎")

            except Exception as e:
                st.error(f"❌ MCP API调用失败: {str(e)}")
                st.info("请检查基金代码是否正确，或稍后重试")

# 辅助函数已移除 - 所有数据均通过MCP API获取
