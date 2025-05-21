import mysql.connector
from datetime import datetime

from utils.db_config import DB_CONFIG

def get_mysql_connection():
    return mysql.connector.connect(**DB_CONFIG)

def get_user_resumes(phonenumber):
    conn = get_mysql_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, resume_name, upload_date, school, education, expected_salary, age, region, gender, state 
        FROM resumes WHERE phonenumber=%s
    """, (phonenumber,))
    resumes = c.fetchall()
    c.close()
    conn.close()
    return resumes

def get_resume_analysis_by_number(phonenumber):
    conn = get_mysql_connection()
    c = conn.cursor()
    c.execute("""
        SELECT score, analysis_time, outcome, state FROM resume_analysis 
        WHERE phonenumber=%s
    """, (phonenumber,))
    analysis = c.fetchall()
    c.close()
    conn.close()
    return analysis

def get_jobs_summary():
    conn = get_mysql_connection()
    c = conn.cursor()
    # 职位分类统计
    c.execute("""
        SELECT job_category, COUNT(*) FROM jobs GROUP BY job_category
    """)
    job_cat_count = c.fetchall()
    # 职位总数
    c.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = c.fetchone()[0]
    c.close()
    conn.close()
    return job_cat_count, total_jobs
