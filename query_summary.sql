SELECT '[ 날짜별 수집 건수 ]' AS 구분, '' AS 건수
UNION ALL
SELECT rcept_dt, COUNT(*)
FROM disclosures GROUP BY rcept_dt
UNION ALL
SELECT '[ 최다 공시 기업 TOP 10 ]' , ''
UNION ALL
SELECT corp_name, cnt FROM (
    SELECT corp_name, COUNT(*) AS cnt
    FROM disclosures GROUP BY corp_name ORDER BY cnt DESC LIMIT 10
) t
UNION ALL
SELECT '[ 최다 접수 공시유형 TOP 10 ]', ''
UNION ALL
SELECT report_nm, cnt FROM (
    SELECT report_nm, COUNT(*) AS cnt
    FROM disclosures GROUP BY report_nm ORDER BY cnt DESC LIMIT 10
) t
UNION ALL
SELECT '[ 전체 합계 ]', ''
UNION ALL
SELECT '총 적재 건수', COUNT(*) FROM disclosures;