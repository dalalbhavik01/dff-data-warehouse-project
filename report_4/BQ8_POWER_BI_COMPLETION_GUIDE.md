# BQ8 Power BI Completion Guide

## Purpose

Use this guide to complete only the Power BI part of Report 4:

- BQ8: Which stores fall into the top 25%, middle 50%, and bottom 25% of total Toothpaste revenue, and how do their demographics differ?
- Tool: Power BI Desktop
- Required screenshots:
  - `report_4/screenshots/screenshot_39.png`
  - `report_4/screenshots/screenshot_40.png`
  - `report_4/screenshots/screenshot_41.png`
- Power BI file to save:
  - `report_4/DFF_BQ8_Dashboard.pbix`

This guide does not change the existing BI completion sequence. It only replaces the Power BI instructions for BQ8.

---

## What This Builds

You will build:

1. A Power BI model view showing the warehouse star schema.
2. A BQ8 dashboard page with:
   - revenue by quartile tier
   - store demographic comparison
   - store-level detail table
   - category filter showing Toothpaste (`TPA`)
3. A BQ8 map page with:
   - store ZIP/city map
   - bubble size by Toothpaste revenue
   - color by quartile tier
   - summary cards

Important: use the SQL summary query in this guide for the dashboard. It matches the Report 4 BQ8 SQL logic and avoids fragile DAX quartile calculations.

---

## Step 0 - Confirm The Data Mart Is Ready

Run this in SSMS before opening Power BI:

```sql
USE team1_dw_area;

SELECT 'FactWeeklySales' AS table_name, COUNT(*) AS row_count FROM dbo.FactWeeklySales
UNION ALL SELECT 'DimStore', COUNT(*) FROM dbo.DimStore
UNION ALL SELECT 'DimCategory', COUNT(*) FROM dbo.DimCategory
UNION ALL SELECT 'DimProduct', COUNT(*) FROM dbo.DimProduct
UNION ALL SELECT 'DimTime', COUNT(*) FROM dbo.DimTime
UNION ALL SELECT 'DimPromotion', COUNT(*) FROM dbo.DimPromotion;
```

Expected checks:

| Table | Expected result |
|:--|:--|
| FactWeeklySales | `11,976,442` rows |
| DimStore | `107` rows |
| DimCategory | `28` rows |
| DimProduct | `3,127` rows |
| DimTime | about `400` rows |
| DimPromotion | `4` rows |

Then confirm BQ8 returns results:

```sql
USE team1_dw_area;

WITH store_revenue AS (
    SELECT
        f.store_key,
        SUM(f.revenue) AS total_revenue
    FROM dbo.FactWeeklySales f
    INNER JOIN dbo.DimCategory dc
        ON f.category_key = dc.category_key
    WHERE dc.category_code = 'TPA'
    GROUP BY f.store_key
),
store_quartiles AS (
    SELECT
        sr.store_key,
        sr.total_revenue,
        NTILE(4) OVER (ORDER BY sr.total_revenue) AS revenue_quartile
    FROM store_revenue sr
)
SELECT
    CASE
        WHEN sq.revenue_quartile = 1 THEN 'Bottom 25%'
        WHEN sq.revenue_quartile IN (2, 3) THEN 'Middle 50%'
        WHEN sq.revenue_quartile = 4 THEN 'Top 25%'
    END AS tier,
    COUNT(*) AS store_count,
    CAST(AVG(sq.total_revenue) AS DECIMAL(12,2)) AS avg_revenue,
    CAST(AVG(ds.avg_income) AS DECIMAL(10,2)) AS avg_income,
    CAST(AVG(ds.population_density) AS DECIMAL(10,2)) AS avg_pop_density,
    SUM(ds.is_urban) AS urban_store_count
FROM store_quartiles sq
INNER JOIN dbo.DimStore ds
    ON sq.store_key = ds.store_key
GROUP BY
    CASE
        WHEN sq.revenue_quartile = 1 THEN 'Bottom 25%'
        WHEN sq.revenue_quartile IN (2, 3) THEN 'Middle 50%'
        WHEN sq.revenue_quartile = 4 THEN 'Top 25%'
    END
ORDER BY avg_revenue DESC;
```

This should return 3 rows: Top 25%, Middle 50%, and Bottom 25%.

---

## Step 1 - Create The Power BI File

1. Open Power BI Desktop.
2. Click `Blank report`.
3. Save immediately as:

```text
report_4/DFF_BQ8_Dashboard.pbix
```

If you are working on a Windows lab machine, save it locally first, then copy it into the project folder later.

---

## Step 2 - Load The Star Schema Tables

These tables are needed for screenshot 39 and to prove the Power BI model uses the data mart.

1. Click `Home` -> `Get data` -> `SQL Server`.
2. Enter:
   - Server: `ISTM637-PC\SQLEXPRESS`
   - Database: `team1_dw_area`
3. Data connectivity mode:
   - Use `Import` if the machine can handle the load.
   - Use `DirectQuery` if import is too slow.
4. Click `OK`.
5. In the Navigator, select:
   - `DimCategory`
   - `DimPromotion`
   - `DimTime`
   - `DimStore`
   - `DimProduct`
   - `FactWeeklySales`
6. Click `Load`.

If `FactWeeklySales` takes too long to load, cancel and reconnect using `DirectQuery`. The screenshot and report can still show the star schema relationships.

---

## Step 3 - Verify Model Relationships

1. Click the `Model view` icon on the left side.
2. Arrange `FactWeeklySales` in the center.
3. Place the dimensions around it.
4. Confirm these relationships:

| From dimension | To fact table | Cardinality | Cross-filter |
|:--|:--|:--|:--|
| `DimStore[store_key]` | `FactWeeklySales[store_key]` | One-to-many | Single |
| `DimCategory[category_key]` | `FactWeeklySales[category_key]` | One-to-many | Single |
| `DimPromotion[promotion_key]` | `FactWeeklySales[promotion_key]` | One-to-many | Single |
| `DimTime[time_key]` | `FactWeeklySales[time_key]` | One-to-many | Single |
| `DimProduct[product_key]` | `FactWeeklySales[product_key]` | One-to-many | Single |

If a relationship is missing:

1. Drag the dimension key onto the matching fact key.
2. Set cardinality to `One-to-many`.
3. Set cross-filter direction to `Single`.
4. Keep the relationship active.

Do not create relationships between dimension tables.

---

## Step 4 - Take Screenshot 39

Screenshot 39 must prove the star schema is loaded in Power BI.

1. Stay in `Model view`.
2. Make sure all six tables are visible:
   - `FactWeeklySales`
   - `DimStore`
   - `DimCategory`
   - `DimPromotion`
   - `DimTime`
   - `DimProduct`
3. Make sure relationship lines are visible.
4. Keep the Fields/Data pane visible on the right if possible.
5. Capture the full Power BI window.
6. Save as:

```text
report_4/screenshots/screenshot_39.png
```

---

## Step 5 - Add The BQ8 Store Quartile Summary Table

This table is the safest source for the dashboard because it uses SQL Server's `NTILE(4)` logic, matching the Report 4 SQL.

1. In Power BI, click `Home` -> `Get data` -> `SQL Server`.
2. Use the same server and database:
   - Server: `ISTM637-PC\SQLEXPRESS`
   - Database: `team1_dw_area`
3. Expand `Advanced options`.
4. Paste this SQL statement:

```sql
WITH store_revenue AS (
    SELECT
        f.store_key,
        SUM(f.revenue) AS total_revenue
    FROM dbo.FactWeeklySales f
    INNER JOIN dbo.DimCategory dc
        ON f.category_key = dc.category_key
    WHERE dc.category_code = 'TPA'
    GROUP BY f.store_key
),
store_quartiles AS (
    SELECT
        sr.store_key,
        sr.total_revenue,
        NTILE(4) OVER (ORDER BY sr.total_revenue) AS revenue_quartile
    FROM store_revenue sr
)
SELECT
    ds.store_key,
    ds.store_id,
    ds.store_name,
    COALESCE(NULLIF(ds.city, ''), 'Chicago') AS city,
    ds.zip_code,
    ds.zone,
    ds.price_tier,
    ds.is_urban,
    ds.avg_income,
    ds.education_pct,
    ds.poverty_pct,
    ds.avg_household_size,
    ds.ethnic_diversity,
    ds.population_density,
    ds.age_under_9_pct,
    ds.age_over_60_pct,
    ds.working_women_pct,
    CAST(sq.total_revenue AS DECIMAL(12,2)) AS total_tpa_revenue,
    sq.revenue_quartile,
    CASE
        WHEN sq.revenue_quartile = 1 THEN 'Bottom 25%'
        WHEN sq.revenue_quartile IN (2, 3) THEN 'Middle 50%'
        WHEN sq.revenue_quartile = 4 THEN 'Top 25%'
    END AS revenue_tier,
    CASE
        WHEN sq.revenue_quartile = 1 THEN 1
        WHEN sq.revenue_quartile IN (2, 3) THEN 2
        WHEN sq.revenue_quartile = 4 THEN 3
    END AS revenue_tier_sort,
    CAST('TPA' AS VARCHAR(3)) AS category_code
FROM store_quartiles sq
INNER JOIN dbo.DimStore ds
    ON sq.store_key = ds.store_key
ORDER BY sq.total_revenue DESC;
```

5. Click `OK`.
6. When the preview opens, click `Transform Data`.
7. Rename the query to:

```text
BQ8_StoreQuartiles
```

8. Confirm or set these data types:

| Column | Type |
|:--|:--|
| `store_key`, `store_id`, `zone`, `revenue_quartile`, `revenue_tier_sort` | Whole number |
| `store_name`, `city`, `zip_code`, `price_tier`, `revenue_tier`, `category_code` | Text |
| `is_urban` | True/False |
| `total_tpa_revenue`, `avg_income`, demographic percent fields | Decimal number |

9. Click `Close & Apply`.

---

## Step 6 - Set Sort And Data Categories

Do this before building visuals.

1. In Data view, select table `BQ8_StoreQuartiles`.
2. Select column `revenue_tier`.
3. Click `Column tools` -> `Sort by column` -> `revenue_tier_sort`.
4. Select column `zip_code`.
5. Click `Column tools` -> `Data category` -> `Postal code`.
6. Select column `city`.
7. Click `Column tools` -> `Data category` -> `City`.
8. Select column `total_tpa_revenue`.
9. Set format to Currency or Decimal with comma separators.

---

## Step 7 - Create The Measures

In the `BQ8_StoreQuartiles` table, create these measures.

Click `Table tools` or `Modeling` -> `New measure`.

```dax
Total TPA Revenue =
SUM(BQ8_StoreQuartiles[total_tpa_revenue])
```

```dax
Total Stores =
DISTINCTCOUNT(BQ8_StoreQuartiles[store_id])
```

```dax
Average Store Income =
AVERAGE(BQ8_StoreQuartiles[avg_income])
```

```dax
Average Population Density =
AVERAGE(BQ8_StoreQuartiles[population_density])
```

Optional measure for the dashboard:

```dax
Urban Stores =
CALCULATE(
    DISTINCTCOUNT(BQ8_StoreQuartiles[store_id]),
    BQ8_StoreQuartiles[is_urban] = TRUE()
)
```

---

## Step 8 - Build Page 1: BQ8 Dashboard

1. Go to `Report view`.
2. Rename Page 1 to:

```text
BQ8 Dashboard
```

3. Add a title text box:

```text
BQ8: Store Quartile Analysis by Toothpaste Revenue
```

4. Add a smaller subtitle:

```text
Category filter: Toothpaste (TPA) | Grain: one row per store
```

### Add Summary Cards

Add three Card visuals:

| Card | Field |
|:--|:--|
| Total TPA Revenue | `[Total TPA Revenue]` |
| Total Stores | `[Total Stores]` |
| Average Store Income | `[Average Store Income]` |

### Add Revenue By Tier Bar Chart

Use a clustered bar chart or clustered column chart. The goal is to show total Toothpaste revenue grouped into the three BQ8 tiers: Top 25%, Middle 50%, and Bottom 25%.

#### Create the visual

1. Make sure you are on the `BQ8 Dashboard` report page.
2. Click a blank area of the canvas so no existing visual is selected.
3. In the `Visualizations` pane, click `Clustered bar chart`.
   - If you prefer vertical bars, use `Clustered column chart`.
   - Clustered bar is usually easier because the tier labels are readable.
4. Resize the visual so it takes the left or upper-middle part of the dashboard.
5. With the chart still selected, drag these fields into the visual wells:

| Visual well | Field |
|:--|:--|
| Axis | `BQ8_StoreQuartiles[revenue_tier]` |
| Values | `[Total TPA Revenue]` |
| Tooltips | `[Total Stores]`, `[Average Store Income]`, `[Average Population Density]` |

If Power BI shows `Sum of total_tpa_revenue` instead of the measure, remove it and use the measure named `[Total TPA Revenue]`.

#### Sort the tiers correctly

1. Click the bar chart.
2. Click the `...` menu in the top-right corner of the visual.
3. Select `Sort axis`.
4. Choose `revenue_tier`.
5. Choose `Ascending`.
6. If the order still looks wrong, go back to Data view and confirm:
   - `revenue_tier` is sorted by `revenue_tier_sort`
   - `revenue_tier_sort` values are Bottom 25% = 1, Middle 50% = 2, Top 25% = 3

For the report screenshot, an acceptable order is Bottom 25%, Middle 50%, Top 25%, because the bar lengths clearly show which group has the most revenue.

#### Set the chart title

1. Select the chart.
2. In the `Visualizations` pane, click `Format visual`.
3. Expand `General`.
4. Expand `Title`.
5. Turn `Title` on.
6. Set the title text to:

```text
Total Toothpaste Revenue by Store Tier
```

7. Set title alignment to `Center`.
8. Use a readable font size, around 12-14.

#### Set data labels

1. With the chart selected, open `Format visual`.
2. Expand `Visual`.
3. Turn `Data labels` on.
4. Set Display units to `Auto` or `Millions`, depending on what looks cleaner.
5. Set decimal places to `0` or `1`.

This makes the revenue difference visible in the screenshot.

#### Set colors by tier

1. Select the chart.
2. Open `Format visual`.
3. Expand `Visual`.
4. Expand `Bars` or `Columns`.
5. Turn on `Show all` if Power BI gives that option under colors.
6. Set colors manually if available:
   - `Top 25%`: green
   - `Middle 50%`: blue
   - `Bottom 25%`: red

If Power BI does not let you assign colors per tier from that menu:

1. Add `BQ8_StoreQuartiles[revenue_tier]` to the chart `Legend` well.
2. Go back to `Format visual` -> `Visual` -> `Bars/Columns` -> `Colors`.
3. Set the legend colors there.

If color assignment is still not available, leave the default colors. The screenshot is still acceptable as long as the tier labels and revenue values are clear.

#### Final check for this visual

- The visual title says `Total Toothpaste Revenue by Store Tier`.
- The axis uses `revenue_tier`.
- The values use `[Total TPA Revenue]`.
- Tooltips include store count, average income, and population density.
- The page filter still shows `category_code = TPA`.
- The bars show three groups: Top 25%, Middle 50%, Bottom 25%.

### Add Demographic Comparison Chart

Use a clustered column chart.

| Visual well | Field |
|:--|:--|
| Axis | `BQ8_StoreQuartiles[revenue_tier]` |
| Values | `Average Store Income`, `Average Population Density` |

Format:

- Title: `Demographic Comparison by Revenue Tier`
- Sort by `revenue_tier_sort`

### Add Store Detail Table

Use a Table visual with these fields:

- `store_id`
- `store_name`
- `city`
- `zip_code`
- `zone`
- `price_tier`
- `is_urban`
- `avg_income`
- `population_density`
- `total_tpa_revenue`
- `revenue_tier`

Sort the table by `total_tpa_revenue` descending.

### Add Filters/Slicers

Add slicers for:

- `price_tier`
- `zone`
- `is_urban`

In the Filters pane, drag `category_code` into `Filters on this page` and select only `TPA`.

This is important because screenshot 40 should clearly show the dashboard is filtered to Toothpaste.

---

## Step 9 - Take Screenshot 40

Screenshot 40 must show the BQ8 dashboard page.

Before capturing, verify:

- Page name is `BQ8 Dashboard`.
- Title says `BQ8: Store Quartile Analysis by Toothpaste Revenue`.
- Cards are visible.
- Revenue-by-tier chart is visible.
- Demographic comparison or store detail table is visible.
- Filters pane shows `category_code is TPA`.
- Fields/Data pane is visible if possible.

Save as:

```text
report_4/screenshots/screenshot_40.png
```

---

## Step 10 - Build Page 2: BQ8 Map

1. Add a new report page.
2. Rename it:

```text
BQ8 Map
```

3. Add a title:

```text
BQ8: Toothpaste Revenue Tier Map
```

4. Add a Map visual.

Use these fields:

| Visual well | Field |
|:--|:--|
| Location | `zip_code` |
| Legend | `revenue_tier` |
| Bubble size | `total_tpa_revenue` |
| Tooltips | `store_name`, `store_id`, `city`, `zone`, `price_tier`, `avg_income`, `population_density` |

5. Add two Card visuals:

| Card | Field |
|:--|:--|
| Total TPA Revenue | `[Total TPA Revenue]` |
| Total Stores | `[Total Stores]` |

6. Add slicers:

- `revenue_tier`
- `price_tier`

7. In the Filters pane, drag `category_code` into `Filters on this page` and select only `TPA`.

If the map is blank:

1. Confirm `zip_code` data category is `Postal code`.
2. Try using `city` as Location and `zip_code` as Tooltip.
3. Check `File` -> `Options and settings` -> `Options` -> `Security`; map visuals may need to be enabled.
4. If the lab blocks map services, keep the page layout but replace the map with a table grouped by ZIP and tier. Add a note in the screenshot caption later only if necessary.

---

## Step 11 - Take Screenshot 41

Screenshot 41 must show the BQ8 map page.

Before capturing, verify:

- Page name is `BQ8 Map`.
- Map or location-based visual is visible.
- Store bubbles or ZIP-level locations are visible.
- Bubble size represents `total_tpa_revenue`.
- Legend represents `revenue_tier`.
- Cards are visible.
- Filters pane shows `category_code is TPA`.

Save as:

```text
report_4/screenshots/screenshot_41.png
```

---

## Step 12 - Save And Regenerate The Report

1. Save the Power BI file:

```text
report_4/DFF_BQ8_Dashboard.pbix
```

2. Confirm these files exist:

```text
report_4/screenshots/screenshot_39.png
report_4/screenshots/screenshot_40.png
report_4/screenshots/screenshot_41.png
```

3. Regenerate the Word report:

```bash
cd "/Users/bhavikdalal/Documents/data warehouse/project/report_4"
python3 generate_docx.py
```

When prompted about missing screenshots, answer `y` only if screenshots 30-38 are still incomplete. If screenshots 39-41 exist with exact names, the generator should embed them automatically.

---

## Final BQ8 QA Checklist

Before submitting, confirm:

- [ ] `DFF_BQ8_Dashboard.pbix` is saved.
- [ ] Screenshot 39 shows Power BI Model view with `FactWeeklySales` connected to all five dimensions.
- [ ] Screenshot 40 shows the BQ8 dashboard with Toothpaste revenue quartiles.
- [ ] Screenshot 40 shows `category_code = TPA` in the Filters pane.
- [ ] Screenshot 40 includes demographic fields such as income, population density, urban flag, education, or poverty.
- [ ] Screenshot 41 shows the BQ8 map/location page.
- [ ] Screenshot 41 uses `revenue_tier` as the color/legend.
- [ ] Screenshot 41 uses `total_tpa_revenue` as bubble size or location metric.
- [ ] The screenshots are saved as PNG files with exact names `screenshot_39.png`, `screenshot_40.png`, and `screenshot_41.png`.
- [ ] `Integrated_Report_4.docx` has been regenerated after placing screenshots in the folder.

---

## Common Mistakes To Avoid

- Do not use the old `14,921,365` fact row count. The verified Report 4 count is `11,976,442`.
- Do not build quartiles manually by guessing. Use the SQL `NTILE(4)` query in this guide.
- Do not use all-category revenue. BQ8 is Toothpaste only, so the query must filter `category_code = 'TPA'`.
- Do not screenshot Power BI before the visuals show real data.
- Do not rename screenshots. The generator only replaces placeholders when the files are named exactly.
- Do not claim the dashboard is complete if screenshots 39-41 are still placeholders in the Word report.
