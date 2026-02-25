# Top 10 OLAP Business Questions — Dominick's Fine Foods

> 10 curated business questions selected from the full pool of 25 questions (15 from main analysis + 10 from Yifei), chosen for **strategic value**, **data feasibility**, and **OLAP operation diversity**. Organized by difficulty: 3 Easy, 4 Medium, 3 Hard.

---

## File Reference — Exact Paths in Your Local `DFF data - zipped` Folder

| File | Path |
|------|------|
| **Soft Drinks Movement** | `Movement/WSDR/wsdr.csv` |
| **Canned Soup Movement** | `Movement/WCSO/WCSO-Done.csv` |
| **Frozen Entrees Movement** | `Movement/WFRE/WFRE-Done.csv` |
| **Cereals Movement** | `Movement/backup-Movement/DONE-WCER.csv` |
| **Beer Movement** | `Movement/backup-Movement/DONE-WBER.csv` |
| **Toothpaste Movement** | `Movement/WTPA/WTPA_done.csv` |
| **Crackers Movement** | `Movement/WCRA/Done-WCRA.csv` |
| **Cigarettes Movement** | `Movement/WCIG/Done-WCIG.csv` |
| **Cheeses Movement** | `Movement/WCHE/Done-WCHE.csv` |
| **Cookies Movement** | `Movement/WCOO/DONE-WCOO.csv` |
| **Bottled Juices Movement** | `Movement/WBJC/DONE-WBJC.csv` |
| **Laundry Detergents Movement** | `Movement/WLND/wlnd.csv` |
| **Demographics** | `Demographics/DEMO.csv` |
| **UPC — Cereals** | `UPC/UPCCER.csv` |
| **UPC — Beer** | `UPC/UPCBER.csv` |
| **UPC — Crackers** | `UPC/UPCCRA.csv` |
| **UPC — Soft Drinks** | `UPC/UPCSDR.csv` |
| **Customer Count** | `Ccount/CCOUNT.csv` |

---

## 🟢 EASY (3 Questions)

*Straightforward aggregation across 1–2 dimensions. Single measure, simple GROUP BY, no window functions.*

---

### E1. What were the total units sold per product category across the entire dataset period?

*(Source: Main Q3)*

| Item | Detail |
|------|--------|
| **Files Needed** | All 24 Movement CSV files (one per category) |
| **Columns** | `MOVE`, `OK` |
| **Feasibility** | ✅ Sum `MOVE` per file, aggregate by category. All data available. |
| **OLAP Operation** | **Roll-up** (aggregate all dimensions up to category) |
| **Business Value** | Category management foundation — determines shelf space allocation and supply chain priorities. |

```sql
SELECT category_code,
       SUM(MOVE) AS total_units_sold
FROM   FactWeeklySales
WHERE  OK = 1
GROUP BY category_code
ORDER BY total_units_sold DESC;
```

#### 📊 Excel Pivot Table Instructions

| Setting | Value |
|---------|-------|
| **Data Source** | Open each Movement CSV individually (e.g., `WSDR/wsdr.csv`, `WCSO/WCSO-Done.csv`, etc.) |
| **Prep Step** | Add a column `Category` to each file with its category name before combining (e.g., "Soft Drinks", "Canned Soup") |
| **Rows** | `Category` (the column you added) |
| **Values** | Sum of `MOVE` |
| **Filters** | `OK = 1` |
| **Chart Type** | Horizontal bar chart, sorted descending by total units |

> **Tip:** You can do this one file at a time. Open each CSV → filter `OK = 1` → use `=SUM(MOVE column)` → record the total in a summary table.

---

### E2. What were the total weekly unit sales of Soft Drinks across all stores for each week?

*(Source: Main Q1)*

| Item | Detail |
|------|--------|
| **File** | 📁 `Movement/WSDR/wsdr.csv` |
| **Columns** | `WEEK`, `MOVE`, `OK` |
| **Feasibility** | ✅ 17.7M rows. |
| **OLAP Operation** | **Roll-up** (aggregate UPC and STORE up to weekly total) |

```sql
SELECT WEEK,
       SUM(MOVE) AS total_units_sold
FROM   FactWeeklySales
WHERE  category_code = 'SDR'
  AND  OK = 1
GROUP BY WEEK
ORDER BY WEEK;
```

#### 📊 Excel Pivot Table Instructions

| Setting | Value |
|---------|-------|
| **Data Source** | `Movement/WSDR/wsdr.csv` |
| **Rows** | `WEEK` |
| **Values** | Sum of `MOVE` |
| **Filters** | `OK = 1` |
| **Chart Type** | Line chart — `WEEK` on X-axis, Total Units on Y-axis |
| **Insight to look for** | Seasonal spikes (summer) and promotional bumps |

---

### E3. How do promotion weeks compare to non-promotion weeks in terms of sales volume?

*(Source: Yifei Q3)*

| Item | Detail |
|------|--------|
| **File** | 📁 `Movement/WSDR/wsdr.csv` (or any Movement file) |
| **Columns** | `SALE`, `MOVE`, `OK` |
| **Feasibility** | ✅ `SALE` = B (Bonus Buy), C (Coupon), S (Sale), or blank (no promo). |
| **OLAP Operation** | **Slice** (fix dimension by promotion status, aggregate sales) |

```sql
SELECT CASE WHEN SALE IS NOT NULL THEN 'Promoted' ELSE 'Not Promoted' END AS promo_status,
       AVG(MOVE)   AS avg_units_sold,
       SUM(MOVE)   AS total_units_sold,
       COUNT(*)    AS num_observations
FROM   FactWeeklySales
WHERE  OK = 1
GROUP BY promo_status
ORDER BY avg_units_sold DESC;
```

#### 📊 Excel Pivot Table Instructions

| Setting | Value |
|---------|-------|
| **Data Source** | `Movement/WSDR/wsdr.csv` |
| **Prep Step** | Add a helper column: `Promo_Status` = `IF(SALE="", "Not Promoted", "Promoted")` |
| **Rows** | `Promo_Status` (or `SALE` directly — blanks = no promo, B/C/S = promoted) |
| **Values** | (1) Average of `MOVE`   (2) Sum of `MOVE`   (3) Count of `MOVE` |
| **Filters** | `OK = 1` |
| **Chart Type** | Clustered bar chart — two bars (Promoted vs Not Promoted) |
| **Insight to look for** | Compare the Average of MOVE between promoted vs non-promoted rows |

---

## 🟡 MEDIUM (4 Questions)

*Cross-dimensional comparisons, time-series trends, conditional aggregations requiring joins or subqueries.*

---

### M1. Which promotion type (B = Bonus Buy, C = Coupon, S = Sale) generated the highest incremental unit sales lift in the Canned Soup category?

*(Source: Main Q6)*

| Item | Detail |
|------|--------|
| **File** | 📁 `Movement/WCSO/WCSO-Done.csv` |
| **Columns** | `UPC`, `STORE`, `WEEK`, `MOVE`, `SALE`, `OK` |
| **Feasibility** | ✅ ~10% of rows have deal flags. |
| **OLAP Operation** | **Dice** (filter by category + promotion type, compare measures) |

```sql
SELECT SALE AS promotion_type,
       AVG(MOVE)  AS avg_units_promoted,
       (SELECT AVG(MOVE) FROM FactWeeklySales
        WHERE category_code = 'CSO' AND SALE IS NULL AND OK = 1) AS avg_units_baseline,
       AVG(MOVE) - (SELECT AVG(MOVE) FROM FactWeeklySales
                     WHERE category_code = 'CSO' AND SALE IS NULL AND OK = 1) AS sales_lift
FROM   FactWeeklySales
WHERE  category_code = 'CSO'
  AND  SALE IS NOT NULL
  AND  OK = 1
GROUP BY SALE
ORDER BY sales_lift DESC;
```

#### 📊 Excel Pivot Table Instructions

| Setting | Value |
|---------|-------|
| **Data Source** | `Movement/WCSO/WCSO-Done.csv` |
| **Rows** | `SALE` (shows B, C, S, and blank — leave blanks labeled as "No Promo / Baseline") |
| **Values** | (1) Average of `MOVE`   (2) Count of `MOVE` |
| **Filters** | `OK = 1` |
| **Chart Type** | Clustered bar chart |
| **Post-Calculation** | Divide each SALE group's average by the blank (No Promo) average → that's the "Lift" (e.g., 9.4× for Sale) |

---

### M2. How did quarterly revenue for Frozen Entrees differ between urban and suburban stores?

*(Source: Main Q7)*

| Item | Detail |
|------|--------|
| **Files** | 📁 `Movement/WFRE/WFRE-Done.csv` + 📁 `Demographics/DEMO.csv` |
| **Columns** | Movement: `STORE`, `WEEK`, `MOVE`, `PRICE`, `QTY`, `OK`;  DEMO: `STORE`, `URBAN` |
| **Feasibility** | ✅ Join on `STORE`. `URBAN` = 1 (urban) or 0 (suburban). |
| **OLAP Operation** | **Drill-down** (from total → by urban/suburban, by quarter) |

```sql
SELECT d.URBAN,
       (f.WEEK / 13) AS quarter_id,
       SUM(f.MOVE * (f.PRICE / f.QTY)) AS quarterly_revenue
FROM   FactWeeklySales f
JOIN   DimStore d ON f.store_id = d.store_id
WHERE  f.category_code = 'FRE'
  AND  f.OK = 1
GROUP BY d.URBAN, quarter_id
ORDER BY quarter_id, d.URBAN;
```

#### 📊 Excel Pivot Table Instructions

| Setting | Value |
|---------|-------|
| **Data Source** | `Movement/WFRE/WFRE-Done.csv` |
| **Prep Step 1** | Add a computed column: `Revenue = MOVE * (PRICE / QTY)` |
| **Prep Step 2** | Add a computed column: `Quarter = INT(WEEK / 13)` |
| **Prep Step 3** | Use VLOOKUP on `STORE` to bring in `URBAN` from `Demographics/DEMO.csv` |
| **Rows** | `Quarter` (the computed column) |
| **Columns** | `URBAN` (0 = Suburban, 1 = Urban) |
| **Values** | Sum of `Revenue` |
| **Filters** | `OK = 1`, `PRICE > 0`, `QTY > 0` |
| **Chart Type** | Clustered bar chart — Quarter on X-axis, two bars per quarter (Urban / Suburban) |

---

### M3. How has the monthly market share (% of total units sold) of the top 5 Cereal brands changed over time?

*(Source: Main Q9)*

| Item | Detail |
|------|--------|
| **Files** | 📁 `Movement/backup-Movement/DONE-WCER.csv` + 📁 `UPC/UPCCER.csv` |
| **Columns** | Movement: `UPC`, `WEEK`, `MOVE`, `OK`;  UPC: `UPC`, `COM_CODE`, `DESCRIP` |
| **Feasibility** | ✅ `COM_CODE` serves as brand/manufacturer proxy. |
| **OLAP Operation** | **Pivot + Ratio-to-Total** (brand share across time periods) |

```sql
WITH brand_total AS (
    SELECT u.COM_CODE,
           (f.WEEK / 4) AS month_id,
           SUM(f.MOVE)  AS brand_units
    FROM   FactWeeklySales f
    JOIN   DimProduct u ON f.upc = u.upc
    WHERE  f.category_code = 'CER' AND f.OK = 1
    GROUP BY u.COM_CODE, month_id
),
top_brands AS (
    SELECT COM_CODE FROM brand_total
    GROUP BY COM_CODE
    ORDER BY SUM(brand_units) DESC
    LIMIT 5
),
monthly_total AS (
    SELECT month_id, SUM(brand_units) AS total_units
    FROM   brand_total
    GROUP BY month_id
)
SELECT bt.COM_CODE,
       bt.month_id,
       bt.brand_units,
       ROUND(100.0 * bt.brand_units / mt.total_units, 2) AS market_share_pct
FROM   brand_total bt
JOIN   monthly_total mt ON bt.month_id = mt.month_id
WHERE  bt.COM_CODE IN (SELECT COM_CODE FROM top_brands)
ORDER BY bt.month_id, market_share_pct DESC;
```

#### 📊 Excel Pivot Table Instructions

| Setting | Value |
|---------|-------|
| **Data Source** | `Movement/backup-Movement/DONE-WCER.csv` |
| **Prep Step 1** | VLOOKUP on `UPC` to bring in `COM_CODE` and `DESCRIP` from `UPC/UPCCER.csv` |
| **Prep Step 2** | Add a computed column: `Month = INT(WEEK / 4)` |
| **Rows** | `COM_CODE` (brand/manufacturer proxy) |
| **Columns** | `Month` (the computed column) |
| **Values** | Sum of `MOVE` |
| **Filters** | `OK = 1` |
| **Show Values As** | Right-click Values → "Show Values As" → **% of Column Total** (this gives market share) |
| **Chart Type** | Stacked area chart — shows how each brand's share evolves over months |
| **Post-Step** | Identify top 5 `COM_CODE` by total volume, filter pivot to show only those 5 |

---

### M4. Which 10 individual products (UPCs) in the Beer category had the largest price variance across stores in the same week?

*(Source: Main Q10)*

| Item | Detail |
|------|--------|
| **Files** | 📁 `Movement/backup-Movement/DONE-WBER.csv` + 📁 `UPC/UPCBER.csv` |
| **Columns** | Movement: `UPC`, `STORE`, `WEEK`, `PRICE`, `QTY`, `OK`;  UPC: `UPC`, `DESCRIP` |
| **Feasibility** | ✅ Compute unit price = `PRICE / QTY`. |
| **OLAP Operation** | **Dice + Ranking** (filter to Beer, rank by price variance) |

```sql
SELECT f.UPC,
       p.DESCRIP,
       f.WEEK,
       VARIANCE(f.PRICE / f.QTY) AS price_variance,
       MAX(f.PRICE / f.QTY) - MIN(f.PRICE / f.QTY) AS price_spread
FROM   FactWeeklySales f
JOIN   DimProduct p ON f.upc = p.upc
WHERE  f.category_code = 'BER'
  AND  f.OK = 1
  AND  f.PRICE > 0
GROUP BY f.UPC, p.DESCRIP, f.WEEK
HAVING COUNT(DISTINCT f.STORE) >= 5
ORDER BY price_variance DESC
LIMIT 10;
```

#### 📊 Excel Pivot Table Instructions

| Setting | Value |
|---------|-------|
| **Data Source** | `Movement/backup-Movement/DONE-WBER.csv` |
| **Prep Step 1** | Add a computed column: `UnitPrice = PRICE / QTY` |
| **Prep Step 2** | VLOOKUP on `UPC` to bring in `DESCRIP` from `UPC/UPCBER.csv` |
| **Rows** | `UPC` + `DESCRIP` |
| **Columns** | `STORE` |
| **Values** | Average of `UnitPrice` |
| **Filters** | `OK = 1`, `PRICE > 0`, `QTY > 0` |
| **Post-Analysis** | Add computed columns outside the pivot: `=MAX(row) - MIN(row)` for price spread and `=STDEV(row)` for variance per UPC |
| **Chart Type** | Bar chart of top 10 UPCs by price spread |

---

## 🔴 HARD (3 Questions)

*Require RANK(), NTILE(), SUM() OVER(), LAG(), PERCENT_RANK(), or running total calculations.*

---

### H1. Which stores fall into the top 25%, middle 50%, and bottom 25% of total revenue for the Toothpaste category, and how do their demographics differ?

*(Source: Main Q13)*

| Item | Detail |
|------|--------|
| **Files** | 📁 `Movement/WTPA/WTPA_done.csv` + 📁 `Demographics/DEMO.csv` |
| **Columns** | Movement: `STORE`, `MOVE`, `PRICE`, `QTY`, `OK`;  DEMO: `STORE`, `INCOME`, `URBAN`, `DENSITY`, `ZONE` |
| **Feasibility** | ✅ Use NTILE/PERCENTILE for quartiles. |
| **OLAP Operation** | **Ranking (NTILE) + Drill-down** |

```sql
WITH store_revenue AS (
    SELECT STORE,
           SUM(MOVE * (PRICE / QTY)) AS total_revenue
    FROM   FactWeeklySales
    WHERE  category_code = 'TPA' AND OK = 1 AND PRICE > 0
    GROUP BY STORE
),
quartiles AS (
    SELECT STORE, total_revenue,
           NTILE(4) OVER (ORDER BY total_revenue) AS revenue_quartile
    FROM   store_revenue
)
SELECT CASE WHEN q.revenue_quartile = 1 THEN 'Bottom 25%'
            WHEN q.revenue_quartile IN (2,3) THEN 'Middle 50%'
            ELSE 'Top 25%' END AS tier,
       COUNT(*) AS store_count,
       AVG(q.total_revenue) AS avg_revenue,
       AVG(CAST(d.INCOME AS FLOAT)) AS avg_income,
       AVG(CAST(d.DENSITY AS FLOAT)) AS avg_density,
       SUM(CAST(d.URBAN AS INT)) AS urban_store_count
FROM   quartiles q
JOIN   DimStore d ON q.STORE = d.store_id
GROUP BY tier
ORDER BY avg_revenue DESC;
```

#### 📊 Excel Pivot Table Instructions

| Setting | Value |
|---------|-------|
| **Data Source** | `Movement/WTPA/WTPA_done.csv` |
| **Step 1 — Revenue Pivot** | Rows = `STORE`, Values = Sum of `Revenue` (compute `MOVE × (PRICE / QTY)`). Sort descending. Filter `OK = 1`, `PRICE > 0`. |
| **Step 2 — Assign Quartiles** | Copy STORE + Revenue to a new sheet. Sort by Revenue. Add column `Quartile`: use `=IF(ROW()<=ROUND(COUNT*0.25,0), "Bottom 25%", IF(ROW()<=ROUND(COUNT*0.75,0), "Middle 50%", "Top 25%"))` or use `PERCENTILE` function. |
| **Step 3 — Add Demographics** | VLOOKUP on `STORE` to bring in `URBAN`, `INCOME`, `ZONE`, `DENSITY` from `Demographics/DEMO.csv` |
| **Step 4 — Summary Pivot** | Rows = `Quartile` (Bottom 25%, Middle 50%, Top 25%), Values = (1) Avg of Revenue, (2) Avg of INCOME, (3) Avg of DENSITY, (4) Sum of URBAN, (5) Count of STORE |
| **Chart Type** | Dual-axis chart — bars for average revenue, line overlay for % Urban |

---

### H2. For each week, rank the top 10 individual products (UPCs) in the Crackers category by unit sales, and show their week-over-week sales change.

*(Source: Main Q14)*

| Item | Detail |
|------|--------|
| **Files** | 📁 `Movement/WCRA/Done-WCRA.csv` + 📁 `UPC/UPCCRA.csv` |
| **Columns** | Movement: `UPC`, `WEEK`, `MOVE`, `OK`;  UPC: `UPC`, `DESCRIP` |
| **Feasibility** | ✅ 3.6M rows. |
| **OLAP Operation** | **Ranking (RANK) + LAG (Week-over-Week Change)** |

```sql
WITH weekly_product AS (
    SELECT f.UPC, p.DESCRIP, f.WEEK,
           SUM(f.MOVE) AS weekly_units,
           RANK() OVER (PARTITION BY f.WEEK ORDER BY SUM(f.MOVE) DESC) AS week_rank
    FROM   FactWeeklySales f
    JOIN   DimProduct p ON f.upc = p.upc
    WHERE  f.category_code = 'CRA' AND f.OK = 1
    GROUP BY f.UPC, p.DESCRIP, f.WEEK
)
SELECT UPC, DESCRIP, WEEK,
       weekly_units,
       week_rank,
       LAG(weekly_units) OVER (PARTITION BY UPC ORDER BY WEEK) AS prev_week_units,
       weekly_units - LAG(weekly_units) OVER (PARTITION BY UPC ORDER BY WEEK) AS wow_change
FROM   weekly_product
WHERE  week_rank <= 10
ORDER BY WEEK, week_rank;
```

#### 📊 Excel Pivot Table Instructions

| Setting | Value |
|---------|-------|
| **Data Source** | `Movement/WCRA/Done-WCRA.csv` |
| **Prep Step** | VLOOKUP on `UPC` to bring in `DESCRIP` from `UPC/UPCCRA.csv` |
| **Step 1 — Weekly Product Pivot** | Rows = `WEEK` + `UPC` + `DESCRIP`, Values = Sum of `MOVE`. Filter `OK = 1`. |
| **Step 2 — Rank** | Copy pivot output. For each WEEK group, add a `Rank` column: `=RANK(this_row_MOVE, MOVE_range_for_this_WEEK)` |
| **Step 3 — Filter Top 10** | Filter to Rank ≤ 10 |
| **Step 4 — WoW Change** | Sort by UPC then WEEK. Add `Prev_Week` column: `=INDEX(MOVE_col, MATCH(this_UPC & (this_WEEK-1), UPC_col & WEEK_col, 0))`. Add `WoW_Change = This_Week - Prev_Week`. |
| **Chart Type** | Table with conditional formatting (green ↑ = positive WoW, red ↓ = negative WoW) |

---

### H3. For each pricing zone, what is the percentile rank of each store's average weekly profit in the Cigarettes category, and how does it compare to the zone average?

*(Source: Main Q15)*

| Item | Detail |
|------|--------|
| **Files** | 📁 `Movement/WCIG/Done-WCIG.csv` + 📁 `Demographics/DEMO.csv` |
| **Columns** | Movement: `STORE`, `WEEK`, `PROFIT`, `OK`;  DEMO: `STORE`, `ZONE` |
| **Feasibility** | ✅ `ZONE` ranges 1–10 in DEMO. 5.4M rows. |
| **OLAP Operation** | **Percentile Ranking (PERCENT_RANK) + Drill-down by Zone** |

```sql
WITH store_avg AS (
    SELECT f.STORE,
           d.ZONE,
           AVG(f.PROFIT) AS avg_weekly_profit
    FROM   FactWeeklySales f
    JOIN   DimStore d ON f.store_id = d.store_id
    WHERE  f.category_code = 'CIG' AND f.OK = 1
    GROUP BY f.STORE, d.ZONE
)
SELECT STORE, ZONE,
       avg_weekly_profit,
       PERCENT_RANK() OVER (PARTITION BY ZONE ORDER BY avg_weekly_profit) AS pctile_rank,
       AVG(avg_weekly_profit) OVER (PARTITION BY ZONE) AS zone_avg_profit,
       avg_weekly_profit - AVG(avg_weekly_profit) OVER (PARTITION BY ZONE) AS vs_zone_avg
FROM   store_avg
ORDER BY ZONE, pctile_rank DESC;
```

#### 📊 Excel Pivot Table Instructions

| Setting | Value |
|---------|-------|
| **Data Source** | `Movement/WCIG/Done-WCIG.csv` |
| **Prep Step** | VLOOKUP on `STORE` to bring in `ZONE` from `Demographics/DEMO.csv` |
| **Step 1 — Store Avg Profit Pivot** | Rows = `ZONE` + `STORE`, Values = Average of `PROFIT`. Filter `OK = 1`. |
| **Step 2 — Copy & Compute Percentiles** | Copy pivot output. Within each ZONE group, add: `Percentile_Rank = PERCENTRANK.EXC(profit_range_for_this_zone, this_store_profit)` |
| **Step 3 — Zone Average** | Add `Zone_Avg = AVERAGEIF(ZONE_col, this_ZONE, Profit_col)` |
| **Step 4 — Difference** | Add `vs_Zone_Avg = this_store_profit - Zone_Avg` |
| **Chart Type** | Box plot per zone (Insert → Statistical Chart → Box and Whisker), or grouped bar chart with zone average as overlay line |

---

## Summary Matrix

| # | Question | Difficulty | OLAP Op | Data Source Files | Feasibility |
|---|----------|------------|---------|-------------------|-------------|
| **E1** | Total units by category | 🟢 Easy | Roll-up | All Movement CSVs | ✅ |
| **E2** | Weekly SDR unit sales trend | 🟢 Easy | Roll-up | `WSDR/wsdr.csv` | ✅ |
| **E3** | Promo vs non-promo sales | 🟢 Easy | Slice | `WSDR/wsdr.csv` | ✅ |
| **M1** | Promo lift by deal type | 🟡 Medium | Dice | `WCSO/WCSO-Done.csv` | ✅ |
| **M2** | Urban vs suburban revenue | 🟡 Medium | Drill-down | `WFRE/WFRE-Done.csv` + `DEMO.csv` | ✅ |
| **M3** | Brand market share over time | 🟡 Medium | Pivot + Ratio | `DONE-WCER.csv` + `UPCCER.csv` | ✅ |
| **M4** | Price variance (Beer) | 🟡 Medium | Dice + Rank | `DONE-WBER.csv` + `UPCBER.csv` | ✅ |
| **H1** | Store quartiles + demographics | 🔴 Hard | NTILE | `WTPA_done.csv` + `DEMO.csv` | ✅ |
| **H2** | Top 10 products + WoW change | 🔴 Hard | RANK + LAG | `Done-WCRA.csv` + `UPCCRA.csv` | ✅ |
| **H3** | Percentile rank by zone | 🔴 Hard | PERCENT_RANK | `Done-WCIG.csv` + `DEMO.csv` | ✅ |
