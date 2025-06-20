import mysql.connector
from datetime import datetime
from oputils.db_config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        port=DB_CONFIG.get('port', 3306)
    )
def add_job(job_name, job_category, job_description):
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO jobs (job_name, job_category, job_description, created_at)
        VALUES (%s, %s, %s, %s)
    """, (job_name, job_category, job_description, created_at))
    conn.commit()
    cursor.close()
    conn.close()

def add_jobs_batch(job_list):
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    values = []
    for job in job_list:
        name = job.get("name", "").strip()
        category = job.get("category", "").strip()
        description = job.get("description", "")
        if name and category:
            values.append((name, category, description, created_at))

    if values:
        cursor.executemany("""
            INSERT INTO jobs (job_name, job_category, job_description, created_at)
            VALUES (%s, %s, %s, %s)
        """, values)
        conn.commit()

    cursor.close()
    conn.close()
    return len(values)

def get_all_jobs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, job_name, job_category, job_description, created_at FROM jobs ORDER BY created_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_job_by_id(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, job_name, job_category, job_description, created_at FROM jobs WHERE id=%s", (job_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def update_job(job_id, job_name, job_category, job_description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE jobs 
        SET job_name=%s, job_category=%s, job_description=%s
        WHERE id=%s
    """, (job_name, job_category, job_description, job_id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_job(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id=%s", (job_id,))
    conn.commit()
    cursor.close()
    conn.close()

def delete_all_jobs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs")  
    conn.commit()
    cursor.close()
    conn.close()
