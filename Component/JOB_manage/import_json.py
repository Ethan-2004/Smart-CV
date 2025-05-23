# file: Component.py
from sqlalchemy import create_engine, Table, Column, Integer, String, Text, MetaData, DateTime
from datetime import datetime
from oputils.db_config import DB_CONFIG

DB_URI = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG.get('port', 3306)}/{DB_CONFIG['database']}?charset=utf8mb4"

engine = create_engine(DB_URI, echo=False)
metadata = MetaData()

jobs_table = Table(
    'jobs', metadata,
    Column('id', Integer, primary_key=True),
    Column('job_name', String(255)),
    Column('job_category', String(255)),
    Column('job_description', Text),
    Column('created_at', DateTime)
)

# ✅ SQLAlchemy 批量插入
def add_jobs_batch_sqlalchemy(job_list):
    conn = engine.connect()
    now = datetime.now()
    values = []

    for job in job_list:
        name = job.get("name", "").strip()
        category = job.get("category", "").strip()
        description = job.get("description", "")
        if name and category:
            values.append({
                "job_name": name,
                "job_category": category,
                "job_description": description,
                "created_at": now
            })

    if values:
        conn.execute(jobs_table.insert(), values)
        conn.commit()
    conn.close()
    return len(values)
