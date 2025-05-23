import json
import mysql.connector
from datetime import datetime
from oputils.db_config import DB_CONFIG

def get_mysql_connection():
    return mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        port=DB_CONFIG.get('port', 3306)
    )

# ——— 绩效评估 ———
def save_performance(phonenumber: str, resume_id: int, analysis_id: int, scores: dict, summary: str):
    conn = get_mysql_connection()
    cur = conn.cursor()
    cur.execute("""
      INSERT INTO performance_evaluations
        (phonenumber, resume_id, analysis_id, scores, summary, created_at)
      VALUES (%s, %s, %s, %s, %s, %s)
    """, (
      phonenumber,
      resume_id,
      analysis_id,
      json.dumps(scores, ensure_ascii=False),
      summary,
      datetime.now()
    ))
    conn.commit()
    cur.close()
    conn.close()

def get_performance_by_user(phonenumber: str, resume_id: int = None):
    conn = get_mysql_connection()
    cur = conn.cursor(dictionary=True)
    if resume_id:
        cur.execute("""
          SELECT id, resume_id, analysis_id, scores, summary, created_at
          FROM performance_evaluations
          WHERE phonenumber=%s AND resume_id=%s
          ORDER BY created_at DESC
        """, (phonenumber, resume_id))
    else:
        cur.execute("""
          SELECT id, resume_id, analysis_id, scores, summary, created_at
          FROM performance_evaluations
          WHERE phonenumber=%s
          ORDER BY created_at DESC
        """, (phonenumber,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# ——— 培训推荐 ———
def save_training(phonenumber: str, resume_id: int, analysis_id: int, content: str):
    conn = get_mysql_connection()
    cur = conn.cursor()
    cur.execute("""
      INSERT INTO training_recommendations
        (phonenumber, resume_id, analysis_id, content, created_at)
      VALUES (%s, %s, %s, %s, %s)
    """, (phonenumber, resume_id, analysis_id, content, datetime.now()))
    conn.commit()
    cur.close()
    conn.close()

def get_training_by_analysis(analysis_id: int):
    conn = get_mysql_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
      SELECT id, resume_id, content, created_at
      FROM training_recommendations
      WHERE analysis_id=%s
      ORDER BY created_at DESC
      LIMIT 1
    """, (analysis_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

# ——— 留存预测 ———
def save_retention(phonenumber: str, resume_id: int, analysis_id: int, risk_level: str, details: dict):
    conn = get_mysql_connection()
    cur = conn.cursor()
    cur.execute("""
      INSERT INTO retention_predictions
        (phonenumber, resume_id, analysis_id, risk_level, details, created_at)
      VALUES (%s, %s, %s, %s, %s, %s)
    """, (
      phonenumber,
      resume_id,
      analysis_id,
      risk_level,
      json.dumps(details, ensure_ascii=False),
      datetime.now()
    ))
    conn.commit()
    cur.close()
    conn.close()

def get_retention_by_user(phonenumber: str, resume_id: int = None):
    conn = get_mysql_connection()
    cur = conn.cursor(dictionary=True)
    if resume_id:
        cur.execute("""
          SELECT id, resume_id, analysis_id, risk_level, details, created_at
          FROM retention_predictions
          WHERE phonenumber=%s AND resume_id=%s
          ORDER BY created_at DESC
        """, (phonenumber, resume_id))
    else:
        cur.execute("""
          SELECT id, resume_id, analysis_id, risk_level, details, created_at
          FROM retention_predictions
          WHERE phonenumber=%s
          ORDER BY created_at DESC
        """, (phonenumber,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
