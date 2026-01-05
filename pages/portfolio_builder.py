"""
投资组合构建页面
Portfolio Builder Page
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

def show():
    st.markdown('<h1 class="main-title">🎯 投资组合构建工具</h1>', unsafe_allow_html=True)

    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["💰 资产配置", "📋 基金选择", "📊 组合分析", "🎲 模拟预测"])

    with tab1:
        show_asset_allocation()

    with tab2:
        show_fund_selection()

    with tab3:
        show_portfolio_analysis()

    with tab4:
        show_monte_carlo()

def show_asset_allocation():
    st.subheader("💰 资产配置方案")

    st.info("""
    根据您的投资目标和风险偏好，制定合理的资产配置方案。
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📝 投资信息")

        total_amount = st.number_input(
            "投资金额(元)",
            min_value=10000,
            max_value=10000000,
            value=500000,
            step=10000
        )

        risk_level = st.select_slider(
            "风险承受能力",
            options=["保守型", "稳健型", "平衡型", "成长型", "进取型"],
            value="稳健型"
        )

        invest_period = st.selectbox(
            "投资期限",
            ["活期", "1年以内", "1-3年", "3-5年", "5年以上"]
        )

        target_return = st.slider(
            "目标年化收益率(%)",
            min_value=3.0,
            max_value=20.0,
            value=8.0,
            step=0.5
        )

    with col2:
        st.markdown("#### 📊 配置方案")

        # 根据风险偏好生成配置方案
        allocation = get_allocation_by_risk(risk_level)

        # 显示饼图
        fig = px.pie(
            values=list(allocation.values()),
            names=list(allocation.keys()),
            title="资产配置比例",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )

        st.plotly_chart(fig, use_container_width=True)

        # 显示具体金额
        st.markdown("#### 💵 具体金额")
        for asset, ratio in allocation.items():
            amount = total_amount * ratio / 100
            st.metric(asset, f"¥{amount:,.0f}", f"{ratio}%")

    # 生成配置方案
    if st.button("🎯 生成配置方案", type="primary", use_container_width=True):
        st.success("✅ 配置方案已生成")

        # 保存到session state
        st.session_state.allocation = {
            'total_amount': total_amount,
            'risk_level': risk_level,
            'allocation': allocation
        }

        # 显示详细方案
        show_allocation_detail(total_amount, risk_level, allocation, target_return)

def show_allocation_detail(total_amount, risk_level, allocation, target_return):
    """显示详细配置方案"""
    st.markdown("---")
    st.markdown("### 📋 配置方案详情")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("总投资金额", f"¥{total_amount:,.0f}")
    with col2:
        st.metric("风险等级", risk_level)
    with col3:
        st.metric("目标收益", f"{target_return}%/年")

    # 预期表现
    st.markdown("### 📈 预期表现")

    performance_data = {
        '指标': ['预期年化收益', '预期最大回撤', '预期波动率', '夏普比率'],
        '乐观情景': ['10-12%', '-10%', '10%', '0.9'],
        '基准情景': ['7-9%', '-15%', '12%', '0.7'],
        '悲观情景': ['4-6%', '-20%', '15%', '0.4']
    }

    df = pd.DataFrame(performance_data)
    st.dataframe(df, hide_index=True, use_container_width=True)

    # 投资建议
    st.markdown("### 💡 投资建议")

    recommendations = get_recommendations(risk_level)

    col1, col2 = st.columns(2)

    with col1:
        st.success(f"""
        **✅ 推荐策略**

        {recommendations['strategy']}
        """)

    with col2:
        st.warning(f"""
        **⚠️ 风险提示**

        {recommendations['risk']}
        """)

def show_fund_selection():
    st.subheader("📋 基金选择")

    # 检查是否已有配置方案
    if 'allocation' not in st.session_state:
        st.warning("⚠️ 请先在「资产配置」页面生成配置方案")
        return

    allocation = st.session_state.allocation
    st.info(f"当前配置: {allocation['risk_level']} | 总金额: ¥{allocation['total_amount']:,.0f}")

    # 为每个资产类别选择基金
    for asset_type, ratio in allocation['allocation'].items():
        amount = allocation['total_amount'] * ratio / 100

        with st.expander(f"📊 {asset_type} ({ratio}% / ¥{amount:,.0f})", expanded=True):
            show_fund_selector(asset_type, amount)

    # 确认组合
    if st.button("✅ 确认组合", type="primary", use_container_width=True):
        if 'portfolio_funds' in st.session_state and st.session_state.portfolio_funds:
            st.success("✅ 投资组合已确认！可以前往「组合分析」页面查看详细分析。")
            st.balloons()
        else:
            st.error("❌ 请至少选择一只基金")

def show_fund_selector(asset_type, amount):
    """基金选择器"""
    # 根据资产类型推荐基金
    recommended_funds = get_recommended_funds(asset_type)

    # 显示推荐基金
    st.markdown(f"**推荐{asset_type}基金:**")

    for fund in recommended_funds:
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])

        with col1:
            st.write(f"**{fund['name']}**")
            st.caption(f"{fund['code']}")

        with col2:
            st.metric("净值", fund['nav'])

        with col3:
            st.metric("今年来", fund['ytd'])

        with col4:
            st.metric("风险", fund['risk'])

        with col5:
            if st.button("选择", key=f"select_{fund['code']}"):
                add_to_portfolio(fund, amount)

def add_to_portfolio(fund, amount):
    """添加基金到组合"""
    if 'portfolio_funds' not in st.session_state:
        st.session_state.portfolio_funds = []

    # 检查是否已存在
    existing = [f for f in st.session_state.portfolio_funds if f['code'] == fund['code']]

    if not existing:
        fund_with_amount = fund.copy()
        fund_with_amount['amount'] = amount
        st.session_state.portfolio_funds.append(fund_with_amount)
        st.success(f"✅ 已添加 {fund['name']}")
    else:
        st.warning(f"⚠️ {fund['name']} 已在组合中")

def show_portfolio_analysis():
    st.subheader("📊 组合分析")

    # 检查是否有组合
    if 'portfolio_funds' not in st.session_state or not st.session_state.portfolio_funds:
        st.warning("⚠️ 请先在「基金选择」页面构建组合")
        return

    portfolio = st.session_state.portfolio_funds

    # 组合概览
    st.markdown("### 📋 组合概览")

    total_amount = sum(f['amount'] for f in portfolio)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("基金数量", f"{len(portfolio)}只")
    with col2:
        st.metric("总金额", f"¥{total_amount:,.0f}")
    with col3:
        st.metric("预期收益", "7.5%/年")
    with col4:
        st.metric("风险评级", "中等")

    # 持仓明细
    st.markdown("### 📊 持仓明细")

    portfolio_df = pd.DataFrame([
        {
            '基金代码': f['code'],
            '基金名称': f['name'],
            '投资金额': f['amount'],
            '占比': f['amount'] / total_amount * 100,
            '预期收益': f.get('expected_return', 8.0)
        }
        for f in portfolio
    ])

    st.dataframe(
        portfolio_df,
        column_config={
            '投资金额': st.column_config.NumberColumn('投资金额(元)', format="¥%.0f"),
            '占比': st.column_config.ProgressColumn('占比(%)', min_value=0, max_value=100, format="%.1f"),
            '预期收益': st.column_config.NumberColumn('预期收益(%)', format="%.1f")
        },
        hide_index=True,
        use_container_width=True
    )

    # 组合分析图表
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💰 资产分布")

        fig = px.pie(
            portfolio_df,
            values='投资金额',
            names='基金名称',
            title='持仓分布'
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 📈 预期收益分布")

        fig = go.Figure(data=[
            go.Bar(
                x=portfolio_df['基金名称'],
                y=portfolio_df['预期收益'],
                text=portfolio_df['预期收益'].apply(lambda x: f'{x:.1f}%'),
                textposition='outside',
                marker_color='#1f77b4'
            )
        ])

        fig.update_layout(
            yaxis_title='预期收益(%)',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    # 风险分析
    st.markdown("### ⚠️ 风险分析")

    show_risk_metrics(portfolio)

    # 优化建议
    st.markdown("### 💡 优化建议")

    show_optimization_suggestions(portfolio)

def show_risk_metrics(portfolio):
    """显示风险指标"""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("组合波动率", "12.5%")
    with col2:
        st.metric("最大回撤", "-15.3%")
    with col3:
        st.metric("夏普比率", "0.72")

    # 相关性矩阵（模拟）
    st.markdown("#### 📊 相关性矩阵")

    n = len(portfolio)
    corr_matrix = np.random.rand(n, n)
    corr_matrix = (corr_matrix + corr_matrix.T) / 2
    np.fill_diagonal(corr_matrix, 1.0)

    fund_names = [f['name'][:8] for f in portfolio]

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=fund_names,
        y=fund_names,
        colorscale='RdYlGn_r',
        zmin=-1,
        zmax=1
    ))

    fig.update_layout(
        title='基金相关性热力图',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

def show_optimization_suggestions(portfolio):
    """显示优化建议"""
    suggestions = [
        ("✅ 资产分散度", "良好", "组合包含多只基金，分散度较好"),
        ("⚠️ 相关性", "需关注", "部分基金相关性较高，建议增加低相关资产"),
        ("✅ 风险收益比", "合理", "组合风险收益比处于合理区间"),
        ("💡 再平衡", "建议", "建议每半年进行一次再平衡")
    ]

    for title, status, desc in suggestions:
        if status == "良好":
            st.success(f"**{title}**: {status} - {desc}")
        elif status == "需关注":
            st.warning(f"**{title}**: {status} - {desc}")
        else:
            st.info(f"**{title}**: {status} - {desc}")

def show_monte_carlo():
    st.subheader("🎲 蒙特卡洛模拟")

    st.info("""
    蒙特卡洛模拟通过大量随机抽样，预测投资组合未来可能的表现。
    """)

    # 检查是否有组合
    if 'portfolio_funds' not in st.session_state or not st.session_state.portfolio_funds:
        st.warning("⚠️ 请先在「基金选择」页面构建组合")
        return

    col1, col2 = st.columns(2)

    with col1:
        years = st.slider("投资年限", 1, 10, 5)
        simulations = st.select_slider(
            "模拟次数",
            options=[1000, 5000, 10000, 50000],
            value=10000
        )

    with col2:
        frequency = st.selectbox(
            "模拟频率",
            ["日度", "周度", "月度", "年度"]
        )

    if st.button("🎲 开始模拟", type="primary", use_container_width=True):
        with st.spinner("正在模拟..."):
            # 模拟结果
            results = run_monte_carlo_simulation(years, simulations)

            # 显示结果
            show_simulation_results(results, years)

def run_monte_carlo_simulation(years, simulations):
    """运行蒙特卡洛模拟"""
    # 模拟参数
    initial_value = sum(f['amount'] for f in st.session_state.portfolio_funds)
    mean_return = 0.075  # 7.5%年化
    std_return = 0.15    # 15%波动率

    # 生成模拟路径
    np.random.seed(42)
    days = years * 252  # 交易日

    returns = np.random.normal(mean_return/252, std_return/np.sqrt(252), (simulations, days))
    price_paths = initial_value * np.exp(np.cumsum(returns, axis=1))

    # 计算终值
    final_values = price_paths[:, -1]

    return {
        'initial_value': initial_value,
        'paths': price_paths,
        'final_values': final_values,
        'years': years
    }

def show_simulation_results(results, years):
    """显示模拟结果"""
    st.markdown("### 📊 模拟结果")

    initial = results['initial_value']
    final_values = results['final_values']

    # 统计指标
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("初始投资", f"¥{initial:,.0f}")
    with col2:
        median_final = np.median(final_values)
        st.metric(
            "中位数终值",
            f"¥{median_final:,.0f}",
            f"+{(median_final/initial-1)*100:.1f}%"
        )
    with col3:
        percentile_10 = np.percentile(final_values, 10)
        st.metric("10%分位", f"¥{percentile_10:,.0f}")
    with col4:
        percentile_90 = np.percentile(final_values, 90)
        st.metric("90%分位", f"¥{percentile_90:,.0f}")

    # 终值分布图
    st.markdown("#### 📊 终值分布")

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=final_values,
        nbinsx=50,
        name='终值分布',
        marker_color='#1f77b4',
        opacity=0.7
    ))

    # 添加百分位线
    fig.add_vline(x=np.percentile(final_values, 10), line_dash="dash", line_color="red",
                  annotation_text="10%分位")
    fig.add_vline(x=np.percentile(final_values, 50), line_dash="dash", line_color="green",
                  annotation_text="50%分位")
    fig.add_vline(x=np.percentile(final_values, 90), line_dash="dash", line_color="blue",
                  annotation_text="90%分位")

    fig.update_layout(
        title=f'{years}年后投资终值分布',
        xaxis_title='终值(元)',
        yaxis_title='频数',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # 概率分析
    st.markdown("#### 🎯 概率分析")

    prob_data = {
        '收益区间': ['亏损', '0-10%', '10-30%', '30-50%', '50-100%', '>100%'],
        '概率': [
            f"{(final_values < initial).sum() / len(final_values) * 100:.1f}%",
            f"{((final_values >= initial) & (final_values < initial * 1.1)).sum() / len(final_values) * 100:.1f}%",
            f"{((final_values >= initial * 1.1) & (final_values < initial * 1.3)).sum() / len(final_values) * 100:.1f}%",
            f"{((final_values >= initial * 1.3) & (final_values < initial * 1.5)).sum() / len(final_values) * 100:.1f}%",
            f"{((final_values >= initial * 1.5) & (final_values < initial * 2.0)).sum() / len(final_values) * 100:.1f}%",
            f"{(final_values >= initial * 2.0).sum() / len(final_values) * 100:.1f}%"
        ]
    }

    df = pd.DataFrame(prob_data)
    st.dataframe(df, hide_index=True, use_container_width=True)

    # 结论
    st.success(f"""
    **📋 模拟结论**

    - 有 **{(final_values >= initial).sum() / len(final_values) * 100:.1f}%** 的概率实现正收益
    - 中位数年化收益率约为 **{((np.median(final_values)/initial)**(1/years)-1)*100:.1f}%**
    - 有 90% 的概率终值在 **¥{percentile_10:,.0f}** 到 **¥{percentile_90:,.0f}** 之间
    """)

# 辅助函数

def get_allocation_by_risk(risk_level):
    """根据风险等级返回资产配置"""
    allocations = {
        "保守型": {"货币基金": 50, "债券基金": 40, "股票基金": 10},
        "稳健型": {"货币基金": 20, "债券基金": 50, "股票基金": 30},
        "平衡型": {"货币基金": 10, "债券基金": 40, "股票基金": 50},
        "成长型": {"货币基金": 5, "债券基金": 25, "股票基金": 70},
        "进取型": {"货币基金": 0, "债券基金": 10, "股票基金": 90}
    }
    return allocations.get(risk_level, allocations["稳健型"])

def get_recommendations(risk_level):
    """获取投资建议"""
    recommendations = {
        "保守型": {
            "strategy": "- 以货币和债券基金为主\n- 保持充足流动性\n- 定期再平衡\n- 控制股票仓位",
            "risk": "- 收益相对较低\n- 需关注利率风险\n- 通胀侵蚀风险"
        },
        "稳健型": {
            "strategy": "- 债券为主，股票增强\n- 分散投资\n- 长期持有\n- 定期定投",
            "risk": "- 市场波动影响\n- 注意再平衡时机\n- 控制回撤幅度"
        },
        "平衡型": {
            "strategy": "- 股债均衡配置\n- 适度分散\n- 波段操作\n- 动态调整",
            "risk": "- 双向市场风险\n- 需要专业判断\n- 时机把握重要"
        },
        "成长型": {
            "strategy": "- 以股票基金为主\n- 精选优质基金\n- 长期持有\n- 承受波动",
            "risk": "- 短期波动较大\n- 最大回撤可能较深\n- 需要强心理承受力"
        },
        "进取型": {
            "strategy": "- 全仓股票基金\n- 追求高收益\n- 接受高波动\n- 长期投资",
            "risk": "- 高波动高风险\n- 可能面临较大亏损\n- 需要专业知识"
        }
    }
    return recommendations.get(risk_level, recommendations["稳健型"])

def get_recommended_funds(asset_type):
    """根据资产类型返回推荐基金"""
    funds_db = {
        "股票基金": [
            {"code": "110022", "name": "易方达消费行业", "nav": "4.235", "ytd": "+15.67%", "risk": "中高"},
            {"code": "161725", "name": "招商中证白酒", "nav": "1.218", "ytd": "+22.34%", "risk": "高"},
            {"code": "163406", "name": "兴全商业模式", "nav": "3.568", "ytd": "+18.92%", "risk": "中高"}
        ],
        "债券基金": [
            {"code": "110008", "name": "易方达稳健收益", "nav": "1.457", "ytd": "+4.23%", "risk": "低"},
            {"code": "050011", "name": "博时信用债券", "nav": "2.345", "ytd": "+3.89%", "risk": "低"},
            {"code": "485111", "name": "工银双利债券", "nav": "1.876", "ytd": "+4.56%", "risk": "低"}
        ],
        "货币基金": [
            {"code": "000704", "name": "易方达天天理财", "nav": "1.000", "ytd": "+2.34%", "risk": "极低"},
            {"code": "000009", "name": "易方达天天增利", "nav": "1.000", "ytd": "+2.45%", "risk": "极低"}
        ]
    }

    return funds_db.get(asset_type, [])
