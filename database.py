import sqlite3
import time

# 为每个用户创建一个会话ID以管理多轮对话
user_sessions = {}

def save_message(cursor, chat_id, user_id, message):
    # 将消息保存到数据库
    cursor.execute('INSERT INTO user_messages (chat_id, user_id, message) VALUES (?, ?, ?)', (chat_id, user_id, message))

def get_messages(cursor, chat_id, limit=None):
    # 获取指定聊天ID的消息，按时间倒序排序
    query = 'SELECT * FROM user_messages WHERE chat_id = ? ORDER BY timestamp DESC'
    if limit is not None:
        query += ' LIMIT {}'.format(limit)
    cursor.execute(query, (chat_id,))
    return cursor.fetchall()
