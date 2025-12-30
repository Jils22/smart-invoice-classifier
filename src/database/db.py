import sqlite3
from contextlib import closing
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = "invoices.db"
DB_COLUMNS = ['id', 'fileName', 'extractedText', 'predictedCategory', 'confidenceScore', 'createdAt']

def get_connection():
    """Get a database connection with optimized settings."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn

def ensure_db():
    """Initialize database and create table if needed."""
    try:
        conn = get_connection()
        with closing(conn.cursor()) as c:
            c.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id TEXT PRIMARY KEY,
                fileName TEXT NOT NULL,
                extractedText TEXT,
                predictedCategory TEXT NOT NULL,
                confidenceScore REAL NOT NULL,
                createdAt TEXT NOT NULL
            )
            ''')
            # Create index for faster queries
            c.execute('''
            CREATE INDEX IF NOT EXISTS idx_createdAt ON invoices(createdAt DESC)
            ''')
            conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise

def insert_invoice(row):
    """Insert or update an invoice record."""
    if not all(key in row for key in ['id', 'fileName', 'predictedCategory', 'confidenceScore', 'createdAt']):
        raise ValueError("Missing required fields in invoice row")
    
    try:
        conn = get_connection()
        with closing(conn.cursor()) as c:
            c.execute('''
                INSERT OR REPLACE INTO invoices 
                (id, fileName, extractedText, predictedCategory, confidenceScore, createdAt)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                row['id'],
                row['fileName'],
                row.get('extractedText', ''),
                row['predictedCategory'],
                row['confidenceScore'],
                row['createdAt']
            ))
            conn.commit()
        conn.close()
        logger.debug(f"Invoice {row['id']} inserted/updated successfully")
    except sqlite3.Error as e:
        logger.error(f"Database insert error for invoice {row.get('id')}: {e}")
        raise

def get_all(limit=100):
    """Retrieve all invoices ordered by creation date."""
    try:
        conn = get_connection()
        with closing(conn.cursor()) as c:
            c.execute(
                'SELECT * FROM invoices ORDER BY createdAt DESC LIMIT ?',
                (limit,)
            )
            rows = c.fetchall()
        conn.close()
        return [dict(zip(DB_COLUMNS, r)) for r in rows]
    except sqlite3.Error as e:
        logger.error(f"Database query error: {e}")
        raise

def get_by_id(invoice_id):
    """Retrieve a single invoice by ID."""
    try:
        conn = get_connection()
        with closing(conn.cursor()) as c:
            c.execute('SELECT * FROM invoices WHERE id = ?', (invoice_id,))
            row = c.fetchone()
        conn.close()
        return dict(zip(DB_COLUMNS, row)) if row else None
    except sqlite3.Error as e:
        logger.error(f"Database query error: {e}")
        raise

def count_invoices():
    """Get total count of invoices."""
    try:
        conn = get_connection()
        with closing(conn.cursor()) as c:
            c.execute('SELECT COUNT(*) FROM invoices')
            count = c.fetchone()[0]
        conn.close()
        return count
    except sqlite3.Error as e:
        logger.error(f"Database count error: {e}")
        raise
