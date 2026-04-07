# SSIS Packages for DFF Data Warehouse ETL

## Scope

These packages implement the ETL for 4 product categories (Soft Drinks, Canned Soup,
Toothpaste, Crackers) supporting 5 selected Business Questions (BQ2, BQ3, BQ4, BQ8, BQ9).
There is one fact table (FactWeeklySales) and five dimensions.

## Before You Open These Packages in SSDT

You MUST update these values before running:

1. **Server name** -- currently set to `infodata16.mbs.tamu.edu`
   - Edit each package's OLE DB connection manager in SSDT
2. **CSV file paths** -- currently set to `C:\DFF_Data\`
   - Edit Package 1's Flat File connection managers to point to your actual CSV folder
3. **Database names** -- currently `team1_staging_area` and `team1_dw_area`
   - Change if your team uses different database names

## 9 Source Files (Package 1)

| # | CSV File | Staging Table |
|---|----------|---------------|
| 1 | wsdr.csv | stg_Movement_SDR |
| 2 | WCSO-Done.csv | stg_Movement_CSO |
| 3 | WTPA_done.csv | stg_Movement_TPA |
| 4 | Done-WCRA.csv | stg_Movement_CRA |
| 5 | UPCSDR.csv | stg_Product_SDR |
| 6 | UPCCSO.csv | stg_Product_CSO |
| 7 | UPCTPA.csv | stg_Product_TPA |
| 8 | UPCCRA.csv | stg_Product_CRA |
| 9 | DEMO.csv | stg_Store |

## Execution Order

1. Run `01_create_databases.sql` in SSMS
2. Run `02_create_staging_tables.sql` in SSMS
3. Run `03_create_dw_tables.sql` in SSMS
4. Execute `01_Extract_to_Staging.dtsx` in SSDT (9 Data Flow Tasks)
5. Execute `02_Transform_Staging.dtsx` in SSDT (Execute SQL Tasks)
6. Execute `03_Load_DataMart.dtsx` in SSDT (Execute SQL Tasks)
7. Run `08_verify_bq_queries.sql` in SSMS to validate

## Package Details

| Package | Type of Tasks | Connections | Purpose |
|---------|--------------|-------------|---------|
| 01_Extract_to_Staging.dtsx | 9 Data Flow Tasks | Staging DB + 9 Flat File | Load 9 CSVs into staging |
| 02_Transform_Staging.dtsx | Execute SQL Tasks | Staging DB | Add CATEGORY_CODE, clean SALE, create tmp_Product_All |
| 03_Load_DataMart.dtsx | Execute SQL Tasks | Staging DB + DW DB | Load 5 dims + FactWeeklySales, drop temps |

## Technical Notes

- Target: **SQL Server 2016** (PackageFormatVersion 8)
- Flat File encoding: **Windows-1252 (CP1252)**
- Column delimiter: **comma**, row delimiter: **CRLF**
- Package 3 uses Execute SQL Tasks only (no Data Flow Tasks)

## Fallback (No SSDT)

If packages don't open in SSDT, run the SQL scripts directly in SSMS in order:
01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08
