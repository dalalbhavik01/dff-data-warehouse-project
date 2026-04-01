-- ============================================================
-- Script 04: Transform and Clean Staging Data
-- DFF Data Warehouse Project — Report 3
-- Run in SSMS AFTER Package 1 (Extract) has loaded CSV data
-- into staging tables. These transformations prepare the data
-- for loading into the data mart.
-- ============================================================
USE [team1_staging_area];
GO

-- ===============================
-- MOVEMENT TABLE TRANSFORMATIONS
-- ===============================

-- T1: Add CATEGORY_CODE column to each movement staging table
-- This column does not exist in the CSV files; it is derived 
-- from the filename (e.g., wsdr.csv → 'SDR')

ALTER TABLE dbo.stg_Movement_SDR ADD CATEGORY_CODE CHAR(3);
GO
UPDATE dbo.stg_Movement_SDR SET CATEGORY_CODE = 'SDR';
GO

ALTER TABLE dbo.stg_Movement_CSO ADD CATEGORY_CODE CHAR(3);
GO
UPDATE dbo.stg_Movement_CSO SET CATEGORY_CODE = 'CSO';
GO

ALTER TABLE dbo.stg_Movement_TPA ADD CATEGORY_CODE CHAR(3);
GO
UPDATE dbo.stg_Movement_TPA SET CATEGORY_CODE = 'TPA';
GO

ALTER TABLE dbo.stg_Movement_CRA ADD CATEGORY_CODE CHAR(3);
GO
UPDATE dbo.stg_Movement_CRA SET CATEGORY_CODE = 'CRA';
GO

PRINT 'T1 Complete: CATEGORY_CODE added to all movement tables.';
GO

-- T2: Replace NULL/blank SALE with 'N' (No Promotion)
-- The SALE column is NULL for ~90% of rows; we normalize to 'N'
-- so that promotion lookup joins work correctly.

UPDATE dbo.stg_Movement_SDR SET SALE = 'N' WHERE SALE IS NULL OR LTRIM(RTRIM(SALE)) = '';
UPDATE dbo.stg_Movement_CSO SET SALE = 'N' WHERE SALE IS NULL OR LTRIM(RTRIM(SALE)) = '';
UPDATE dbo.stg_Movement_TPA SET SALE = 'N' WHERE SALE IS NULL OR LTRIM(RTRIM(SALE)) = '';
UPDATE dbo.stg_Movement_CRA SET SALE = 'N' WHERE SALE IS NULL OR LTRIM(RTRIM(SALE)) = '';
GO

PRINT 'T2 Complete: NULL SALE values replaced with N.';
GO

-- Verification: Check SALE distribution after cleaning
SELECT 'SDR' AS Category, SALE, COUNT(*) AS cnt FROM dbo.stg_Movement_SDR GROUP BY SALE
UNION ALL
SELECT 'CSO', SALE, COUNT(*) FROM dbo.stg_Movement_CSO GROUP BY SALE
UNION ALL
SELECT 'TPA', SALE, COUNT(*) FROM dbo.stg_Movement_TPA GROUP BY SALE
UNION ALL
SELECT 'CRA', SALE, COUNT(*) FROM dbo.stg_Movement_CRA GROUP BY SALE
ORDER BY 1, 2;
GO

-- ===============================
-- PRODUCT (UPC) TABLE TRANSFORMATIONS
-- ===============================

-- T3: Add CATEGORY_CODE column to each UPC staging table

ALTER TABLE dbo.stg_Product_SDR ADD CATEGORY_CODE CHAR(3);
GO
UPDATE dbo.stg_Product_SDR SET CATEGORY_CODE = 'SDR';
GO

ALTER TABLE dbo.stg_Product_CSO ADD CATEGORY_CODE CHAR(3);
GO
UPDATE dbo.stg_Product_CSO SET CATEGORY_CODE = 'CSO';
GO

ALTER TABLE dbo.stg_Product_TPA ADD CATEGORY_CODE CHAR(3);
GO
UPDATE dbo.stg_Product_TPA SET CATEGORY_CODE = 'TPA';
GO

ALTER TABLE dbo.stg_Product_CRA ADD CATEGORY_CODE CHAR(3);
GO
UPDATE dbo.stg_Product_CRA SET CATEGORY_CODE = 'CRA';
GO

PRINT 'T3 Complete: CATEGORY_CODE added to all product tables.';
GO

-- T4: Clean product descriptions — strip leading # and ~ characters
UPDATE dbo.stg_Product_SDR SET DESCRIP = LTRIM(REPLACE(REPLACE(DESCRIP, '#', ''), '~', ''));
UPDATE dbo.stg_Product_CSO SET DESCRIP = LTRIM(REPLACE(REPLACE(DESCRIP, '#', ''), '~', ''));
UPDATE dbo.stg_Product_TPA SET DESCRIP = LTRIM(REPLACE(REPLACE(DESCRIP, '#', ''), '~', ''));
UPDATE dbo.stg_Product_CRA SET DESCRIP = LTRIM(REPLACE(REPLACE(DESCRIP, '#', ''), '~', ''));
GO

PRINT 'T4 Complete: Product descriptions cleaned.';
GO

-- T5: Create unified tmp_Product_All table (UNION of 4 category tables)
-- This temporary table is used to load DimProduct
IF OBJECT_ID('dbo.tmp_Product_All', 'U') IS NOT NULL
    DROP TABLE dbo.tmp_Product_All;
GO

SELECT COM_CODE, UPC, DESCRIP, SIZE, CASE_PACK, NITEM, CATEGORY_CODE
INTO dbo.tmp_Product_All
FROM (
    SELECT COM_CODE, UPC, DESCRIP, SIZE, CASE_PACK, NITEM, CATEGORY_CODE FROM dbo.stg_Product_SDR
    UNION ALL
    SELECT COM_CODE, UPC, DESCRIP, SIZE, CASE_PACK, NITEM, CATEGORY_CODE FROM dbo.stg_Product_CSO
    UNION ALL
    SELECT COM_CODE, UPC, DESCRIP, SIZE, CASE_PACK, NITEM, CATEGORY_CODE FROM dbo.stg_Product_TPA
    UNION ALL
    SELECT COM_CODE, UPC, DESCRIP, SIZE, CASE_PACK, NITEM, CATEGORY_CODE FROM dbo.stg_Product_CRA
) AS all_products;
GO

PRINT 'T5 Complete: tmp_Product_All created.';
SELECT 'tmp_Product_All' AS TableName, COUNT(*) AS RowCount FROM dbo.tmp_Product_All;
GO

-- ===============================
-- STORE (DEMOGRAPHICS) TRANSFORMATIONS
-- ===============================

-- T6: Remove the '.' placeholder row (first row of DEMO.csv)
-- The first row in DEMO.csv has STORE = '.' for all fields
DELETE FROM dbo.stg_Store WHERE STORE = '.' OR ISNUMERIC(STORE) = 0;
GO

-- T7: Replace NULL/blank NAME and CITY with 'UNKNOWN'
UPDATE dbo.stg_Store SET NAME = 'UNKNOWN' WHERE NAME IS NULL OR LTRIM(RTRIM(NAME)) = '';
UPDATE dbo.stg_Store SET CITY = 'UNKNOWN' WHERE CITY IS NULL OR LTRIM(RTRIM(CITY)) = '';
GO

PRINT 'T6-T7 Complete: Store data cleaned.';
SELECT COUNT(*) AS StoreCount FROM dbo.stg_Store;
GO

-- ===============================
-- CUSTOMER TRAFFIC TRANSFORMATIONS
-- ===============================

-- T8: Replace '.' placeholders with NULL across all department columns
-- The CCOUNT.csv file uses '.' instead of NULL for missing values

UPDATE dbo.stg_CustomerTraffic SET GROCERY   = NULL WHERE GROCERY = '.';
UPDATE dbo.stg_CustomerTraffic SET DAIRY     = NULL WHERE DAIRY = '.';
UPDATE dbo.stg_CustomerTraffic SET FROZEN    = NULL WHERE FROZEN = '.';
UPDATE dbo.stg_CustomerTraffic SET MEAT      = NULL WHERE MEAT = '.';
UPDATE dbo.stg_CustomerTraffic SET PRODUCE   = NULL WHERE PRODUCE = '.';
UPDATE dbo.stg_CustomerTraffic SET DELI      = NULL WHERE DELI = '.';
UPDATE dbo.stg_CustomerTraffic SET BAKERY    = NULL WHERE BAKERY = '.';
UPDATE dbo.stg_CustomerTraffic SET PHARMACY  = NULL WHERE PHARMACY = '.';
UPDATE dbo.stg_CustomerTraffic SET BEER      = NULL WHERE BEER = '.';
UPDATE dbo.stg_CustomerTraffic SET WINE      = NULL WHERE WINE = '.';
UPDATE dbo.stg_CustomerTraffic SET SPIRITS   = NULL WHERE SPIRITS = '.';
UPDATE dbo.stg_CustomerTraffic SET CUSTCOUN  = NULL WHERE CUSTCOUN = '.';
UPDATE dbo.stg_CustomerTraffic SET MVPCLUB   = NULL WHERE MVPCLUB = '.';
UPDATE dbo.stg_CustomerTraffic SET GROCCOUP  = NULL WHERE GROCCOUP = '.';
UPDATE dbo.stg_CustomerTraffic SET DAIRYCOUP = NULL WHERE DAIRYCOUP = '.';
UPDATE dbo.stg_CustomerTraffic SET FROZNCOUP = NULL WHERE FROZNCOUP = '.';
UPDATE dbo.stg_CustomerTraffic SET MEATCOUP  = NULL WHERE MEATCOUP = '.';
UPDATE dbo.stg_CustomerTraffic SET PRODCOUP  = NULL WHERE PRODCOUP = '.';
UPDATE dbo.stg_CustomerTraffic SET DELICOUP  = NULL WHERE DELICOUP = '.';
UPDATE dbo.stg_CustomerTraffic SET BAKCOUP   = NULL WHERE BAKCOUP = '.';
UPDATE dbo.stg_CustomerTraffic SET PHARMCOUP = NULL WHERE PHARMCOUP = '.';
UPDATE dbo.stg_CustomerTraffic SET BEERCOUP  = NULL WHERE BEERCOUP = '.';
UPDATE dbo.stg_CustomerTraffic SET WINECOUP  = NULL WHERE WINECOUP = '.';
UPDATE dbo.stg_CustomerTraffic SET SPIRCOUP  = NULL WHERE SPIRCOUP = '.';
GO

-- T9: Filter out STORE = 0 rows (header/summary rows)
DELETE FROM dbo.stg_CustomerTraffic 
WHERE STORE = '0' OR ISNUMERIC(STORE) = 0;
GO

-- T10: Filter out negative WEEK values (pre-tracking period)
DELETE FROM dbo.stg_CustomerTraffic 
WHERE ISNUMERIC(WEEK) = 1 AND CAST(WEEK AS INT) < 1;
GO

PRINT 'T8-T10 Complete: Customer traffic data cleaned.';
SELECT COUNT(*) AS TrafficRowCount FROM dbo.stg_CustomerTraffic;
GO

-- ===============================
-- FINAL VERIFICATION
-- ===============================
PRINT '========================================';
PRINT '  STAGING TRANSFORMATION COMPLETE';
PRINT '========================================';

SELECT 'stg_Movement_SDR' AS TableName, COUNT(*) AS RowCount FROM dbo.stg_Movement_SDR
UNION ALL SELECT 'stg_Movement_CSO', COUNT(*) FROM dbo.stg_Movement_CSO
UNION ALL SELECT 'stg_Movement_TPA', COUNT(*) FROM dbo.stg_Movement_TPA
UNION ALL SELECT 'stg_Movement_CRA', COUNT(*) FROM dbo.stg_Movement_CRA
UNION ALL SELECT 'stg_Product_SDR',  COUNT(*) FROM dbo.stg_Product_SDR
UNION ALL SELECT 'stg_Product_CSO',  COUNT(*) FROM dbo.stg_Product_CSO
UNION ALL SELECT 'stg_Product_TPA',  COUNT(*) FROM dbo.stg_Product_TPA
UNION ALL SELECT 'stg_Product_CRA',  COUNT(*) FROM dbo.stg_Product_CRA
UNION ALL SELECT 'stg_Store',        COUNT(*) FROM dbo.stg_Store
UNION ALL SELECT 'stg_CustomerTraffic', COUNT(*) FROM dbo.stg_CustomerTraffic
UNION ALL SELECT 'tmp_Product_All',  COUNT(*) FROM dbo.tmp_Product_All
ORDER BY TableName;
GO
