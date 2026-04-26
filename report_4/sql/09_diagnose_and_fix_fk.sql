-- ============================================================
-- Script 09: Diagnose and Fix Foreign Key Issues
-- DFF Data Warehouse Project — Report 4
-- PURPOSE: Find and fix the "strange FK values" the professor flagged
-- SAFE: No DROP statements. No schema destruction. Only targeted fixes.
-- ============================================================

-- ============================================================
-- PART 1: DISCOVER — What schema is actually on the server?
-- Run this FIRST to see your fact table structure
-- ============================================================
USE [team1_dw_area];
GO

PRINT '=== STEP 1: Current fact table columns ==='
SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME LIKE 'Fact%' OR TABLE_NAME LIKE 'fact%'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
GO

PRINT '=== STEP 2: Current dimension tables ==='
SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME LIKE 'Dim%' OR TABLE_NAME LIKE 'dim%'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
GO

PRINT '=== STEP 3: Sample fact rows (first 10) ==='
-- Uncomment the line that matches YOUR fact table name:
SELECT TOP 10 * FROM dbo.FactWeeklySales;
-- SELECT TOP 10 * FROM dbo.fact_dept_sales;
GO

-- ============================================================
-- PART 2: ORPHAN FK DETECTION
-- These queries find fact rows whose FK values
-- do NOT exist in the corresponding dimension table.
-- Orphan FKs = the "strange values" the professor saw.
-- ============================================================

-- -------------------------------------------------------
-- IF your fact table is FactWeeklySales (Report 4 schema):
-- -------------------------------------------------------
PRINT '=== ORPHAN CHECK: product_key ==='
SELECT 'Orphan product_key' AS Issue, COUNT(*) AS OrphanCount
FROM dbo.FactWeeklySales f
WHERE NOT EXISTS (SELECT 1 FROM dbo.DimProduct d WHERE d.product_key = f.product_key);

PRINT '=== ORPHAN CHECK: store_key ==='
SELECT 'Orphan store_key' AS Issue, COUNT(*) AS OrphanCount
FROM dbo.FactWeeklySales f
WHERE NOT EXISTS (SELECT 1 FROM dbo.DimStore d WHERE d.store_key = f.store_key);

PRINT '=== ORPHAN CHECK: time_key ==='
SELECT 'Orphan time_key' AS Issue, COUNT(*) AS OrphanCount
FROM dbo.FactWeeklySales f
WHERE NOT EXISTS (SELECT 1 FROM dbo.DimTime d WHERE d.time_key = f.time_key);

PRINT '=== ORPHAN CHECK: category_key ==='
SELECT 'Orphan category_key' AS Issue, COUNT(*) AS OrphanCount
FROM dbo.FactWeeklySales f
WHERE NOT EXISTS (SELECT 1 FROM dbo.DimCategory d WHERE d.category_key = f.category_key);

PRINT '=== ORPHAN CHECK: promotion_key ==='
SELECT 'Orphan promotion_key' AS Issue, COUNT(*) AS OrphanCount
FROM dbo.FactWeeklySales f
WHERE NOT EXISTS (SELECT 1 FROM dbo.DimPromotion d WHERE d.promotion_key = f.promotion_key);
GO

-- Show the actual orphan rows (if any) — limit to 20 for inspection
PRINT '=== SAMPLE ORPHAN ROWS (if any) ==='
SELECT TOP 20 f.*
FROM dbo.FactWeeklySales f
WHERE NOT EXISTS (SELECT 1 FROM dbo.DimProduct d WHERE d.product_key = f.product_key)
   OR NOT EXISTS (SELECT 1 FROM dbo.DimStore d WHERE d.store_key = f.store_key)
   OR NOT EXISTS (SELECT 1 FROM dbo.DimTime d WHERE d.time_key = f.time_key)
   OR NOT EXISTS (SELECT 1 FROM dbo.DimCategory d WHERE d.category_key = f.category_key)
   OR NOT EXISTS (SELECT 1 FROM dbo.DimPromotion d WHERE d.promotion_key = f.promotion_key);
GO

-- NULL FK check
PRINT '=== NULL FK CHECK ==='
SELECT 'NULL product_key'   AS Issue, COUNT(*) AS Cnt FROM dbo.FactWeeklySales WHERE product_key IS NULL
UNION ALL SELECT 'NULL store_key',     COUNT(*) FROM dbo.FactWeeklySales WHERE store_key IS NULL
UNION ALL SELECT 'NULL time_key',      COUNT(*) FROM dbo.FactWeeklySales WHERE time_key IS NULL
UNION ALL SELECT 'NULL category_key',  COUNT(*) FROM dbo.FactWeeklySales WHERE category_key IS NULL
UNION ALL SELECT 'NULL promotion_key', COUNT(*) FROM dbo.FactWeeklySales WHERE promotion_key IS NULL;
GO

-- ============================================================
-- PART 3: FIX — Delete orphan rows (SAFE)
-- Only run this AFTER Part 2 confirms orphans exist.
-- This removes fact rows with invalid FK references.
-- ============================================================

/*
-- UNCOMMENT THIS BLOCK ONLY AFTER REVIEWING PART 2 RESULTS

PRINT '=== DELETING ORPHAN FACT ROWS ==='

-- Count before
SELECT COUNT(*) AS BeforeCount FROM dbo.FactWeeklySales;

-- Delete facts with no matching product
DELETE FROM dbo.FactWeeklySales
WHERE NOT EXISTS (SELECT 1 FROM dbo.DimProduct d WHERE d.product_key = FactWeeklySales.product_key);
PRINT 'Deleted orphan product_key rows';

-- Delete facts with no matching store
DELETE FROM dbo.FactWeeklySales
WHERE NOT EXISTS (SELECT 1 FROM dbo.DimStore d WHERE d.store_key = FactWeeklySales.store_key);
PRINT 'Deleted orphan store_key rows';

-- Delete facts with no matching time
DELETE FROM dbo.FactWeeklySales
WHERE NOT EXISTS (SELECT 1 FROM dbo.DimTime d WHERE d.time_key = FactWeeklySales.time_key);
PRINT 'Deleted orphan time_key rows';

-- Delete facts with no matching category
DELETE FROM dbo.FactWeeklySales
WHERE NOT EXISTS (SELECT 1 FROM dbo.DimCategory d WHERE d.category_key = FactWeeklySales.category_key);
PRINT 'Deleted orphan category_key rows';

-- Delete facts with no matching promotion
DELETE FROM dbo.FactWeeklySales
WHERE NOT EXISTS (SELECT 1 FROM dbo.DimPromotion d WHERE d.promotion_key = FactWeeklySales.promotion_key);
PRINT 'Deleted orphan promotion_key rows';

-- Count after
SELECT COUNT(*) AS AfterCount FROM dbo.FactWeeklySales;
PRINT 'Orphan cleanup complete.';

*/

-- ============================================================
-- PART 4: ADD FK CONSTRAINTS (if they don't already exist)
-- This PREVENTS future orphan rows. Safe to run — it will
-- fail gracefully if constraints already exist.
-- ============================================================

/*
-- UNCOMMENT AFTER Part 3 cleanup is done (constraints require 0 orphans)

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Fact_Product')
    ALTER TABLE dbo.FactWeeklySales
    ADD CONSTRAINT FK_Fact_Product FOREIGN KEY (product_key) REFERENCES dbo.DimProduct(product_key);

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Fact_Store')
    ALTER TABLE dbo.FactWeeklySales
    ADD CONSTRAINT FK_Fact_Store FOREIGN KEY (store_key) REFERENCES dbo.DimStore(store_key);

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Fact_Time')
    ALTER TABLE dbo.FactWeeklySales
    ADD CONSTRAINT FK_Fact_Time FOREIGN KEY (time_key) REFERENCES dbo.DimTime(time_key);

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Fact_Category')
    ALTER TABLE dbo.FactWeeklySales
    ADD CONSTRAINT FK_Fact_Category FOREIGN KEY (category_key) REFERENCES dbo.DimCategory(category_key);

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Fact_Promotion')
    ALTER TABLE dbo.FactWeeklySales
    ADD CONSTRAINT FK_Fact_Promotion FOREIGN KEY (promotion_key) REFERENCES dbo.DimPromotion(promotion_key);

PRINT 'FK constraints added successfully.';
*/

-- ============================================================
-- PART 5: FINAL VERIFICATION
-- Run this after all fixes to prove FK integrity
-- SCREENSHOT THIS for the report
-- ============================================================
PRINT '=== FINAL VERIFICATION ==='

-- Row counts
SELECT 'DimCategory'       AS TableName, COUNT(*) AS RowCount FROM dbo.DimCategory
UNION ALL SELECT 'DimPromotion',    COUNT(*) FROM dbo.DimPromotion
UNION ALL SELECT 'DimTime',         COUNT(*) FROM dbo.DimTime
UNION ALL SELECT 'DimStore',        COUNT(*) FROM dbo.DimStore
UNION ALL SELECT 'DimProduct',      COUNT(*) FROM dbo.DimProduct
UNION ALL SELECT 'FactWeeklySales', COUNT(*) FROM dbo.FactWeeklySales
ORDER BY TableName;
GO

-- FK integrity proof (all should be 0)
SELECT 'Orphan product_key'   AS Check_Name, COUNT(*) AS Violations
FROM dbo.FactWeeklySales f WHERE NOT EXISTS (SELECT 1 FROM dbo.DimProduct d WHERE d.product_key = f.product_key)
UNION ALL
SELECT 'Orphan store_key',   COUNT(*)
FROM dbo.FactWeeklySales f WHERE NOT EXISTS (SELECT 1 FROM dbo.DimStore d WHERE d.store_key = f.store_key)
UNION ALL
SELECT 'Orphan time_key',    COUNT(*)
FROM dbo.FactWeeklySales f WHERE NOT EXISTS (SELECT 1 FROM dbo.DimTime d WHERE d.time_key = f.time_key)
UNION ALL
SELECT 'Orphan category_key', COUNT(*)
FROM dbo.FactWeeklySales f WHERE NOT EXISTS (SELECT 1 FROM dbo.DimCategory d WHERE d.category_key = f.category_key)
UNION ALL
SELECT 'Orphan promotion_key', COUNT(*)
FROM dbo.FactWeeklySales f WHERE NOT EXISTS (SELECT 1 FROM dbo.DimPromotion d WHERE d.promotion_key = f.promotion_key);
GO

-- Existing FK constraints
SELECT name AS ConstraintName, OBJECT_NAME(parent_object_id) AS TableName
FROM sys.foreign_keys
WHERE OBJECT_NAME(parent_object_id) LIKE 'Fact%';
GO

PRINT '=== DIAGNOSIS COMPLETE ==='
