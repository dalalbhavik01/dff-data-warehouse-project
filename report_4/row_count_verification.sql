-- ============================================================
-- ROW COUNT VERIFICATION QUERIES
-- Run on SSMS connected to infodata16.mbs.tamu.edu
-- Compare results with numbers in the report
-- ============================================================

-- ============================================================
-- 1. DATA WAREHOUSE TABLES (team1_dw_area)
-- ============================================================
USE [team1_dw_area];
GO

-- FactWeeklySales: Report claims 11,976,442
SELECT 'FactWeeklySales' AS TableName, COUNT(*) AS Cnt FROM dbo.FactWeeklySales;
GO

-- DimProduct: Report claims ~3,112
SELECT 'DimProduct' AS TableName, COUNT(*) AS Cnt FROM dbo.DimProduct;
GO

-- DimStore: Report claims 107
SELECT 'DimStore' AS TableName, COUNT(*) AS Cnt FROM dbo.DimStore;
GO

-- DimTime: Report claims ~400
SELECT 'DimTime' AS TableName, COUNT(*) AS Cnt FROM dbo.DimTime;
GO

-- DimCategory: Report claims 28
SELECT 'DimCategory' AS TableName, COUNT(*) AS Cnt FROM dbo.DimCategory;
GO

-- DimPromotion: Report claims 4
SELECT 'DimPromotion' AS TableName, COUNT(*) AS Cnt FROM dbo.DimPromotion;
GO

-- ============================================================
-- 2. STAGING TABLES (team1_staging_area)
-- ============================================================
USE [team1_staging_area];
GO

-- Movement tables
SELECT 'stg_Movement_SDR' AS TableName, COUNT(*) AS Cnt FROM dbo.stg_Movement_SDR;  -- Report: ~3.7M
GO
SELECT 'stg_Movement_CSO' AS TableName, COUNT(*) AS Cnt FROM dbo.stg_Movement_CSO;  -- Report: ~2.8M
GO
SELECT 'stg_Movement_TPA' AS TableName, COUNT(*) AS Cnt FROM dbo.stg_Movement_TPA;  -- Report: ~1.9M
GO
SELECT 'stg_Movement_CRA' AS TableName, COUNT(*) AS Cnt FROM dbo.stg_Movement_CRA;  -- Report: ~2.4M
GO

-- Product (UPC) tables
SELECT 'stg_Product_SDR' AS TableName, COUNT(*) AS Cnt FROM dbo.stg_Product_SDR;    -- Report: 1,746
GO
SELECT 'stg_Product_CSO' AS TableName, COUNT(*) AS Cnt FROM dbo.stg_Product_CSO;
GO
SELECT 'stg_Product_TPA' AS TableName, COUNT(*) AS Cnt FROM dbo.stg_Product_TPA;
GO
SELECT 'stg_Product_CRA' AS TableName, COUNT(*) AS Cnt FROM dbo.stg_Product_CRA;
GO

-- Store demographics
SELECT 'stg_Store' AS TableName, COUNT(*) AS Cnt FROM dbo.stg_Store;                -- Report: 107
GO

-- ============================================================
-- 3. ALL DW COUNTS IN ONE QUERY
-- ============================================================
USE [team1_dw_area];
SELECT 'DimProduct' AS T, COUNT(*) AS N FROM dbo.DimProduct
UNION ALL SELECT 'DimStore', COUNT(*) FROM dbo.DimStore
UNION ALL SELECT 'DimTime', COUNT(*) FROM dbo.DimTime
UNION ALL SELECT 'DimCategory', COUNT(*) FROM dbo.DimCategory
UNION ALL SELECT 'DimPromotion', COUNT(*) FROM dbo.DimPromotion
UNION ALL SELECT 'FactWeeklySales', COUNT(*) FROM dbo.FactWeeklySales;
GO

-- ============================================================
-- 4. ALL STAGING COUNTS IN ONE QUERY
-- ============================================================
USE [team1_staging_area];
SELECT 'stg_Movement_SDR' AS T, COUNT(*) AS N FROM dbo.stg_Movement_SDR
UNION ALL SELECT 'stg_Movement_CSO', COUNT(*) FROM dbo.stg_Movement_CSO
UNION ALL SELECT 'stg_Movement_TPA', COUNT(*) FROM dbo.stg_Movement_TPA
UNION ALL SELECT 'stg_Movement_CRA', COUNT(*) FROM dbo.stg_Movement_CRA
UNION ALL SELECT 'stg_Product_SDR', COUNT(*) FROM dbo.stg_Product_SDR
UNION ALL SELECT 'stg_Product_CSO', COUNT(*) FROM dbo.stg_Product_CSO
UNION ALL SELECT 'stg_Product_TPA', COUNT(*) FROM dbo.stg_Product_TPA
UNION ALL SELECT 'stg_Product_CRA', COUNT(*) FROM dbo.stg_Product_CRA
UNION ALL SELECT 'stg_Store', COUNT(*) FROM dbo.stg_Store;
GO
