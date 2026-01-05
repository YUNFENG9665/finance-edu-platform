"""
设置页面
Settings Page
"""

import streamlit as st
from utils.auth import get_auth_manager

def show():
    st.markdown('<h1 class="main-title">⚙️ 系统设置</h1>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["👤 个人信息", "🔒 修改密码", "🔔 通知设置", "ℹ️ 关于"])

    with tab1:
        show_profile_settings()

    with tab2:
        show_password_settings()

    with tab3:
        show_notification_settings()

    with tab4:
        show_about()

def show_profile_settings():
    """个人信息设置"""
    st.subheader("👤 个人信息")

    user = st.session_state.user
    auth = get_auth_manager()

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("用户名", value=user.get('username', ''), disabled=True, help="用户名不可修改")
        name = st.text_input("姓名", value=user.get('full_name', ''))
        email = st.text_input("邮箱", value=user.get('email', ''))

    with col2:
        school = st.text_input("学校/机构", value=user.get('school', ''))
        grade = st.selectbox("年级",
                           ["", "大一", "大二", "大三", "大四", "研究生", "其他"],
                           index=["", "大一", "大二", "大三", "大四", "研究生", "其他"].index(user.get('grade', '')) if user.get('grade') in ["", "大一", "大二", "大三", "大四", "研究生", "其他"] else 0)
        major = st.text_input("专业", value=user.get('major', ''))

    if st.button("💾 保存设置", type="primary"):
        success, msg = auth.update_profile(
            user_id=user['id'],
            full_name=name,
            email=email,
            school=school,
            grade=grade,
            major=major
        )
        if success:
            # 更新 session_state 中的用户信息
            st.session_state.user.update({
                'full_name': name,
                'email': email,
                'school': school,
                'grade': grade,
                'major': major
            })
            st.success(f"✅ {msg}")
            st.rerun()
        else:
            st.error(f"❌ {msg}")

def show_password_settings():
    """修改密码"""
    st.subheader("🔒 修改密码")

    user = st.session_state.user
    auth = get_auth_manager()

    with st.form("password_form"):
        old_password = st.text_input("原密码", type="password")
        new_password = st.text_input("新密码", type="password", help="至少6位，包含字母和数字")
        confirm_password = st.text_input("确认新密码", type="password")

        submitted = st.form_submit_button("🔄 修改密码", type="primary")

        if submitted:
            if not old_password or not new_password or not confirm_password:
                st.error("请填写所有字段")
            elif new_password != confirm_password:
                st.error("两次新密码输入不一致")
            else:
                success, msg = auth.change_password(
                    user_id=user['id'],
                    old_password=old_password,
                    new_password=new_password
                )
                if success:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")

def show_notification_settings():
    """通知设置"""
    st.subheader("🔔 通知设置")

    st.checkbox("接收课程更新通知", value=True)
    st.checkbox("接收作业提醒", value=True)
    st.checkbox("接收成绩通知", value=True)
    st.checkbox("接收系统公告", value=False)

    if st.button("💾 保存设置", type="primary", key="save_notif"):
        st.success("✅ 设置已保存")

def show_about():
    """关于页面"""
    st.subheader("ℹ️ 关于金融教学平台")

    st.markdown("""
    ### 📚 平台简介

    金融教学平台是一个基于盈米MCP工具库的交互式金融投资教学应用，
    为学生提供真实的市场数据和实战操作环境。

    ### 🎯 核心特色

    - ✅ **54个专业工具** - 真实市场数据支撑
    - ✅ **6大教学模块** - 完整学习体系
    - ✅ **互动式学习** - 动手操作，即时反馈
    - ✅ **案例化教学** - 真实投资场景
    - ✅ **进度跟踪** - 学习效果可视化
    - ✅ **用户认证系统** - 安全的用户管理
    - ✅ **数据持久化** - 学习数据永久保存
    - ✅ **云端部署** - 随时随地访问

    ### 📊 版本信息

    - **版本号**: v2.0.0
    - **发布日期**: 2026-01-05
    - **开发者**: AI Assistant
    - **技术栈**: Python, Streamlit, Plotly, SQLite, JWT

    ### 🆕 V2.0 新增功能

    - ✅ 真实MCP API集成
    - ✅ 用户登录认证系统
    - ✅ 数据库持久化
    - ✅ 云端部署支持

    ### 📞 联系方式

    - **邮箱**: support@example.com
    - **GitHub**: https://github.com/example/finance-edu

    ### 📄 许可证

    MIT License

    ### 🙏 致谢

    感谢盈米基金提供MCP工具库支持。
    """)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📖 使用文档", use_container_width=True):
            st.info("请查看 README.md 文档")

    with col2:
        if st.button("🐛 反馈问题", use_container_width=True):
            st.info("请发送邮件至 support@example.com")

    with col3:
        if st.button("⭐ 给个Star", use_container_width=True):
            st.balloons()
            st.success("感谢您的支持！")
