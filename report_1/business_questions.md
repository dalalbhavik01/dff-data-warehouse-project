# OLAP Business Questions — Dominick's Fine Foods

> 15 analytical business questions for DFF management, organized into 3 tiers of difficulty. Each question is designed for OLAP-style aggregation, slicing, and dicing across the store, product, time, category, and promotion dimensions.

---

## Subject Area Understanding — Retail Domain Research

Dominick's Finer Foods (DFF) was a major Chicago-area supermarket chain operating approximately 100 stores from the late 1980s through the mid-1990s. Between 1989 and 1994, the University of Chicago Booth School of Business (Kilts Center for Marketing) partnered with DFF to conduct extensive store-level research on shelf management and pricing, producing one of the most comprehensive publicly available retail scanner datasets (Kilts Center, 2013).

The following literature review identifies key retail problems relevant to DFF's operations and directly informs the business questions below:

### Key Research Findings

**1. Pricing Strategy and Zone Pricing.**
Hoch, Kim, Montgomery & Rossi (1995) demonstrated that DFF implemented a micro-marketing pricing strategy, segmenting its stores into high, medium, and low price zones based on local competitive conditions. Their analysis showed that optimizing zone-level pricing based on category-specific demand elasticities could increase profits by 3–5% without increasing average prices. This finding motivates our questions on cross-zone performance comparison (Q13, Q15).

**2. Promotion Effectiveness and Sales Lifts.**
Chevalier, Kashyap & Rossi (2003) used the DFF dataset to study promotional pricing effects, finding that retail margins decrease during peak demand periods (such as holidays) while sales volume increases substantially. Our statistical analysis confirms this: promotions boost Soft Drink sales by 13.6× and Canned Soup by 3.4× (see Data Exploration Summary, Section 8.2). This validates questions on promotional lift measurement (Q6) and customer traffic during promotions (Q8).

**3. Consumer Demand Patterns and Stockpiling.**
Pesendorfer (2002) analyzed cyclical pricing policies in the retail grocery sector and found that consumers strategically time purchases around promotional cycles. This stockpiling behavior explains why weekly sales MOVE values exhibit extreme variance (e.g., Soft Drinks: mean = 17.07, max = 4,637). Understanding these patterns is critical for DFF's inventory management, motivating time-series and running total questions (Q1, Q11, Q14).

**4. Brand Competition and Market Share Dynamics.**
Chintagunta (2002) studied competitive brand interactions in retail grocery categories using scanner data and found that promotional activity by one brand significantly impacts competitors' market share within the same category. This supports cross-brand market share analysis questions (Q9, Q10).

**5. Store Location, Demographics, and Performance.**
Montgomery (1997) showed that store-level demographic characteristics — income, household size, education — are strong predictors of demand elasticity and category sales performance. The DFF DEMO file contains these exact variables for 107 stores, enabling demographic segmentation analysis (Q7, Q13, Q15).

### Retail Domain Problems Relevant to DFF

Based on the literature, the following business challenges are most relevant for DFF:

| # | Problem | Relevance to DFF | Related BQs |
|---|---------|-----------------|-------------|
| 1 | **Promotion ROI measurement** — Which deal types drive incremental sales vs. just shifting demand? | DFF runs Bonus Buys (B), Coupons (C), and Sales (S) across 24 categories | Q6, Q8 |
| 2 | **Zone pricing optimization** — Are pricing zones correctly calibrated to competitive landscapes? | DFF uses 15 pricing zones across 107 stores | Q13, Q15 |
| 3 | **Category management** — Which categories deserve more shelf space and promotional investment? | DFF tracks 24+ categories with vastly different profit profiles | Q3, Q5, Q12 |
| 4 | **Trend detection and seasonality** — How do sales evolve over time and across seasons? | 5+ years of weekly data enables rich time-series analysis | Q1, Q9, Q11, Q14 |
| 5 | **Store performance benchmarking** — Which stores outperform/underperform relative to their demographic potential? | Demographics + sales data enables performance attribution | Q2, Q7, Q13 |

---

## TIER 1 — Easy OLAP Questions

*Straightforward aggregation across 1–2 dimensions. Single measure, one or two GROUP BY dimensions, no ranking or window functions needed.*

---

### Q1. What were the total weekly unit sales of Soft Drinks across all stores for each week in the dataset?

| Item | Detail |
|------|--------|
| **Files Needed** | `Movement/wsdr.csv` |
| **Columns** | `WEEK`, `MOVE` |
| **Feasibility** | ✅ Fully available. `MOVE` = units sold; `WEEK` = week identifier. 17.7M rows. |
| **OLAP Operation** | **Roll-up** (aggregate UPC and STORE up to the weekly total) |

```sql
SELECT WEEK,
       SUM(MOVE) AS total_units_sold
FROM   FactWeeklySales
WHERE  category_code = 'SDR'
  AND  OK = 1
GROUP BY WEEK
ORDER BY WEEK;
```

---

### Q2. What was the average weekly revenue per store for the Cereals category?

| Item | Detail |
|------|--------|
| **Files Needed** | `Movement/DONE-WCER.csv` |
| **Columns** | `STORE`, `WEEK`, `MOVE`, `PRICE`, `QTY` |
| **Feasibility** | ✅ Revenue can be computed as `MOVE × (PRICE / QTY)`. 6.6M rows. |
| **OLAP Operation** | **Roll-up** (aggregate to store level, then average across weeks) |

```sql
SELECT STORE,
       AVG(weekly_revenue) AS avg_weekly_revenue
FROM (
    SELECT STORE, WEEK,
           SUM(MOVE * (PRICE / QTY)) AS weekly_revenue
    FROM   FactWeeklySales
    WHERE  category_code = 'CER' AND OK = 1
    GROUP BY STORE, WEEK
) sub
GROUP BY STORE
ORDER BY avg_weekly_revenue DESC;
```

---

### Q3. What were the total units sold per product category across the entire dataset period?

| Item | Detail |
|------|--------|
| **Files Needed** | All 24 Movement files |
| **Columns** | `MOVE`, plus derived `category_code` (from filename) |
| **Feasibility** | ✅ Sum `MOVE` per file, then aggregate by category. All data available. |
| **OLAP Operation** | **Roll-up** (aggregate all dimensions up to category) |

```sql
SELECT category_code,
       SUM(MOVE) AS total_units_sold
FROM   FactWeeklySales
WHERE  OK = 1
GROUP BY category_code
ORDER BY total_units_sold DESC;
```

---

### Q4. How many distinct UPCs (products) were sold each week in the Cookies category?

| Item | Detail |
|------|--------|
| **Files Needed** | `Movement/DONE-WCOO.csv` |
| **Columns** | `WEEK`, `UPC`, `MOVE` |
| **Feasibility** | ✅ Count distinct UPCs where `MOVE > 0` per week. 13.4M rows. |
| **OLAP Operation** | **Slice** (fix category = Cookies, aggregate by week) |

```sql
SELECT WEEK,
       COUNT(DISTINCT UPC) AS active_products
FROM   FactWeeklySales
WHERE  category_code = 'COO'
  AND  MOVE > 0
  AND  OK = 1
GROUP BY WEEK
ORDER BY WEEK;
```

---

### Q5. What was the total gross profit by store for the Cheeses category over the full dataset period?

| Item | Detail |
|------|--------|
| **Files Needed** | `Movement/Done-WCHE.csv` |
| **Columns** | `STORE`, `PROFIT` |
| **Feasibility** | ✅ `PROFIT` column directly available. 9.4M rows. |
| **OLAP Operation** | **Roll-up** (aggregate weeks and UPCs up to store total) |

```sql
SELECT STORE,
       SUM(PROFIT) AS total_gross_profit
FROM   FactWeeklySales
WHERE  category_code = 'CHE'
  AND  OK = 1
GROUP BY STORE
ORDER BY total_gross_profit DESC;
```

---

## TIER 2 — Moderately Difficult OLAP Questions

*Cross-dimensional comparisons, time-series trends, and conditional aggregations requiring 2–3 table joins, GROUP BY + HAVING, or subqueries.*

---

### Q6. Which promotion type (B = Bonus Buy, C = Coupon, S = Sale) generated the highest incremental unit sales lift in the Canned Soup category?

| Item | Detail |
|------|--------|
| **Files Needed** | `Movement/WCSO-Done.csv` |
| **Columns** | `UPC`, `STORE`, `WEEK`, `MOVE`, `SALE` |
| **Feasibility** | ✅ Compare average `MOVE` when `SALE IS NOT NULL` (promoted) vs. `SALE IS NULL` (non-promoted). ~10% of rows have deal flags. |
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

---

### Q7. How did quarterly revenue for Frozen Entrees differ between urban and suburban stores?

| Item | Detail |
|------|--------|
| **Files Needed** | `Movement/WFRE-Done.csv`, `Demographics/DEMO.csv` |
| **Columns** | Movement: `STORE`, `WEEK`, `MOVE`, `PRICE`, `QTY`; DEMO: `STORE`, `URBAN` |
| **Feasibility** | ✅ Join on `STORE`. Derive quarter from `WEEK` (Week 1 ≈ Sep 1989, 13 weeks/quarter). `URBAN` is a binary flag in DEMO. |
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

---

### Q8. Which stores had the highest total customer traffic (CUSTCOUN) during weeks when Soft Drink promotional deals were active?

| Item | Detail |
|------|--------|
| **Files Needed** | `Movement/wsdr.csv`, `Ccount/CCOUNT.csv` |
| **Columns** | Movement: `STORE`, `WEEK`, `SALE`; CCOUNT: `STORE`, `WEEK`, `CUSTCOUN` |
| **Feasibility** | ✅ Join Movement and CCOUNT on `STORE + WEEK`. Filter where `SALE IS NOT NULL` in Movement. CCOUNT `CUSTCOUN` field available. |
| **OLAP Operation** | **Dice** (filter by category = SDR + promotion active, aggregate customer count) |

```sql
SELECT c.STORE,
       SUM(c.CUSTCOUN) AS total_traffic
FROM   CCOUNT c
JOIN   (SELECT DISTINCT STORE, WEEK
        FROM FactWeeklySales
        WHERE category_code = 'SDR' AND SALE IS NOT NULL AND OK = 1) promo
     ON c.STORE = promo.STORE AND c.WEEK = promo.WEEK
GROUP BY c.STORE
ORDER BY total_traffic DESC
LIMIT 10;
```

---

### Q9. How has the monthly market share (% of total units sold) of the top 5 Cereal brands changed over time?

| Item | Detail |
|------|--------|
| **Files Needed** | `Movement/DONE-WCER.csv`, `UPC/UPCCER.csv` |
| **Columns** | Movement: `UPC`, `WEEK`, `MOVE`; UPC: `UPC`, `COM_CODE` (as brand proxy) |
| **Feasibility** | ✅ Join on `UPC`. Use `COM_CODE` as a brand/manufacturer proxy. Derive month from `WEEK`. Requires subquery to find top 5 brands and ratio calculation. |
| **OLAP Operation** | **Pivot** + **Ratio-to-Total** (brand share across time periods) |

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

---

### Q10. Which 10 individual products (UPCs) in the Beer category had the largest price variance across stores in the same week?

| Item | Detail |
|------|--------|
| **Files Needed** | `Movement/DONE-WBER.csv`, `UPC/UPCBER.csv` |
| **Columns** | Movement: `UPC`, `STORE`, `WEEK`, `PRICE`, `QTY`; UPC: `UPC`, `DESCRIP` |
| **Feasibility** | ✅ Compute `PRICE / QTY` as unit price. Calculate variance across stores within each week. Join UPC for description. |
| **OLAP Operation** | **Dice** + **Ranking** (filter to Beer, rank by price variance) |

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

---

## TIER 3 — Very Difficult OLAP Questions (Window Functions Required)

*Require RANK(), NTILE(), SUM() OVER(), LAG(), LEAD(), ratio-to-total, or running total calculations. Cross-store or cross-category percentile analysis.*

---

### Q11. What were the running (cumulative) total unit sales of Bottled Juices for each store across weeks?

| Item | Detail |
|------|--------|
| **Files Needed** | `Movement/DONE-WBJC.csv` |
| **Columns** | `STORE`, `WEEK`, `MOVE` |
| **Feasibility** | ✅ Sum `MOVE` by `STORE + WEEK`, then apply `SUM() OVER(PARTITION BY STORE ORDER BY WEEK)` for running total. 6.2M rows. |
| **OLAP Operation** | **Running Total** |

```sql
SELECT STORE,
       WEEK,
       SUM(MOVE) AS weekly_units,
       SUM(SUM(MOVE)) OVER (PARTITION BY STORE ORDER BY WEEK
                             ROWS UNBOUNDED PRECEDING) AS cumulative_units
FROM   FactWeeklySales
WHERE  category_code = 'BJC'
  AND  OK = 1
GROUP BY STORE, WEEK
ORDER BY STORE, WEEK;
```

---

### Q12. For the Laundry Detergents category, what is each store's weekly revenue as a percentage of the total category revenue for that week?

| Item | Detail |
|------|--------|
| **Files Needed** | `Movement/wlnd.csv` |
| **Columns** | `STORE`, `WEEK`, `MOVE`, `PRICE`, `QTY` |
| **Feasibility** | ✅ Compute revenue per store-week, then divide by total week revenue using `SUM() OVER(PARTITION BY WEEK)`. 6.7M rows. |
| **OLAP Operation** | **Ratio-to-Total** |

```sql
SELECT STORE,
       WEEK,
       SUM(MOVE * (PRICE / QTY)) AS store_weekly_revenue,
       SUM(MOVE * (PRICE / QTY)) /
         SUM(SUM(MOVE * (PRICE / QTY))) OVER (PARTITION BY WEEK) * 100
         AS pct_of_category_revenue
FROM   FactWeeklySales
WHERE  category_code = 'LND'
  AND  OK = 1
  AND  PRICE > 0
GROUP BY STORE, WEEK
ORDER BY WEEK, pct_of_category_revenue DESC;
```

---

### Q13. Which stores fall into the top 25%, middle 50%, and bottom 25% of total revenue for the Toothpaste category, and how do their demographics differ?

| Item | Detail |
|------|--------|
| **Files Needed** | `Movement/WTPA_done.csv`, `Demographics/DEMO.csv` |
| **Columns** | Movement: `STORE`, `MOVE`, `PRICE`, `QTY`; DEMO: `STORE`, `INCOME`, `URBAN`, `DENSITY`, `ZONE` |
| **Feasibility** | ✅ Use `NTILE(4)` over total store revenue to assign quartiles, then join DEMO for demographic comparison. |
| **OLAP Operation** | **Ranking (NTILE)** + **Drill-down** |

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

---

### Q14. For each week, rank the top 10 individual products (UPCs) in the Crackers category by unit sales, and show their week-over-week sales change using LAG().

| Item | Detail |
|------|--------|
| **Files Needed** | `Movement/Done-WCRA.csv`, `UPC/UPCCRA.csv` |
| **Columns** | Movement: `UPC`, `WEEK`, `MOVE`; UPC: `UPC`, `DESCRIP` |
| **Feasibility** | ✅ Rank by `SUM(MOVE)` within each week using `RANK()`, then apply `LAG()` to compare with previous week. 3.6M rows. |
| **OLAP Operation** | **Ranking (RANK)** + **LAG (Week-over-Week Change)** |

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

---

### Q15. For each pricing zone, what is the percentile rank of each store's average weekly profit in the Cigarettes category, and how does it compare to the zone average?

| Item | Detail |
|------|--------|
| **Files Needed** | `Movement/Done-WCIG.csv`, `Demographics/DEMO.csv` |
| **Columns** | Movement: `STORE`, `WEEK`, `PROFIT`; DEMO: `STORE`, `ZONE` |
| **Feasibility** | ✅ Join on `STORE`. Compute avg weekly profit per store, then apply `PERCENT_RANK()` within each zone. `ZONE` ranges 1–10 in DEMO. 5.4M rows. |
| **OLAP Operation** | **Percentile Ranking (PERCENT_RANK)** + **Drill-down by Zone** |

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

---

## Summary Matrix

| # | Question Summary | Tier | OLAP Operation | Files Required | Feasibility |
|---|-----------------|------|----------------|----------------|-------------|
| Q1 | Weekly SDR unit sales | 1 | Roll-up | Movement | ✅ |
| Q2 | Avg weekly revenue per store (Cereals) | 1 | Roll-up | Movement | ✅ |
| Q3 | Total units by category | 1 | Roll-up | All Movement | ✅ |
| Q4 | Distinct UPCs sold weekly (Cookies) | 1 | Slice | Movement | ✅ |
| Q5 | Total profit by store (Cheeses) | 1 | Roll-up | Movement | ✅ |
| Q6 | Promo lift by deal type (Canned Soup) | 2 | Dice | Movement | ✅ |
| Q7 | Quarterly revenue: urban vs suburban (Frozen Entrees) | 2 | Drill-down | Movement + DEMO | ✅ |
| Q8 | Customer traffic during SDR promos | 2 | Dice | Movement + CCOUNT | ✅ |
| Q9 | Top 5 cereal brand market share over time | 2 | Pivot + Ratio | Movement + UPC | ✅ |
| Q10 | Price variance across stores (Beer) | 2 | Dice + Ranking | Movement + UPC | ✅ |
| Q11 | Running total units (Bottled Juices) | 3 | Running Total | Movement | ✅ |
| Q12 | Store % of weekly category revenue (Laundry) | 3 | Ratio-to-Total | Movement | ✅ |
| Q13 | Store quartile tiers + demographics (Toothpaste) | 3 | NTILE + Drill-down | Movement + DEMO | ✅ |
| Q14 | Weekly top 10 products + WoW change (Crackers) | 3 | RANK + LAG | Movement + UPC | ✅ |
| Q15 | Percentile rank by zone (Cigarettes) | 3 | PERCENT_RANK | Movement + DEMO | ✅ |

---

## Prioritization of Business Questions

The 15 business questions are prioritized below based on **strategic value to DFF management**, **data availability**, and **implementability**. Priority 1 = highest importance.

| Priority | Question | Strategic Rationale |
|----------|----------|--------------------|
| **1** | **Q6** – Promo lift by deal type | **Highest ROI impact.** Our data shows promotions drive 2.6× to 13.6× sales lifts. Understanding which deal type works best per category directly impacts DFF's promotional budget allocation — a multi-million dollar decision. Supported by Chevalier et al. (2003). |
| **2** | **Q3** – Total units by category | **Category management foundation.** Understanding total volume across 24 categories determines shelf space allocation, supply chain priorities, and merchandising strategy. This is the baseline for all downstream analysis. |
| **3** | **Q13** – Store quartile tiers + demographics | **Zone pricing validation.** Hoch et al. (1995) showed DFF's zone pricing could increase profits 3–5%. Identifying which stores underperform their demographic potential reveals miscalibrated zones. |
| **4** | **Q9** – Brand market share over time | **Competitive intelligence.** Tracking brand share trends helps DFF negotiate with manufacturers, identify emerging brands, and optimize category assortment. Aligned with Chintagunta (2002). |
| **5** | **Q1** – Weekly SDR unit sales | **High-volume trend monitoring.** Soft Drinks is the largest category (17.7M rows). Weekly trend tracking enables demand forecasting and inventory optimization. |
| **6** | **Q7** – Urban vs suburban revenue | **Location strategy.** 30% of DFF stores are urban vs 70% suburban. Understanding revenue differences by location type informs new store openings and remodeling investments. |
| **7** | **Q15** – Percentile rank by zone (Cigarettes) | **Profit optimization.** Cigarettes have high margins (avg profit $16.44). Identifying top/bottom performers within each zone reveals operational improvement opportunities. |
| **8** | **Q8** – Customer traffic during promos | **Cross-sell measurement.** Linking promotions to store traffic (CCOUNT) reveals whether promos bring in incremental customers or just shift existing traffic — critical for evaluating true promotion ROI. |
| **9** | **Q5** – Total profit by store (Cheeses) | **Margin management.** Cheeses have the highest average profit ($22.66). Store-level profit analysis reveals which locations maximize this high-margin category. |
| **10** | **Q2** – Avg weekly revenue per store (Cereals) | **Performance benchmarking.** Weekly revenue per store enables same-store comparison and identification of growth opportunities in the breakfast category. |
| **11** | **Q12** – Store % of weekly category revenue | **Market concentration analysis.** Understanding revenue distribution reveals whether a few stores dominate category sales or revenue is evenly distributed. |
| **12** | **Q11** – Running total units (Bottled Juices) | **Growth trajectory tracking.** Cumulative sales show whether categories are accelerating or decelerating over the dataset period. |
| **13** | **Q14** – Weekly top 10 products + WoW change | **Product velocity monitoring.** Identifying which products are rising/falling in sales rank each week enables rapid assortment adjustment. |
| **14** | **Q10** – Price variance across stores (Beer) | **Pricing consistency audit.** Large price variance for the same product across stores may indicate pricing errors or unauthorized discounting. |
| **15** | **Q4** – Distinct UPCs sold weekly (Cookies) | **Assortment health check.** Tracking active SKU count over time reveals whether product variety is expanding or contracting. |

### Prioritization Rationale Summary

The prioritization follows these principles:

1. **Revenue & profit impact first** — Questions that directly inform pricing, promotion, and category management decisions (Q6, Q3, Q13) rank highest because they impact DFF's top and bottom line.
2. **Strategic alignment** — Questions supported by published research on the DFF dataset (Hoch et al., 1995; Chevalier et al., 2003) receive higher priority because they address validated business problems.
3. **Data richness determines feasibility** — Questions leveraging the most complete and granular data (Movement files with 134.9M rows) are ranked higher than those dependent on the CCOUNT file (which has corrupted dates).
4. **Actionability** — Questions that produce immediately actionable insights (e.g., "which promotion type works best?") are prioritized over descriptive questions (e.g., "how many UPCs were sold?").

---

## Data Evidence Supporting Business Questions

From our statistical analysis of the dataset (see `data_exploration_summary.md`, Section 8):

| Evidence | Supports BQ | Implication |
|----------|-------------|-------------|
| SDR promotion lift = 13.6× | Q6, Q8 | Promotions are highly effective for Soft Drinks — worth deep analysis |
| Cheeses avg profit = $22.66 (highest) | Q5 | High-margin category; store-level profit analysis is strategically valuable |
| SDR avg profit = -$8.28 (negative) | Q5, Q15 | Soft Drinks used as loss leaders; understanding cross-category profit trade-offs is critical |
| 15 pricing zones in DEMO | Q13, Q15 | Rich zoning data enables Hoch et al.'s zone pricing optimization analysis |
| 107 stores with full demographics | Q7, Q13 | Urban/suburban, income, density data enables segmentation |
| Bonus Buy (B) dominates promotions | Q6 | Most categories rely on Bonus Buys; comparing effectiveness of B vs S vs C is feasible |
| Week range 1–399 (~7.7 years) | Q1, Q9, Q11, Q14 | Sufficient time series for trend analysis, seasonality detection, and running totals |

---

## References

1. Chevalier, J.A., Kashyap, A.K., & Rossi, P.E. (2003). "Why Don't Prices Rise During Periods of Peak Demand? Evidence from Scanner Data." *American Economic Review*, 93(1), 15–37.

2. Chintagunta, P.K. (2002). "Investigating Category Pricing Behavior at a Retail Chain." *Journal of Marketing Research*, 39(2), 141–154.

3. Hoch, S.J., Kim, B.D., Montgomery, A.L., & Rossi, P.E. (1995). "Determinants of Store-Level Price Elasticity." *Journal of Marketing Research*, 32(1), 17–29.

4. Montgomery, A.L. (1997). "Creating Micro-Marketing Pricing Strategies Using Supermarket Scanner Data." *Marketing Science*, 16(4), 315–337.

5. Pesendorfer, M. (2002). "Retail Sales: A Study of Pricing Behavior in Supermarkets." *Journal of Business*, 75(1), 33–66.

6. Kilts Center for Marketing (2013). *Dominick's Data Manual and Codebook.* University of Chicago Booth School of Business. Available at: https://www.chicagobooth.edu/research/kilts/datasets/dominicks
