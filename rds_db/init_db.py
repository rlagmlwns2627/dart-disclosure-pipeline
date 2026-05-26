import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

RDS_HOST     = os.environ.get('RDS_HOST')
RDS_USER     = os.environ.get('RDS_USER')
RDS_PASSWORD = os.environ.get('RDS_PASSWORD')
RDS_DB       = os.environ.get('RDS_DB')

# 1. DB 생성
conn = pymysql.connect(
    host=RDS_HOST,
    user=RDS_USER,
    password=RDS_PASSWORD,
    port=3306,
    charset='utf8mb4'
)

with conn.cursor() as cur:
    cur.execute("CREATE DATABASE IF NOT EXISTS dart_pipeline")
    print("dart_pipeline DB 생성 완료")

conn.close()

# 2. 테이블 생성
conn = pymysql.connect(
    host=RDS_HOST,
    user=RDS_USER,
    password=RDS_PASSWORD,
    db=RDS_DB,
    port=3306,
    charset='utf8mb4'
)

with conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS disclosures (
            id         BIGINT AUTO_INCREMENT PRIMARY KEY,
            rcept_no   VARCHAR(20)  NOT NULL UNIQUE COMMENT '접수번호',
            corp_name  VARCHAR(100) COMMENT '회사명',
            corp_code  VARCHAR(10)  COMMENT '종목코드',
            stock_code VARCHAR(10)  COMMENT '종목코드(상장사)',
            report_nm  VARCHAR(200) COMMENT '보고서명',
            rcept_dt   DATE         COMMENT '접수일자',
            flr_nm     VARCHAR(100) COMMENT '제출인',
            rm         VARCHAR(10)  COMMENT '비고',
            created_at DATETIME     DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_rcept_dt (rcept_dt),
            INDEX idx_corp_code (corp_code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    conn.commit()
    print("disclosures 테이블 생성 완료")

conn.close()