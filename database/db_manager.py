import sqlite3


class Database:
    def __init__(self, db_name="tutor_bot.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # Таблиця для зберігання повідомлень: id користувача, роль (user/assistant) і текст
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history
            (user_id INTEGER, role TEXT, content TEXT)
        """)
        self.conn.commit()

    def add_message(self, user_id, role, content):
        self.cursor.execute(
            "INSERT INTO history VALUES (?, ?, ?)", (user_id, role, content)
        )
        self.conn.commit()

    def get_context(self, user_id, limit=10):
        # Отримуємо останні 10 повідомлень для контексту
        self.cursor.execute(
            "SELECT role, content FROM history WHERE user_id = ? ORDER BY rowid DESC LIMIT ?",
            (user_id, limit),
        )
        rows = self.cursor.fetchall()
        # Повертаємо у правильному хронологічному порядку
        return [{"role": row[0], "content": row[1]} for row in reversed(rows)]

    def clear_history(self, user_id):
        self.cursor.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
        self.conn.commit()


db = Database()
