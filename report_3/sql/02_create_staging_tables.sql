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
    OK            INT
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
    OK            INT
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
    OK            INT
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
    OK            INT
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
    NITEM         BIGINT
);
GO

-- Canned Soup UPC — 453 rows from UPCCSO.csv
CREATE TABLE dbo.stg_Product_CSO (
    COM_CODE      INT,
    UPC           BIGINT,
    DESCRIP       VARCHAR(100),
    SIZE          VARCHAR(30),
    CASE_PACK     INT,
    NITEM         BIGINT
);
GO

-- Toothpaste UPC — 608 rows from UPCTPA.csv
CREATE TABLE dbo.stg_Product_TPA (
    COM_CODE      INT,
    UPC           BIGINT,
    DESCRIP       VARCHAR(100),
    SIZE          VARCHAR(30),
    CASE_PACK     INT,
    NITEM         BIGINT
);
GO

-- Crackers UPC — 305 rows from UPCCRA.csv
CREATE TABLE dbo.stg_Product_CRA (
    COM_CODE      INT,
    UPC           BIGINT,
    DESCRIP       VARCHAR(100),
    SIZE          VARCHAR(30),
    CASE_PACK     INT,
    NITEM         BIGINT
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
-- Customer Traffic Staging Table
-- Source: Ccount/CCOUNT.csv (327,045 rows)
-- Many columns stored as VARCHAR because source uses '.'
-- as placeholder for missing values
-- -------------------------------------------------------
CREATE TABLE dbo.stg_CustomerTraffic (
    STORE         VARCHAR(10),
    DATE_COL      VARCHAR(50),
    GROCERY       VARCHAR(20),
    DAIRY         VARCHAR(20),
    FROZEN        VARCHAR(20),
    MEAT          VARCHAR(20),
    PRODUCE       VARCHAR(20),
    DELI          VARCHAR(20),
    BAKERY        VARCHAR(20),
    PHARMACY      VARCHAR(20),
    BEER          VARCHAR(20),
    WINE          VARCHAR(20),
    SPIRITS       VARCHAR(20),
    CUSTCOUN      VARCHAR(20),
    MVPCLUB       VARCHAR(20),
    GROCCOUP      VARCHAR(20),
    DAIRYCOUP     VARCHAR(20),
    FROZNCOUP     VARCHAR(20),
    MEATCOUP      VARCHAR(20),
    PRODCOUP      VARCHAR(20),
    DELICOUP      VARCHAR(20),
    BAKCOUP       VARCHAR(20),
    PHARMCOUP     VARCHAR(20),
    BEERCOUP      VARCHAR(20),
    WINECOUP      VARCHAR(20),
    SPIRCOUP      VARCHAR(20),
    WEEK          VARCHAR(10)
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
