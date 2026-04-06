# Report 3 — Step-by-Step Implementation Guide

**Based on professor feedback from Reports 1 & 2**

---

## Professor Feedback Analysis (Critical Fixes for Integrated Report)

### Report 1 Feedback (-8 pts from 50)

| Points Lost | Professor Comment | What Went Wrong | Fix for Report 3 |
|:--|:--|:--|:--|
| **-3** | *"Wrong. ERDs do not become a STAR schema. At this point, we are only interested in the data that we have from DFF."* | We drew a star schema ERD in Section 1 instead of showing the **source data relationships** (Movement → UPC, Movement → DEMO, etc.) | **§1.5: Replace with a proper source-data ERD showing OLTP file relationships only.** Use Visio/LucidChart. |
| **-3** | *"Did not prioritize the BQs."* | BQs were listed but not ranked/prioritized | **§2.3: Already fixed — added priority ranking 1–10 with rationale** |
| **-2** | *"Why this is here?"* (p.12 — data sampling section) | The data sampling methodology section was misplaced or unnecessary | **Remove the "Data Sampling Methodology" sub-section from §1. Not needed.** |
| — | *"Nice"* (p.9 — average price by category chart) | Positive feedback on data visualizations | Keep similar charts in the integrated report |

### Report 2 Feedback (-2 pts from 75)

| Points Lost | Professor Comment | What Went Wrong | Fix for Report 3 |
|:--|:--|:--|:--|
| **-2** | *"This is not an ERD."* (p.15) | Star schema diagram was not done in a proper ERD tool | **§4.4: Must create proper ERD using Visio or LucidChart** — NOT markdown or code-generated |
| — | *"As these relationships do not have any meaning, do not label them. Refrain from referring them PK and FK. In dimStore table write store_key INT PK"* | Labeled relationships incorrectly; should show PK inside the table box, not on relationship lines | **§4.4: In the star schema diagram, write "store_key INT PK" inside the table box. Do NOT label relationship lines with PK/FK.** |
| — | *"Irrelevant para. Unless you have multiple data marts, no reason to worry about conformability."* (p.8) | Discussed conformed dimensions when we only have one data mart | **§3: Remove conformability discussion. We have ONE data mart, so conformed dimensions are not relevant.** |

---

## Corrective Actions in Integrated_Report_3.md

### Must Fix Before Submission

1. **§1.5 ERD** — Replace star schema with **source data ERD** showing:
   - Movement files → UPC files (via UPC column)
   - Movement files → DEMO (via STORE column)
   - Movement files → CCOUNT (via STORE + WEEK)
   - Use **Visio or LucidChart** (professor specifically requires this)

2. **§2 Remove "Data Sampling Methodology"** — Professor flagged it as misplaced ("Why is this here?")

3. **§3 Remove conformability paragraph** — Professor said it's irrelevant with one data mart

4. **§4.4 Star Schema ERD** — Must be from **Visio/LucidChart**, NOT code-generated. Inside each table box, write attributes as: `store_key INT PK`, `store_id INT`, etc. Do NOT label relationship lines.

5. **§2.3 BQ Prioritization** — Already fixed (was missing in Report 1)

---

## SSIS Package Creation — Step-by-Step Guide

### Prerequisites
- SQL Server 2016 instance (e.g., `infodata16.mbs.tamu.edu`)
- SQL Server Data Tools (SSDT) or Visual Studio 2022 with SSIS extension
- CSV data files accessible from the server

**⚠️ CRITICAL: Connecting From Home**
If you are doing this project from home instead of the Mays lab, you MUST do the following to connect to the database and use SSIS:
1. Turn on the **Cisco Secure Client VPN** (`connect.tamu.edu`).
2. Do not open Visual Studio or SSMS normally. You must launch them via Command Prompt so they authenticate with your NetID on the TAMU domain.
3. Open the **Run** app (Win + R) or **Command Prompt** and paste exactly:
   ```cmd
   C:\Windows\System32\runas.exe /netonly /user:auth\YOUR_NETID "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe"
   ```
   *(Make sure to change `YOUR_NETID` to your actual NetID).*
4. A dark command prompt screen will pop up asking for your password. Type your NetID password and hit Enter. Visual Studio will now open securely connected to the TAMU domain!

### Step 1: Create Databases in SSMS

1. Open SSMS → Connect to `infodata16.mbs.tamu.edu`
2. Open `report_3/sql/01_create_databases.sql`
3. Execute (F5)
4. **📸 Screenshot 1:** Object Explorer showing both databases
5. Open `report_3/sql/02_create_staging_tables.sql` → Execute
6. **📸 Screenshot 2:** Object Explorer → team1_staging_area → Tables
7. Open `report_3/sql/03_create_dw_tables.sql` → Execute
8. **📸 Screenshot 3:** Object Explorer → team1_dw_area → Tables

### Step 2: Create SSIS Project in Visual Studio

1. Open Visual Studio (with SSDT installed)
2. File → New → Project → **Integration Services Project**
3. Name: `DFF_ETL_Project`
4. Three packages will be created (right-click Solution Explorer → Add New SSIS Package):
   - `01_Extract_to_Staging.dtsx`
   - `02_Transform_Staging.dtsx`
   - `03_Load_DataMart.dtsx`

### Step 3: Build Package 1 — Extract to Staging

**Connection Managers (create these first):**

1. Right-click Connection Managers tray → **New Flat File Connection**
   - Name: `FF_wsdr`
   - File: Browse to `wsdr.csv`
   - Format: Delimited
   - Header row delimiter: `{CR}{LF}`
   - Column delimiter: `Comma {,}`
   - Code page: `1252 (ANSI - Latin I)`
   - ✅ Column names in the first data row
   - Click **Columns** tab → verify all 9 columns detected
   - Click **Advanced** tab → set data types:
     - UPC: eight-byte signed integer [DT_I8]
     - STORE, WEEK, MOVE, QTY, OK: four-byte signed integer [DT_I4]
     - PRICE, PROFIT: float [DT_R8]
     - SALE: string [DT_STR] length 5

2. Repeat for each CSV file (WCSO-Done.csv, WTPA_done.csv, Done-WCRA.csv, UPCSDR.csv, UPCCSO.csv, UPCTPA.csv, UPCCRA.csv, DEMO.csv, CCOUNT.csv)

3. Right-click Connection Managers → **New OLE DB Connection**
   - Server: `infodata16.mbs.tamu.edu`
   - Database: `team1_staging_area`
   - Name: `OLEDB_Staging`

**Control Flow (drag from Toolbox):**

4. Drag 10 **Data Flow Tasks** onto the Control Flow canvas:
   - DFT_Movement_SDR, DFT_Movement_CSO, DFT_Movement_TPA, DFT_Movement_CRA
   - DFT_Product_SDR, DFT_Product_CSO, DFT_Product_TPA, DFT_Product_CRA
   - DFT_Store, DFT_CustomerTraffic

5. **📸 Screenshot 4:** Control Flow showing all 10 tasks

**Data Flow (for each task):**

6. Double-click `DFT_Movement_SDR` → opens Data Flow tab
7. Drag **Flat File Source** → configure with `FF_wsdr` connection
8. Drag **OLE DB Destination** → configure:
   - Connection: `OLEDB_Staging`
   - Table: `stg_Movement_SDR`
   - Click **Mappings** → verify columns map correctly
9. Connect arrow from Source → Destination (green arrow)
10. **📸 Screenshot 5:** Data Flow showing Source → Destination
11. **📸 Screenshot 6:** Flat File Connection Manager properties

12. Repeat Steps 6-9 for all 10 Data Flow Tasks

**Execute Package 1:**

13. Before execution: Run in SSMS:
    ```sql
    SELECT COUNT(*) FROM [team1_staging_area].dbo.stg_Movement_SDR;
    -- Should show 0
    ```
14. **📸 Screenshot 8:** SSMS showing 0 rows

15. Right-click Package → **Execute Package** (or press Ctrl+F5)
16. **📸 Screenshot 7:** All tasks show green checkmarks

17. After execution: Run in SSMS:
    ```sql
    SELECT TOP 10 * FROM [team1_staging_area].dbo.stg_Movement_SDR;
    ```
18. **📸 Screenshot 9:** Data visible in staging table

19. Run row count verification from `02_create_staging_tables.sql` (bottom query)
20. **📸 Screenshot 10:** Row counts for all staging tables

### Step 4: Build Package 2 — Transform Staging

**Connection Manager:**
1. Add OLE DB Connection to `team1_staging_area` (reuse or create new)

**Control Flow:**
2. Drag 6 **Execute SQL Tasks** onto canvas:
   - `SQL_Add_CategoryCode`
   - `SQL_Replace_Null_Sale`
   - `SQL_Clean_Products`
   - `SQL_Clean_Store`
   - `SQL_Clean_CCOUNT`
   - `SQL_Create_Tmp_Products`
3. Connect them with green arrows (sequential — top to bottom)

**Configure each Execute SQL Task:**
4. Double-click each task → General tab:
   - Connection: `OLEDB_Staging`
   - SQLStatement: Copy the relevant SQL from `04_transform_staging.sql`
   
   For `SQL_Add_CategoryCode`, paste:
   ```sql
   ALTER TABLE dbo.stg_Movement_SDR ADD CATEGORY_CODE CHAR(3);
   UPDATE dbo.stg_Movement_SDR SET CATEGORY_CODE = 'SDR';
   ALTER TABLE dbo.stg_Movement_CSO ADD CATEGORY_CODE CHAR(3);
   UPDATE dbo.stg_Movement_CSO SET CATEGORY_CODE = 'CSO';
   -- ... (all 8 ALTER+UPDATE statements)
   ```

5. **📸 Screenshot 11:** Control Flow of Package 2
6. **📸 Screenshot 12:** SQL visible in one Execute SQL Task

**Execute Package 2:**
7. Right-click → Execute Package
8. **📸 Screenshot 13:** All green checkmarks
9. Verify in SSMS:
   ```sql
   SELECT TOP 5 *, CATEGORY_CODE FROM [team1_staging_area].dbo.stg_Movement_SDR;
   ```
10. **📸 Screenshot 14:** CATEGORY_CODE column visible

### Step 5: Build Package 3 — Load Data Mart

**Connection Managers:**
1. Add OLE DB Connection to `team1_dw_area` (Name: `OLEDB_DW`)
2. Keep connection to `team1_staging_area` (Name: `OLEDB_Staging`)

**Control Flow:**
3. Drag Execute SQL Tasks and Data Flow Tasks:
   - `SQL_Load_DimCategory` (Execute SQL → paste from `05_load_dimensions.sql` DimCategory section)
   - `SQL_Load_DimPromotion` (Execute SQL → paste DimPromotion section)
   - `SQL_Load_DimTime` (Execute SQL → paste DimTime CTE)
   - `SQL_Load_DimStore` (Execute SQL → paste DimStore INSERT...SELECT)
   - `SQL_Load_DimProduct` (Execute SQL → paste DimProduct INSERT...SELECT)
   - `SQL_Load_FactWeeklySales` (Execute SQL → paste from `06_load_facts.sql`)
   - `SQL_Drop_Temp_Tables` (Execute SQL → paste from `07_drop_temp_tables.sql`)

4. Connect with green arrows: Category → Promotion → Time → Store → Product → FactWeeklySales → DropTemp

5. **📸 Screenshot 15:** Control Flow of Package 3

**For DimStore, you can alternatively use a Data Flow Task:**
6. If using Data Flow: OLE DB Source (query from staging) → OLE DB Destination (DimStore in DW)
7. **📸 Screenshot 16:** Data Flow for DimStore

**Execute Package 3:**
8. Right-click → Execute Package (this will take several minutes for FactWeeklySales)
9. **📸 Screenshot 17:** All green checkmarks

**Verify dimension tables:**
10. Run in SSMS:
    ```sql
    USE [team1_dw_area];
    SELECT * FROM DimCategory;          -- 28 rows
    SELECT * FROM DimPromotion;         -- 4 rows
    SELECT TOP 10 * FROM DimTime;       -- ~400 rows
    SELECT TOP 10 * FROM DimStore;      -- ~107 rows
    SELECT TOP 10 * FROM DimProduct;    -- ~3,112 rows
    ```
11. **📸 Screenshots 18-22:** One for each dimension table

**Verify fact table:**
12. Run in SSMS:
    ```sql
    SELECT TOP 10 * FROM FactWeeklySales;
    SELECT COUNT(*) FROM FactWeeklySales;    -- ~34.6M
    ```
13. **📸 Screenshot 23:** FactWeeklySales TOP 10 + COUNT

**Verify temp table cleanup:**
14. Check Object Explorer → team1_staging_area → Tables
15. **📸 Screenshot 25:** tmp_Product_All gone

### Step 6: Run Business Question Verification

1. Open `report_3/sql/08_verify_bq_queries.sql` in SSMS
2. Execute each BQ query one at a time
3. **📸 Screenshot 26:** BQ2 query results

### Step 7: Create ERD Diagrams

**Source Data ERD (for §1.5) — MUST use Visio or LucidChart:**
1. Open Visio or go to lucidchart.com
2. Create a new ERD diagram with these entities:
   - `Movement_Files (Wxxx)`: UPC, STORE, WEEK, MOVE, QTY, PRICE, SALE, PROFIT, OK
   - `UPC_Files (UPCxxx)`: COM_CODE, UPC, DESCRIP, SIZE, CASE, NITEM
   - `DEMO`: STORE, NAME, CITY, ZIP, ZONE, URBAN, WEEKVOL, INCOME, ...
   - `CCOUNT`: STORE, DATE, WEEK, GROCERY, DAIRY, ..., CUSTCOUN
3. Draw relationships:
   - Movement.UPC → UPC.UPC (many-to-one)
   - Movement.STORE → DEMO.STORE (many-to-one)
   - Movement.STORE+WEEK → CCOUNT.STORE+WEEK (many-to-one)
4. **NO star schema here** — this is source data only
5. Export as image → insert into §1.5

**Star Schema ERD (for §4.4) — MUST use Visio or LucidChart:**
1. Create another ERD diagram
2. Center: FactWeeklySales with all columns listed as:
   ```
   sales_fact_id   INT PK
   product_key     INT
   store_key       INT
   time_key        INT
   category_key    INT
   promotion_key   INT
   units_sold      INT
   unit_price      DECIMAL(8,2)
   ...
   ```
3. Surrounding dimensions: DimProduct, DimStore, DimTime, DimCategory, DimPromotion
4. Draw lines from fact to dimensions — **DO NOT label the lines** (per professor's feedback)
5. Write PK inside the table box (e.g., `store_key INT PK`), NOT on the lines
6. Export as image → insert into §4.4

### Step 8: Create Excel Mapping Tables

1. Open Excel
2. **Sheet 1 "Mapping Table 1":** Copy the Source → Staging mapping from §4.5 of the report
   - Columns: Source File Name, Source File Attribute, Mapping, Staging Table Type, Staging Table Name, Staging Table Attribute
3. **Sheet 2 "Mapping Table 2":** Copy the Staging → DW mapping from §4.6
   - Columns: Staging Table, Staging Table Attribute, Mapping, Data Mart Table Type, Data Mart Table Name, Data Mart Table Attribute
4. Save as `report_3/MappingTables.xlsx`
5. Insert both tables into the report

### Step 9: Assemble Final Document

1. Convert `Integrated_Report_3.md` to Word/PDF
2. Replace all `*[Screenshot X]*` placeholders with actual screenshots
3. Fill in "Actual Rows" in Section 6.10
4. Insert ERD images from Step 7
5. Add cover page with team name, course, date
6. Auto-generate Table of Contents
7. Review against rubric one final time
8. Submit

---

## Pre-Submission Checklist

| Check | Status |
|:--|:--|
| §1.5 has source data ERD (NOT star schema) from Visio/LucidChart | ☐ |
| §2.2 has exactly 10 BQs with Easy/Medium/Hard labels | ☐ |
| §2.3 has prioritized BQs with rationale | ☐ |
| §2 does NOT have "Data Sampling Methodology" sub-section | ☐ |
| §3 does NOT discuss conformability (irrelevant with one data mart) | ☐ |
| §4.4 has star schema ERD from Visio/LucidChart — PK inside box, no labels on lines | ☐ |
| §4.5 + §4.6 mapping tables also included as Excel file | ☐ |
| §5 ETL Plan covers all 10 sub-items | ☐ |
| §6 has all 26 screenshots inserted | ☐ |
| §6 includes ALL SQL statements | ☐ |
| §6 lists temporary tables (tmp_Product_All) | ☐ |
| §6 has before/after evidence for ETL runs | ☐ |
| §6 discusses granularity of fact table | ☐ |
| Report "tells a story" — self-explanatory text throughout | ☐ |
| All three reports feel like one integrated document | ☐ |
| References section complete | ☐ |
