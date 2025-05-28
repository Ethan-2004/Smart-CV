import mysql.connector
from datetime import datetime

from oputils.db_config import DB_CONFIG

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
        SELECT 
            r.resume_name,
            j.job_name,
            ra.overall_score,
            ra.analysis_time,
            ra.json_analysis_result,
            ra.status
        FROM resume_analysis ra
        LEFT JOIN resumes r ON ra.resume_id = r.id
        LEFT JOIN jobs j ON ra.job_id = j.id
        WHERE ra.phonenumber = %s
        ORDER BY ra.analysis_time DESC
    """, (phonenumber,))

    analysis = c.fetchall()
    c.close()
    conn.close()
    return analysis


def get_jobs_summary():
    conn = get_mysql_connection()
    c = conn.cursor()

    c.execute("""
        SELECT job_category, COUNT(*) FROM jobs GROUP BY job_category
    """)
    job_cat_count = c.fetchall()

    c.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = c.fetchone()[0]
    c.close()
    conn.close()
    return job_cat_count, total_jobs
