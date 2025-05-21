# import sqlite3
# from datetime import datetime

# DB_NAME = "jobs.db"

# def get_user_resumes(phonenumber):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute("""
#         SELECT id, resume_name, upload_date, school, education, expected_salary, age, region, gender, state 
#         FROM resumes WHERE phonenumber=?
#     """, (phonenumber,))
#     resumes = c.fetchall()
#     conn.close()
#     return resumes

# def get_resume_analysis_by_number(phonenumber):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute("""
#         SELECT score, analysis_time, outcome, state FROM resume_analysis 
#         WHERE phonenumber=?
#     """, (phonenumber,))
#     analysis = c.fetchall()
#     conn.close()
#     return analysis

# def get_jobs_summary():
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     # 职位分类统计
#     c.execute("""
#         SELECT job_category, COUNT(*) FROM jobs GROUP BY job_category
#     """)
#     job_cat_count = c.fetchall()
#     # 职位总数
#     c.execute("SELECT COUNT(*) FROM jobs")
#     total_jobs = c.fetchone()[0]
#     conn.close()
#     return job_cat_count, total_jobs
