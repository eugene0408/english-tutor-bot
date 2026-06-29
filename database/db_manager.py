import sqlite3

from groq.types.chat import ChatCompletionMessageParam


class Database:
    def __init__(self, db_name="tutor_bot.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # Table message storage: user id, role: (user/assistant) and text
        # sql
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history
            (user_id INTEGER, role TEXT, content TEXT)
        """)
        # sql
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings
            (
            user_id INTEGER PRIMARY KEY,
            level TEXT DEFAULT 'B2',
            temperature REAL DEFAULT 0.7 CHECK(temperature >= 0.0 AND temperature <= 1.0)
            )
        """)

        self.conn.commit()

    def add_message(self, user_id, role, content):
        self.cursor.execute(
            "INSERT INTO history VALUES (?, ?, ?)", (user_id, role, content)
        )
        self.conn.commit()

    def get_context(self, user_id, limit=10) -> list[ChatCompletionMessageParam]:
        # Get 10 last messages for context
        # language=sql
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

    def get_user_settings(self, user_id: int) -> dict:
        self.cursor.execute(
            """
            SELECT level, temperature FROM user_settings WHERE user_id = ?
        """,
            (user_id,),
        )
        row = self.cursor.fetchone()

        if row:
            return {
                "user_id": user_id,
                "level": row[0],
                "temperature": row[1],  # return decimal
            }

        # Default values for first-time users.
        return {"user_id": user_id, "level": "B2", "temperature": 0.7}

    def set_user_temperature_from_frontend(self, user_id: int, frontend_value: int):
        try:
            raw_value = int(frontend_value)

            if 1 <= raw_value <= 10:
                ai_temperature = raw_value / 10

            self.cursor.execute(
                """
                INSERT INTO user_settings (user_id, temperature)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET temperature = excluded.temperature
                """,
                (user_id, ai_temperature),
            )
            self.conn.commit()
        except (ValueError, TypeError):
            return "Error: Incorect data"

    def set_user_level_from_frontend(self, user_id: int, frontend_value: str):
        ALLOWED_LEVELS = {"B1", "B2", "C1", "C2"}

        level = str(frontend_value).strip().upper()

        if level in ALLOWED_LEVELS:
            self.cursor.execute(
                """
                INSERT INTO user_settings (user_id, level)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET level = excluded.level
                """,
                (user_id, level),
            )
            self.conn.commit()
        else:
            return f"Error: Incorect level {level}. Alowed levels : B1, B2, C1, C2."


db = Database()
