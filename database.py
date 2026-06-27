import sqlite3
from datetime import datetime

DB_NAME = "context_bot.db"

def init_db():
    """Создает таблицы в базе данных, если их еще нет"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Таблица для хранения истории сессий по проектам
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def add_session_log(project: str, content: str):
    """Сохраняет новую запись о проделанной работе"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute(
        "INSERT INTO sessions (project, content, created_at) VALUES (?, ?, ?)",
        (project, content, current_time)
    )
    
    conn.commit()
    conn.close()

def get_latest_context(project: str, limit: int = 5):
    """Возвращает последние записи по конкретному проекту"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT content, created_at FROM sessions WHERE project = ? ORDER BY id DESC LIMIT ?",
        (project, limit)
    )
    rows = cursor.fetchall()
    
    conn.close()
    return rows