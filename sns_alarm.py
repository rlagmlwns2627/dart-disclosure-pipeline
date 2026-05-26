import boto3
import os
from dotenv import load_dotenv

load_dotenv()

SNS_ARN = os.environ['SNS_ARN']

cw = boto3.client('cloudwatch', region_name='ap-northeast-2')

# 알람 1. Lambda 에러 감지
cw.put_metric_alarm(
    AlarmName='dart-collector-errors',       # 알람 이름 (콘솔에 표시됨)
    MetricName='Errors',                     # 감시할 지표 (Lambda 실행 에러 횟수)
    Namespace='AWS/Lambda',                  # 지표가 속한 그룹 (AWS 기본 제공)
    Dimensions=[{
        'Name': 'FunctionName',
        'Value': 'dart-collector'            # 감시 대상 Lambda 함수 지정
    }],
    Statistic='Sum',                         # 기간 내 에러 횟수를 합산
    Period=300,                              # 집계 기간 (초). 300 = 5분
    EvaluationPeriods=1,                     # 몇 번 연속 조건 충족 시 알람 발동. 1 = 즉시
    Threshold=1,                             # 기준값. 에러가 1번 이상이면 알람
    ComparisonOperator='GreaterThanOrEqualToThreshold',  # 지표 >= Threshold
    AlarmActions=[SNS_ARN],                  # 알람 발동 시 SNS로 이메일 발송
    TreatMissingData='notBreaching'          # 데이터 없으면(미실행) 정상으로 간주
)
print("dart-collector-errors 생성 완료")

# 알람 2. 실행 시간 초과 감지
cw.put_metric_alarm(
    AlarmName='dart-collector-duration',
    MetricName='Duration',                   # Lambda 실행 시간 (밀리초 단위)
    Namespace='AWS/Lambda',
    Dimensions=[{
        'Name': 'FunctionName',
        'Value': 'dart-collector'
    }],
    Statistic='Average',                     # 기간 내 평균 실행 시간으로 판단
    Period=300,
    EvaluationPeriods=1,
    Threshold=25000,                         # 25,000ms = 25초 (타임아웃 30초 기준)
    ComparisonOperator='GreaterThanThreshold',  # 지표 > Threshold
    AlarmActions=[SNS_ARN],
    TreatMissingData='notBreaching'
)
print("dart-collector-duration 생성 완료")

# 알람 3. 수집 건수 0건 감지
cw.put_metric_alarm(
    AlarmName='dart-zero-disclosures',
    MetricName='CollectedCount',             # handler.py에서 직접 전송한 커스텀 지표
    Namespace='DartPipeline',                # 커스텀 네임스페이스 (AWS/Lambda 아님)
    Statistic='Sum',
    Period=86400,                            # 86,400초 = 24시간 (하루 단위 집계)
    EvaluationPeriods=1,
    Threshold=1,                             # 하루 수집 건수가 1 미만(=0건)이면 알람
    ComparisonOperator='LessThanThreshold',  # 지표 < Threshold
    AlarmActions=[SNS_ARN],
    TreatMissingData='breaching'             # 데이터 없으면(미실행) 알람으로 간주
)
print("dart-zero-disclosures 생성 완료")