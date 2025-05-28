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
        port=DB_CONFIG.get('port', 3306),
        auth_plugin='mysql_native_password'  
    )

def insert_resume(phonenumber, resume_name, save_path, upload_date, content_summary,
                school, education, expected_salary, age, region, gender, state, file_hash,json_resume_data):
    conn = get_mysql_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO resumes (phonenumber, resume_name,  save_path, upload_date, content_summary,
            school, education, expected_salary, age, region, gender, state, file_hash,json_resume_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (phonenumber, resume_name, save_path,upload_date,  content_summary,
        school, education, expected_salary, age, region, gender, state, file_hash,json_resume_data))
    conn.commit()
    c.close()
    conn.close()


def get_all_resumes(phonenumber):
    conn = get_mysql_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM resumes WHERE phonenumber = %s ORDER BY upload_date DESC", (phonenumber,))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows

def delete_resume(resume_id):
    conn = get_mysql_connection()
    c = conn.cursor()
    c.execute("DELETE FROM resumes WHERE id = %s", (resume_id,))
    conn.commit()
    c.close()
    conn.close()

def update_resume(resume_id, field, value):
    conn = get_mysql_connection()
    c = conn.cursor()
    query = f"UPDATE resumes SET {field} = %s WHERE id = %s"
    c.execute(query, (value, resume_id))
    conn.commit()
    c.close()
    conn.close()

def get_resume_by_id(resume_id):
    conn = get_mysql_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM resumes WHERE id = %s", (resume_id,))
    row = c.fetchone()
    c.close()
    conn.close()
    return row

def check_resume_by_hash(file_hash):
    conn = get_mysql_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM resumes WHERE file_hash = %s", (file_hash,))
    count = c.fetchone()[0]
    c.close()
    conn.close()
    return count > 0

def update_json_resume_data(resume_id, structured_resume):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE resumes
        SET json_resume_data = %s
        WHERE id = %s
    """, (json.dumps(structured_resume, ensure_ascii=False), resume_id))
    conn.commit()
    cursor.close()
    conn.close()