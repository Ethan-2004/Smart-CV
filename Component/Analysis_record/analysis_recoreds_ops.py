import mysql.connector
from oputils.db_config import DB_CONFIG
from oputils.secret import *

def get_connection():
    return mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        port=DB_CONFIG.get('port', 3306)
    )
def save_resume_score_detail(analysis_id, score_data, job_name):
    """
    将评分结果保存到数据库的 resume_score_detail 表中。
    :param analysis_id: 对应 resume_analysis 表中的 id
    :param score_data: 包含各项评分的字典
    :param job_name: 所选岗位名称
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    query = """
    INSERT INTO resume_score_detail (
        analysis_id,
        choose_job,
        education_score,
        skills_score,
        experience_score,
        certifications_score,
        personal_qualities_score,
        honors_score,
        languages_score,
        tools_score
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        analysis_id,
        job_name,
        score_data.get("education_score", 0),
        score_data.get("skills_score", 0),
        score_data.get("experience_score", 0),
        score_data.get("certifications_score", 0),
        score_data.get("personal_qualities_score", 0),
        score_data.get("honors_score", 0),
        score_data.get("languages_score", 0),
        score_data.get("tools_score", 0)
    )
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()


def get_latest_resume_score(phonenumber):
    """
    获取该用户最新一次的评分详情数据，用于图表展示。
    返回格式：dict
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT rsd.*
    FROM resume_score_detail rsd
    JOIN resume_analysis ra ON rsd.analysis_id = ra.id
    WHERE ra.phonenumber = %s
    ORDER BY ra.analysis_time DESC
    LIMIT 1
    """
    cursor.execute(query, (phonenumber,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def get_resume_score_detail_by_analysis_id(analysis_id):
    """
    根据传入的 analysis_id 获取对应的评分详情数据，用于图表展示。
    返回格式：dict（如果找不到返回 None）
    """
    if not analysis_id:
        return None

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT *
    FROM resume_score_detail
    WHERE analysis_id = %s
    LIMIT 1
    """
    cursor.execute(query, (analysis_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result
