"""
database.py
Простая обёртка над SQLite.

Таблица `vault_meta` хранит ОДНУ строку: хеш мастер-пароля, соль для
деривации ключа и контрольный токен (зашифрованная строка "check"),
по которому при входе проверяется, что мастер-пароль подобран верно
и ключ расшифровки действительно подходит.

Таблица `entries` хранит сами записи. Поля username/password/notes/url
лежат в зашифрованном виде (шифрует/расшифровывает их security.py,
сама база ничего не знает о шифровании).
"""

import sqlite3
from dataclasses import dataclass
from typing import Optional, List

DB_PATH = "vault.db"


@dataclass
class Entry:
    id: Optional[int]
    title: str
    username: str
    password: str
    url: str
    notes: str


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vault_meta (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            master_hash TEXT NOT NULL,
            salt BLOB NOT NULL,
            check_token TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            username TEXT,
            password TEXT,
            url TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()


def vault_exists() -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM vault_meta")
    row = cur.fetchone()
    conn.close()
    return row["c"] > 0


def create_vault(master_hash: str, salt: bytes, check_token: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO vault_meta (id, master_hash, salt, check_token) VALUES (1, ?, ?, ?)",
        (master_hash, salt, check_token),
    )
    conn.commit()
    conn.close()


def get_vault_meta():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM vault_meta WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    return row


def add_entry(title, username_enc, password_enc, url_enc, notes_enc) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO entries (title, username, password, url, notes) VALUES (?, ?, ?, ?, ?)",
        (title, username_enc, password_enc, url_enc, notes_enc),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_entry(entry_id, title, username_enc, password_enc, url_enc, notes_enc):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """UPDATE entries SET title=?, username=?, password=?, url=?, notes=?
           WHERE id=?""",
        (title, username_enc, password_enc, url_enc, notes_enc, entry_id),
    )
    conn.commit()
    conn.close()


def delete_entry(entry_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()


def get_all_entries() -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM entries ORDER BY title COLLATE NOCASE")
    rows = cur.fetchall()
    conn.close()
    return rows
