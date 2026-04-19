-- ============================================================
-- Script 08: Verify Business Questions Against Loaded DW
-- DFF Data Warehouse Project — Report 3
-- Run AFTER all tables are loaded to validate the ETL.
-- Each query corresponds to one of the 5 selected BQs.
-- ============================================================
USE [team1_dw_area];
GO

-- ===============================
-- BQ2: Total weekly unit sales of Soft Drinks across all stores
-- Difficulty: Easy | OLAP Operation: Roll-up
-- ===============================
PRINT '=== BQ2: Weekly Soft Drink Unit Sales ===';

SELECT 
    dt.[year],
    dt.[month],
    dt.week_id,
    dt.week_start_date,
    SUM(f.units_sold)          AS total_units_sold,
    SUM(f.revenue)             AS total_revenue,
    COUNT(DISTINCT f.store_key) AS num_stores
FROM dbo.FactWeeklySales f
INNER JOIN dbo.DimTime dt      ON f.time_key     = dt.time_key
INNER JOIN dbo.DimCategory dc  ON f.category_key  = dc.category_key
WHERE dc.category_code = 'SDR'
GROUP BY dt.[year], dt.[month], dt.week_id, dt.week_start_date
ORDER BY dt.week_id;
GO

-- ===============================
-- BQ3: Promotion vs Non-Promotion weeks — sales comparison
-- Difficulty: Easy | OLAP Operation: Dice (Slice by promotion status)
-- ===============================
PRINT '=== BQ3: Promoted vs Non-Promoted Sales Volume ===';

SELECT 
    dp.deal_type                AS promotion_status,
    dp.is_promoted,
    COUNT(*)                    AS num_records,
    SUM(f.units_sold)           AS total_units_sold,
    AVG(CAST(f.units_sold AS FLOAT)) AS avg_units_per_record,
    SUM(f.revenue)              AS total_revenue
FROM dbo.FactWeeklySales f
INNER JOIN dbo.DimPromotion dp ON f.promotion_key = dp.promotion_key
INNER JOIN dbo.DimCategory dc  ON f.category_key  = dc.category_key
WHERE dc.category_code = 'SDR'
GROUP BY dp.deal_type, dp.is_promoted
ORDER BY avg_units_per_record DESC;
GO

-- ===============================
-- BQ4: Which promotion type has highest incremental sales lift in Canned Soup?
-- Difficulty: Medium | OLAP Operation: Dice (filter by category + promo type)
-- ===============================
PRINT '=== BQ4: Promotion Lift by Deal Type — Canned Soup ===';

-- First get the baseline (no promotion average)
DECLARE @baseline_avg FLOAT;
SELECT @baseline_avg = AVG(CAST(f.units_sold AS FLOAT))
FROM dbo.FactWeeklySales f
INNER JOIN dbo.DimPromotion dp ON f.promotion_key = dp.promotion_key
INNER JOIN dbo.DimCategory dc  ON f.category_key  = dc.category_key
WHERE dc.category_code = 'CSO' AND dp.is_promoted = 0;

SELECT 
    dp.deal_type,
    COUNT(*)                                AS num_promoted_records,
    AVG(CAST(f.units_sold AS FLOAT))        AS avg_units_promoted,
    @baseline_avg                            AS avg_units_baseline,
    AVG(CAST(f.units_sold AS FLOAT)) - @baseline_avg AS incremental_lift,
    CASE WHEN @baseline_avg > 0 
         THEN CAST(AVG(CAST(f.units_sold AS FLOAT)) / @baseline_avg AS DECIMAL(5,2))
         ELSE NULL 
    END                                      AS lift_multiplier
FROM dbo.FactWeeklySales f
INNER JOIN dbo.DimPromotion dp ON f.promotion_key = dp.promotion_key
INNER JOIN dbo.DimCategory dc  ON f.category_key  = dc.category_key
WHERE dc.category_code = 'CSO' AND dp.is_promoted = 1
GROUP BY dp.deal_type
ORDER BY incremental_lift DESC;
GO

-- ===============================
-- BQ8: Store quartile tiers by Toothpaste revenue + demographics
-- Difficulty: Hard | OLAP Operation: NTILE + Drill-down
-- ===============================
PRINT '=== BQ8: Store Revenue Quartiles — Toothpaste ===';

WITH store_revenue AS (
    SELECT 
        f.store_key,
        SUM(f.revenue) AS total_revenue
    FROM dbo.FactWeeklySales f
    INNER JOIN dbo.DimCategory dc ON f.category_key = dc.category_key
    WHERE dc.category_code = 'TPA'
    GROUP BY f.store_key
),
store_quartiles AS (
    SELECT 
        sr.store_key,
        sr.total_revenue,
        NTILE(4) OVER (ORDER BY sr.total_revenue) AS revenue_quartile
    FROM store_revenue sr
)
SELECT 
    CASE 
        WHEN sq.revenue_quartile = 1 THEN 'Bottom 25%'
        WHEN sq.revenue_quartile IN (2, 3) THEN 'Middle 50%'
        WHEN sq.revenue_quartile = 4 THEN 'Top 25%'
    END                                          AS tier,
    COUNT(*)                                     AS store_count,
    CAST(AVG(sq.total_revenue) AS DECIMAL(12,2)) AS avg_revenue,
    CAST(AVG(ds.avg_income) AS DECIMAL(10,2))    AS avg_income,
    CAST(AVG(ds.population_density) AS DECIMAL(10,2)) AS avg_pop_density,
    SUM(ds.is_urban)                             AS urban_store_count,
    CAST(AVG(ds.education_pct) AS DECIMAL(5,2))  AS avg_education_pct,
    CAST(AVG(ds.poverty_pct) AS DECIMAL(5,2))    AS avg_poverty_pct
FROM store_quartiles sq
INNER JOIN dbo.DimStore ds ON sq.store_key = ds.store_key
GROUP BY 
    CASE 
        WHEN sq.revenue_quartile = 1 THEN 'Bottom 25%'
        WHEN sq.revenue_quartile IN (2, 3) THEN 'Middle 50%'
        WHEN sq.revenue_quartile = 4 THEN 'Top 25%'
    END
ORDER BY avg_revenue DESC;
GO

-- ===============================
-- BQ9: Weekly top 10 Cracker products by unit sales with WoW change
-- Difficulty: Hard | OLAP Operation: RANK + LAG
-- ===============================
PRINT '=== BQ9: Weekly Top 10 Cracker Products with WoW Change ===';

WITH weekly_product AS (
    SELECT 
        dp.upc,
        dp.description,
        dt.week_id,
        dt.week_start_date,
        SUM(f.units_sold)                                        AS weekly_units,
        RANK() OVER (PARTITION BY dt.week_id 
                     ORDER BY SUM(f.units_sold) DESC)            AS week_rank
    FROM dbo.FactWeeklySales f
    INNER JOIN dbo.DimProduct dp  ON f.product_key = dp.product_key
    INNER JOIN dbo.DimTime dt     ON f.time_key    = dt.time_key
    INNER JOIN dbo.DimCategory dc ON f.category_key = dc.category_key
    WHERE dc.category_code = 'CRA'
    GROUP BY dp.upc, dp.description, dt.week_id, dt.week_start_date
)
SELECT 
    week_id,
    week_start_date,
    upc,
    description,
    weekly_units,
    week_rank,
    LAG(weekly_units) OVER (PARTITION BY upc ORDER BY week_id) AS prev_week_units,
    weekly_units - LAG(weekly_units) OVER (PARTITION BY upc ORDER BY week_id) AS wow_change
FROM weekly_product
WHERE week_rank <= 10
ORDER BY week_id, week_rank;
GO

-- ===============================
-- OVERALL VALIDATION SUMMARY
-- ===============================
PRINT '========================================';
PRINT '  BUSINESS QUESTION VERIFICATION COMPLETE';
PRINT '========================================';

-- Final row count summary
SELECT 'DimCategory'          AS TableName, COUNT(*) AS RowCount FROM dbo.DimCategory
UNION ALL SELECT 'DimPromotion',       COUNT(*) FROM dbo.DimPromotion
UNION ALL SELECT 'DimTime',            COUNT(*) FROM dbo.DimTime
UNION ALL SELECT 'DimStore',           COUNT(*) FROM dbo.DimStore
UNION ALL SELECT 'DimProduct',         COUNT(*) FROM dbo.DimProduct
UNION ALL SELECT 'FactWeeklySales',    COUNT(*) FROM dbo.FactWeeklySales
ORDER BY TableName;
GO
