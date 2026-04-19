# Report 4 — Final Completion Guide
## What You Need To Do Before Submission

> **Status**: Report text is 100% complete. The ONLY remaining work is generating
> 12 BI tool screenshots on the TAMU lab machine and embedding them.
> This guide walks you through every step in exact order.

---

## Prerequisites

Before starting, make sure you have access to:

- [ ] **SQL Server 2016** with `team1_dw_area` database populated (from Report 3)
- [ ] **Visual Studio 2015** (SSDT) with SSRS and SSAS project templates
- [ ] **Power BI Desktop** (free download from Microsoft)
- [ ] **AWS Academy Lab** with Redshift access
- [ ] The `report_4/` folder from this project on your machine

---

## Part 1: SSRS Reports (Screenshots 30–33)

### BQ2 — Weekly Soft Drink Unit Sales Trend Report

**Step 1: Create the SSRS project**
1. Open Visual Studio 2015 → File → New Project → Report Server Project
2. Name it `DFF_BI_Reports`

**Step 2: Create the data source**
1. In Solution Explorer, right-click `Shared Data Sources` → Add New
2. Connection string: `Data Source=ISTM637-PC\SQLEXPRESS;Initial Catalog=team1_dw_area`
3. Use Windows Authentication

**Step 3: Create the BQ2 report**
1. Right-click `Reports` → Add New Item → Report → name it `BQ2_Weekly_SDR_Sales.rdl`
2. Create a Dataset with this query:
```sql
SELECT dt.week_id,
       dt.week_start_date,
       SUM(f.units_sold) AS total_units_sold
FROM   FactWeeklySales f
JOIN   DimTime dt ON f.time_key = dt.time_key
JOIN   DimCategory dc ON f.category_key = dc.category_key
WHERE  dc.category_code = 'SDR'
GROUP BY dt.week_id, dt.week_start_date
ORDER BY dt.week_id;
```
3. Insert a **Chart** → Line Chart
   - Category (X-axis): `week_start_date`
   - Values (Y-axis): `total_units_sold`
   - Title: "BQ2: Weekly Soft Drink Unit Sales Across All Stores"
4. Add a **Table** below the chart showing `week_id`, `week_start_date`, `total_units_sold`

**Step 4: Take screenshots**
- 📸 **Screenshot 30**: Report Designer view showing the layout (chart + table)
- 📸 **Screenshot 31**: Click Preview tab — showing the rendered chart with data

Save as: `report_4/screenshots/screenshot_30.png` and `screenshot_31.png`

---

### BQ9 — Top 10 Cracker Products with Week-over-Week Change

**Step 5: Create the BQ9 report**
1. Add New Report → `BQ9_Top10_Crackers.rdl`
2. Add a **Report Parameter**: `@WeekID` (Integer, prompt: "Select Week")
   - Available Values query:
```sql
SELECT DISTINCT week_id FROM DimTime ORDER BY week_id;
```
3. Main Dataset query:
```sql
WITH ranked AS (
    SELECT dp.upc,
           dp.description,
           dt.week_id,
           SUM(f.units_sold) AS units_sold,
           RANK() OVER (PARTITION BY dt.week_id ORDER BY SUM(f.units_sold) DESC) AS sales_rank
    FROM   FactWeeklySales f
    JOIN   DimProduct dp ON f.product_key = dp.product_key
    JOIN   DimTime dt ON f.time_key = dt.time_key
    JOIN   DimCategory dc ON f.category_key = dc.category_key
    WHERE  dc.category_code = 'CRA'
    GROUP BY dp.upc, dp.description, dt.week_id
),
with_lag AS (
    SELECT *,
           LAG(units_sold) OVER (PARTITION BY upc ORDER BY week_id) AS prev_week_units,
           units_sold - LAG(units_sold) OVER (PARTITION BY upc ORDER BY week_id) AS wow_change
    FROM   ranked
    WHERE  sales_rank <= 10
)
SELECT * FROM with_lag
WHERE  week_id = @WeekID
ORDER BY sales_rank;
```
4. Insert a **Table** with columns: Rank, UPC, Description, Units Sold, Previous Week, WoW Change
5. Add conditional formatting: green for positive WoW, red for negative

**Step 6: Take screenshots**
- 📸 **Screenshot 32**: Report Designer view showing layout with parameter
- 📸 **Screenshot 33**: Preview tab with a specific week selected (e.g., week 100) showing 10 rows

Save as: `report_4/screenshots/screenshot_32.png` and `screenshot_33.png`

---

## Part 2: SSAS Cube (Screenshots 34–36)

### BQ3 — Promotion vs Non-Promotion Sales Volume

**Step 7: Create the SSAS project**
1. Visual Studio → New Project → Analysis Services Multidimensional Project
2. Name it `DFF_Sales_Cube`

**Step 8: Create the Data Source and Data Source View**
1. Add Data Source → point to `team1_dw_area`
2. Add Data Source View → select: `FactWeeklySales`, `DimPromotion`, `DimCategory`, `DimTime`
3. Verify relationships are detected from FK constraints

**Step 9: Create the Cube**
1. Right-click `Cubes` → New Cube → Use Existing Tables
2. Select `FactWeeklySales` as the measure group
3. Add measures: `units_sold` (Sum), `revenue` (Sum)
4. Select dimensions: `DimPromotion`, `DimCategory`, `DimTime`
5. Deploy to the local SSAS instance

**Step 10: Browse the Cube**
1. Double-click the cube → click the **Browser** tab
2. Drag `DimPromotion.deal_type` to ROWS
3. Drag `units_sold` to VALUES
4. Filter by `DimCategory.category_code = 'SDR'` (to match BQ3)
5. You should see:
   - `No Promotion` — baseline
   - `Bonus Buy (B)` — promoted
   - `Coupon (C)` — promoted
   - `Sale/Discount (S)` — promoted

**Step 11: Drill down**
1. Drag `DimTime.year` to COLUMNS
2. This shows promotion vs non-promotion sales broken down by year

**Step 12: Take screenshots**
- 📸 **Screenshot 34**: Solution Explorer showing cube structure (measures, dimensions)
- 📸 **Screenshot 35**: Cube Browser pivot — deal_type rows vs units_sold values (filtered to SDR)
- 📸 **Screenshot 36**: Same view with `year` added as columns (drill-down)

Save as: `report_4/screenshots/screenshot_34.png`, `screenshot_35.png`, `screenshot_36.png`

---

## Part 3: Redshift Query v.2 (Screenshots 37–38)

### BQ4 — Promotion Lift by Deal Type in Canned Soup

**Step 13: Export data from SQL Server**

Run in SSMS and save results as CSV:
```sql
-- Export FactWeeklySales (filtered to CSO only for BQ4)
SELECT f.units_sold, f.revenue, p.deal_type, p.is_promoted, c.category_code
FROM   FactWeeklySales f
JOIN   DimPromotion p ON f.promotion_key = p.promotion_key
JOIN   DimCategory c ON f.category_key = c.category_key
WHERE  c.category_code = 'CSO';
```
Save as `bq4_cso_data.csv`

**Step 14: Load into Redshift**
1. Log into AWS Academy → Open Redshift Query Editor v.2
2. Create the table:
```sql
CREATE TABLE bq4_cso_sales (
    units_sold     INT,
    revenue        DECIMAL(12,2),
    deal_type      VARCHAR(20),
    is_promoted    INT,
    category_code  CHAR(3)
);
```
3. Upload the CSV using the Redshift COPY command or the Query Editor's "Load Data" feature

**Step 15: Run the BQ4 query**

Paste this exact query (it's already in the report):
```sql
-- BQ4: Promotion Lift by Deal Type — Canned Soup (Redshift Query v.2)
WITH baseline AS (
    SELECT AVG(units_sold) AS avg_baseline_units
    FROM   bq4_cso_sales
    WHERE  is_promoted = 0
),
promo_stats AS (
    SELECT deal_type,
           COUNT(*)          AS num_weeks,
           AVG(units_sold)   AS avg_promo_units,
           SUM(units_sold)   AS total_promo_units
    FROM   bq4_cso_sales
    WHERE  is_promoted = 1
    GROUP BY deal_type
)
SELECT p.deal_type,
       p.num_weeks,
       p.avg_promo_units,
       b.avg_baseline_units,
       p.avg_promo_units - b.avg_baseline_units   AS incremental_lift,
       ROUND(CAST(p.avg_promo_units AS DECIMAL) / 
             NULLIF(b.avg_baseline_units, 0), 2)   AS lift_multiplier
FROM   promo_stats p
CROSS JOIN baseline b
ORDER BY lift_multiplier DESC;
```

**Step 16: Take screenshots**
- 📸 **Screenshot 37**: The Redshift Query Editor with the SQL visible (before running)
- 📸 **Screenshot 38**: The query results showing deal_type, lift values (after running)

Save as: `report_4/screenshots/screenshot_37.png` and `screenshot_38.png`

---

## Part 4: Power BI Dashboard (Screenshots 39–41)

### BQ8 — Store Quartile Tiers by Toothpaste Revenue + Demographics

**Step 17: Connect Power BI to SQL Server**
1. Open Power BI Desktop → Get Data → SQL Server
2. Server: `ISTM637-PC\SQLEXPRESS`  Database: `team1_dw_area`
3. Import these tables: `FactWeeklySales`, `DimStore`, `DimCategory`, `DimTime`
4. Power BI should auto-detect relationships. If not, create them manually matching the FK keys.

**Step 18: Create the BQ8 measures**
In Power BI, add these DAX measures:
```
Total TPA Revenue = 
CALCULATE(
    SUM(FactWeeklySales[revenue]),
    DimCategory[category_code] = "TPA"
)

Store Quartile = 
VAR CurrentRevenue = [Total TPA Revenue]
VAR AllRevenues = 
    CALCULATETABLE(
        ADDCOLUMNS(VALUES(DimStore[store_id]), "Rev", [Total TPA Revenue]),
        ALL(DimStore)
    )
RETURN
    SWITCH(TRUE(),
        CurrentRevenue >= PERCENTILE.INC([Rev], 0.75), "Q1 (Top 25%)",
        CurrentRevenue >= PERCENTILE.INC([Rev], 0.50), "Q2",
        CurrentRevenue >= PERCENTILE.INC([Rev], 0.25), "Q3",
        "Q4 (Bottom 25%)"
    )
```

Alternatively, use a simpler approach — just create a calculated column or write a supporting query.

**Step 19: Build the Dashboard**
Create a report page with:
1. **Bar Chart**: X-axis = Store Quartile, Y-axis = Total TPA Revenue
2. **Table Visual**: Columns = Store Name, City, Revenue, avg_income, is_urban, price_tier, Quartile
3. **Optional Map**: Use city/zip for location, color by Quartile

**Step 20: Take screenshots**
- 📸 **Screenshot 39**: Model View tab showing the star schema table relationships
- 📸 **Screenshot 40**: Report page with bar chart + demographic table
- 📸 **Screenshot 41**: Same page or second page with map view (if added) or an alternate visualization

Save as: `report_4/screenshots/screenshot_39.png`, `screenshot_40.png`, `screenshot_41.png`

---

## Part 5: Embed Screenshots and Generate Final DOCX

**Step 21: Verify all 12 screenshots exist**
```
report_4/screenshots/
├── screenshot_30.png   (SSRS BQ2 Designer)
├── screenshot_31.png   (SSRS BQ2 Preview)
├── screenshot_32.png   (SSRS BQ9 Designer)
├── screenshot_33.png   (SSRS BQ9 Preview)
├── screenshot_34.png   (SSAS Solution Explorer)
├── screenshot_35.png   (SSAS Cube Browser - BQ3 pivot)
├── screenshot_36.png   (SSAS Cube Browser - drill-down)
├── screenshot_37.png   (Redshift Query Editor)
├── screenshot_38.png   (Redshift BQ4 Results)
├── screenshot_39.png   (Power BI Model View)
├── screenshot_40.png   (Power BI BQ8 Dashboard)
└── screenshot_41.png   (Power BI BQ8 Map/Alt View)
```

**Step 22: Update the markdown to embed them**

Open `Integrated_Report_4.md` and replace each remaining placeholder:

Find:
```
*[Screenshot 30: SSRS Report Designer — BQ2 Weekly SDR Sales trend report]*
```
Replace with:
```
![SSRS Report Designer — BQ2 Weekly SDR Sales trend report](screenshots/screenshot_30.png)
```

Repeat for screenshots 31–41. Or run this one-liner in Terminal:
```bash
cd "/Users/bhavikdalal/Documents/data warehouse/project/report_4"
python3 -c "
import re
with open('Integrated_Report_4.md','r') as f: content = f.read()
for n in range(30, 42):
    # Pattern 1
    content = re.sub(
        rf'\*\[Screenshot {n}:([^\]]*)\]\*',
        lambda m: f'![Screenshot {n}:{m.group(1)}](screenshots/screenshot_{n:02d}.png)',
        content)
with open('Integrated_Report_4.md','w') as f: f.write(content)
print('Done — all BI placeholders replaced')
"
```

**Step 23: Regenerate the DOCX**
```bash
cd "/Users/bhavikdalal/Documents/data warehouse/project/report_4"
python3 generate_docx.py
```

Expected output: file size should increase to ~12–14 MB with all 43 images.

**Step 24: Final verification**
Open `Integrated_Report_4.docx` in Word and check:
- [ ] Title page has: DFF name, team names, group 1, email, date
- [ ] Section 5.2.1: Two SSRS screenshots visible (BQ2 chart, BQ9 table)
- [ ] Section 5.2.2: Three SSAS screenshots visible (cube, pivot, drill-down)
- [ ] Section 5.2.3: Two Redshift screenshots visible (query editor, results)
- [ ] Section 5.2.4: Three Power BI screenshots visible (model, dashboard, map)
- [ ] Appendix C lists all 41 screenshots
- [ ] No yellow placeholder boxes remain

---

## Quick Reference: Grading Breakdown (50 points)

| Category | Points | Status |
|:--|:--|:--|
| Presentation, English, clean writing | 10 | ✅ Ready |
| SSAS (cube + browser for BQ3) | 15 | ⏳ Need screenshots 34-36 |
| SSRS (reports for BQ2, BQ9) | 15 | ⏳ Need screenshots 30-33 |
| Redshift Query v.2 (BQ4 lift query) | 15 | ⏳ Need screenshots 37-38 |
| Power BI (BQ8 dashboard) | 15 | ⏳ Need screenshots 39-41 |
| Integration quality | 5 | ✅ Ready |

> **The text, narrative, SQL queries, and report structure are all done.**
> **You just need to execute the tools and take the screenshots.**

---

## Estimated Time

| Task | Time |
|:--|:--|
| SSRS setup + 2 reports + 4 screenshots | ~45 min |
| SSAS cube + deploy + browse + 3 screenshots | ~30 min |
| Redshift export/load/query + 2 screenshots | ~20 min |
| Power BI connect + dashboard + 3 screenshots | ~30 min |
| Embed + regenerate DOCX + verify | ~10 min |
| **Total** | **~2.5 hours** |
