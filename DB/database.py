import sqlite3
from datetime import datetime

DB_NAME = "jobs.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")  # 启用外键支持

    # 用户表 users
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        name TEXT,
        password TEXT,
        email TEXT,
        phonenumber TEXT UNIQUE,
        created_at TEXT
    );
    """)

    # 简历表 resumes
    c.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phonenumber TEXT,
        resume_name TEXT,
        save_path TEXT,
        upload_date TEXT,
        content_summary TEXT,
        school TEXT,
        education TEXT,
        expected_salary TEXT,
        age TEXT,
        region TEXT,
        gender TEXT,
        state TEXT,
        FOREIGN KEY (phonenumber) REFERENCES users(phonenumber)
            ON UPDATE CASCADE ON DELETE CASCADE
    );
    """)

    # 简历分析表 resume_analysis
    c.execute("""
    CREATE TABLE IF NOT EXISTS resume_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phonenumber TEXT,
        resume_id INTEGER,
        score INTEGER,
        analysis_time TEXT,
        outcome TEXT,
        state TEXT,
        FOREIGN KEY (phonenumber) REFERENCES users(phonenumber)
            ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (resume_id) REFERENCES resumes(id)
            ON UPDATE CASCADE ON DELETE CASCADE
    );
    """)

    # 分析API表 analysis_api
    c.execute("""
    CREATE TABLE IF NOT EXISTS analysis_api (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phonenumber TEXT,
        api_name TEXT,
        api_url TEXT,
        api_key TEXT,
        created_at TEXT,
        FOREIGN KEY (phonenumber) REFERENCES users(phonenumber)
            ON UPDATE CASCADE ON DELETE CASCADE
    );
    """)

    # 职位表 jobs
    c.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_name TEXT,
        job_category TEXT,
        job_description TEXT,
        created_at TEXT
    );
    """)

    conn.commit()
    conn.close()

# 初始化数据库
if __name__ == "__main__":
    init_db()
