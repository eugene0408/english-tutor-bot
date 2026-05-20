import sqlite3

from groq.types.chat import ChatCompletionMessageParam


class Database:
    def __init__(self, db_name="tutor_bot.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # Table message storage: user id, role: (user/assistant) and text
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

    def get_context(self, user_id, limit=10) -> list[ChatCompletionMessageParam]:
        # Get 10 last messages for context
        self.cursor.execute(
            "SELECT role, content FROM history WHERE user_id = ? ORDER BY rowid DESC LIMIT ?",
            (user_id, limit),
        )
        rows = self.cursor.fetchall()
        # Return in correct chronological order
        return [{"role": row[0], "content": row[1]} for row in reversed(rows)]

    def clear_history(self, user_id):
        self.cursor.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
        self.conn.commit()


db = Database()
