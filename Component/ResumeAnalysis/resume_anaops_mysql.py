import mysql.connector
from datetime import datetime
from utils.db_config import DB_CONFIG

def get_mysql_connection():
    return mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        port=DB_CONFIG.get('port', 3307),
        # auth_plugin='mysql_native_password'  # 视情况可删
    )

def get_user_resumes(phonenumber):
    conn = get_mysql_connection()
    c = conn.cursor()
    c.execute("SELECT id, resume_name FROM resumes WHERE phonenumber=%s", (phonenumber,))
    result = c.fetchall()
    c.close()
    conn.close()
    return result

def get_resume_analysis(resume_id, start_date=None, end_date=None):
    conn = get_mysql_connection()
    c = conn.cursor()

    query = "SELECT id, score, analysis_time, outcome, state FROM resume_analysis WHERE resume_id=%s"
    params = [resume_id]

    if start_date and end_date:
        query += " AND DATE(analysis_time) BETWEEN DATE(%s) AND DATE(%s)"
        params.extend([start_date, end_date])

    query += " ORDER BY analysis_time DESC"
    c.execute(query, params)
    result = c.fetchall()
    c.close()
    conn.close()
    return result

def delete_analysis(analysis_id):
    conn = get_mysql_connection()
    c = conn.cursor()
    c.execute("DELETE FROM resume_analysis WHERE id=%s", (analysis_id,))
    conn.commit()
    c.close()
    conn.close()

def insert_analysis(phonenumber, resume_id, score, outcome, state="已完成"):
    conn = get_mysql_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO resume_analysis (phonenumber, resume_id, score, analysis_time, outcome, state)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (phonenumber, resume_id, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), outcome, state))
    conn.commit()
    c.close()
    conn.close()
