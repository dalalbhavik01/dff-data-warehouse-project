-- ============================================================
-- Script 06: Load Fact Tables
-- DFF Data Warehouse Project — Report 3
-- Run AFTER Script 05 (Load Dimensions).
-- Dimensions must be populated first because fact tables
-- reference dimension surrogate keys via foreign keys.
-- ============================================================
USE [team1_dw_area];
GO

-- ===============================
-- 1. FactWeeklySales
-- ===============================
-- Grain: One row per UPC × Store × Week
-- Sources: 4 movement staging tables (SDR, CSO, TPA, CRA)
-- Filters: OK = 1 (valid data), PRICE > 0 (avoid zero-price rows)
-- Derived columns:
--   unit_price        = PRICE / QTY
--   revenue           = MOVE × (PRICE / QTY)
--   profit_margin_pct = (PROFIT / revenue) × 100

PRINT 'Loading FactWeeklySales... (this may take several minutes for ~34M rows)';
GO

INSERT INTO dbo.FactWeeklySales
    (product_key, store_key, time_key, category_key, promotion_key,
     units_sold, unit_price, shelf_price, price_qty, revenue, 
     gross_profit, profit_margin_pct)
SELECT 
    dp.product_key,
    ds.store_key,
    dt.time_key,
    dc.category_key,
    dpr.promotion_key,
    sm.MOVE                                                    AS units_sold,
    CASE WHEN sm.QTY > 0 
         THEN CAST(sm.PRICE / sm.QTY AS DECIMAL(8,2)) 
         ELSE NULL 
    END                                                        AS unit_price,
    CAST(sm.PRICE AS DECIMAL(8,2))                             AS shelf_price,
    sm.QTY                                                     AS price_qty,
    CASE WHEN sm.QTY > 0 
         THEN CAST(sm.MOVE * (sm.PRICE / sm.QTY) AS DECIMAL(12,2)) 
         ELSE 0 
    END                                                        AS revenue,
    CAST(sm.PROFIT AS DECIMAL(10,2))                           AS gross_profit,
    CASE WHEN sm.MOVE > 0 AND sm.QTY > 0 AND sm.PRICE > 0
         THEN CAST(
              (sm.PROFIT / (sm.MOVE * (sm.PRICE / sm.QTY))) * 100 
              AS DECIMAL(5,2))
         ELSE NULL 
    END                                                        AS profit_margin_pct
FROM (
    -- UNION ALL of the 4 category movement staging tables
    SELECT UPC, STORE, WEEK, MOVE, QTY, PRICE, SALE, PROFIT, OK, CATEGORY_CODE 
    FROM [team1_staging_area].dbo.stg_Movement_SDR 
    WHERE OK = 1 AND PRICE > 0
    UNION ALL
    SELECT UPC, STORE, WEEK, MOVE, QTY, PRICE, SALE, PROFIT, OK, CATEGORY_CODE 
    FROM [team1_staging_area].dbo.stg_Movement_CSO 
    WHERE OK = 1 AND PRICE > 0
    UNION ALL
    SELECT UPC, STORE, WEEK, MOVE, QTY, PRICE, SALE, PROFIT, OK, CATEGORY_CODE 
    FROM [team1_staging_area].dbo.stg_Movement_TPA 
    WHERE OK = 1 AND PRICE > 0
    UNION ALL
    SELECT UPC, STORE, WEEK, MOVE, QTY, PRICE, SALE, PROFIT, OK, CATEGORY_CODE 
    FROM [team1_staging_area].dbo.stg_Movement_CRA 
    WHERE OK = 1 AND PRICE > 0
) sm
-- Join to dimension tables to get surrogate keys
INNER JOIN dbo.DimProduct dp 
    ON sm.UPC = dp.upc
INNER JOIN dbo.DimStore ds 
    ON sm.STORE = ds.store_id
INNER JOIN dbo.DimTime dt 
    ON sm.WEEK = dt.week_id
INNER JOIN dbo.DimCategory dc 
    ON sm.CATEGORY_CODE = dc.category_code
LEFT JOIN dbo.DimPromotion dpr 
    ON (sm.SALE = dpr.deal_code)
    OR (sm.SALE = 'N' AND dpr.deal_code IS NULL);
GO

PRINT 'FactWeeklySales loaded:';
SELECT COUNT(*) AS RowCount FROM dbo.FactWeeklySales;
SELECT TOP 10 * FROM dbo.FactWeeklySales ORDER BY sales_fact_id;
GO

-- Row count by category (verification)
SELECT dc.category_name, COUNT(*) AS FactRows
FROM dbo.FactWeeklySales f
JOIN dbo.DimCategory dc ON f.category_key = dc.category_key
GROUP BY dc.category_name
ORDER BY FactRows DESC;
GO

-- ===============================
-- 2. FactCustomerTraffic
-- ===============================
-- Grain: One row per Store × Week
-- Source: stg_CustomerTraffic (cleaned)
-- Joins to DimStore and DimTime for surrogate keys
-- Derived: total_coupon_redemptions = SUM of all *COUP columns

PRINT 'Loading FactCustomerTraffic...';
GO

INSERT INTO dbo.FactCustomerTraffic
    (store_key, time_key, total_customers, 
     grocery_count, dairy_count, frozen_count, meat_count,
     produce_count, deli_count, bakery_count, pharmacy_count,
     beer_count, spirits_count, mvp_club_count, total_coupon_redemptions)
SELECT 
    ds.store_key,
    dt.time_key,
    CAST(ct.CUSTCOUN AS DECIMAL(10,2))                         AS total_customers,
    CAST(ct.GROCERY AS DECIMAL(10,2))                          AS grocery_count,
    CAST(ct.DAIRY AS DECIMAL(10,2))                            AS dairy_count,
    CAST(ct.FROZEN AS DECIMAL(10,2))                           AS frozen_count,
    CAST(ct.MEAT AS DECIMAL(10,2))                             AS meat_count,
    CAST(ct.PRODUCE AS DECIMAL(10,2))                          AS produce_count,
    CAST(ct.DELI AS DECIMAL(10,2))                             AS deli_count,
    CAST(ct.BAKERY AS DECIMAL(10,2))                           AS bakery_count,
    CAST(ct.PHARMACY AS DECIMAL(10,2))                         AS pharmacy_count,
    CAST(ct.BEER AS DECIMAL(10,2))                             AS beer_count,
    CAST(ct.SPIRITS AS DECIMAL(10,2))                          AS spirits_count,
    CAST(ct.MVPCLUB AS DECIMAL(10,2))                          AS mvp_club_count,
    -- Sum all coupon columns for total_coupon_redemptions
    ISNULL(CAST(ct.GROCCOUP AS DECIMAL(10,2)), 0) +
    ISNULL(CAST(ct.DAIRYCOUP AS DECIMAL(10,2)), 0) +
    ISNULL(CAST(ct.FROZNCOUP AS DECIMAL(10,2)), 0) +
    ISNULL(CAST(ct.MEATCOUP AS DECIMAL(10,2)), 0) +
    ISNULL(CAST(ct.PRODCOUP AS DECIMAL(10,2)), 0) +
    ISNULL(CAST(ct.DELICOUP AS DECIMAL(10,2)), 0) +
    ISNULL(CAST(ct.BAKCOUP AS DECIMAL(10,2)), 0) +
    ISNULL(CAST(ct.PHARMCOUP AS DECIMAL(10,2)), 0) +
    ISNULL(CAST(ct.BEERCOUP AS DECIMAL(10,2)), 0) +
    ISNULL(CAST(ct.WINECOUP AS DECIMAL(10,2)), 0) +
    ISNULL(CAST(ct.SPIRCOUP AS DECIMAL(10,2)), 0)             AS total_coupon_redemptions
FROM [team1_staging_area].dbo.stg_CustomerTraffic ct
INNER JOIN dbo.DimStore ds 
    ON CAST(ct.STORE AS INT) = ds.store_id
INNER JOIN dbo.DimTime dt 
    ON CAST(ct.WEEK AS INT) = dt.week_id;
GO

PRINT 'FactCustomerTraffic loaded:';
SELECT COUNT(*) AS RowCount FROM dbo.FactCustomerTraffic;
SELECT TOP 10 * FROM dbo.FactCustomerTraffic ORDER BY traffic_fact_id;
GO

-- ===============================
-- FACT TABLE VERIFICATION
-- ===============================
PRINT '========================================';
PRINT '  ALL FACT TABLES LOADED';
PRINT '========================================';

SELECT 'FactWeeklySales'      AS TableName, COUNT(*) AS RowCount FROM dbo.FactWeeklySales
UNION ALL 
SELECT 'FactCustomerTraffic', COUNT(*) FROM dbo.FactCustomerTraffic;
GO

-- Quick data quality check: any NULL keys?
SELECT 'NULL product_key'   AS Issue, COUNT(*) AS Cnt FROM dbo.FactWeeklySales WHERE product_key IS NULL
UNION ALL SELECT 'NULL store_key',   COUNT(*) FROM dbo.FactWeeklySales WHERE store_key IS NULL
UNION ALL SELECT 'NULL time_key',    COUNT(*) FROM dbo.FactWeeklySales WHERE time_key IS NULL
UNION ALL SELECT 'NULL category_key', COUNT(*) FROM dbo.FactWeeklySales WHERE category_key IS NULL
UNION ALL SELECT 'NULL promotion_key', COUNT(*) FROM dbo.FactWeeklySales WHERE promotion_key IS NULL;
GO
