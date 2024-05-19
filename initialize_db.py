import sqlite3

# Подключение к базе данных (создание файла базы данных)
conn = sqlite3.connect('quiz_bot.db')
c = conn.cursor()

# Создание таблицы для хранения ответов пользователей
c.execute('''
CREATE TABLE IF NOT EXISTS user_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    selected_option TEXT NOT NULL,
    correct INTEGER NOT NULL
)
''')

conn.commit()
conn.close()

print("Database initialized and table created.")
