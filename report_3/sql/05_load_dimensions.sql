-- ============================================================
-- Script 05: Load Dimension Tables
-- DFF Data Warehouse Project — Report 3
-- Run AFTER Script 04 (Transform). Loads dimensions BEFORE facts.
-- Order: DimCategory → DimPromotion → DimTime → DimStore → DimProduct
-- ============================================================
USE [team1_dw_area];
GO

-- ===============================
-- 1. DimCategory (28 rows — hardcoded)
-- ===============================
-- These are the 28 product categories from the DFF dataset.
-- Category codes are derived from the 3-letter filename abbreviations.
-- Department groupings are based on standard grocery store organization.

INSERT INTO dbo.DimCategory (category_code, category_name, department) VALUES
('ANA', 'Analgesics',          'Health & Beauty'),
('BAT', 'Bath Soap',           'Health & Beauty'),
('BER', 'Beer',                'Beverages'),
('BJC', 'Bottled Juices',      'Beverages'),
('CER', 'Cereals',             'Grocery'),
('CHE', 'Cheeses',             'Dairy'),
('CIG', 'Cigarettes',          'Tobacco'),
('COO', 'Cookies',             'Snacks'),
('CRA', 'Crackers',            'Snacks'),
('CSO', 'Canned Soup',         'Grocery'),
('DID', 'Dish Detergent',      'Household'),
('FEC', 'Front End Candies',   'Snacks'),
('FRD', 'Frozen Dinners',      'Frozen'),
('FRE', 'Frozen Entrees',      'Frozen'),
('FRJ', 'Frozen Juices',       'Beverages'),
('FSF', 'Fabric Softeners',    'Household'),
('GRO', 'Grooming Products',   'Health & Beauty'),
('LND', 'Laundry Detergents',  'Household'),
('OAT', 'Oatmeal',             'Grocery'),
('PTW', 'Paper Towels',        'Household'),
('SDR', 'Soft Drinks',         'Beverages'),
('SHA', 'Shampoos',            'Health & Beauty'),
('SNA', 'Snack Crackers',      'Snacks'),
('SOA', 'Soaps',               'Health & Beauty'),
('TBR', 'Toothbrushes',        'Health & Beauty'),
('TNA', 'Canned Tuna',         'Grocery'),
('TPA', 'Toothpaste',          'Health & Beauty'),
('TTI', 'Toilet Tissue',       'Household');
GO

PRINT '1/5 DimCategory loaded:';
SELECT COUNT(*) AS RowCount FROM dbo.DimCategory;
SELECT * FROM dbo.DimCategory ORDER BY category_key;
GO

-- ===============================
-- 2. DimPromotion (4 rows — hardcoded)
-- ===============================
-- Maps the SALE column values from Movement files to descriptive labels.
-- NULL/blank/'N' → 'No Promotion', B → 'Bonus Buy', C → 'Coupon', S → 'Sale/Discount'
-- deal_code for 'No Promotion' is stored as NULL (original source value).

INSERT INTO dbo.DimPromotion (deal_code, deal_type, is_promoted) VALUES
(NULL, 'No Promotion', 0),
('B',  'Bonus Buy',    1),
('C',  'Coupon',       1),
('S',  'Sale/Discount', 1);
GO

PRINT '2/5 DimPromotion loaded:';
SELECT * FROM dbo.DimPromotion;
GO

-- ===============================
-- 3. DimTime (~400 rows — generated via CTE)
-- ===============================
-- DFF uses proprietary week IDs (WEEK column in Movement/CCOUNT files).
-- Week 1 corresponds to September 14, 1989 per the DFF codebook.
-- Each subsequent week_id increments by 7 days.
-- We generate week_id 1 through 400 to cover the full dataset period.

;WITH WeekCTE AS (
    SELECT 1 AS week_id
    UNION ALL
    SELECT week_id + 1 FROM WeekCTE WHERE week_id < 400
)
INSERT INTO dbo.DimTime 
    (week_id, week_start_date, week_end_date, [month], month_name, 
     [quarter], [year], fiscal_year, is_holiday_week)
SELECT 
    week_id,
    DATEADD(WEEK, week_id - 1, '1989-09-14')     AS week_start_date,
    DATEADD(DAY, 6, DATEADD(WEEK, week_id - 1, '1989-09-14')) AS week_end_date,
    MONTH(DATEADD(WEEK, week_id - 1, '1989-09-14'))           AS [month],
    DATENAME(MONTH, DATEADD(WEEK, week_id - 1, '1989-09-14')) AS month_name,
    DATEPART(QUARTER, DATEADD(WEEK, week_id - 1, '1989-09-14')) AS [quarter],
    YEAR(DATEADD(WEEK, week_id - 1, '1989-09-14'))            AS [year],
    YEAR(DATEADD(WEEK, week_id - 1, '1989-09-14'))            AS fiscal_year,
    -- Mark common US holiday weeks (Thanksgiving week ~47-48, Christmas ~52, July 4th ~27)
    CASE 
        WHEN DATEPART(WEEK, DATEADD(WEEK, week_id - 1, '1989-09-14')) IN (47, 48, 52, 1, 27)
        THEN 1 ELSE 0 
    END AS is_holiday_week
FROM WeekCTE
OPTION (MAXRECURSION 400);
GO

PRINT '3/5 DimTime loaded:';
SELECT COUNT(*) AS RowCount FROM dbo.DimTime;
SELECT TOP 10 * FROM dbo.DimTime ORDER BY time_key;
GO

-- ===============================
-- 4. DimStore (~107 rows — from staging)
-- ===============================
-- Loaded from cleaned stg_Store in the staging database.
-- Transformations applied during INSERT:
--   - CAST string columns to proper data types
--   - Derive price_tier from binary flags (PRICLOW/PRICMED/PRICHIGH)
--   - Replace NULL NAME/CITY with 'UNKNOWN' (already done in Script 04)

INSERT INTO dbo.DimStore 
    (store_id, store_name, city, zip_code, zone, is_urban, weekly_volume,
     avg_income, education_pct, poverty_pct, avg_household_size,
     ethnic_diversity, population_density, price_tier,
     age_under_9_pct, age_over_60_pct, working_women_pct)
SELECT 
    CAST(s.STORE AS INT)                          AS store_id,
    s.NAME                                        AS store_name,
    s.CITY                                        AS city,
    s.ZIP                                         AS zip_code,
    CAST(s.ZONE AS INT)                           AS zone,
    CAST(s.URBAN AS INT)                          AS is_urban,
    CAST(s.WEEKVOL AS INT)                        AS weekly_volume,
    CAST(s.INCOME AS DECIMAL(10,2))               AS avg_income,
    CAST(s.EDUC AS DECIMAL(5,2))                  AS education_pct,
    CAST(s.POVERTY AS DECIMAL(5,2))               AS poverty_pct,
    CAST(s.HSIZEAVG AS DECIMAL(4,2))              AS avg_household_size,
    CAST(s.ETHNIC AS DECIMAL(5,2))                AS ethnic_diversity,
    CAST(s.DENSITY AS DECIMAL(10,2))              AS population_density,
    CASE 
        WHEN s.PRICLOW = '1'  THEN 'Low'
        WHEN s.PRICMED = '1'  THEN 'Medium'
        WHEN s.PRICHIGH = '1' THEN 'High'
        ELSE 'Unknown'
    END                                           AS price_tier,
    CAST(s.AGE9 AS DECIMAL(5,2))                  AS age_under_9_pct,
    CAST(s.AGE60 AS DECIMAL(5,2))                 AS age_over_60_pct,
    CAST(s.WORKWOM AS DECIMAL(5,2))               AS working_women_pct
FROM [team1_staging_area].dbo.stg_Store s
WHERE ISNUMERIC(s.STORE) = 1;
GO

PRINT '4/5 DimStore loaded:';
SELECT COUNT(*) AS RowCount FROM dbo.DimStore;
SELECT TOP 10 * FROM dbo.DimStore ORDER BY store_key;
GO

-- ===============================
-- 5. DimProduct (~3,112 rows — from staging)
-- ===============================
-- Loaded from tmp_Product_All in staging (UNION of 4 category tables).
-- Joins to DimCategory to get the surrogate category_key.

INSERT INTO dbo.DimProduct 
    (upc, description, size, case_pack, commodity_code, item_number, category_key)
SELECT 
    p.UPC,
    p.DESCRIP                                     AS description,
    p.SIZE                                        AS size,
    p.CASE_PACK                                   AS case_pack,
    p.COM_CODE                                    AS commodity_code,
    p.NITEM                                       AS item_number,
    dc.category_key
FROM [team1_staging_area].dbo.tmp_Product_All p
INNER JOIN dbo.DimCategory dc ON p.CATEGORY_CODE = dc.category_code;
GO

PRINT '5/5 DimProduct loaded:';
SELECT COUNT(*) AS RowCount FROM dbo.DimProduct;
SELECT TOP 10 * FROM dbo.DimProduct ORDER BY product_key;
GO

-- ===============================
-- DIMENSION LOAD VERIFICATION
-- ===============================
PRINT '========================================';
PRINT '  ALL DIMENSION TABLES LOADED';
PRINT '========================================';

SELECT 'DimCategory'  AS TableName, COUNT(*) AS RowCount FROM dbo.DimCategory
UNION ALL SELECT 'DimPromotion', COUNT(*) FROM dbo.DimPromotion
UNION ALL SELECT 'DimTime',      COUNT(*) FROM dbo.DimTime
UNION ALL SELECT 'DimStore',     COUNT(*) FROM dbo.DimStore
UNION ALL SELECT 'DimProduct',   COUNT(*) FROM dbo.DimProduct
ORDER BY TableName;
GO
