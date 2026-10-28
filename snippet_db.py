import sqlite3
import os
from utils import resource_path
from config import get_setting

_DB_PATH = None


def get_max_snippets():
    return get_setting("snippets", "max_snippets")


def get_max_content_length():
    return get_setting("snippets", "max_content_length")


def _get_db_path():
    global _DB_PATH
    if _DB_PATH is None:
        _DB_PATH = resource_path("db", "db.sqlite")
    return _DB_PATH


def _get_connection():
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    db_dir = resource_path("db")
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    conn = _get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS snippets (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT NOT NULL,
                content    TEXT NOT NULL,
                use_count  INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    finally:
        conn.close()


def get_all_snippets():
    conn = _get_connection()
    try:
        rows = conn.execute(
            "SELECT id, title, content, use_count FROM snippets ORDER BY use_count DESC, updated_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_snippet_count():
    conn = _get_connection()
    try:
        return conn.execute("SELECT COUNT(*) FROM snippets").fetchone()[0]
    finally:
        conn.close()


def add_snippet(title, content):
    max_snippets = get_max_snippets()
    if get_snippet_count() >= max_snippets:
        return f"Maximum of {max_snippets} snippets reached."

    max_length = get_max_content_length()
    if len(content) > max_length:
        return f"Snippet content exceeds {max_length} characters."

    conn = _get_connection()
    try:
        dup = conn.execute(
            "SELECT id FROM snippets WHERE content = ?", (content,)
        ).fetchone()
        if dup:
            return "A snippet with identical content already exists."

        conn.execute(
            "INSERT INTO snippets (title, content) VALUES (?, ?)",
            (title, content),
        )
        conn.commit()
        return None
    finally:
        conn.close()


def update_snippet(snippet_id, title, content):
    max_length = get_max_content_length()
    if len(content) > max_length:
        return f"Snippet content exceeds {max_length} characters."

    conn = _get_connection()
    try:
        dup = conn.execute(
            "SELECT id FROM snippets WHERE content = ? AND id != ?",
            (content, snippet_id),
        ).fetchone()
        if dup:
            return "A snippet with identical content already exists."

        conn.execute(
            "UPDATE snippets SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (title, content, snippet_id),
        )
        conn.commit()
        return None
    finally:
        conn.close()


def delete_snippet(snippet_id):
    conn = _get_connection()
    try:
        conn.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))
        conn.commit()
    finally:
        conn.close()


def increment_use_count(snippet_id):
    conn = _get_connection()
    try:
        conn.execute(
            "UPDATE snippets SET use_count = use_count + 1 WHERE id = ?",
            (snippet_id,),
        )
        conn.commit()
    finally:
        conn.close()


def search_snippets(query):
    conn = _get_connection()
    try:
        pattern = f"%{query}%"
        rows = conn.execute(
            "SELECT id, title, content, use_count FROM snippets WHERE title LIKE ? OR content LIKE ? ORDER BY use_count DESC",
            (pattern, pattern),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
