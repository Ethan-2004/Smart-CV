# import sqlite3
# from datetime import datetime

# DB_NAME = "jobs.db"

# def connect_db():
#     conn = sqlite3.connect(DB_NAME)
#     return conn

# # 增加职位
# def add_job(job_name, job_category, job_description):
#     conn = connect_db()
#     c = conn.cursor()
#     created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     c.execute("""
#         INSERT INTO jobs (job_name, job_category, job_description, created_at)
#         VALUES (?, ?, ?, ?)
#     """, (job_name, job_category, job_description, created_at))
#     conn.commit()
#     conn.close()

# # 查询所有职位
# def get_all_jobs():
#     conn = connect_db()
#     c = conn.cursor()
#     c.execute("SELECT id, job_name, job_category, job_description, created_at FROM jobs ORDER BY created_at DESC")
#     rows = c.fetchall()
#     conn.close()
#     return rows

# # 根据ID查询单个职位
# def get_job_by_id(job_id):
#     conn = connect_db()
#     c = conn.cursor()
#     c.execute("SELECT id, job_name, job_category, job_description, created_at FROM jobs WHERE id=?", (job_id,))
#     row = c.fetchone()
#     conn.close()
#     return row

# # 更新职位
# def update_job(job_id, job_name, job_category, job_description):
#     conn = connect_db()
#     c = conn.cursor()
#     c.execute("""
#         UPDATE jobs 
#         SET job_name=?, job_category=?, job_description=?
#         WHERE id=?
#     """, (job_name, job_category, job_description, job_id))
#     conn.commit()
#     conn.close()

# # 删除职位
# def delete_job(job_id):
#     conn = connect_db()
#     c = conn.cursor()
#     c.execute("DELETE FROM jobs WHERE id=?", (job_id,))
#     # conn.commit()
#     conn.close()
