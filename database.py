import sqlite3
import time

# 用户会话字典，用于管理多轮对话
user_sessions = {}

def get_db_connection():
    """
    获取数据库连接
    返回：数据库连接对象
    """
    conn = sqlite3.connect('user_messages.db')
    return conn

def close_db_connection(conn):
    """
    关闭数据库连接
    参数：conn - 数据库连接对象
    """
    conn.close()

def save_message(chat_id, user_id, message):
    """
    将消息保存到数据库
    参数：
        chat_id - 聊天 ID
        user_id - 用户 ID
        message - 用户发送的消息
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_messages (chat_id, user_id, message) VALUES (?, ?, ?)', (chat_id, user_id, message))
    conn.commit()
    close_db_connection(conn)

def get_messages(chat_id, limit=None):
    """
    获取指定聊天 ID 的消息，按时间倒序排序
    参数：
        chat_id - 聊天 ID
        limit - 可选参数，限制返回的消息数量
    返回：查询结果列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'SELECT * FROM user_messages WHERE chat_id = ? ORDER BY timestamp DESC'
    if limit is not None:
        query += ' LIMIT {}'.format(limit)
    cursor.execute(query, (chat_id,))
    result = cursor.fetchall()
    close_db_connection(conn)
    return result
