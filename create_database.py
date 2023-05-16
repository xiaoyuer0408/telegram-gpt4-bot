import sqlite3
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
def save_message(chat_id, user_id, message):
    cursor.execute('INSERT INTO user_messages (chat_id, user_id, message) VALUES (?, ?, ?)', (chat_id, user_id, message))
    conn.commit()
def get_messages(chat_id, limit=None):
    query = 'SELECT * FROM user_messages WHERE chat_id = ? ORDER BY timestamp DESC'
    if limit is not None:
        query += ' LIMIT {}'.format(limit)
    cursor.execute(query, (chat_id,))
    return cursor.fetchall()
chat_id = 123456789
user_id = 987654321
message = "Hello, how are you?"

save_message(chat_id, user_id, message)

recent_messages = get_messages(chat_id, limit=5)
for msg in recent_messages:
    print(msg)
conn.close()
