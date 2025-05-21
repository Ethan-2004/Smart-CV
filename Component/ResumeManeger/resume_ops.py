# import sqlite3
# from datetime import datetime

# DB_NAME = "jobs.db"

# def insert_resume(phonenumber, resume_name, save_path, content_summary, school, education, expected_salary, age, region, gender, state):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute("""
#         INSERT INTO resumes (phonenumber, resume_name, save_path, upload_date, content_summary, school, education, expected_salary, age, region, gender, state)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """, (phonenumber, resume_name, save_path, datetime.now().strftime("%Y-%m-%d %H:%M"), content_summary, school, education, expected_salary, age, region, gender, state))
#     conn.commit()
#     conn.close()

# def get_all_resumes(phonenumber):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute("SELECT * FROM resumes WHERE phonenumber = ? ORDER BY upload_date DESC", (phonenumber,))
#     rows = c.fetchall()
#     conn.close()
#     return rows

# def delete_resume(resume_id):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
#     conn.commit()
#     conn.close()

# def update_resume(resume_id, field, value):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     query = f"UPDATE resumes SET {field} = ? WHERE id = ?"
#     c.execute(query, (value, resume_id))
#     conn.commit()
#     conn.close()

# def get_resume_by_id(resume_id):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
#     row = c.fetchone()
#     conn.close()
#     return row