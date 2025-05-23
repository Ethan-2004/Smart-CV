import mysql.connector
from mysql.connector import errorcode
from datetime import datetime

#/oputils/db_config.py

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'smartcv',
    'port': 3306
}
def init_mysql_db():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.database = DB_CONFIG['database']

        # 开启外键约束
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        # 创建 users 表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE,
            name VARCHAR(255),
            password VARCHAR(255),
            email VARCHAR(255),
            phonenumber VARCHAR(20) UNIQUE,
            created_at DATETIME
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 创建 resumes 表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            phonenumber VARCHAR(20),
            resume_name VARCHAR(255),
            file_hash VARCHAR(128),
            save_path TEXT,
            upload_date DATETIME,
            content_summary TEXT,
            school VARCHAR(255),
            education VARCHAR(100),
            expected_salary VARCHAR(100),
            age VARCHAR(10),
            region VARCHAR(100),
            gender VARCHAR(10),
            state VARCHAR(50),
            CONSTRAINT fk_resumes_users FOREIGN KEY (phonenumber)
                REFERENCES users(phonenumber) ON UPDATE CASCADE ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 创建 resume_analysis 表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resume_analysis (
            id INT AUTO_INCREMENT PRIMARY KEY,
            phonenumber VARCHAR(20),
            resume_id INT,
            score INT,
            analysis_time DATETIME,
            outcome TEXT,
            state VARCHAR(50),
            CONSTRAINT fk_analysis_users FOREIGN KEY (phonenumber)
                REFERENCES users(phonenumber) ON UPDATE CASCADE ON DELETE CASCADE,
            CONSTRAINT fk_analysis_resumes FOREIGN KEY (resume_id)
                REFERENCES resumes(id) ON UPDATE CASCADE ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 创建 analysis_api 表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_api (
            id INT AUTO_INCREMENT PRIMARY KEY,
            phonenumber VARCHAR(20),
            api_name VARCHAR(255),
            api_url TEXT,
            api_key TEXT,
            created_at DATETIME,
            CONSTRAINT fk_api_users FOREIGN KEY (phonenumber)
                REFERENCES users(phonenumber) ON UPDATE CASCADE ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 创建 jobs 表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            job_name VARCHAR(255),
            job_category VARCHAR(255),
            job_description TEXT,
            created_at DATETIME
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        conn.commit()
        print("MySQL 数据库和表初始化成功！")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("用户名或密码错误")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("数据库不存在")
        else:
            print(err)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_mysql_db()
