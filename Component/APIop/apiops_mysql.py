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

def insert_analysis_api(phonenumber, api_name, api_url, api_key, created_at):
    encrypted_key = encrypt_api_key(api_key) if api_key else None
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO analysis_api (phonenumber, api_name, api_url, api_key, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """, (phonenumber, api_name, api_url, encrypted_key, created_at))
    conn.commit()
    cursor.close()
    conn.close()

def update_analysis_api(id, phonenumber, api_name, api_url, api_key):
    encrypted_key = encrypt_api_key(api_key) if api_key else None
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE analysis_api SET
        phonenumber=%s, api_name=%s, api_url=%s, api_key=%s
        WHERE id=%s
    """, (phonenumber, api_name, api_url, encrypted_key, id))
    conn.commit()
    cursor.close()
    conn.close()

def get_analysis_api(phonenumber):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, phonenumber, api_name, api_url, api_key, created_at
        FROM analysis_api
        WHERE phonenumber=%s
    """, (phonenumber,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    result = []
    for row in rows:
        id, phone, name, url, encrypted_key, created_at = row
        api_key = decrypt_api_key(encrypted_key) if encrypted_key else ""
        result.append({
            "id": id,
            "phonenumber": phone,
            "api_name": name,
            "api_url": url,
            "api_key": api_key,
            "created_at": created_at
        })
    return result

def delete_analysis_api(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analysis_api WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

def get_all_models(phonenumber):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT api_name, api_url, api_key
        FROM analysis_api
        WHERE phonenumber = %s
        ORDER BY created_at DESC
    """, (phonenumber,))
    results = cursor.fetchall()
    cursor.close()
    return results
