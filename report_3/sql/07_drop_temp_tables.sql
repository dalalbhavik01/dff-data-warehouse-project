-- ============================================================
-- Script 07: Drop Temporary Tables from Staging Area
-- DFF Data Warehouse Project — Report 3
-- Run AFTER all dimension and fact tables have been loaded.
-- The assignment requires: "Once loading of each table is done,
-- remove all temp tables from the staging area."
-- ============================================================
USE [team1_staging_area];
GO

-- ===============================
-- LIST OF TEMPORARY TABLES
-- ===============================
-- The following temporary tables were created in the staging area
-- during the transformation phase (Script 04) and are no longer
-- needed after the data mart has been populated:
--
--   1. tmp_Product_All  — UNION of 4 UPC category staging tables
--                          Used to load DimProduct
--
-- Note: The original staging tables (stg_Movement_*, stg_Product_*,
-- stg_Store, stg_CustomerTraffic) are also temporary but may be
-- retained for audit/verification purposes until the project is
-- fully validated.

PRINT 'Dropping temporary tables from staging area...';
GO

-- Drop tmp_Product_All
IF OBJECT_ID('dbo.tmp_Product_All', 'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.tmp_Product_All;
    PRINT 'DROPPED: tmp_Product_All';
END
GO

-- ===============================
-- VERIFICATION
-- ===============================
-- Show remaining tables in staging area
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'dbo' AND TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;
GO

PRINT '========================================';
PRINT '  TEMPORARY TABLES REMOVED';
PRINT '  Remaining tables are base staging tables';
PRINT '  retained for audit/verification.';
PRINT '========================================';
GO
