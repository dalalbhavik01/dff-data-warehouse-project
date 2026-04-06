# SSIS Packages for DFF Data Warehouse ETL

## Before You Open These Packages

1. **Server:** Update the connection string server name if different from `infodata16.mbs.tamu.edu`
2. **CSV Path:** Update the flat file paths from `C:\DFF_Data\` to your actual CSV location
3. **Database names:** Currently set to `team1_staging_area` and `team1_dw_area`

## Package Execution Order

1. **Run Scripts 01-03 in SSMS first** (create databases + staging tables + DW tables)
2. Open `01_Extract_to_Staging.dtsx` in Visual Studio (SSDT) and execute
3. Open `02_Transform_Staging.dtsx` and execute
4. Open `03_Load_DataMart.dtsx` and execute
5. Run Script 08 in SSMS to verify BQ queries

## Package Details

| Package | Tasks | Connection | Purpose |
|---------|-------|-----------|---------|
| 01_Extract_to_Staging.dtsx | 9 Data Flow Tasks | Staging DB + 9 Flat File | Load CSVs into staging |
| 02_Transform_Staging.dtsx | Execute SQL Tasks | Staging DB | Clean & transform staging data |
| 03_Load_DataMart.dtsx | Execute SQL Tasks | Staging DB + DW DB | Load dims, fact, drop temps |

## Important Notes

- These packages target **SQL Server 2016** (PackageFormatVersion 8)
- Flat File Sources use **Windows-1252 (CP1252)** encoding
- Column delimiter is **comma**, row delimiter is **CRLF**
- If packages don't open cleanly in SSDT, you can alternatively run the SQL scripts
  directly in SSMS in order: 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08
