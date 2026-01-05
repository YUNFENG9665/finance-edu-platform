"""
教学案例页面
Teaching Cases Page
"""

import streamlit as st

def show():
    st.markdown('<h1 class="main-title">💡 教学案例库</h1>', unsafe_allow_html=True)

    st.info("""
    ### 📚 实战案例学习

    通过真实投资案例，学习如何分析基金、构建组合、评估风险。
    每个案例都包含完整的分析流程和实战工具应用。
    """)

    # 案例列表
    cases = [
        {
            "id": 1,
            "title": "📊 案例1：基金分析实战",
            "subtitle": "易方达蓝筹精选全面分析",
            "level": "初级",
            "duration": "90分钟",
            "tools": 9,
            "desc": "学习如何系统分析一只基金，从基本信息到投资建议",
            "objectives": [
                "掌握7步基金分析框架",
                "学会使用9个MCP工具",
                "能够撰写专业分析报告"
            ]
        },
        {
            "id": 2,
            "title": "🎯 案例2：构建稳健型投资组合",
            "subtitle": "50万元资金的配置方案",
            "level": "中级",
            "duration": "180分钟",
            "tools": 12,
            "desc": "为45岁客户构建稳健型投资组合，学习资产配置方法",
            "objectives": [
                "掌握资产配置的完整流程",
                "学会根据客户需求定制方案",
                "理解风险分散和相关性",
                "掌握组合分析工具的综合运用"
            ]
        },
        {
            "id": 3,
            "title": "💰 案例3：家庭财务规划",
            "subtitle": "三口之家的完整规划",
            "level": "中级",
            "duration": "150分钟",
            "tools": 7,
            "desc": "为三口之家制定完整的财务规划方案",
            "objectives": [
                "掌握家庭财务规划流程",
                "学会现金流管理",
                "能够制定投资方案"
            ]
        },
        {
            "id": 4,
            "title": "⚠️ 案例4：风险管理实战",
            "subtitle": "组合风险评估与优化",
            "level": "高级",
            "duration": "120分钟",
            "tools": 6,
            "desc": "学习如何评估和控制投资组合风险",
            "objectives": [
                "理解风险指标的含义",
                "掌握风险评估方法",
                "学会优化组合降低风险"
            ]
        }
    ]

    # 显示案例卡片
    for case in cases:
        with st.expander(f"{case['title']}", expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"### {case['subtitle']}")
                st.write(case['desc'])

                st.markdown("**📝 学习目标**:")
                for obj in case['objectives']:
                    st.write(f"- {obj}")

            with col2:
                st.metric("难度", case['level'])
                st.metric("时长", case['duration'])
                st.metric("工具数", f"{case['tools']}个")

                if st.button(f"开始学习", key=f"case_{case['id']}"):
                    show_case_detail(case)

    # 快速开始指南
    st.markdown("---")
    st.markdown("### 🚀 如何使用案例")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        #### 1️⃣ 阅读背景

        仔细阅读案例背景和客户需求，理解分析目标。
        """)

    with col2:
        st.markdown("""
        #### 2️⃣ 跟随步骤

        按照案例步骤，使用相应的MCP工具进行分析。
        """)

    with col3:
        st.markdown("""
        #### 3️⃣ 完成练习

        独立完成案例练习，撰写分析报告。
        """)

def show_case_detail(case):
    """显示案例详情"""
    st.markdown("---")
    st.subheader(f"📖 {case['title']} - 详情")

    # 案例导航
    tabs = st.tabs(["📋 案例介绍", "🛠️ 使用工具", "📝 练习题", "💡 参考答案"])

    with tabs[0]:
        show_case_intro(case)

    with tabs[1]:
        show_case_tools(case)

    with tabs[2]:
        show_case_exercises(case)

    with tabs[3]:
        show_case_answer(case)

def show_case_intro(case):
    """案例介绍"""
    st.markdown(f"""
    ### {case['subtitle']}

    **难度等级**: {case['level']}
    **预计时长**: {case['duration']}
    **涉及工具**: {case['tools']}个

    {case['desc']}

    ### 学习目标

    """)

    for obj in case['objectives']:
        st.write(f"✅ {obj}")

    st.markdown("""
    ### 案例文档

    完整案例请参考案例库文档：
    """)

    if case['id'] == 1:
        st.info("📄 `/金融教学应用/案例库/案例1_基金分析实战.md`")
    elif case['id'] == 2:
        st.info("📄 `/金融教学应用/案例库/案例2_构建稳健型投资组合.md`")

def show_case_tools(case):
    """显示工具列表"""
    st.markdown("### 🛠️ 本案例使用的MCP工具")

    if case['id'] == 1:
        tools = [
            ("mcp_qieman_GuessFundCode", "确认基金代码"),
            ("mcp_qieman_BatchGetFundsDetail", "获取基金详情"),
            ("mcp_qieman_GetBatchFundPerformance", "业绩分析"),
            ("mcp_qieman_BatchGetFundNavHistory", "净值走势"),
            ("mcp_qieman_BatchGetFundsHolding", "持仓结构"),
            ("mcp_qieman_BatchGetFundsFeeRule", "费率信息"),
            ("mcp_qieman_GetFundDiagnosis", "基金诊断"),
            ("mcp_qieman_DiagnoseFundPortfolio", "综合诊断")
        ]
    elif case['id'] == 2:
        tools = [
            ("mcp_qieman_GetAssetAllocationPlan", "资产配置方案"),
            ("mcp_qieman_SearchFunds", "基金搜索"),
            ("mcp_qieman_GetAssetAllocation", "资产配置分析"),
            ("mcp_qieman_AnalyzePortfolioRisk", "风险评估"),
            ("mcp_qieman_GetFundsCorrelation", "相关性分析"),
            ("mcp_qieman_GetFundsBackTest", "组合回测"),
            ("mcp_qieman_DiagnoseFundPortfolio", "组合诊断"),
            ("mcp_qieman_MonteCarloSimulate", "蒙特卡洛模拟")
        ]
    else:
        tools = []

    for i, (tool, desc) in enumerate(tools, 1):
        st.markdown(f"**{i}. {tool}**")
        st.caption(f"   用途: {desc}")

def show_case_exercises(case):
    """显示练习题"""
    st.markdown("### 📝 练习题")

    if case['id'] == 1:
        st.markdown("""
        #### 任务：全面分析一只基金

        **要求**:
        1. 选择一只基金进行分析（建议：易方达蓝筹精选 005827）
        2. 按照7步分析框架完成分析
        3. 撰写完整的分析报告（1000字以上）
        4. 给出明确的投资建议

        **评分标准** (总分100分):
        - 基本信息查询（10分）
        - 业绩表现分析（20分）
        - 持仓结构分析（20分）
        - 费率成本分析（15分）
        - 风险评估（20分）
        - 投资建议（10分）
        - 报告质量（5分）

        **提交方式**:
        将分析报告保存为Markdown文件
        """)

        # 提交区域
        st.markdown("---")
        st.markdown("#### 📤 提交作业")

        fund_code = st.text_input("基金代码")
        report = st.text_area("分析报告", height=300)

        if st.button("提交", type="primary"):
            if fund_code and report:
                st.success("✅ 作业已提交！请等待老师批改。")
            else:
                st.error("❌ 请填写完整信息")

    elif case['id'] == 2:
        st.markdown("""
        #### 任务：构建投资组合

        **客户信息**:
        - 年龄：45岁
        - 风险偏好：稳健型
        - 投资金额：50万元
        - 投资期限：5年
        - 收益目标：年化6-8%

        **要求**:
        1. 设计资产配置方案
        2. 选择具体基金（至少5只）
        3. 进行组合分析（风险、相关性、回测）
        4. 撰写投资方案书

        **提交内容**:
        - 资产配置方案
        - 基金选择清单
        - 组合分析报告
        - 投资方案书
        """)

def show_case_answer(case):
    """显示参考答案"""
    st.markdown("### 💡 参考答案")

    if case['id'] == 1:
        st.markdown("""
        #### 基金分析报告示例

        **一、基本情况**
        - 基金代码：005827
        - 基金名称：易方达蓝筹精选混合
        - 基金经理：张坤
        - 成立日期：2018-06-20
        - 基金规模：150亿元

        **二、业绩表现**
        - 近一年收益：+18.5%
        - 近三年年化：+22.3%
        - 最大回撤：-28.5%
        - 夏普比率：1.2

        **三、持仓分析**
        重仓行业：
        - 食品饮料：28%
        - 金融：15%
        - 医药：12%

        **四、投资建议**
        - 适合稳健型以上投资者
        - 建议配置比例：30-40%
        - 建议持有期限：3年以上
        """)

        st.info("""
        完整答案请参考:
        `/金融教学应用/案例库/案例1_基金分析实战.md`
        """)

    elif case['id'] == 2:
        st.markdown("""
        #### 投资组合方案示例

        **资产配置**:
        - 股票基金：30% (15万)
        - 债券基金：50% (25万)
        - 货币基金：20% (10万)

        **基金清单**:
        1. 易方达蓝筹精选 (110022) - 8万
        2. 招商中证白酒 (161725) - 4万
        3. 兴全商业模式 (163406) - 3万
        4. 易方达稳健收益 (110008) - 12万
        5. 博时信用债 (050011) - 8万
        6. 工银双利债券 (485111) - 5万
        7. 易方达天天理财 (000704) - 10万

        **预期表现**:
        - 年化收益：7-9%
        - 最大回撤：-15%
        - 夏普比率：0.7
        """)

        st.info("""
        完整答案请参考:
        `/金融教学应用/案例库/案例2_构建稳健型投资组合.md`
        """)

def show_settings():
    """设置页面（占位）"""
    st.subheader("⚙️ 设置")
    st.info("设置功能开发中...")
