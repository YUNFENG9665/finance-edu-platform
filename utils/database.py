"""
数据库持久化模块
Database Persistence Module

提供学习进度、投资组合、练习提交等数据的持久化存储
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import streamlit as st
from pathlib import Path


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: str = "data/education.db"):
        """
        初始化数据库管理器

        Args:
            db_path: 数据库路径
        """
        self.db_path = db_path
        # 确保数据目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建学习进度表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                module_name TEXT NOT NULL,
                lesson_name TEXT NOT NULL,
                status TEXT DEFAULT 'not_started',
                score REAL,
                completed_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, module_name, lesson_name),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # 创建练习提交表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercise_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                case_id TEXT NOT NULL,
                question_id TEXT NOT NULL,
                answer TEXT,
                is_correct BOOLEAN,
                score REAL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # 创建投资组合表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                portfolio_name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # 创建持仓明细表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                fund_code TEXT NOT NULL,
                fund_name TEXT,
                weight REAL NOT NULL,
                amount REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE
            )
        ''')

        # 创建学习笔记表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                module_name TEXT NOT NULL,
                lesson_name TEXT,
                note_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # 创建学习活动日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                activity_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()

    # ==================== 学习进度管理 ====================

    def get_user_progress(self, user_id: int) -> List[Dict]:
        """
        获取用户学习进度

        Args:
            user_id: 用户ID

        Returns:
            进度列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT module_name, lesson_name, status, score, completed_at, updated_at
            FROM learning_progress
            WHERE user_id = ?
            ORDER BY module_name, lesson_name
        ''', (user_id,))

        results = cursor.fetchall()
        conn.close()

        return [{
            'module_name': row[0],
            'lesson_name': row[1],
            'status': row[2],
            'score': row[3],
            'completed_at': row[4],
            'updated_at': row[5]
        } for row in results]

    def update_progress(self, user_id: int, module_name: str, lesson_name: str,
                       status: str = None, score: float = None) -> Tuple[bool, str]:
        """
        更新学习进度

        Args:
            user_id: 用户ID
            module_name: 模块名称
            lesson_name: 课程名称
            status: 状态 (not_started/in_progress/completed)
            score: 分数

        Returns:
            (是否成功, 消息)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            completed_at = datetime.now() if status == 'completed' else None

            cursor.execute('''
                INSERT INTO learning_progress
                (user_id, module_name, lesson_name, status, score, completed_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, module_name, lesson_name)
                DO UPDATE SET
                    status = COALESCE(?, status),
                    score = COALESCE(?, score),
                    completed_at = COALESCE(?, completed_at),
                    updated_at = ?
            ''', (user_id, module_name, lesson_name, status, score, completed_at,
                  datetime.now(), status, score, completed_at, datetime.now()))

            conn.commit()
            conn.close()
            return True, "进度更新成功"
        except Exception as e:
            conn.close()
            return False, f"进度更新失败: {str(e)}"

    def get_module_statistics(self, user_id: int, module_name: str) -> Dict:
        """
        获取模块统计信息

        Args:
            user_id: 用户ID
            module_name: 模块名称

        Returns:
            统计信息
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                AVG(CASE WHEN score IS NOT NULL THEN score ELSE 0 END) as avg_score
            FROM learning_progress
            WHERE user_id = ? AND module_name = ?
        ''', (user_id, module_name))

        row = cursor.fetchone()
        conn.close()

        return {
            'total': row[0] or 0,
            'completed': row[1] or 0,
            'avg_score': row[2] or 0
        }

    # ==================== 练习提交管理 ====================

    def submit_exercise(self, user_id: int, case_id: str, question_id: str,
                       answer: str, is_correct: bool = None,
                       score: float = None) -> Tuple[bool, str]:
        """
        提交练习答案

        Args:
            user_id: 用户ID
            case_id: 案例ID
            question_id: 题目ID
            answer: 答案
            is_correct: 是否正确
            score: 分数

        Returns:
            (是否成功, 消息)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO exercise_submissions
                (user_id, case_id, question_id, answer, is_correct, score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, case_id, question_id, answer, is_correct, score))

            conn.commit()
            conn.close()
            return True, "提交成功"
        except Exception as e:
            conn.close()
            return False, f"提交失败: {str(e)}"

    def get_user_submissions(self, user_id: int, case_id: str = None) -> List[Dict]:
        """
        获取用户提交记录

        Args:
            user_id: 用户ID
            case_id: 案例ID（可选）

        Returns:
            提交记录列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if case_id:
            cursor.execute('''
                SELECT case_id, question_id, answer, is_correct, score, submitted_at
                FROM exercise_submissions
                WHERE user_id = ? AND case_id = ?
                ORDER BY submitted_at DESC
            ''', (user_id, case_id))
        else:
            cursor.execute('''
                SELECT case_id, question_id, answer, is_correct, score, submitted_at
                FROM exercise_submissions
                WHERE user_id = ?
                ORDER BY submitted_at DESC
            ''', (user_id,))

        results = cursor.fetchall()
        conn.close()

        return [{
            'case_id': row[0],
            'question_id': row[1],
            'answer': row[2],
            'is_correct': row[3],
            'score': row[4],
            'submitted_at': row[5]
        } for row in results]

    # ==================== 投资组合管理 ====================

    def create_portfolio(self, user_id: int, portfolio_name: str,
                        description: str = "") -> Tuple[bool, str, Optional[int]]:
        """
        创建投资组合

        Args:
            user_id: 用户ID
            portfolio_name: 组合名称
            description: 描述

        Returns:
            (是否成功, 消息, 组合ID)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO portfolios (user_id, portfolio_name, description)
                VALUES (?, ?, ?)
            ''', (user_id, portfolio_name, description))

            portfolio_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return True, "组合创建成功", portfolio_id
        except Exception as e:
            conn.close()
            return False, f"组合创建失败: {str(e)}", None

    def get_user_portfolios(self, user_id: int) -> List[Dict]:
        """
        获取用户所有投资组合

        Args:
            user_id: 用户ID

        Returns:
            组合列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, portfolio_name, description, created_at, updated_at
            FROM portfolios
            WHERE user_id = ?
            ORDER BY updated_at DESC
        ''', (user_id,))

        results = cursor.fetchall()
        conn.close()

        return [{
            'id': row[0],
            'portfolio_name': row[1],
            'description': row[2],
            'created_at': row[3],
            'updated_at': row[4]
        } for row in results]

    def update_portfolio_holdings(self, portfolio_id: int,
                                 holdings: List[Dict]) -> Tuple[bool, str]:
        """
        更新组合持仓

        Args:
            portfolio_id: 组合ID
            holdings: 持仓列表 [{"fund_code": "xxx", "fund_name": "xxx", "weight": 0.3, "amount": 10000}, ...]

        Returns:
            (是否成功, 消息)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 删除旧持仓
            cursor.execute('DELETE FROM holdings WHERE portfolio_id = ?', (portfolio_id,))

            # 插入新持仓
            for holding in holdings:
                cursor.execute('''
                    INSERT INTO holdings (portfolio_id, fund_code, fund_name, weight, amount)
                    VALUES (?, ?, ?, ?, ?)
                ''', (portfolio_id, holding['fund_code'], holding.get('fund_name', ''),
                      holding['weight'], holding.get('amount', 0)))

            # 更新组合更新时间
            cursor.execute('''
                UPDATE portfolios SET updated_at = ? WHERE id = ?
            ''', (datetime.now(), portfolio_id))

            conn.commit()
            conn.close()
            return True, "持仓更新成功"
        except Exception as e:
            conn.close()
            return False, f"持仓更新失败: {str(e)}"

    def get_portfolio_holdings(self, portfolio_id: int) -> List[Dict]:
        """
        获取组合持仓

        Args:
            portfolio_id: 组合ID

        Returns:
            持仓列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT fund_code, fund_name, weight, amount, updated_at
            FROM holdings
            WHERE portfolio_id = ?
        ''', (portfolio_id,))

        results = cursor.fetchall()
        conn.close()

        return [{
            'fund_code': row[0],
            'fund_name': row[1],
            'weight': row[2],
            'amount': row[3],
            'updated_at': row[4]
        } for row in results]

    def delete_portfolio(self, portfolio_id: int) -> Tuple[bool, str]:
        """
        删除投资组合

        Args:
            portfolio_id: 组合ID

        Returns:
            (是否成功, 消息)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM portfolios WHERE id = ?', (portfolio_id,))
            conn.commit()
            conn.close()
            return True, "组合删除成功"
        except Exception as e:
            conn.close()
            return False, f"组合删除失败: {str(e)}"

    # ==================== 学习笔记管理 ====================

    def save_note(self, user_id: int, module_name: str, lesson_name: str,
                 note_content: str) -> Tuple[bool, str]:
        """
        保存学习笔记

        Args:
            user_id: 用户ID
            module_name: 模块名称
            lesson_name: 课程名称
            note_content: 笔记内容

        Returns:
            (是否成功, 消息)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO study_notes (user_id, module_name, lesson_name, note_content)
                VALUES (?, ?, ?, ?)
            ''', (user_id, module_name, lesson_name, note_content))

            conn.commit()
            conn.close()
            return True, "笔记保存成功"
        except Exception as e:
            conn.close()
            return False, f"笔记保存失败: {str(e)}"

    def get_user_notes(self, user_id: int, module_name: str = None) -> List[Dict]:
        """
        获取用户笔记

        Args:
            user_id: 用户ID
            module_name: 模块名称（可选）

        Returns:
            笔记列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if module_name:
            cursor.execute('''
                SELECT id, module_name, lesson_name, note_content, created_at, updated_at
                FROM study_notes
                WHERE user_id = ? AND module_name = ?
                ORDER BY created_at DESC
            ''', (user_id, module_name))
        else:
            cursor.execute('''
                SELECT id, module_name, lesson_name, note_content, created_at, updated_at
                FROM study_notes
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))

        results = cursor.fetchall()
        conn.close()

        return [{
            'id': row[0],
            'module_name': row[1],
            'lesson_name': row[2],
            'note_content': row[3],
            'created_at': row[4],
            'updated_at': row[5]
        } for row in results]

    # ==================== 学习活动日志 ====================

    def log_activity(self, user_id: int, activity_type: str,
                    activity_data: Dict = None) -> bool:
        """
        记录学习活动

        Args:
            user_id: 用户ID
            activity_type: 活动类型
            activity_data: 活动数据

        Returns:
            是否成功
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            data_json = json.dumps(activity_data) if activity_data else None
            cursor.execute('''
                INSERT INTO activity_logs (user_id, activity_type, activity_data)
                VALUES (?, ?, ?)
            ''', (user_id, activity_type, data_json))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            return False

    def get_activity_logs(self, user_id: int, days: int = 30) -> List[Dict]:
        """
        获取活动日志

        Args:
            user_id: 用户ID
            days: 最近天数

        Returns:
            活动日志列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT activity_type, activity_data, created_at
            FROM activity_logs
            WHERE user_id = ? AND created_at > datetime('now', '-' || ? || ' days')
            ORDER BY created_at DESC
        ''', (user_id, days))

        results = cursor.fetchall()
        conn.close()

        return [{
            'activity_type': row[0],
            'activity_data': json.loads(row[1]) if row[1] else {},
            'created_at': row[2]
        } for row in results]

    def get_daily_activity_stats(self, user_id: int, days: int = 30) -> List[Dict]:
        """
        获取每日活动统计

        Args:
            user_id: 用户ID
            days: 最近天数

        Returns:
            每日统计列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                DATE(created_at) as activity_date,
                COUNT(*) as activity_count
            FROM activity_logs
            WHERE user_id = ? AND created_at > datetime('now', '-' || ? || ' days')
            GROUP BY DATE(created_at)
            ORDER BY activity_date DESC
        ''', (user_id, days))

        results = cursor.fetchall()
        conn.close()

        return [{
            'date': row[0],
            'count': row[1]
        } for row in results]


# 创建全局数据库管理器实例
@st.cache_resource
def get_db_manager() -> DatabaseManager:
    """获取数据库管理器单例"""
    return DatabaseManager()
