import boto3
import requests
import json
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()
KST = timezone(timedelta(hours=9))

DART_API_KEY = os.environ.get('DART_API_KEY')
S3_BUCKET    = os.environ.get('S3_BUCKET')

def handler(event, context):
    today = datetime.now(KST).strftime('%Y%m%d')

    # 1. DART API 전체 페이지 수집
    url = "https://opendart.fss.or.kr/api/list.json"
    all_list = []
    page_no  = 1

    while True:
        params = {
            "crtfc_key": DART_API_KEY,
            "bgn_de": today,
            "end_de": today,
            "page_count": 100,
            "page_no": page_no,
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise RuntimeError(f"DART API 호출 실패: {e}")

        if data.get("status") != "000":
            break

        all_list.extend(data.get('list', []))

        if page_no >= data.get('total_page', 1):
            break

        page_no += 1

    # 2. S3 raw 저장
    s3  = boto3.client('s3')
    now = now = datetime.now(KST)
    key = f"raw/disclosure/{now.year}/{now.month:02d}/{now.day:02d}/data_{now.strftime('%H%M%S')}.json"

    try:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps({"list": all_list}, ensure_ascii=False),
            ContentType="application/json"
        )
    except Exception as e:
        raise RuntimeError(f"S3 저장 실패: {e}")

    # 3. CloudWatch 커스텀 메트릭 전송
    cw = boto3.client('cloudwatch')
    cw.put_metric_data(
        Namespace='DartPipeline',
        MetricData=[{
            'MetricName': 'CollectedCount',
            'Value': len(all_list),
            'Unit': 'Count'
        }]
    )

    print(f"[INFO] 수집 완료: {len(all_list)}건 → s3://{S3_BUCKET}/{key}")
    return {"statusCode": 200, "collected": len(all_list)}