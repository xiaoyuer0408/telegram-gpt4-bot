# database.py

import sqlite3

def connect_to_db():
    # 连接数据库
    conn = sqlite3.connect('user_messages.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            user_id INTEGER,
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    return conn, cursor

def save_message(conn, cursor, chat_id, user_id, message):
    cursor.execute('INSERT INTO user_messages (chat_id, user_id, message) VALUES (?, ?, ?)', (chat_id, user_id, message))
    conn.commit()

def get_messages(cursor, chat_id, limit=None):
    query = 'SELECT * FROM user_messages WHERE chat_id = ? ORDER BY timestamp DESC'
    if limit is not None:
        query += ' LIMIT {}'.format(limit)
    cursor.execute(query, (chat_id,))
    return cursor.fetchall()
