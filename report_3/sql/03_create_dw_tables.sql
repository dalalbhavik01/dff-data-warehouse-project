-- ============================================================
-- Script 03: Create Data Warehouse (Data Mart) Tables
-- DFF Data Warehouse Project — Report 3
-- Run in SSMS after Script 02. Creates the star schema tables.
-- IMPORTANT: Create DIMENSION tables first, then FACT tables
--            (fact tables have FK references to dimensions).
-- ============================================================
USE [team1_dw_area];
GO

-- ===============================
-- DIMENSION TABLES
-- ===============================

-- -------------------------------------------------------
-- DimCategory — 28 product categories
-- Grain: One row per product category
-- Cardinality: 28 rows (static, hardcoded)
-- -------------------------------------------------------
CREATE TABLE dbo.DimCategory (
    category_key    INT IDENTITY(1,1) NOT NULL,
    category_code   CHAR(3)           NOT NULL,
    category_name   VARCHAR(30)       NOT NULL,
    department      VARCHAR(20)       NOT NULL,
    CONSTRAINT PK_DimCategory PRIMARY KEY CLUSTERED (category_key),
    CONSTRAINT UQ_DimCategory_code UNIQUE (category_code)
);
GO

-- -------------------------------------------------------
-- DimPromotion — 4 promotion types
-- Grain: One row per deal type
-- Cardinality: 4 rows (static, hardcoded)
-- -------------------------------------------------------
CREATE TABLE dbo.DimPromotion (
    promotion_key   INT IDENTITY(1,1) NOT NULL,
    deal_code       CHAR(1)           NOT NULL,
    deal_type       VARCHAR(20)       NOT NULL,
    is_promoted     BIT               NOT NULL,
    CONSTRAINT PK_DimPromotion PRIMARY KEY CLUSTERED (promotion_key)
);
GO

-- -------------------------------------------------------
-- DimTime — ~400 weeks (DFF proprietary week IDs)
-- Grain: One row per unique week
-- Week 1 = September 14, 1989 (per DFF codebook)
-- Cardinality: ~400 rows (generated via CTE)
-- -------------------------------------------------------
CREATE TABLE dbo.DimTime (
    time_key          INT IDENTITY(1,1) NOT NULL,
    week_id           INT               NOT NULL,
    week_start_date   DATE              NOT NULL,
    week_end_date     DATE              NOT NULL,
    [month]           INT               NOT NULL,
    month_name        VARCHAR(15)       NOT NULL,
    [quarter]         INT               NOT NULL,
    [year]            INT               NOT NULL,
    fiscal_year       INT               NOT NULL,
    is_holiday_week   BIT               NOT NULL DEFAULT 0,
    CONSTRAINT PK_DimTime PRIMARY KEY CLUSTERED (time_key),
    CONSTRAINT UQ_DimTime_weekid UNIQUE (week_id)
);
GO

-- -------------------------------------------------------
-- DimStore — ~107 stores
-- Grain: One row per physical store location
-- Source: Cleaned from DEMO.csv staging table
-- Cardinality: ~107 rows
-- -------------------------------------------------------
CREATE TABLE dbo.DimStore (
    store_key            INT IDENTITY(1,1) NOT NULL,
    store_id             INT               NOT NULL,
    store_name           VARCHAR(50)       NULL,
    city                 VARCHAR(40)       NULL,
    zip_code             VARCHAR(10)       NULL,
    zone                 INT               NULL,
    is_urban             INT               NULL,
    weekly_volume        INT               NULL,
    avg_income           DECIMAL(10,2)     NULL,
    education_pct        DECIMAL(5,2)      NULL,
    poverty_pct          DECIMAL(5,2)      NULL,
    avg_household_size   DECIMAL(4,2)      NULL,
    ethnic_diversity     DECIMAL(5,2)      NULL,
    population_density   DECIMAL(10,2)     NULL,
    price_tier           VARCHAR(10)       NULL,
    age_under_9_pct      DECIMAL(5,2)      NULL,
    age_over_60_pct      DECIMAL(5,2)      NULL,
    working_women_pct    DECIMAL(5,2)      NULL,
    CONSTRAINT PK_DimStore PRIMARY KEY CLUSTERED (store_key),
    CONSTRAINT UQ_DimStore_storeid UNIQUE (store_id)
);
GO

-- -------------------------------------------------------
-- DimProduct — ~3,112 UPCs (for 4 selected categories)
-- Grain: One row per unique UPC
-- Source: Cleaned from UPC staging tables
-- Cardinality: SDR(1746) + CSO(453) + TPA(608) + CRA(305) = 3,112
-- -------------------------------------------------------
CREATE TABLE dbo.DimProduct (
    product_key     INT IDENTITY(1,1) NOT NULL,
    upc             BIGINT            NOT NULL,
    description     VARCHAR(100)      NULL,
    size            VARCHAR(30)       NULL,
    case_pack       INT               NULL,
    commodity_code  INT               NULL,
    item_number     BIGINT            NULL,
    category_key    INT               NULL,
    CONSTRAINT PK_DimProduct PRIMARY KEY CLUSTERED (product_key),
    CONSTRAINT FK_DimProduct_Category FOREIGN KEY (category_key)
        REFERENCES dbo.DimCategory(category_key)
);
GO

-- ===============================
-- FACT TABLES
-- ===============================

-- -------------------------------------------------------
-- FactWeeklySales — Central fact table
-- Grain: One row per UPC × Store × Week
-- Source: Movement staging tables (filtered OK=1, PRICE>0)
-- Estimated: ~34.6M rows for 4 categories
-- -------------------------------------------------------
CREATE TABLE dbo.FactWeeklySales (
    sales_fact_id     INT IDENTITY(1,1)  NOT NULL,
    product_key       INT                NOT NULL,
    store_key         INT                NOT NULL,
    time_key          INT                NOT NULL,
    category_key      INT                NOT NULL,
    promotion_key     INT                NOT NULL,
    units_sold        INT                NULL,
    unit_price        DECIMAL(8,2)       NULL,
    shelf_price       DECIMAL(8,2)       NULL,
    price_qty         INT                NULL,
    revenue           DECIMAL(12,2)      NULL,
    gross_profit      DECIMAL(10,2)      NULL,
    profit_margin_pct DECIMAL(5,2)       NULL,
    CONSTRAINT PK_FactWeeklySales PRIMARY KEY CLUSTERED (sales_fact_id),
    CONSTRAINT FK_Fact_Product   FOREIGN KEY (product_key)   REFERENCES dbo.DimProduct(product_key),
    CONSTRAINT FK_Fact_Store     FOREIGN KEY (store_key)     REFERENCES dbo.DimStore(store_key),
    CONSTRAINT FK_Fact_Time      FOREIGN KEY (time_key)      REFERENCES dbo.DimTime(time_key),
    CONSTRAINT FK_Fact_Category  FOREIGN KEY (category_key)  REFERENCES dbo.DimCategory(category_key),
    CONSTRAINT FK_Fact_Promotion FOREIGN KEY (promotion_key) REFERENCES dbo.DimPromotion(promotion_key)
);
GO


-- -------------------------------------------------------
-- Verification: List all DW tables
-- -------------------------------------------------------
SELECT TABLE_NAME, TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'dbo'
ORDER BY TABLE_NAME;
GO

PRINT '=== All data warehouse tables created successfully ===';
GO
