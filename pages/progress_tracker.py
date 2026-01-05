"""
学习进度跟踪页面
Progress Tracker Page
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from utils.database import get_db_manager

def show():
    st.markdown('<h1 class="main-title">📈 学习进度跟踪</h1>', unsafe_allow_html=True)

    user = st.session_state.user
    user_id = user['id']
    db = get_db_manager()

    # 获取学习进度
    progress_data = db.get_user_progress(user_id)

    if not progress_data:
        show_empty_state()
        return

    # 总体进度
    show_overall_progress(progress_data, user_id, db)

    st.markdown("---")

    # 模块详情
    show_module_details(progress_data)

    st.markdown("---")

    # 学习统计
    show_learning_stats(progress_data, user_id, db)

def show_empty_state():
    """显示空状态"""
    st.info("""
    ### 📚 开始您的学习之旅

    您还没有学习记录。点击左侧菜单选择一个模块开始学习吧！

    **推荐学习路径**:
    1. 📊 基金投资入门
    2. 🎯 投资组合构建
    3. ⚠️ 风险管理
    4. 📰 市场分析
    5. 💰 财务规划
    6. 📈 策略研究
    """)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("总课程数", "60+", delta=None)

    with col2:
        st.metric("实战案例", "30+", delta=None)

    with col3:
        st.metric("MCP工具", "54", delta=None)

def show_overall_progress(progress_data, user_id, db):
    """显示总体进度"""
    st.subheader("📊 总体进度")

    # 计算统计数据
    total_lessons = len(progress_data)
    completed = sum(1 for p in progress_data if p['status'] == 'completed')
    in_progress = sum(1 for p in progress_data if p['status'] == 'in_progress')

    # 计算平均分
    scores = [p['score'] for p in progress_data if p['score'] is not None]
    avg_score = sum(scores) / len(scores) if scores else 0

    # 计算完成率
    completion_rate = (completed / total_lessons * 100) if total_lessons > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("完成率", f"{completion_rate:.1f}%", f"{completed}/{total_lessons}课")

    with col2:
        st.metric("平均分", f"{avg_score:.1f}", help="已完成课程的平均分")

    with col3:
        st.metric("进行中", f"{in_progress}", "课程")

    with col4:
        # 计算学习天数
        activity_stats = db.get_daily_activity_stats(user_id, days=30)
        learning_days = len(activity_stats)
        st.metric("学习天数", f"{learning_days}", "近30天")

    # 学习轨迹图
    st.subheader("📈 学习轨迹")

    if scores and len(scores) > 1:
        # 创建学习进度曲线
        fig = go.Figure()

        # 按完成时间排序
        completed_lessons = [p for p in progress_data if p['status'] == 'completed' and p['score'] is not None]
        completed_lessons.sort(key=lambda x: x['completed_at'] if x['completed_at'] else '')

        dates = [p['completed_at'][:10] if p['completed_at'] else '' for p in completed_lessons]
        scores_timeline = [p['score'] for p in completed_lessons]

        fig.add_trace(go.Scatter(
            x=list(range(len(scores_timeline))),
            y=scores_timeline,
            mode='lines+markers',
            name='分数',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=8)
        ))

        fig.update_layout(
            title="学习成绩变化趋势",
            xaxis_title="课程序号",
            yaxis_title="分数",
            hovermode='x unified',
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("完成更多课程后将显示学习轨迹图")

def show_module_details(progress_data):
    """显示模块详情"""
    st.subheader("📚 模块详情")

    # 按模块分组
    modules = {}
    for p in progress_data:
        module = p['module_name']
        if module not in modules:
            modules[module] = []
        modules[module].append(p)

    if not modules:
        st.info("暂无学习数据")
        return

    # 显示每个模块
    for module_name, lessons in modules.items():
        with st.expander(f"📖 {module_name}", expanded=True):
            completed = sum(1 for l in lessons if l['status'] == 'completed')
            total = len(lessons)
            module_progress = (completed / total * 100) if total > 0 else 0

            # 模块进度条
            st.progress(module_progress / 100)
            st.caption(f"进度: {completed}/{total} 课 ({module_progress:.1f}%)")

            # 课程列表
            df_data = []
            for lesson in lessons:
                status_emoji = {
                    'completed': '✅',
                    'in_progress': '🔄',
                    'not_started': '⏸️'
                }.get(lesson['status'], '⏸️')

                df_data.append({
                    '状态': status_emoji,
                    '课程名称': lesson['lesson_name'],
                    '分数': f"{lesson['score']:.0f}" if lesson['score'] is not None else '-',
                    '更新时间': lesson['updated_at'][:10] if lesson['updated_at'] else '-'
                })

            if df_data:
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

def show_learning_stats(progress_data, user_id, db):
    """显示学习统计"""
    st.subheader("📊 学习统计")

    col1, col2 = st.columns(2)

    with col1:
        # 分数分布
        st.markdown("##### 📈 分数分布")

        scores = [p['score'] for p in progress_data if p['score'] is not None]

        if scores:
            fig = go.Figure(data=[go.Histogram(
                x=scores,
                nbinsx=10,
                marker_color='#1f77b4',
                opacity=0.7
            )])

            fig.update_layout(
                xaxis_title="分数",
                yaxis_title="课程数",
                height=300,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无分数数据")

    with col2:
        # 学习活跃度
        st.markdown("##### 📅 学习活跃度（近30天）")

        activity_stats = db.get_daily_activity_stats(user_id, days=30)

        if activity_stats:
            dates = [s['date'] for s in activity_stats]
            counts = [s['count'] for s in activity_stats]

            fig = go.Figure(data=[go.Bar(
                x=dates,
                y=counts,
                marker_color='#2ca02c',
                opacity=0.7
            )])

            fig.update_layout(
                xaxis_title="日期",
                yaxis_title="活动次数",
                height=300,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无活动记录")

    # 学习建议
    st.markdown("---")
    st.subheader("💡 学习建议")

    scores = [p['score'] for p in progress_data if p['score'] is not None]
    avg_score = sum(scores) / len(scores) if scores else 0
    completed_count = sum(1 for p in progress_data if p['status'] == 'completed')

    suggestions = []

    if avg_score < 60:
        suggestions.append("📚 建议加强基础知识学习，重点复习得分较低的课程")
    elif avg_score < 80:
        suggestions.append("💪 学习进展不错，继续保持！可以尝试一些进阶内容")
    else:
        suggestions.append("🎉 学习成绩优秀！可以挑战更高难度的案例")

    if completed_count < 5:
        suggestions.append("🎯 建议每周完成至少2-3节课，保持学习连贯性")
    elif completed_count < 20:
        suggestions.append("⭐ 学习进度良好，继续按照学习路径推进")
    else:
        suggestions.append("🏆 已完成大量课程，可以尝试实战项目巩固所学知识")

    activity_stats = db.get_daily_activity_stats(user_id, days=7)
    if len(activity_stats) < 3:
        suggestions.append("📅 建议增加学习频率，每周至少学习3-4天效果更好")

    for suggestion in suggestions:
        st.info(suggestion)

    # 下载报告
    st.markdown("---")
    if st.button("📥 下载学习报告", type="primary"):
        # 生成学习报告
        report = generate_learning_report(progress_data, user_id, db)
        st.download_button(
            label="💾 保存为文本文件",
            data=report,
            file_name=f"learning_report_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

def generate_learning_report(progress_data, user_id, db):
    """生成学习报告"""
    total = len(progress_data)
    completed = sum(1 for p in progress_data if p['status'] == 'completed')
    scores = [p['score'] for p in progress_data if p['score'] is not None]
    avg_score = sum(scores) / len(scores) if scores else 0

    report = f"""
================================================================
                    学习进度报告
================================================================

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

----------------------------------------------------------------
总体数据
----------------------------------------------------------------
总课程数: {total}
已完成: {completed}
完成率: {(completed/total*100):.1f}%
平均分: {avg_score:.1f}

----------------------------------------------------------------
模块详情
----------------------------------------------------------------
"""

    # 按模块分组
    modules = {}
    for p in progress_data:
        module = p['module_name']
        if module not in modules:
            modules[module] = []
        modules[module].append(p)

    for module_name, lessons in modules.items():
        completed_in_module = sum(1 for l in lessons if l['status'] == 'completed')
        total_in_module = len(lessons)
        report += f"\n{module_name}:\n"
        report += f"  完成进度: {completed_in_module}/{total_in_module}\n"

        for lesson in lessons:
            status = lesson['status']
            score = lesson['score'] if lesson['score'] is not None else '-'
            report += f"  - {lesson['lesson_name']}: {status} (分数: {score})\n"

    report += "\n================================================================\n"

    return report
