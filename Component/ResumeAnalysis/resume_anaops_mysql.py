import json
import mysql.connector
from datetime import datetime

#/oputils/db_config.py

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'smartcv',
    'port': 3307 
}
def get_mysql_connection():
    return mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        port=DB_CONFIG.get('port', 3307),
    )

# resume_anaops_mysql.py 中添加
def get_resume_json_by_resume_id(resume_id):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT json_resume_data FROM resumes WHERE id = %s", (resume_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row and row["json_resume_data"]:
        try:
            return json.loads(row["json_resume_data"])
        except Exception as e:
            print("JSON 解析失败:", e)
            return None
    return None


    #     SELECT 
    #         r.resume_name,
    #         j.job_name,
    #         ra.overall_score,
    #         ra.analysis_time,
    #         ra.json_analysis_result,
    #         ra.status
    #     FROM resume_analysis ra
    #     LEFT JOIN resumes r ON ra.resume_id = r.id
    #     LEFT JOIN jobs j ON ra.job_id = j.id
    #     WHERE ra.phonenumber = %s
    #     ORDER BY ra.analysis_time DESC
    # """, (phonenumber,))
# resume_anaops_mysql.py 中添加
def get_analy_json_by_analysis_id(analysis_id):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""SELECT 
                    json_analysis_result,
                    j.job_name
                    FROM resume_analysis ra
                    LEFT JOIN resumes r ON ra.resume_id = r.id
                    LEFT JOIN jobs j ON ra.job_id = j.id 
                    WHERE ra.id = %s""", (analysis_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row and row["json_analysis_result"]:
        try:
            print("解析结果:", row)
            return row
        except Exception as e:
            print("JSON 解析失败:", e)
            return None
    return None

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

    query = "SELECT id, overall_score, analysis_time, json_analysis_result, status FROM resume_analysis WHERE resume_id=%s"
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

def insert_analysis(phonenumber, resume_id, job_id, overall_score, analysis_summary, json_analysis_result, status="已完成"):
    """
    将简历分析结果插入到数据库 resume_analysis 表中。
    返回新插入的记录ID。
    """
    conn = get_mysql_connection()
    c = conn.cursor()

    insert_sql = """
        INSERT INTO resume_analysis (
            phonenumber, resume_id, job_id, overall_score, analysis_time,
            analysis_summary, json_analysis_result, status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        phonenumber, resume_id, job_id, overall_score,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        analysis_summary, json_analysis_result, status
    )

    c.execute(insert_sql, values)
    inserted_id = c.lastrowid
    conn.commit()
    c.close()
    conn.close()
    return inserted_id


# ✅ 修改后的 save_analysis_result 函数
def save_analysis_result(phonenumber, resume_id, job_id, overall_score, analysis_summary, json_analysis_result, status):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    analysis_time = datetime.now()

    cursor.execute("""
        INSERT INTO resume_analysis (
            phonenumber, resume_id, job_id, overall_score, analysis_time,
            analysis_summary, json_analysis_result, status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        phonenumber, resume_id, job_id, overall_score, analysis_time,
        analysis_summary, json_analysis_result, status
    ))

    conn.commit()
    analysis_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return analysis_id

# 保持不变
def save_score_detail(analysis_id, job_name, score_dict):
    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO resume_score_detail (
            analysis_id, choose_job,
            education_score, knowledge_score, experience_score,
            certification_score, personal_quality_score
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        analysis_id, job_name,
        score_dict["education_score"],
        score_dict["knowledge_score"],
        score_dict["experience_score"],
        score_dict["certification_score"],
        score_dict["personal_quality_score"]
    ))

    conn.commit()
    cursor.close()
    conn.close()

