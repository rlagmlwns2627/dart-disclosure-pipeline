import json
import os
import boto3
import pymysql
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

RDS_HOST     = os.environ['RDS_HOST']
RDS_USER     = os.environ['RDS_USER']
RDS_PASSWORD = os.environ['RDS_PASSWORD']
RDS_DB       = os.environ['RDS_DB']

def lambda_handler(event, context):
    s3 = boto3.client('s3')

    # S3 트리거에서 버킷/키 추출
    record = event['Records'][0]['s3']
    bucket = record['bucket']['name']
    key    = record['object']['key']

    print(f"[INFO] 처리 시작: s3://{bucket}/{key}")

    # S3에서 JSON 읽기
    obj  = s3.get_object(Bucket=bucket, Key=key)
    data = json.loads(obj['Body'].read().decode('utf-8'))
    items = data.get('list', [])

    if not items:
        print("[INFO] 수집 데이터 없음 (공휴일/주말)")
        return {"statusCode": 200, "inserted": 0}

    # RDS 연결
    conn = pymysql.connect(
        host=RDS_HOST,
        user=RDS_USER,
        password=RDS_PASSWORD,
        database=RDS_DB,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    sql = """
        INSERT IGNORE INTO disclosures
            (rcept_no, corp_name, corp_code, stock_code,
             report_nm, rcept_dt, flr_nm, rm)
        VALUES
            (%(rcept_no)s, %(corp_name)s, %(corp_code)s, %(stock_code)s,
             %(report_nm)s, %(rcept_dt)s, %(flr_nm)s, %(rm)s)
    """

    inserted = 0
    with conn:
        with conn.cursor() as cursor:
            for item in items:
                try:
                    cursor.execute(sql, {
                        'rcept_no'  : item.get('rcept_no'),
                        'corp_name' : item.get('corp_name'),
                        'corp_code' : item.get('corp_code'),
                        'stock_code': item.get('stock_code'),
                        'report_nm' : item.get('report_nm'),
                        'rcept_dt'  : item.get('rcept_dt'),
                        'flr_nm'    : item.get('flr_nm'),
                        'rm'        : item.get('rm'),
                    })
                    inserted += cursor.rowcount
                except Exception as e:
                    print(f"[WARN] INSERT 실패: {item.get('rcept_no')} — {e}")
        conn.commit()

    print(f"[INFO] 완료: {len(items)}건 중 {inserted}건 신규 INSERT")
    return {"statusCode": 200, "inserted": inserted}