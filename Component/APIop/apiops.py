# import sqlite3
# from utils.secret import *

# DB_PATH = "jobs.db"

# def insert_analysis_api(phonenumber, api_name, api_url, api_key, created_at):
#     encrypted_key = encrypt_api_key(api_key) if api_key else None
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("""
#         INSERT INTO analysis_api (phonenumber, api_name, api_url, api_key, created_at)
#         VALUES (?, ?, ?, ?, ?)
#     """, (phonenumber, api_name, api_url, encrypted_key, created_at))
#     conn.commit()
#     conn.close()

# def update_analysis_api(id, phonenumber, api_name, api_url, api_key):
#     encrypted_key = encrypt_api_key(api_key) if api_key else None
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("""
#         UPDATE analysis_api SET
#         phonenumber=?, api_name=?, api_url=?, api_key=?
#         WHERE id=?
#     """, (phonenumber, api_name, api_url, encrypted_key, id))
#     conn.commit()
#     conn.close()

# def get_analysis_api(phonenumber):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("""
#         SELECT id, phonenumber, api_name, api_url, api_key, created_at
#         FROM analysis_api
#         WHERE phonenumber=?
#     """, (phonenumber,))
#     rows = c.fetchall()
#     conn.close()

#     result = []
#     for row in rows:
#         id, phone, name, url, encrypted_key, created_at = row
#         api_key = decrypt_api_key(encrypted_key) if encrypted_key else ""
#         result.append({
#             "id": id,
#             "phonenumber": phone,
#             "api_name": name,
#             "api_url": url,
#             "api_key": api_key,
#             "created_at": created_at
#         })
#     return result

# def delete_analysis_api(id):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("DELETE FROM analysis_api WHERE id=?", (id,))
#     conn.commit()
#     conn.close()
