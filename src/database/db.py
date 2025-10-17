import sqlite3
from contextlib import closing
import os

DB_PATH = "invoices.db"

def ensure_db():
    conn = sqlite3.connect(DB_PATH)
    with closing(conn.cursor()) as c:
        c.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id TEXT PRIMARY KEY,
            fileName TEXT,
            extractedText TEXT,
            predictedCategory TEXT,
            confidenceScore REAL,
            createdAt TEXT
        )
        ''')
        conn.commit()
    conn.close()

def insert_invoice(row):
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    with closing(conn.cursor()) as c:
        c.execute('''
            INSERT OR REPLACE INTO invoices (id,fileName,extractedText,predictedCategory,confidenceScore,createdAt)
            VALUES (?,?,?,?,?,?)
        ''', (row['id'], row['fileName'], row['extractedText'], row['predictedCategory'], row['confidenceScore'], row['createdAt']))
        conn.commit()
    conn.close()

def get_all(limit=100):
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    with closing(conn.cursor()) as c:
        c.execute('SELECT * FROM invoices ORDER BY createdAt DESC LIMIT ?', (limit,))
        rows = c.fetchall()
    conn.close()
    cols = ['id','fileName','extractedText','predictedCategory','confidenceScore','createdAt']
    return [dict(zip(cols, r)) for r in rows]
