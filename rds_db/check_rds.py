# scripts/check_rds.py
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

conn = pymysql.connect(
    host=os.environ['RDS_HOST'],
    user=os.environ['RDS_USER'],
    password=os.environ['RDS_PASSWORD'],
    database=os.environ['RDS_DB'],
    charset='utf8mb4'
)

with conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM disclosures")
        count = cursor.fetchone()
        print(f"총 적재 건수: {count[0]}건")

        cursor.execute("SELECT rcept_no, corp_name, report_nm, rcept_dt FROM disclosures ORDER BY rcept_dt DESC LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(row)