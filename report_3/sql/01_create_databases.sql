-- ============================================================
-- Script 01: Create Databases
-- DFF Data Warehouse Project — Report 3 (ISTM 637, Spring 2026)
-- Run this in SSMS connected to SQL Server 2016
-- ============================================================

-- Step 1: Create the Staging Area database
-- This database holds raw imported CSV data and temporary 
-- transformation tables. It is purged after ETL is complete.
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'team1_staging_area')
BEGIN
    CREATE DATABASE [team1_staging_area];
    PRINT 'Database [team1_staging_area] created successfully.';
END
ELSE
    PRINT 'Database [team1_staging_area] already exists.';
GO

-- Step 2: Create the Data Mart / Presentation Server database
-- This database holds the final star schema (dimension + fact tables)
-- that end users query for business intelligence.
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'team1_dw_area')
BEGIN
    CREATE DATABASE [team1_dw_area];
    PRINT 'Database [team1_dw_area] created successfully.';
END
ELSE
    PRINT 'Database [team1_dw_area] already exists.';
GO

-- Verification: List both databases
SELECT name, create_date 
FROM sys.databases 
WHERE name IN ('team1_staging_area', 'team1_dw_area');
GO
