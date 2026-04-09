# SSIS/SSMS Implementation Guide

## DFF Data Warehouse - Team 1

This guide walks you through every step to implement the ETL pipeline in SSMS and SSIS. Follow it in order.

---

## Prerequisites

- Connected to `infodata16.mbs.tamu.edu` via VPN + `runas /netonly`
- SQL Server Data Tools (SSDT) or Visual Studio with SSIS extension installed
- All 9 CSV source files accessible from the server
- All 8 SQL scripts from `report_3/sql/` folder copied to the server

---

## PHASE 1: SSMS - Run SQL Scripts (Steps 1-3)

### Step 1: Create Databases

1. Open SSMS, connect to `infodata16.mbs.tamu.edu`
2. Open `01_create_databases.sql`
3. Click **Execute** (F5)
4. Verify: Expand **Databases** node in Object Explorer - you should see:
   - `team1_staging_area`
   - `team1_dw_area`
5. **SCREENSHOT 1:** Object Explorer showing both databases

### Step 2: Create Staging Tables

1. Open `02_create_staging_tables.sql`
2. Click **Execute** (F5)
3. Verify: Expand `team1_staging_area` > `Tables` - you should see 9 tables:
   - `dbo.stg_Movement_SDR`
   - `dbo.stg_Movement_CSO`
   - `dbo.stg_Movement_TPA`
   - `dbo.stg_Movement_CRA`
   - `dbo.stg_Product_SDR`
   - `dbo.stg_Product_CSO`
   - `dbo.stg_Product_TPA`
   - `dbo.stg_Product_CRA`
   - `dbo.stg_Store`
4. **SCREENSHOT 2:** Object Explorer showing all staging tables

### Step 3: Create Data Mart Tables

1. Open `03_create_dw_tables.sql`
2. Click **Execute** (F5)
3. Verify: Expand `team1_dw_area` > `Tables` - you should see 6 tables:
   - `dbo.DimCategory`
   - `dbo.DimPromotion`
   - `dbo.DimTime`
   - `dbo.DimStore`
   - `dbo.DimProduct`
   - `dbo.FactWeeklySales`
4. **SCREENSHOT 3:** Object Explorer showing all DW tables

---

## PHASE 2: SSIS - Build 3 Packages

### Create the SSIS Project

1. Open Visual Studio / SSDT
2. **File > New > Project**
3. Select **Integration Services Project**
4. Name: `DFF_ETL`
5. Location: Choose your working folder
6. Click **OK**
7. You'll have one default package (`Package.dtsx`) - rename it or delete it

---

### PACKAGE 1: `01_Extract_to_Staging.dtsx`

**Purpose:** Load all 9 CSV files into staging tables.

#### Create the Package

1. Right-click **SSIS Packages** in Solution Explorer > **Add New SSIS Package**
2. Name it: `01_Extract_to_Staging.dtsx`

#### Create OLE DB Connection Manager (do this once)

1. Right-click in **Connection Managers** area (bottom of design surface)
2. **New OLE DB Connection...**
3. Server: `infodata16.mbs.tamu.edu`
4. Authentication: Use your credentials
5. Database: `team1_staging_area`
6. Click **Test Connection** > OK
7. Rename it to: `StagingDB`

#### Create Data Flow Task #1: Load wsdr.csv -> stg_Movement_SDR

1. **Drag a Data Flow Task** onto the Control Flow surface
2. Rename it: `DFT_Movement_SDR`
3. **Double-click** to enter the Data Flow tab

**Configure Flat File Source:**
4. Drag **Flat File Source** onto the Data Flow surface
5. Double-click it > **New...** to create a Flat File Connection Manager
6. Set these properties:

- **Connection manager name:** `FF_wsdr`
- **File name:** Browse to `wsdr.csv`
- **Format:** Delimited
- **Text qualifier:** `<none>`
- **Header row delimiter:** `{CR}{LF}`
- **Header rows to skip:** 0
- **Column names in the first data row:** CHECKED
- **Locale:** English (United States)
- **Code page:** 1252 (ANSI - Latin I)

7. Click **Columns** tab on the left:

   - Row delimiter: `{CR}{LF}`
   - Column delimiter: `Comma {,}`
   - Preview the data to verify columns look correct
8. Click **Advanced** tab:

   - Set column data types to match staging table:

   | Column | DataType                          | Length |
   | :----- | :-------------------------------- | :----- |
   | UPC    | eight-byte signed integer [DT_I8] | -      |
   | STORE  | four-byte signed integer [DT_I4]  | -      |
   | WEEK   | four-byte signed integer [DT_I4]  | -      |
   | MOVE   | four-byte signed integer [DT_I4]  | -      |
   | QTY    | four-byte signed integer [DT_I4]  | -      |
   | PRICE  | double-precision float [DT_R8]    | -      |
   | SALE   | string [DT_STR]                   | 5      |
   | PROFIT | double-precision float [DT_R8]    | -      |
   | OK     | four-byte signed integer [DT_I4]  | -      |
9. Click **OK** twice

**Configure OLE DB Destination:**
10. Drag **OLE DB Destination** onto the Data Flow surface
11. Connect the green arrow from Flat File Source to OLE DB Destination
12. Double-click OLE DB Destination:
    - Connection manager: `StagingDB`
    - Table: `[dbo].[stg_Movement_SDR]`
    - Click **Mappings** tab - verify all columns auto-map correctly
13. Click **OK**

#### Repeat for remaining 3 Movement files

Create 3 more Data Flow Tasks with these settings:

| DFT Name         | CSV File      | Flat File CM Name | Destination Table |
| :--------------- | :------------ | :---------------- | :---------------- |
| DFT_Movement_CSO | WCSO-Done.csv | FF_WCSO           | stg_Movement_CSO  |
| DFT_Movement_TPA | WTPA_done.csv | FF_WTPA           | stg_Movement_TPA  |
| DFT_Movement_CRA | Done-WCRA.csv | FF_WCRA           | stg_Movement_CRA  |

Same column types as SDR. Same procedure: Flat File Source > OLE DB Destination.

#### Create Data Flow Tasks for 4 UPC files

| DFT Name        | CSV File   | Flat File CM Name | Destination Table |
| :-------------- | :--------- | :---------------- | :---------------- |
| DFT_Product_SDR | UPCSDR.csv | FF_UPCSDR         | stg_Product_SDR   |
| DFT_Product_CSO | UPCCSO.csv | FF_UPCCSO         | stg_Product_CSO   |
| DFT_Product_TPA | UPCTPA.csv | FF_UPCTPA         | stg_Product_TPA   |
| DFT_Product_CRA | UPCCRA.csv | FF_UPCCRA         | stg_Product_CRA   |

**UPC column types:**

| Column    | DataType                          | Length |
| :-------- | :-------------------------------- | :----- |
| COM_CODE  | four-byte signed integer [DT_I4]  | -      |
| UPC       | eight-byte signed integer [DT_I8] | -      |
| DESCRIP   | string [DT_STR]                   | 100    |
| SIZE      | string [DT_STR]                   | 30     |
| CASE_PACK | four-byte signed integer [DT_I4]  | -      |
| NITEM     | eight-byte signed integer [DT_I8] | -      |

> **IMPORTANT:** The CSV header says `CASE` but your staging table column is `CASE_PACK`. In the **Mappings** tab of the OLE DB Destination, manually map `CASE` (source) to `CASE_PACK` (destination).

#### Create Data Flow Task for DEMO.csv

| DFT Name  | CSV File | Flat File CM Name | Destination Table |
| :-------- | :------- | :---------------- | :---------------- |
| DFT_Store | DEMO.csv | FF_DEMO           | stg_Store         |

**DEMO column types (ALL strings because DEMO has dirty data with dots):**

| Column   | DataType        | Length |
| :------- | :-------------- | :----- |
| STORE    | string [DT_STR] | 10     |
| NAME     | string [DT_STR] | 60     |
| CITY     | string [DT_STR] | 50     |
| ZIP      | string [DT_STR] | 10     |
| ZONE     | string [DT_STR] | 10     |
| URBAN    | string [DT_STR] | 10     |
| WEEKVOL  | string [DT_STR] | 20     |
| INCOME   | string [DT_STR] | 20     |
| EDUC     | string [DT_STR] | 20     |
| POVERTY  | string [DT_STR] | 20     |
| HSIZEAVG | string [DT_STR] | 20     |
| ETHNIC   | string [DT_STR] | 20     |
| DENSITY  | string [DT_STR] | 20     |
| AGE9     | string [DT_STR] | 20     |
| AGE60    | string [DT_STR] | 20     |
| WORKWOM  | string [DT_STR] | 20     |
| PRICLOW  | string [DT_STR] | 10     |
| PRICMED  | string [DT_STR] | 10     |
| PRICHIGH | string [DT_STR] | 10     |

> **NOTE:** DEMO.csv has many more columns than we need. In the Flat File Connection Manager **Columns** tab, you will see all columns. You only need to map the 19 columns listed above. In the **OLE DB Destination Mappings**, just map the ones your staging table has and ignore the rest.
>
> **ALTERNATIVE (EASIER):** If DEMO.csv has too many columns making it hard to configure, you can instead: (1) use an Execute SQL Task to run a `BULK INSERT` command, or (2) select only the needed columns in the Flat File Source's **Columns** output.

#### Final Package 1 Layout

Your Control Flow should have **9 Data Flow Tasks**. They can all be independent (no precedence constraints needed between them, or you can chain them with green arrows if you prefer sequential execution).

**Before running Package 1, take this screenshot:**

- Run in SSMS: `SELECT COUNT(*) FROM [team1_staging_area].dbo.stg_Movement_SDR;` -- should return 0
- **SCREENSHOT 8:** SSMS showing 0 rows before load

#### Run Package 1

1. Right-click `01_Extract_to_Staging.dtsx` > **Execute Package**
2. Wait for all 9 tasks to turn green
3. **SCREENSHOT 4:** Control Flow showing all 9 DFTs
4. **SCREENSHOT 5:** Double-click one DFT to show Data Flow (Flat File Source > OLE DB Dest)
5. **SCREENSHOT 6:** Double-click a Flat File Connection Manager to show encoding/delimiter
6. **SCREENSHOT 7:** Execution result - all green checkmarks

**After running, verify in SSMS:**

```sql
USE [team1_staging_area];
SELECT TOP 10 * FROM dbo.stg_Movement_SDR;
```

- **SCREENSHOT 9:** TOP 10 rows showing loaded data

```sql
SELECT 'stg_Movement_SDR' AS TableName, COUNT(*) AS RowCount FROM stg_Movement_SDR
UNION ALL SELECT 'stg_Movement_CSO', COUNT(*) FROM stg_Movement_CSO
UNION ALL SELECT 'stg_Movement_TPA', COUNT(*) FROM stg_Movement_TPA
UNION ALL SELECT 'stg_Movement_CRA', COUNT(*) FROM stg_Movement_CRA
UNION ALL SELECT 'stg_Product_SDR',  COUNT(*) FROM stg_Product_SDR
UNION ALL SELECT 'stg_Product_CSO',  COUNT(*) FROM stg_Product_CSO
UNION ALL SELECT 'stg_Product_TPA',  COUNT(*) FROM stg_Product_TPA
UNION ALL SELECT 'stg_Product_CRA',  COUNT(*) FROM stg_Product_CRA
UNION ALL SELECT 'stg_Store',        COUNT(*) FROM stg_Store
ORDER BY TableName;
```

- **SCREENSHOT 10:** Row counts for all staging tables

---

### PACKAGE 2: `02_Transform_Staging.dtsx`

**Purpose:** Run staging-area transformations using Execute SQL Tasks.

#### Create the Package

1. Add new SSIS package: `02_Transform_Staging.dtsx`

#### Create OLE DB Connection Manager

1. Reuse or create connection to `team1_staging_area` (same as Package 1)
2. Name it: `StagingDB`

#### Add Execute SQL Tasks

You need to add **Execute SQL Tasks** to the Control Flow, chaining them with green arrows (top to bottom). Each task runs a block of SQL from `04_transform_staging.sql`.

**Task 1: Add CATEGORY_CODE to Movement tables**

1. Drag **Execute SQL Task** to Control Flow
2. Rename: `EST_Add_CategoryCode_Movement`
3. Double-click > General tab:
   - Connection: `StagingDB`
   - SQLStatement: paste the following:

```sql
ALTER TABLE dbo.stg_Movement_SDR ADD CATEGORY_CODE CHAR(3);
END
UPDATE dbo.stg_Movement_SDR SET CATEGORY_CODE = 'SDR';

IF COL_LENGTH('dbo.stg_Movement_CSO', 'CATEGORY_CODE') IS NULL
BEGIN
    ALTER TABLE dbo.stg_Movement_CSO ADD CATEGORY_CODE CHAR(3);
END
UPDATE dbo.stg_Movement_CSO SET CATEGORY_CODE = 'CSO';

IF COL_LENGTH('dbo.stg_Movement_TPA', 'CATEGORY_CODE') IS NULL
BEGIN
    ALTER TABLE dbo.stg_Movement_TPA ADD CATEGORY_CODE CHAR(3);
END
UPDATE dbo.stg_Movement_TPA SET CATEGORY_CODE = 'TPA';

IF COL_LENGTH('dbo.stg_Movement_CRA', 'CATEGORY_CODE') IS NULL
BEGIN
    ALTER TABLE dbo.stg_Movement_CRA ADD CATEGORY_CODE CHAR(3);
END
UPDATE dbo.stg_Movement_CRA SET CATEGORY_CODE = 'CRA';
```

4. Click OK

**Task 2: Replace NULL SALE with 'N'**

1. Drag another Execute SQL Task, connect green arrow from Task 1
2. Rename: `EST_Replace_NULL_SALE`
3. SQL:

```sql
UPDATE dbo.stg_Movement_SDR SET SALE = 'N' WHERE SALE IS NULL OR LTRIM(RTRIM(SALE)) = '';
UPDATE dbo.stg_Movement_CSO SET SALE = 'N' WHERE SALE IS NULL OR LTRIM(RTRIM(SALE)) = '';
UPDATE dbo.stg_Movement_TPA SET SALE = 'N' WHERE SALE IS NULL OR LTRIM(RTRIM(SALE)) = '';
UPDATE dbo.stg_Movement_CRA SET SALE = 'N' WHERE SALE IS NULL OR LTRIM(RTRIM(SALE)) = '';
```

**Task 3: Add CATEGORY_CODE to Product tables**

1. Drag another Execute SQL Task, connect green arrow from Task 2
2. Rename: `EST_Add_CategoryCode_Product`
3. SQL:

```sql
IF COL_LENGTH('dbo.stg_Product_SDR', 'CATEGORY_CODE') IS NULL
BEGIN
    ALTER TABLE dbo.stg_Product_SDR ADD CATEGORY_CODE CHAR(3);
END
UPDATE dbo.stg_Product_SDR SET CATEGORY_CODE = 'SDR';

IF COL_LENGTH('dbo.stg_Product_CSO', 'CATEGORY_CODE') IS NULL
BEGIN
    ALTER TABLE dbo.stg_Product_CSO ADD CATEGORY_CODE CHAR(3);
END
UPDATE dbo.stg_Product_CSO SET CATEGORY_CODE = 'CSO';

IF COL_LENGTH('dbo.stg_Product_TPA', 'CATEGORY_CODE') IS NULL
BEGIN
    ALTER TABLE dbo.stg_Product_TPA ADD CATEGORY_CODE CHAR(3);
END
UPDATE dbo.stg_Product_TPA SET CATEGORY_CODE = 'TPA';

IF COL_LENGTH('dbo.stg_Product_CRA', 'CATEGORY_CODE') IS NULL
BEGIN
    ALTER TABLE dbo.stg_Product_CRA ADD CATEGORY_CODE CHAR(3);
END
UPDATE dbo.stg_Product_CRA SET CATEGORY_CODE = 'CRA';
```

**Task 4: Clean Product Descriptions**

1. Rename: `EST_Clean_Descriptions`
2. SQL:

```sql
UPDATE dbo.stg_Product_SDR SET DESCRIP = REPLACE(REPLACE(DESCRIP, '#', ''), '~', '');
UPDATE dbo.stg_Product_CSO SET DESCRIP = REPLACE(REPLACE(DESCRIP, '#', ''), '~', '');
UPDATE dbo.stg_Product_TPA SET DESCRIP = REPLACE(REPLACE(DESCRIP, '#', ''), '~', '');
UPDATE dbo.stg_Product_CRA SET DESCRIP = REPLACE(REPLACE(DESCRIP, '#', ''), '~', '');
```

**Task 5: Create tmp_Product_All**

1. Rename: `EST_Create_tmp_Product_All`
2. SQL:

```sql
SELECT COM_CODE, UPC, DESCRIP, SIZE, CASE_PACK, NITEM, CATEGORY_CODE
INTO dbo.tmp_Product_All
FROM (
    SELECT COM_CODE, UPC, DESCRIP, SIZE, CASE_PACK, NITEM, CATEGORY_CODE FROM stg_Product_SDR
    UNION ALL
    SELECT COM_CODE, UPC, DESCRIP, SIZE, CASE_PACK, NITEM, CATEGORY_CODE FROM stg_Product_CSO
    UNION ALL
    SELECT COM_CODE, UPC, DESCRIP, SIZE, CASE_PACK, NITEM, CATEGORY_CODE FROM stg_Product_TPA
    UNION ALL
    SELECT COM_CODE, UPC, DESCRIP, SIZE, CASE_PACK, NITEM, CATEGORY_CODE FROM stg_Product_CRA
) AS all_products;
```

**Task 6: Clean Store Data**

1. Rename: `EST_Clean_Store`
2. SQL:

```sql
DELETE FROM dbo.stg_Store WHERE STORE = '.';
UPDATE dbo.stg_Store SET NAME = 'UNKNOWN' WHERE NAME IS NULL OR LTRIM(RTRIM(NAME)) = '';
UPDATE dbo.stg_Store SET CITY = 'UNKNOWN' WHERE CITY IS NULL OR LTRIM(RTRIM(CITY)) = '';
```

#### Final Package 2 Layout

6 Execute SQL Tasks chained with green arrows (top to bottom).

#### Run Package 2

1. Execute the package
2. **SCREENSHOT 11:** Control Flow showing all Execute SQL Tasks
3. **SCREENSHOT 12:** Double-click one task to show the SQL inside
4. **SCREENSHOT 13:** Execution result - all green
5. In SSMS, verify:

```sql
SELECT TOP 5 *, CATEGORY_CODE FROM dbo.stg_Movement_SDR;
```

6. **SCREENSHOT 14:** SSMS showing CATEGORY_CODE column added

---

### PACKAGE 3: `03_Load_DataMart.dtsx`

**Purpose:** Load dimensions, then fact table, then drop temp tables.

#### Create the Package

1. Add new SSIS package: `03_Load_DataMart.dtsx`

#### Create OLE DB Connection Manager for DW

1. Create new OLE DB Connection to `team1_dw_area`
2. Name it: `DWDB`
3. Also add a connection to `team1_staging_area` named `StagingDB` (if not inherited)

#### Add Execute SQL Tasks

Chain all tasks with green arrows, top to bottom.

---

**Task 1: Load DimCategory**

1. Rename: `EST_Load_DimCategory`
2. Connection: `DWDB`
3. SQLStatement:

```sql
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
```

---

**Task 2: Load DimPromotion**

1. Rename: `EST_Load_DimPromotion`
2. Connection: `DWDB`
3. SQLStatement:

```sql
INSERT INTO dbo.DimPromotion (deal_code, deal_type, is_promoted) VALUES
('N',  'No Promotion', 0),
('B',  'Bonus Buy',    1),
('C',  'Coupon',       1),
('S',  'Sale/Discount', 1);
```

---

**Task 3: Load DimTime**

1. Rename: `EST_Load_DimTime`
2. Connection: `DWDB`
3. SQLStatement:

```sql
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
    CASE 
        WHEN DATEPART(WEEK, DATEADD(WEEK, week_id - 1, '1989-09-14')) IN (47, 48, 52, 1, 27)
        THEN 1 ELSE 0 
    END AS is_holiday_week
FROM WeekCTE
OPTION (MAXRECURSION 400);
```

---

**Task 4: Load DimStore**

1. Rename: `EST_Load_DimStore`
2. Connection: `DWDB`
3. SQLStatement:

```sql
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
    CAST(s.URBAN AS BIT)                          AS is_urban,
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
```

---

**Task 5: Load DimProduct**

1. Rename: `EST_Load_DimProduct`
2. Connection: `DWDB`
3. SQLStatement:

```sql
INSERT INTO dbo.DimProduct 
    (upc, description, size, case_pack, commodity_code, item_number)
SELECT 
    p.UPC,
    p.DESCRIP                                     AS description,
    p.SIZE                                        AS size,
    p.CASE_PACK                                   AS case_pack,
    p.COM_CODE                                    AS commodity_code,
    p.NITEM                                       AS item_number
FROM [team1_staging_area].dbo.tmp_Product_All p;
```

---

**Task 6: Load FactWeeklySales**

1. Rename: `EST_Load_FactWeeklySales`
2. Connection: `DWDB`
3. **⚠️ This is the big one — it will take several minutes for ~34M rows. Be patient.**
4. SQLStatement:

```sql
INSERT INTO dbo.FactWeeklySales
    (product_key, store_key, time_key, category_key, promotion_key,
     units_sold, unit_price, shelf_price, price_qty, revenue, 
     gross_profit, profit_margin_pct)
SELECT 
    dp.product_key,
    ds.store_key,
    dt.time_key,
    dc.category_key,
    dpr.promotion_key,
    sm.MOVE                                                    AS units_sold,
    CASE WHEN sm.QTY > 0 
         THEN CAST(sm.PRICE / sm.QTY AS DECIMAL(8,2)) 
         ELSE NULL 
    END                                                        AS unit_price,
    CAST(sm.PRICE AS DECIMAL(8,2))                             AS shelf_price,
    sm.QTY                                                     AS price_qty,
    CASE WHEN sm.QTY > 0 
         THEN CAST(sm.MOVE * (sm.PRICE / sm.QTY) AS DECIMAL(12,2)) 
         ELSE 0 
    END                                                        AS revenue,
    CAST(sm.PROFIT AS DECIMAL(10,2))                           AS gross_profit,
    CASE WHEN sm.MOVE > 0 AND sm.QTY > 0 AND sm.PRICE > 0
         THEN CAST(
              (sm.PROFIT / (sm.MOVE * (sm.PRICE / sm.QTY))) * 100 
              AS DECIMAL(5,2))
         ELSE NULL 
    END                                                        AS profit_margin_pct
FROM (
    SELECT UPC, STORE, WEEK, MOVE, QTY, PRICE, SALE, PROFIT, OK, CATEGORY_CODE 
    FROM [team1_staging_area].dbo.stg_Movement_SDR 
    WHERE OK = 1 AND PRICE > 0
    UNION ALL
    SELECT UPC, STORE, WEEK, MOVE, QTY, PRICE, SALE, PROFIT, OK, CATEGORY_CODE 
    FROM [team1_staging_area].dbo.stg_Movement_CSO 
    WHERE OK = 1 AND PRICE > 0
    UNION ALL
    SELECT UPC, STORE, WEEK, MOVE, QTY, PRICE, SALE, PROFIT, OK, CATEGORY_CODE 
    FROM [team1_staging_area].dbo.stg_Movement_TPA 
    WHERE OK = 1 AND PRICE > 0
    UNION ALL
    SELECT UPC, STORE, WEEK, MOVE, QTY, PRICE, SALE, PROFIT, OK, CATEGORY_CODE 
    FROM [team1_staging_area].dbo.stg_Movement_CRA 
    WHERE OK = 1 AND PRICE > 0
) sm
INNER JOIN dbo.DimProduct dp 
    ON sm.UPC = dp.upc
INNER JOIN dbo.DimStore ds 
    ON sm.STORE = ds.store_id
INNER JOIN dbo.DimTime dt 
    ON sm.WEEK = dt.week_id
INNER JOIN dbo.DimCategory dc 
    ON sm.CATEGORY_CODE = dc.category_code
INNER JOIN dbo.DimPromotion dpr 
    ON sm.SALE = dpr.deal_code;
```

---

**Task 7: Drop Temp Tables**

1. Rename: `EST_Drop_Temp_Tables`
2. Connection: `StagingDB` (**staging**, not DW!)
3. SQLStatement:

```sql
IF OBJECT_ID('dbo.tmp_Product_All', 'U') IS NOT NULL
    DROP TABLE dbo.tmp_Product_All;
```

#### Final Package 3 Layout

7 Execute SQL Tasks chained with green arrows.

#### Run Package 3

1. Execute the package
2. **SCREENSHOT 15:** Control Flow showing all tasks
3. **SCREENSHOT 17:** Execution result - all green

**Verify dimensions in SSMS:**

```sql
USE [team1_dw_area];
SELECT * FROM DimCategory;                    -- 28 rows
SELECT * FROM DimPromotion;                   -- 4 rows
SELECT TOP 10 * FROM DimTime;                 -- ~400 rows total
SELECT TOP 10 * FROM DimStore;                -- ~107 rows total
SELECT TOP 10 * FROM DimProduct;              -- ~3,112 rows total
SELECT TOP 10 * FROM FactWeeklySales;         -- ~34.6M rows total
SELECT COUNT(*) AS FactRowCount FROM FactWeeklySales;
```

4. **SCREENSHOT 18:** DimCategory (28 rows)
5. **SCREENSHOT 19:** DimPromotion (4 rows)
6. **SCREENSHOT 20:** DimTime TOP 10
7. **SCREENSHOT 21:** DimStore TOP 10
8. **SCREENSHOT 22:** DimProduct TOP 10
9. **SCREENSHOT 23:** FactWeeklySales TOP 10 + COUNT

**Verify temp table cleanup:**

```sql
USE [team1_staging_area];
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE 'tmp%';
-- Should return empty
```

10. **SCREENSHOT 24:** Object Explorer showing tmp_Product_All is gone

---

## PHASE 3: SSMS - Verify Business Questions

Run `08_verify_bq_queries.sql` in SSMS against `team1_dw_area`:

### BQ2 - Weekly Soft Drink Sales

```sql
SELECT dt.week_id, dt.week_start_date,
       SUM(f.units_sold) AS total_units_sold
FROM FactWeeklySales f
JOIN DimTime dt ON f.time_key = dt.time_key
JOIN DimCategory dc ON f.category_key = dc.category_key
WHERE dc.category_code = 'SDR'
GROUP BY dt.week_id, dt.week_start_date
ORDER BY dt.week_id;
```

**SCREENSHOT 25:** BQ2 results

### BQ3 - Promotion vs Non-Promotion

```sql
SELECT dp.deal_type, dp.is_promoted,
       COUNT(*) AS num_records,
       AVG(CAST(f.units_sold AS FLOAT)) AS avg_units
FROM FactWeeklySales f
JOIN DimPromotion dp ON f.promotion_key = dp.promotion_key
JOIN DimCategory dc ON f.category_key = dc.category_key
WHERE dc.category_code = 'SDR'
GROUP BY dp.deal_type, dp.is_promoted
ORDER BY avg_units DESC;
```

**SCREENSHOT 26:** BQ3 results

### BQ4 - Promotion Lift (Canned Soup)

Run the BQ4 block from `08_verify_bq_queries.sql`
**SCREENSHOT 27:** BQ4 results

### BQ8 - Store Quartiles (Toothpaste)

Run the BQ8 block from `08_verify_bq_queries.sql`
**SCREENSHOT 28:** BQ8 results

### BQ9 - Top 10 Crackers Weekly

Run the BQ9 block from `08_verify_bq_queries.sql`
**SCREENSHOT 29:** BQ9 results

---

## PHASE 4: Fill In Report

After all screenshots are taken:

1. **Insert screenshots** into the DOCX at each placeholder
2. **Fill actual row counts** in Section 6.10:

| Table           | Expected | Actual            |
| :-------------- | :------- | :---------------- |
| DimCategory     | 28       | (from your COUNT) |
| DimPromotion    | 4        | (from your COUNT) |
| DimTime         | ~400     | (from your COUNT) |
| DimStore        | ~107     | (from your COUNT) |
| DimProduct      | ~3,112   | (from your COUNT) |
| FactWeeklySales | ~34.6M   | (from your COUNT) |

3. **Insert ERDs** at Section 1.5 and Section 4.4 placeholders
4. **Insert MappingTables.xlsx** screenshots into Appendix B
5. Export final DOCX/PDF

---

## Quick Reference: Screenshot Checklist

| #  | What                                  | When                 |
| :- | :------------------------------------ | :------------------- |
| 1  | Object Explorer - both databases      | After Step 1         |
| 2  | Staging tables list                   | After Step 2         |
| 3  | DW tables list                        | After Step 3         |
| 4  | Package 1 Control Flow                | Before running Pkg 1 |
| 5  | Sample Data Flow (one DFT)            | Before running Pkg 1 |
| 6  | Flat File Connection Manager settings | Before running Pkg 1 |
| 7  | Package 1 execution - all green       | After running Pkg 1  |
| 8  | SSMS COUNT = 0 (before load)          | Before running Pkg 1 |
| 9  | SSMS TOP 10 (after load)              | After running Pkg 1  |
| 10 | All staging row counts                | After running Pkg 1  |
| 11 | Package 2 Control Flow                | Before running Pkg 2 |
| 12 | Execute SQL Task showing SQL          | Before running Pkg 2 |
| 13 | Package 2 execution - all green       | After running Pkg 2  |
| 14 | CATEGORY_CODE visible in staging      | After running Pkg 2  |
| 15 | Package 3 Control Flow                | Before running Pkg 3 |
| 16 | Package 3 Data Flow (DimStore)        | Before running Pkg 3 |
| 17 | Package 3 execution - all green       | After running Pkg 3  |
| 18 | DimCategory (28 rows)                 | After running Pkg 3  |
| 19 | DimPromotion (4 rows)                 | After running Pkg 3  |
| 20 | DimTime TOP 10                        | After running Pkg 3  |
| 21 | DimStore TOP 10                       | After running Pkg 3  |
| 22 | DimProduct TOP 10                     | After running Pkg 3  |
| 23 | FactWeeklySales TOP 10 + COUNT        | After running Pkg 3  |
| 24 | tmp tables removed                    | After running Pkg 3  |
| 25 | BQ2 query results                     | Phase 3              |
| 26 | BQ3 query results                     | Phase 3              |
| 27 | BQ4 query results                     | Phase 3              |
| 28 | BQ8 query results                     | Phase 3              |
| 29 | BQ9 query results                     | Phase 3              |
