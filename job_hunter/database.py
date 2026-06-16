"""
Gestion de la base de données SQLite pour tracker les offres et candidatures
"""

import sqlite3
from datetime import datetime
from config import DB_PATH


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            job_id TEXT,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            salary TEXT,
            url TEXT UNIQUE NOT NULL,
            description TEXT,
            score REAL,
            score_reason TEXT,
            found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'found'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER REFERENCES jobs(id),
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            method TEXT,
            account_created INTEGER DEFAULT 0,
            confirmation TEXT,
            error TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)

    conn.commit()
    conn.close()


def save_job(source, title, company, location, url, description="", salary="", job_id=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT OR IGNORE INTO jobs (source, job_id, title, company, location, salary, url, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (source, job_id, title, company, location, salary, url, description))
        conn.commit()
        return c.lastrowid
    except Exception as e:
        print(f"  [DB] Erreur sauvegarde: {e}")
        return None
    finally:
        conn.close()


def update_job_score(url, score, reason):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE jobs SET score=?, score_reason=? WHERE url=?", (score, reason, url))
    conn.commit()
    conn.close()


def save_application(job_db_id, method, account_created=False, confirmation="", error="", status="success"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO applications (job_id, method, account_created, confirmation, error, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (job_db_id, method, 1 if account_created else 0, confirmation, error, status))
    c.execute("UPDATE jobs SET status=? WHERE id=?", (status, job_db_id))
    conn.commit()
    conn.close()


def get_pending_jobs(min_score=0.5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, source, title, company, url, score, score_reason
        FROM jobs
        WHERE score >= ? AND status = 'found'
        ORDER BY score DESC
    """, (min_score,))
    rows = c.fetchall()
    conn.close()
    return rows


def get_all_jobs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT j.id, j.source, j.title, j.company, j.url, j.score, j.status,
               a.applied_at, a.status as app_status
        FROM jobs j
        LEFT JOIN applications a ON a.job_id = j.id
        ORDER BY j.score DESC, j.found_at DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows


def already_seen(url):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM jobs WHERE url=?", (url,))
    result = c.fetchone()
    conn.close()
    return result is not None
