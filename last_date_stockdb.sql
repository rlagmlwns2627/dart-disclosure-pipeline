USE stock_db;

SELECT
    -- 최근 데이터 (당일 기준)
    s.ticker        AS 종목,
    s.date          AS 최근_날짜,
    s.close         AS 최근_종가,
    s.volume_ratio  AS 최근_거래량비율,
    s.trade_signal  AS 최근_신호,

    -- 누적 데이터 (전체 기간 기준)
    (SELECT COUNT(DISTINCT ticker, date) FROM stock_signals) AS 누적_총건수,
    (SELECT COUNT(DISTINCT date)         FROM stock_signals) AS 누적_거래일수,
    (SELECT MIN(date)                    FROM stock_signals) AS 누적_시작일,
    (SELECT MAX(date)                    FROM stock_signals) AS 누적_종료일

FROM stock_signals s
WHERE s.id IN (
    SELECT MAX(id)
    FROM stock_signals
    WHERE date = (SELECT MAX(date) FROM stock_signals)
    GROUP BY ticker
)
ORDER BY s.ticker;