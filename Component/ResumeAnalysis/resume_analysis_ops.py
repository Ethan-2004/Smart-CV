# import sqlite3
# from datetime import datetime

# DB_NAME = "jobs.db"

# def get_user_resumes(phonenumber):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute("SELECT id, resume_name FROM resumes WHERE phonenumber=?", (phonenumber,))
#     result = c.fetchall()
#     conn.close()
#     return result

# def get_resume_analysis(resume_id, start_date=None, end_date=None):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()

#     query = "SELECT id, score, analysis_time, outcome, state FROM resume_analysis WHERE resume_id=?"
#     params = [resume_id]

#     if start_date and end_date:
#         query += " AND date(analysis_time) BETWEEN date(?) AND date(?)"
#         params.extend([start_date, end_date])

#     query += " ORDER BY analysis_time DESC"
#     c.execute(query, params)
#     result = c.fetchall()
#     conn.close()
#     return result

# def delete_analysis(analysis_id):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute("DELETE FROM resume_analysis WHERE id=?", (analysis_id,))
#     conn.commit()
#     conn.close()

# def insert_analysis(phonenumber, resume_id, score, outcome, state="已完成"):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute("""
#         INSERT INTO resume_analysis (phonenumber, resume_id, score, analysis_time, outcome, state)
#         VALUES (?, ?, ?, ?, ?, ?)
#     """, (phonenumber, resume_id, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), outcome, state))
#     conn.commit()
#     conn.close()
