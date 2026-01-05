"""
用户认证模块
User Authentication Module

提供用户登录、注册、权限管理功能
"""

import streamlit as st
import hashlib
import jwt
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import re

class AuthManager:
    """用户认证管理器"""

    def __init__(self, db_path: str = "data/users.db", secret_key: str = None):
        """
        初始化认证管理器

        Args:
            db_path: 数据库路径
            secret_key: JWT密钥
        """
        self.db_path = db_path
        self.secret_key = secret_key or st.secrets.get("JWT_SECRET", "finance-edu-secret-key-2026")
        self._init_database()

    def _init_database(self):
        """初始化用户数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                school TEXT,
                grade TEXT,
                major TEXT,
                role TEXT DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')

        # 创建会话表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()

    @staticmethod
    def hash_password(password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        验证密码强度

        Returns:
            (是否有效, 错误消息)
        """
        if len(password) < 6:
            return False, "密码长度至少6位"
        if not re.search(r'[A-Za-z]', password):
            return False, "密码必须包含字母"
        if not re.search(r'\d', password):
            return False, "密码必须包含数字"
        return True, ""

    def register(self, username: str, email: str, password: str,
                full_name: str = "", school: str = "", grade: str = "",
                major: str = "", role: str = "student") -> Tuple[bool, str]:
        """
        用户注册

        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            full_name: 姓名
            school: 学校
            grade: 年级
            major: 专业
            role: 角色 (student/teacher/admin)

        Returns:
            (是否成功, 消息)
        """
        # 验证邮箱
        if not self.validate_email(email):
            return False, "邮箱格式不正确"

        # 验证密码
        is_valid, msg = self.validate_password(password)
        if not is_valid:
            return False, msg

        # 检查用户名和邮箱是否已存在
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?",
                      (username, email))
        if cursor.fetchone():
            conn.close()
            return False, "用户名或邮箱已存在"

        # 插入新用户
        password_hash = self.hash_password(password)
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name,
                                 school, grade, major, role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, full_name, school, grade, major, role))
            conn.commit()
            conn.close()
            return True, "注册成功"
        except Exception as e:
            conn.close()
            return False, f"注册失败: {str(e)}"

    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        用户登录

        Args:
            username: 用户名或邮箱
            password: 密码

        Returns:
            (是否成功, 消息, 用户信息)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        password_hash = self.hash_password(password)

        # 支持用户名或邮箱登录
        cursor.execute('''
            SELECT id, username, email, full_name, school, grade, major, role
            FROM users
            WHERE (username = ? OR email = ?) AND password_hash = ? AND is_active = 1
        ''', (username, username, password_hash))

        user = cursor.fetchone()

        if not user:
            conn.close()
            return False, "用户名或密码错误", None

        # 更新最后登录时间
        cursor.execute("UPDATE users SET last_login = ? WHERE id = ?",
                      (datetime.now(), user[0]))
        conn.commit()

        # 生成JWT token
        token = self._generate_token(user[0])

        # 保存会话
        expires_at = datetime.now() + timedelta(days=7)
        cursor.execute('''
            INSERT INTO sessions (user_id, token, expires_at)
            VALUES (?, ?, ?)
        ''', (user[0], token, expires_at))
        conn.commit()
        conn.close()

        user_info = {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'full_name': user[3],
            'school': user[4],
            'grade': user[5],
            'major': user[6],
            'role': user[7],
            'token': token
        }

        return True, "登录成功", user_info

    def logout(self, token: str):
        """用户登出"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        conn.close()

    def verify_token(self, token: str) -> Optional[Dict]:
        """
        验证token

        Returns:
            用户信息或None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 检查会话是否存在且未过期
        cursor.execute('''
            SELECT s.user_id, u.username, u.email, u.full_name, u.role
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ? AND s.expires_at > ? AND u.is_active = 1
        ''', (token, datetime.now()))

        result = cursor.fetchone()
        conn.close()

        if not result:
            return None

        return {
            'id': result[0],
            'username': result[1],
            'email': result[2],
            'full_name': result[3],
            'role': result[4],
            'token': token
        }

    def _generate_token(self, user_id: int) -> str:
        """生成JWT token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def update_profile(self, user_id: int, **kwargs) -> Tuple[bool, str]:
        """
        更新用户资料

        Args:
            user_id: 用户ID
            **kwargs: 要更新的字段

        Returns:
            (是否成功, 消息)
        """
        allowed_fields = ['full_name', 'school', 'grade', 'major', 'email']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return False, "没有要更新的字段"

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 构建UPDATE语句
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [user_id]

        try:
            cursor.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
            conn.commit()
            conn.close()
            return True, "更新成功"
        except Exception as e:
            conn.close()
            return False, f"更新失败: {str(e)}"

    def change_password(self, user_id: int, old_password: str,
                       new_password: str) -> Tuple[bool, str]:
        """
        修改密码

        Returns:
            (是否成功, 消息)
        """
        # 验证新密码强度
        is_valid, msg = self.validate_password(new_password)
        if not is_valid:
            return False, msg

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 验证旧密码
        old_hash = self.hash_password(old_password)
        cursor.execute("SELECT id FROM users WHERE id = ? AND password_hash = ?",
                      (user_id, old_hash))

        if not cursor.fetchone():
            conn.close()
            return False, "原密码错误"

        # 更新密码
        new_hash = self.hash_password(new_password)
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                      (new_hash, user_id))
        conn.commit()
        conn.close()

        return True, "密码修改成功"


# Streamlit认证组件
def show_login_page():
    """显示登录页面"""
    st.markdown('<h1 class="main-title">🔐 用户登录</h1>', unsafe_allow_html=True)

    auth = get_auth_manager()

    # 创建标签页
    tab1, tab2 = st.tabs(["登录", "注册"])

    with tab1:
        st.subheader("登录账户")

        username = st.text_input("用户名或邮箱", key="login_username")
        password = st.text_input("密码", type="password", key="login_password")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("登录", type="primary", use_container_width=True):
                if not username or not password:
                    st.error("请填写完整信息")
                else:
                    success, msg, user_info = auth.login(username, password)
                    if success:
                        st.session_state.user = user_info
                        st.session_state.authenticated = True
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        with col2:
            if st.button("演示账户登录", use_container_width=True):
                # 自动创建演示账户
                demo_username = "demo_student"
                demo_password = "demo123"

                # 检查演示账户是否存在，不存在则创建
                success, msg, user_info = auth.login(demo_username, demo_password)
                if not success:
                    auth.register(demo_username, "demo@example.com", demo_password,
                                full_name="演示学生", school="演示大学",
                                grade="大三", major="金融学")
                    success, msg, user_info = auth.login(demo_username, demo_password)

                if success:
                    st.session_state.user = user_info
                    st.session_state.authenticated = True
                    st.success("已使用演示账户登录")
                    st.rerun()

    with tab2:
        st.subheader("注册新用户")

        with st.form("register_form"):
            col1, col2 = st.columns(2)

            with col1:
                reg_username = st.text_input("用户名*")
                reg_email = st.text_input("邮箱*")
                reg_password = st.text_input("密码*", type="password")
                reg_password2 = st.text_input("确认密码*", type="password")

            with col2:
                reg_name = st.text_input("姓名")
                reg_school = st.text_input("学校/机构")
                reg_grade = st.selectbox("年级", ["", "大一", "大二", "大三", "大四", "研究生", "其他"])
                reg_major = st.text_input("专业")

            submitted = st.form_submit_button("注册", type="primary", use_container_width=True)

            if submitted:
                if not all([reg_username, reg_email, reg_password, reg_password2]):
                    st.error("请填写所有必填项（标*）")
                elif reg_password != reg_password2:
                    st.error("两次密码输入不一致")
                else:
                    success, msg = auth.register(
                        reg_username, reg_email, reg_password,
                        reg_name, reg_school, reg_grade, reg_major
                    )
                    if success:
                        st.success(f"{msg}，请登录")
                    else:
                        st.error(msg)


def require_auth(func):
    """需要认证的装饰器"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('authenticated', False):
            show_login_page()
            return None
        return func(*args, **kwargs)
    return wrapper


def check_role(allowed_roles: list):
    """检查用户角色"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = st.session_state.get('user', {})
            if user.get('role') not in allowed_roles:
                st.error("您没有权限访问此功能")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator


@st.cache_resource
def get_auth_manager() -> AuthManager:
    """获取认证管理器单例"""
    return AuthManager()


def logout_user():
    """登出用户"""
    if 'user' in st.session_state:
        auth = get_auth_manager()
        auth.logout(st.session_state.user.get('token', ''))
        del st.session_state.user
        del st.session_state.authenticated
    st.rerun()
