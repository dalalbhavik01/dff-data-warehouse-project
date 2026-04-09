-- ============================================================
-- Script 02: Create Staging Tables
-- DFF Data Warehouse Project — Report 3
-- Run in SSMS after Script 01. These tables receive raw CSV data.
-- ============================================================
USE [team1_staging_area];
GO

-- -------------------------------------------------------
-- Movement Staging Tables (one per category)
-- Source: Movement CSV files (comma-delimited, encoding 1252)
-- Columns match the raw CSV structure exactly
-- -------------------------------------------------------

-- Soft Drinks (SDR) — 17.7 million rows from wsdr.csv
CREATE TABLE dbo.stg_Movement_SDR (
    UPC           BIGINT,
    STORE         INT,
    WEEK          INT,
    MOVE          INT,
    QTY           INT,
    PRICE         FLOAT,
    SALE          VARCHAR(5),
    PROFIT        FLOAT,
    OK            INT,
    CATEGORY_CODE CHAR(3)
);
GO

-- Canned Soup (CSO) — 7.0 million rows from WCSO-Done.csv
CREATE TABLE dbo.stg_Movement_CSO (
    UPC           BIGINT,
    STORE         INT,
    WEEK          INT,
    MOVE          INT,
    QTY           INT,
    PRICE         FLOAT,
    SALE          VARCHAR(5),
    PROFIT        FLOAT,
    OK            INT,
    CATEGORY_CODE CHAR(3)
);
GO

-- Toothpaste (TPA) — 6.3 million rows from WTPA_done.csv
CREATE TABLE dbo.stg_Movement_TPA (
    UPC           BIGINT,
    STORE         INT,
    WEEK          INT,
    MOVE          INT,
    QTY           INT,
    PRICE         FLOAT,
    SALE          VARCHAR(5),
    PROFIT        FLOAT,
    OK            INT,
    CATEGORY_CODE CHAR(3)
);
GO

-- Crackers (CRA) — 3.6 million rows from Done-WCRA.csv
CREATE TABLE dbo.stg_Movement_CRA (
    UPC           BIGINT,
    STORE         INT,
    WEEK          INT,
    MOVE          INT,
    QTY           INT,
    PRICE         FLOAT,
    SALE          VARCHAR(5),
    PROFIT        FLOAT,
    OK            INT,
    CATEGORY_CODE CHAR(3)
);
GO

-- -------------------------------------------------------
-- Product (UPC) Staging Tables (one per category)
-- Source: UPC CSV files (encoding 1252 / latin-1)
-- -------------------------------------------------------

-- Soft Drinks UPC — 1,746 rows from UPCSDR.csv
CREATE TABLE dbo.stg_Product_SDR (
    COM_CODE      INT,
    UPC           BIGINT,
    DESCRIP       VARCHAR(100),
    SIZE          VARCHAR(30),
    CASE_PACK     INT,
    NITEM         BIGINT,
    CATEGORY_CODE CHAR(3)
);
GO

-- Canned Soup UPC — 453 rows from UPCCSO.csv
CREATE TABLE dbo.stg_Product_CSO (
    COM_CODE      INT,
    UPC           BIGINT,
    DESCRIP       VARCHAR(100),
    SIZE          VARCHAR(30),
    CASE_PACK     INT,
    NITEM         BIGINT,
    CATEGORY_CODE CHAR(3)
);
GO

-- Toothpaste UPC — 608 rows from UPCTPA.csv
CREATE TABLE dbo.stg_Product_TPA (
    COM_CODE      INT,
    UPC           BIGINT,
    DESCRIP       VARCHAR(100),
    SIZE          VARCHAR(30),
    CASE_PACK     INT,
    NITEM         BIGINT,
    CATEGORY_CODE CHAR(3)
);
GO

-- Crackers UPC — 305 rows from UPCCRA.csv
CREATE TABLE dbo.stg_Product_CRA (
    COM_CODE      INT,
    UPC           BIGINT,
    DESCRIP       VARCHAR(100),
    SIZE          VARCHAR(30),
    CASE_PACK     INT,
    NITEM         BIGINT,
    CATEGORY_CODE CHAR(3)
);
GO

-- -------------------------------------------------------
-- Store Demographics Staging Table
-- Source: Demographics/DEMO.csv (108 rows, 510 columns)
-- We only stage the columns needed for DimStore
-- -------------------------------------------------------
CREATE TABLE dbo.stg_Store (
    STORE         VARCHAR(10),
    NAME          VARCHAR(60),
    CITY          VARCHAR(50),
    ZIP           VARCHAR(10),
    ZONE          VARCHAR(10),
    URBAN         VARCHAR(10),
    WEEKVOL       VARCHAR(20),
    INCOME        VARCHAR(20),
    EDUC          VARCHAR(20),
    POVERTY       VARCHAR(20),
    HSIZEAVG      VARCHAR(20),
    ETHNIC        VARCHAR(20),
    DENSITY       VARCHAR(20),
    AGE9          VARCHAR(20),
    AGE60         VARCHAR(20),
    WORKWOM       VARCHAR(20),
    PRICLOW       VARCHAR(10),
    PRICMED       VARCHAR(10),
    PRICHIGH      VARCHAR(10)
);
GO


-- -------------------------------------------------------
-- Verification: List all staging tables
-- -------------------------------------------------------
SELECT TABLE_NAME, TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'dbo'
ORDER BY TABLE_NAME;
GO

PRINT '=== All staging tables created successfully ===';
GO
