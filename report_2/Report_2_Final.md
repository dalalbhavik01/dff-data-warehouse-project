# Report 2: Logical Design and Physical Design of the Data Warehouse Schema

**Course:** ISTM 637 – Spring 2026  
**Project:** Design and Implementation of a Data Warehouse for Dominick's Fine Foods (DFF)  
**Team:** Team 1  

---

## 1. Introduction

This report presents the logical and physical design of the data warehouse for Dominick's Fine Foods (DFF), a retail store chain with multiple branches across the Chicago metropolitan area. Building upon the requirements analysis and star schema proposed in Report 1, this report details the Dimensional Modeling process using Kimball's methodology, justifies the schema design against each assigned business question, and provides the two required mapping tables (Source → Staging and Staging → Data Mart) along with a physical design plan.

**Design Specifications (from Report 1):**
- **Implementation Architecture:** Hybrid Data Pipeline
- **Warehouse Architecture:** Independent Data Marts
- **Modeling Scheme:** Dimensional Modeling (Star Schema)
- **OLAP Style:** HOLAP (Hybrid Online Analytical Processing)
- **Target Infrastructure:** SQL Server 2016

**Selected Business Questions for Report 2:**
BQ2, BQ3, BQ4, BQ8, BQ9 (selected from the 15 BQs proposed in Report 1).

---

## 2. Overview of Kimball's Methodology

The data warehouse logical design strictly follows Kimball's bottom-up methodology for building independent, conformable data marts. The steps, as discussed in class (Task 3A), are applied below:

### Step 1: Requirements Analysis
In Report 1, we gathered 15 business questions from stakeholder analysis and research on the DFF dataset. From those 15 questions, the professor has selected 5 BQs (BQ2, BQ3, BQ4, BQ8, BQ9) for this report. These BQs span four product categories (Soft Drinks, Canned Soup, Toothpaste, Crackers) and require time-series analysis, promotional lift measurement, demographic segmentation, and product ranking.

### Step 2: Build the Bus Matrix
A matrix is created with **data marts** (business processes) on one axis and **dimensions** on the other:
- **Step 2.1 – List the Data Marts:** We first identified single-source data marts centered on weekly store-level sales (FactWeeklySales) and customer traffic (FactCustomerTraffic).
- **Step 2.2 – List the Dimensions:** The conformed dimensions are DimTime, DimStore, DimProduct, DimCategory, and DimPromotion.
- **Step 2.3 – Mark the Intersections:** See the Bus Matrix in Section 3.

### Step 3: Design Fact Tables
- **Step 3A – Choose the Data Mart:** FactWeeklySales (the primary mart for all 5 BQs).
- **Step 3B – Declare the Grain:** One row = weekly sales of one UPC at one store (UPC × Store × Week).
- **Step 3C – Choose the Facts:** Additive measures (units_sold, revenue, gross_profit), non-additive (unit_price, profit_margin_pct), and semi-additive (shelf_price, price_qty).
- **Step 3D – Include Derived Facts:** Revenue (units_sold × unit_price), profit_margin_pct (gross_profit / revenue × 100).
- **Step 3E – Document Facts:** All base and derived facts are cross-referenced with the BQs  (see Section 4).
- **Step 3F – Create Fact Table Diagram:** See Section 8 (ER Diagram).

### Step 4: Design Dimension Tables
Each dimension table has been drawn with:
- Surrogate keys (4-byte INT, meaningless DW keys as required by Kimball)
- Natural keys retained as attributes for traceability
- **Denormalized** flat structure (no snowflaking — as emphasized in class, snowflaking slows browsing, confuses users, and causes problems with bitmapped indexes)

### Step 5: Feedback for the Design
- **5A (IS Team):** Schema was validated against all 15 original BQs in Report 1; all 15 are answerable.
- **5B (Core Users):** Schema supports drill-down, roll-up, slice, dice, ranking, and windowed operations.
- **5C (Business Users):** The 5 selected BQs were checked against the schema; all are fully supported (Section 4.3).

### Step 6: Data Sourcing
- **Formal Sources:** DFF Movement files (24 categories), UPC files (28 files), DEMO.csv, CCOUNT.csv.
- **Data Source Definitions:** Source, platform, location documented in Section 9.
- **Mapping Type 1:** Source → Staging (Section 5).
- **Mapping Type 2:** Staging → Data Mart (Section 6).

**Why is this methodology important for independent data marts?**

Kimball's methodology ensures each data mart is driven by business needs, not merely mirroring source systems. By using **conformed dimensions** (shared dimensions like DimStore, DimTime, DimProduct, DimCategory across data marts), independent data marts can be queried together without requiring a monolithic enterprise data warehouse. The emphasis on denormalized star schemas guarantees high-performance query access and an intuitive format for business users.

---

## 3. Data Mart / Dimension Bus Matrix (Step 2)

| Data Mart (Business Process) | DimTime | DimStore | DimProduct | DimCategory | DimPromotion | Business Questions Supported |
|:-|:-:|:-:|:-:|:-:|:-:|:-|
| **FactWeeklySales** | ✓ | ✓ | ✓ | ✓ | ✓ | BQ2, BQ3, BQ4, BQ8, BQ9 |
| **FactCustomerTraffic** | ✓ | ✓ | — | — | — | (supplementary) |

All five dimensions are **conformed** and reusable across current and future data marts.

---

## 4. Data Warehouse Logical Design (Star Schema Design)

### 4.1 Selected Business Questions

| BQ ID | Business Question | Report 1 Ref | Category | OLAP Operation |
|:--|:--|:--|:--|:--|
| BQ2 | What were the total weekly unit sales of Soft Drinks across all stores for each week? | Q1 | Soft Drinks (SDR) | Roll-up |
| BQ3 | How do promotion weeks compare to non-promotion weeks in terms of sales volume? | Q6 (related) | Soft Drinks (SDR) | Dice |
| BQ4 | Which promotion type (B/C/S) generated the highest incremental unit sales lift in the Canned Soup category? | Q6 | Canned Soup (CSO) | Dice |
| BQ8 | Which stores fall into the top 25%, middle 50%, and bottom 25% of total revenue for Toothpaste, and how do their demographics differ? | Q13 | Toothpaste (TPA) | NTILE + Drill-down |
| BQ9 | For each week, rank the top 10 individual products (UPCs) in Crackers by unit sales, and show their week-over-week sales change. | Q14 | Crackers (CRA) | RANK + LAG |

### 4.2 Star Schema — Table Definitions (from Report 1 ERD)

The schema below matches the ER diagram submitted in Report 1 and is the foundation for the logical design.

---

#### FactWeeklySales (Central Fact Table)

| Column | Data Type | Description | Source | Additivity |
|:--|:--|:--|:--|:--|
| **sales_fact_id** (PK) | INT | Surrogate key | Generated | — |
| product_key (FK → DimProduct) | INT | Product dimension key | Mapped from UPC | — |
| store_key (FK → DimStore) | INT | Store dimension key | Mapped from STORE | — |
| time_key (FK → DimTime) | INT | Time dimension key | Mapped from WEEK | — |
| category_key (FK → DimCategory) | INT | Category dimension key | Derived from source filename | — |
| promotion_key (FK → DimPromotion) | INT | Promotion dimension key | Mapped from SALE | — |
| units_sold | INT | Units moved/sold | MOVE | Additive |
| unit_price | DECIMAL(8,2) | Price per unit | PRICE / QTY | Non-additive |
| shelf_price | DECIMAL(8,2) | Listed shelf price | PRICE | Semi-additive |
| price_qty | INT | Quantity for listed price | QTY | Semi-additive |
| revenue | DECIMAL(12,2) | Derived: MOVE × (PRICE / QTY) | Computed | Additive |
| gross_profit | DECIMAL(10,2) | Gross profit | PROFIT | Additive |
| profit_margin_pct | DECIMAL(5,2) | Derived: (PROFIT / revenue) × 100 | Computed | Non-additive |

**Grain:** One row per UPC × Store × Week  
**Source:** All 24 Movement CSV files  

---

#### FactCustomerTraffic (Secondary Fact Table)

| Column | Data Type | Description | Source |
|:--|:--|:--|:--|
| **traffic_fact_id** (PK) | INT | Surrogate key | Generated |
| store_key (FK → DimStore) | INT | Store dimension key | STORE from CCOUNT |
| time_key (FK → DimTime) | INT | Time dimension key | Derived from DATE |
| total_customers | DECIMAL(10,2) | Total customer count | CUSTCOUN |
| grocery_count | DECIMAL(10,2) | Customer count – Grocery | GROCERY |
| dairy_count | DECIMAL(10,2) | Customer count – Dairy | DAIRY |
| frozen_count | DECIMAL(10,2) | Customer count – Frozen | FROZEN |
| meat_count | DECIMAL(10,2) | Customer count – Meat | MEAT |
| produce_count | DECIMAL(10,2) | Customer count – Produce | PRODUCE |
| deli_count | DECIMAL(10,2) | Customer count – Deli | DELI |
| bakery_count | DECIMAL(10,2) | Customer count – Bakery | BAKERY |
| pharmacy_count | DECIMAL(10,2) | Customer count – Pharmacy | PHARMACY |
| beer_count | DECIMAL(10,2) | Customer count – Beer | BEER |
| spirits_count | DECIMAL(10,2) | Customer count – Spirits | SPIRITS |
| mvp_club_count | DECIMAL(10,2) | MVP loyalty count | MVPCLUB |
| total_coupon_redemptions | DECIMAL(10,2) | Sum of all coupon columns | Computed |

**Grain:** One row per Store × Week  
**Source:** `Ccount/CCOUNT.csv`

---

#### DimProduct

| Column | Data Type | Description | Source |
|:--|:--|:--|:--|
| **product_key** (PK) | INT | Surrogate key | Generated |
| upc (Unique) | BIGINT | Universal Product Code (natural key) | UPC from UPC files |
| description | VARCHAR(100) | Product description | DESCRIP |
| size | VARCHAR(20) | Package size | SIZE |
| case_pack | INT | Case pack quantity | CASE |
| commodity_code | INT | Manufacturer/company code | COM_CODE |
| item_number | BIGINT | Internal DFF item number | NITEM |
| category_key (FK → DimCategory) | INT | Category dimension key | Derived from filename |

**Grain:** One row per unique UPC  
**Cardinality:** ~14,000 rows  

---

#### DimStore

| Column | Data Type | Description | Source |
|:--|:--|:--|:--|
| **store_key** (PK) | INT | Surrogate key | Generated |
| store_id (Unique) | INT | Original store number | STORE |
| store_name | VARCHAR(50) | Store name | NAME |
| city | VARCHAR(40) | City | CITY |
| zip_code | VARCHAR(10) | ZIP code | ZIP |
| zone | INT | Pricing zone | ZONE |
| is_urban | INT | Urban flag | URBAN |
| weekly_volume | INT | Avg weekly volume | WEEKVOL |
| avg_income | DECIMAL(10,2) | Avg area income (log) | INCOME |
| education_pct | DECIMAL(5,2) | % higher education | EDUC |
| poverty_pct | DECIMAL(5,2) | % below poverty line | POVERTY |
| avg_household_size | DECIMAL(4,2) | Avg household size | HSIZEAVG |
| ethnic_diversity | DECIMAL(5,2) | Ethnic diversity index | ETHNIC |
| population_density | DECIMAL(10,2) | Population density | DENSITY |
| price_tier | VARCHAR(10) | Low / Medium / High | Derived from PRICLOW/MED/HIGH |
| age_under_9_pct | DECIMAL(5,2) | % population under 9 | AGE9 |
| age_over_60_pct | DECIMAL(5,2) | % population over 60 | AGE60 |
| working_women_pct | DECIMAL(5,2) | % working women | WORKWOM |

**Grain:** One row per store  
**Cardinality:** ~107 rows  

---

#### DimTime

| Column | Data Type | Description | Source |
|:--|:--|:--|:--|
| **time_key** (PK) | INT | Surrogate key | Generated |
| week_id | INT | DFF week number (natural key) | WEEK |
| week_start_date | DATE | Start date | 1989-09-14 + (week_id - 1) × 7 |
| week_end_date | DATE | End date | week_start_date + 6 |
| month | INT | Month (1–12) | Derived |
| month_name | VARCHAR(10) | Month name | Derived |
| quarter | INT | Quarter (1–4) | Derived |
| year | INT | Calendar year | Derived |
| fiscal_year | INT | DFF fiscal year | Derived |
| is_holiday_week | BIT | Holiday flag | Engineered |

**Grain:** One row per unique week  
**Cardinality:** ~400 rows  

---

#### DimCategory

| Column | Data Type | Description | Source |
|:--|:--|:--|:--|
| **category_key** (PK) | INT | Surrogate key | Generated |
| category_code (Unique) | CHAR(3) | 3-letter code | Derived from filename |
| category_name | VARCHAR(30) | Full name | Mapped from codebook |
| department | VARCHAR(20) | Department grouping | Engineered |

**Categories relevant to Report 2 BQs:**

| category_code | category_name | department |
|:--|:--|:--|
| SDR | Soft Drinks | Beverages |
| CSO | Canned Soup | Grocery |
| TPA | Toothpaste | Health & Beauty |
| CRA | Crackers | Snacks |

**Grain:** One row per category  
**Cardinality:** 28 rows  

---

#### DimPromotion

| Column | Data Type | Description | Source |
|:--|:--|:--|:--|
| **promotion_key** (PK) | INT | Surrogate key | Generated |
| deal_code | CHAR(1) | Deal flag | SALE |
| deal_type | VARCHAR(20) | Descriptive name | Mapped |
| is_promoted | BIT | Whether any deal was active | Derived |

| deal_code | deal_type | is_promoted |
|:--|:--|:--|
| (NULL/blank) | No Promotion | 0 |
| B | Bonus Buy | 1 |
| C | Coupon | 1 |
| S | Sale/Discount | 1 |

**Grain:** One row per promotion type  
**Cardinality:** 4 rows  

---

### 4.3 Schema Justification — How Each BQ Is Supported

#### BQ2: Total weekly unit sales of Soft Drinks across all stores for each week

**Tables Used:** FactWeeklySales, DimTime, DimCategory  
**OLAP Operation:** Roll-up (aggregate UPC and STORE up to weekly total)  
**How the schema supports it:** The `units_sold` measure (from MOVE) in FactWeeklySales is fully additive. By filtering on `category_key` where `category_code = 'SDR'` (through DimCategory) and grouping by `time_key` (or `week_id` through DimTime), the schema directly returns total weekly unit sales across all stores.

```sql
-- From Report 1, Q1
SELECT t.week_id,
       SUM(f.units_sold) AS total_units_sold
FROM   FactWeeklySales f
JOIN   DimTime t ON f.time_key = t.time_key
JOIN   DimCategory c ON f.category_key = c.category_key
WHERE  c.category_code = 'SDR'
GROUP BY t.week_id
ORDER BY t.week_id;
```

#### BQ3: How do promotion weeks compare to non-promotion weeks in terms of sales volume?

**Tables Used:** FactWeeklySales, DimPromotion, DimCategory  
**OLAP Operation:** Dice (filter by category, group by promotion status)  
**How the schema supports it:** By joining FactWeeklySales with DimPromotion on `promotion_key`, users can group the sum of `units_sold` by `is_promoted` (or `deal_type`). This provides a direct comparison of promoted vs. non-promoted sales volume. The `is_promoted` flag in DimPromotion cleanly separates the two states.

```sql
SELECT p.is_promoted,
       p.deal_type,
       SUM(f.units_sold) AS total_units,
       AVG(f.units_sold) AS avg_units_per_record
FROM   FactWeeklySales f
JOIN   DimPromotion p ON f.promotion_key = p.promotion_key
JOIN   DimCategory c ON f.category_key = c.category_key
WHERE  c.category_code = 'SDR'
GROUP BY p.is_promoted, p.deal_type
ORDER BY p.is_promoted DESC;
```

#### BQ4: Which promotion type (B/C/S) generated the highest incremental unit sales lift in Canned Soup?

**Tables Used:** FactWeeklySales, DimPromotion, DimCategory  
**OLAP Operation:** Dice (filter by category + promotion type, compare to baseline)  
**How the schema supports it:** The schema captures each sales record's promotion type via `promotion_key → DimPromotion.deal_code`. The incremental lift is calculated by comparing the average `units_sold` during promoted periods (B, C, or S) against the average during non-promoted periods (NULL). Grouping by `deal_code` reveals which promotion type delivers the highest lift.

```sql
-- From Report 1, Q6
SELECT p.deal_code AS promotion_type,
       AVG(f.units_sold) AS avg_units_promoted,
       (SELECT AVG(f2.units_sold)
        FROM FactWeeklySales f2
        JOIN DimPromotion p2 ON f2.promotion_key = p2.promotion_key
        JOIN DimCategory c2 ON f2.category_key = c2.category_key
        WHERE c2.category_code = 'CSO' AND p2.is_promoted = 0) AS avg_units_baseline,
       AVG(f.units_sold) -
       (SELECT AVG(f2.units_sold)
        FROM FactWeeklySales f2
        JOIN DimPromotion p2 ON f2.promotion_key = p2.promotion_key
        JOIN DimCategory c2 ON f2.category_key = c2.category_key
        WHERE c2.category_code = 'CSO' AND p2.is_promoted = 0) AS sales_lift
FROM   FactWeeklySales f
JOIN   DimPromotion p ON f.promotion_key = p.promotion_key
JOIN   DimCategory c ON f.category_key = c.category_key
WHERE  c.category_code = 'CSO'
  AND  p.is_promoted = 1
GROUP BY p.deal_code
ORDER BY sales_lift DESC;
```

#### BQ8: Store quartile tiers by Toothpaste revenue with demographic comparison

**Tables Used:** FactWeeklySales, DimStore, DimCategory  
**OLAP Operation:** NTILE (ranking) + Drill-down (demographics)  
**How the schema supports it:** The `revenue` derived fact in FactWeeklySales (MOVE × PRICE / QTY) is summed by `store_key` and filtered by `category_code = 'TPA'`. SQL Server 2016's `NTILE(4)` window function divides stores into quartiles. Joining with DimStore (which contains all demographic attributes in a denormalized, flat structure) exposes Income, Education, Poverty, Ethnic Diversity, Urban status, and more — enabling a full demographic comparison across the three tiers.

```sql
-- From Report 1, Q13
WITH store_revenue AS (
    SELECT f.store_key,
           SUM(f.revenue) AS total_revenue
    FROM   FactWeeklySales f
    JOIN   DimCategory c ON f.category_key = c.category_key
    WHERE  c.category_code = 'TPA'
    GROUP BY f.store_key
),
quartiles AS (
    SELECT store_key, total_revenue,
           NTILE(4) OVER (ORDER BY total_revenue) AS revenue_quartile
    FROM   store_revenue
)
SELECT CASE WHEN q.revenue_quartile = 1 THEN 'Bottom 25%'
            WHEN q.revenue_quartile IN (2,3) THEN 'Middle 50%'
            ELSE 'Top 25%' END AS tier,
       COUNT(*) AS store_count,
       AVG(q.total_revenue) AS avg_revenue,
       AVG(d.avg_income) AS avg_income,
       AVG(d.education_pct) AS avg_education,
       AVG(d.poverty_pct) AS avg_poverty,
       AVG(d.ethnic_diversity) AS avg_ethnic_diversity,
       AVG(d.population_density) AS avg_density,
       SUM(d.is_urban) AS urban_store_count
FROM   quartiles q
JOIN   DimStore d ON q.store_key = d.store_key
GROUP BY CASE WHEN q.revenue_quartile = 1 THEN 'Bottom 25%'
              WHEN q.revenue_quartile IN (2,3) THEN 'Middle 50%'
              ELSE 'Top 25%' END
ORDER BY avg_revenue DESC;
```

#### BQ9: Weekly top 10 Cracker products by unit sales with week-over-week change

**Tables Used:** FactWeeklySales, DimProduct, DimTime, DimCategory  
**OLAP Operation:** RANK (ranking) + LAG (week-over-week change)  
**How the schema supports it:** FactWeeklySales stores granular `units_sold` per UPC per Store per Week. Aggregating by `product_key` and `time_key` while filtering `category_code = 'CRA'` gives weekly totals per product. `RANK() OVER(PARTITION BY week_id ORDER BY ...)` identifies the top 10 per week, and `LAG()` computes the week-over-week variance. Joining DimProduct provides the product description.

```sql
-- From Report 1, Q14
WITH weekly_product AS (
    SELECT p.upc, p.description, t.week_id,
           SUM(f.units_sold) AS weekly_units,
           RANK() OVER (PARTITION BY t.week_id
                        ORDER BY SUM(f.units_sold) DESC) AS week_rank
    FROM   FactWeeklySales f
    JOIN   DimProduct p ON f.product_key = p.product_key
    JOIN   DimTime t ON f.time_key = t.time_key
    JOIN   DimCategory c ON f.category_key = c.category_key
    WHERE  c.category_code = 'CRA'
    GROUP BY p.upc, p.description, t.week_id
)
SELECT upc, description, week_id,
       weekly_units,
       week_rank,
       LAG(weekly_units) OVER (PARTITION BY upc ORDER BY week_id) AS prev_week_units,
       weekly_units - LAG(weekly_units) OVER (PARTITION BY upc ORDER BY week_id) AS wow_change
FROM   weekly_product
WHERE  week_rank <= 10
ORDER BY week_id, week_rank;
```

---

## 5. Mapping Table #1: Source Files → Staging Tables

### 5.1 Movement Files → Staging

| Source File Name | Source Attribute | Mapping Description | Staging Table Type | Staging Table Name | Staging Table Attribute |
|:--|:--|:--|:--|:--|:--|
| wsdr.csv (Soft Drinks) | STORE | Copy | Relation | stg_Movement | STORE |
| wsdr.csv | UPC | Copy | Relation | stg_Movement | UPC |
| wsdr.csv | WEEK | Copy | Relation | stg_Movement | WEEK |
| wsdr.csv | MOVE | Copy | Relation | stg_Movement | MOVE |
| wsdr.csv | QTY | Copy | Relation | stg_Movement | QTY |
| wsdr.csv | PRICE | Copy | Relation | stg_Movement | PRICE |
| wsdr.csv | SALE | Transform: Replace blank/NULL with 'N' | Relation | stg_Movement | SALE |
| wsdr.csv | PROFIT | Copy | Relation | stg_Movement | PROFIT |
| wsdr.csv | OK | Copy (data quality flag) | Relation | stg_Movement | OK |
| wsdr.csv | (filename) | Transform: Extract 'SDR' from filename | Relation | stg_Movement | CATEGORY_CODE |
| WCSO-Done.csv (Canned Soup) | (all columns) | Same mapping as above | Relation | stg_Movement | (same) |
| WCSO-Done.csv | (filename) | Transform: Extract 'CSO' | Relation | stg_Movement | CATEGORY_CODE |
| WTPA_done.csv (Toothpaste) | (all columns) | Same mapping as above | Relation | stg_Movement | (same) |
| WTPA_done.csv | (filename) | Transform: Extract 'TPA' | Relation | stg_Movement | CATEGORY_CODE |
| Done-WCRA.csv (Crackers) | (all columns) | Same mapping as above | Relation | stg_Movement | (same) |
| Done-WCRA.csv | (filename) | Transform: Extract 'CRA' | Relation | stg_Movement | CATEGORY_CODE |

*Note: All 24 Movement files follow this same pattern. Only the 4 categories relevant to the selected BQs are shown. In production, all 24 would be loaded to stg_Movement with distinct CATEGORY_CODE values.*

### 5.2 UPC Files → Staging

| Source File Name | Source Attribute | Mapping Description | Staging Table Type | Staging Table Name | Staging Table Attribute |
|:--|:--|:--|:--|:--|:--|
| UPCSDR.csv | COM_CODE | Copy | Relation | stg_Product | COM_CODE |
| UPCSDR.csv | UPC | Copy | Relation | stg_Product | UPC |
| UPCSDR.csv | DESCRIP | Transform: Strip leading '#' and '~' characters | Relation | stg_Product | DESCRIP |
| UPCSDR.csv | SIZE | Transform: Standardize format (e.g., "1.75 O" → "1.75 OZ") | Relation | stg_Product | SIZE |
| UPCSDR.csv | CASE | Copy | Relation | stg_Product | CASE_PACK |
| UPCSDR.csv | NITEM | Copy | Relation | stg_Product | NITEM |
| UPCSDR.csv | (filename) | Transform: Extract 'SDR' → map to CATEGORY_CODE | Relation | stg_Product | CATEGORY_CODE |
| UPCCSO.csv | (all columns) | Same mapping; CATEGORY_CODE = 'CSO' | Relation | stg_Product | (same) |
| UPCTPA.csv | (all columns) | Same mapping; CATEGORY_CODE = 'TPA' | Relation | stg_Product | (same) |
| UPCCRA.csv | (all columns) | Same mapping; CATEGORY_CODE = 'CRA' | Relation | stg_Product | (same) |

### 5.3 Demographics File → Staging

| Source File Name | Source Attribute | Mapping Description | Staging Table Type | Staging Table Name | Staging Table Attribute |
|:--|:--|:--|:--|:--|:--|
| DEMO.csv | STORE | Copy | Relation | stg_Store | STORE |
| DEMO.csv | NAME | Copy (handle 23 NULLs → 'UNKNOWN') | Relation | stg_Store | NAME |
| DEMO.csv | CITY | Copy (handle 23 NULLs → 'UNKNOWN') | Relation | stg_Store | CITY |
| DEMO.csv | ZIP | Copy | Relation | stg_Store | ZIP |
| DEMO.csv | ZONE | Copy | Relation | stg_Store | ZONE |
| DEMO.csv | URBAN | Copy | Relation | stg_Store | URBAN |
| DEMO.csv | WEEKVOL | Copy | Relation | stg_Store | WEEKVOL |
| DEMO.csv | INCOME | Copy | Relation | stg_Store | INCOME |
| DEMO.csv | EDUC | Copy | Relation | stg_Store | EDUC |
| DEMO.csv | POVERTY | Copy | Relation | stg_Store | POVERTY |
| DEMO.csv | HSIZEAVG | Copy | Relation | stg_Store | HSIZEAVG |
| DEMO.csv | ETHNIC | Copy | Relation | stg_Store | ETHNIC |
| DEMO.csv | DENSITY | Copy | Relation | stg_Store | DENSITY |
| DEMO.csv | AGE9 | Copy | Relation | stg_Store | AGE9 |
| DEMO.csv | AGE60 | Copy | Relation | stg_Store | AGE60 |
| DEMO.csv | WORKWOM | Copy | Relation | stg_Store | WORKWOM |
| DEMO.csv | PRICLOW, PRICMED, PRICHIGH | Transform: Map binary flags → single PRICE_TIER label | Relation | stg_Store | PRICE_TIER |

### 5.4 Customer Counts File → Staging

| Source File Name | Source Attribute | Mapping Description | Staging Table Type | Staging Table Name | Staging Table Attribute |
|:--|:--|:--|:--|:--|:--|
| CCOUNT.csv | STORE | Copy | Relation | stg_CustomerTraffic | STORE |
| CCOUNT.csv | DATE | Copy | Relation | stg_CustomerTraffic | DATE |
| CCOUNT.csv | GROCERY | Transform: Replace '.' with NULL | Relation | stg_CustomerTraffic | GROCERY |
| CCOUNT.csv | DAIRY | Transform: Replace '.' with NULL | Relation | stg_CustomerTraffic | DAIRY |
| CCOUNT.csv | FROZEN | Transform: Replace '.' with NULL | Relation | stg_CustomerTraffic | FROZEN |
| CCOUNT.csv | MEAT | Transform: Replace '.' with NULL | Relation | stg_CustomerTraffic | MEAT |
| CCOUNT.csv | PRODUCE | Transform: Replace '.' with NULL | Relation | stg_CustomerTraffic | PRODUCE |
| CCOUNT.csv | *COUP columns | Transform: Sum all coupon columns → total | Relation | stg_CustomerTraffic | TOTAL_COUPONS |

---

## 6. Mapping Table #2: Staging Tables → Data Mart Tables (Presentation Server)

### 6.1 Staging → Dimension Tables

| Staging Table | Staging Attribute | Mapping Description | DM Table Type | Data Mart Table | Data Mart Attribute |
|:--|:--|:--|:--|:--|:--|
| stg_Store | (row number) | Transform: Generate surrogate key (INT, auto-increment) | Dimension | DimStore | store_key (PK) |
| stg_Store | STORE | Copy | Dimension | DimStore | store_id |
| stg_Store | NAME | Copy | Dimension | DimStore | store_name |
| stg_Store | CITY | Copy | Dimension | DimStore | city |
| stg_Store | ZIP | Copy | Dimension | DimStore | zip_code |
| stg_Store | ZONE | Copy | Dimension | DimStore | zone |
| stg_Store | URBAN | Copy | Dimension | DimStore | is_urban |
| stg_Store | WEEKVOL | Copy | Dimension | DimStore | weekly_volume |
| stg_Store | INCOME | Copy | Dimension | DimStore | avg_income |
| stg_Store | EDUC | Copy | Dimension | DimStore | education_pct |
| stg_Store | POVERTY | Copy | Dimension | DimStore | poverty_pct |
| stg_Store | HSIZEAVG | Copy | Dimension | DimStore | avg_household_size |
| stg_Store | ETHNIC | Copy | Dimension | DimStore | ethnic_diversity |
| stg_Store | DENSITY | Copy | Dimension | DimStore | population_density |
| stg_Store | PRICE_TIER | Copy | Dimension | DimStore | price_tier |
| stg_Store | AGE9 | Copy | Dimension | DimStore | age_under_9_pct |
| stg_Store | AGE60 | Copy | Dimension | DimStore | age_over_60_pct |
| stg_Store | WORKWOM | Copy | Dimension | DimStore | working_women_pct |
| stg_Product | (row number) | Transform: Generate surrogate key | Dimension | DimProduct | product_key (PK) |
| stg_Product | UPC | Copy | Dimension | DimProduct | upc |
| stg_Product | DESCRIP | Copy | Dimension | DimProduct | description |
| stg_Product | SIZE | Copy | Dimension | DimProduct | size |
| stg_Product | CASE_PACK | Copy | Dimension | DimProduct | case_pack |
| stg_Product | COM_CODE | Copy | Dimension | DimProduct | commodity_code |
| stg_Product | NITEM | Copy | Dimension | DimProduct | item_number |
| stg_Product | CATEGORY_CODE | Transform: Lookup category_key from DimCategory | Dimension | DimProduct | category_key (FK) |
| (Generated) | WEEK values | Transform: Generate unique list, calc dates from base 1989-09-14 | Dimension | DimTime | time_key, week_id, week_start_date, week_end_date, month, month_name, quarter, year, fiscal_year, is_holiday_week |
| (Derived) | CATEGORY_CODE | Transform: Map 28 codes to names and departments | Dimension | DimCategory | category_key, category_code, category_name, department |
| (Derived) | SALE values | Transform: Map {NULL,B,C,S} → 4 descriptive rows | Dimension | DimPromotion | promotion_key, deal_code, deal_type, is_promoted |

### 6.2 Staging → Fact Tables

| Staging Table | Staging Attribute | Mapping Description | DM Table Type | Data Mart Table | Data Mart Attribute |
|:--|:--|:--|:--|:--|:--|
| stg_Movement | (row number) | Transform: Generate surrogate key | Fact | FactWeeklySales | sales_fact_id (PK) |
| stg_Movement | UPC | Transform: Lookup product_key from DimProduct using UPC | Fact | FactWeeklySales | product_key (FK) |
| stg_Movement | STORE | Transform: Lookup store_key from DimStore using STORE | Fact | FactWeeklySales | store_key (FK) |
| stg_Movement | WEEK | Transform: Lookup time_key from DimTime using WEEK | Fact | FactWeeklySales | time_key (FK) |
| stg_Movement | CATEGORY_CODE | Transform: Lookup category_key from DimCategory | Fact | FactWeeklySales | category_key (FK) |
| stg_Movement | SALE | Transform: Lookup promotion_key from DimPromotion | Fact | FactWeeklySales | promotion_key (FK) |
| stg_Movement | MOVE | Copy | Fact | FactWeeklySales | units_sold |
| stg_Movement | PRICE, QTY | Transform: PRICE / QTY | Fact | FactWeeklySales | unit_price |
| stg_Movement | PRICE | Copy | Fact | FactWeeklySales | shelf_price |
| stg_Movement | QTY | Copy | Fact | FactWeeklySales | price_qty |
| stg_Movement | MOVE, PRICE, QTY | Transform: MOVE × (PRICE / QTY) | Fact | FactWeeklySales | revenue |
| stg_Movement | PROFIT | Copy | Fact | FactWeeklySales | gross_profit |
| stg_Movement | PROFIT, revenue | Transform: (PROFIT / revenue) × 100 | Fact | FactWeeklySales | profit_margin_pct |
| stg_CustomerTraffic | (similar lookups) | (same pattern as above) | Fact | FactCustomerTraffic | (all traffic measures) |

---

## 7. Physical Design Plan

The physical design transforms the logical star schemas into a deployable structure on SQL Server 2016, addressing the four key areas as described in the course materials (Task 3B).

### 7.1 Data Aggregate Plan
With FactWeeklySales containing ~134.9 million rows across all 24 categories, pre-computed aggregate tables will improve query performance for frequently asked analytical questions. The following summary tables are planned:

- **agg_Weekly_Category_Sales:** Pre-aggregates `SUM(units_sold)`, `SUM(revenue)` by week_id and category_code (across all stores and UPCs). Directly accelerates BQ2-type queries.
- **agg_Store_Category_Revenue:** Aggregates total revenue by store_key and category_code (across all weeks). Directly accelerates BQ8-type quartile analysis.
- **agg_Weekly_Product_Sales:** Aggregates `SUM(units_sold)` by week_id and product_key within a category (across all stores). Directly accelerates BQ9-type ranking queries.

These aggregate fact tables echo the original FactWeeklySales structure with reduced grain, following Kimball's guidance that "a mature set of aggregates could involve a dozen separate aggregate fact tables, all echoing the original structure of the base fact table."

### 7.2 Indexing Plan
The indexing plan follows the framework discussed in class (Task 3B), distinguishing between fact table and dimension table indexing:

**Fact Table Indexing (FactWeeklySales):**
- **Clustered B-Tree index** on the composite key (time_key, store_key, product_key). The primary key of a fact table is the concatenation of all dimension PKs. The key order prioritizes time-based filtering as the most common access pattern.
- **Non-clustered B-Tree index** on `promotion_key` to accelerate BQ3 and BQ4 queries that filter on promotion type.
- **Non-clustered B-Tree index** on `category_key` to accelerate category-specific filtering across all BQs.
- Bitmapped indexes are **not** applied to the fact table because fact table columns have high selectivity (many unique values), as noted in class.

**Dimension Table Indexing:**
- **Unique B-Tree index** on each dimension's single-column surrogate primary key (e.g., `store_key`, `product_key`).
- **Bitmapped indexes** on low-cardinality columns ideal for filtering: `DimPromotion.deal_code` (4 values), `DimPromotion.is_promoted` (2 values), `DimCategory.department` (6 values), `DimStore.price_tier` (3 values), `DimStore.is_urban` (2 values).

**Loading Strategy:** During bulk ETL loads, indexes will be dropped before loading and recreated afterward to avoid performance degradation during bulk inserts.

### 7.3 Data Standardization Plan
- **Naming Standards:** Dimension tables prefixed with `Dim`, fact tables with `Fact`, staging tables with `stg_`, and aggregate tables with `agg_`. Column names use snake_case consistently (e.g., `units_sold`, `store_key`).
- **Data Types:** All surrogate keys are 4-byte INT. Monetary values use DECIMAL(8,2) or DECIMAL(12,2). Descriptive text uses VARCHAR(n). Promotion codes use CHAR(1). Boolean flags use BIT.
- **Null Handling:** Blank/NULL promotion codes → mapped to 'No Promotion' row in DimPromotion. Store NAME/CITY nulls → replaced with 'UNKNOWN'. CCOUNT dot placeholders → replaced with NULL.
- **Data Quality:** Rows with `OK = 0` in movement files are excluded from FactWeeklySales loads. Rows with `PRICE = 0` are filtered to avoid division-by-zero in derived calculations.

### 7.4 Storage Plan
The storage plan accounts for the current data volume and future growth as DFF adds more time periods or categories.

- **Table Partitioning:** The large FactWeeklySales table will be horizontally partitioned by `time_key` (yearly partitions, ~52 weeks per partition). This ensures queries for a specific time range scan only the relevant partition, new data can be loaded without locking historical partitions, and backup/recovery can be performed at the partition level.
- **Estimated Storage:**
  - Dimension tables: < 10 MB total (small, mostly static tables)
  - FactWeeklySales: ~4-5 GB (134.9M rows × ~40 bytes per row)
  - FactCustomerTraffic: ~20 MB (327K rows)
  - Aggregate tables: ~50 MB total
  - Staging area: Temporary; ~2 GB (same as source files; purged after ETL)
  - Index storage: ~30-50% of base table sizes
  - **Total: ~8-10 GB**, well within SQL Server 2016 capacity
- **Scalability:** The independent data mart architecture allows new product categories or business processes to be added as new data marts without modifying existing tables. Conformed dimensions can be extended with additional attributes as needed.

---

## 8. Star Schema Diagrams

The visual diagrams below represent the logical star schema ERD as established in Report 1. These should be recreated in Visio or LucidChart for the final submission document.

### 8.1 FactWeeklySales Star Schema (Primary — supports all 5 BQs)

```
                        ┌──────────────────────────┐
                        │       DimCategory         │
                        ├──────────────────────────┤
                        │ category_key PK    INT    │
                        │ category_code Uniq CHAR(3)│
                        │ category_name    VARCHAR  │
                        │ department       VARCHAR  │
                        └────────────┬─────────────┘
                                     │
              "category_key"         │         "category_key"
          ┌──────────────────┐       │       ┌─────────────────┐
          │   DimProduct     │       │       │    DimStore      │
          ├──────────────────┤       │       ├─────────────────┤
          │ product_key PK   │       │       │ store_key PK    │
          │ upc Unique       │       │       │ store_id Unique │
          │ description      │       │       │ store_name      │
          │ size             │       │       │ city            │
          │ case_pack        │       │       │ zip_code        │
          │ commodity_code   │       │       │ zone            │
          │ item_number      │       │       │ is_urban        │
          │ category_key FK  │       │       │ weekly_volume   │
          └───────┬──────────┘       │       │ avg_income      │
                  │                  │       │ education_pct   │
   "product_key"  │                  │       │ poverty_pct     │
                  │    ┌─────────────┴──┐    │ avg_hh_size     │
                  ├────┤ FactWeekly     ├────┤ ethnic_diversity│
                  │    │ Sales          │    │ pop_density     │
                  │    ├────────────────┤    │ price_tier      │
                  │    │ sales_fact_id  │    │ age_under_9     │
                  │    │ product_key FK │    │ age_over_60     │
                  │    │ store_key FK   │    │ working_women   │
                  │    │ time_key FK    │    └─────────────────┘
                  │    │ category_key FK│         "store_key"
                  │    │ promo_key FK   │
                  │    │ units_sold     │
                  │    │ unit_price     │
                  │    │ shelf_price    │    ┌─────────────────┐
                  │    │ price_qty      │    │   DimTime       │
                  │    │ revenue        │    ├─────────────────┤
                  │    │ gross_profit   │    │ time_key PK     │
                  │    │ profit_margin  │    │ week_id         │
                  │    └───────┬────────┘    │ week_start_date │
                  │            │             │ week_end_date   │
                  │   "promo_key"            │ month           │
                  │            │             │ month_name      │
          ┌───────┴────────┐   │             │ quarter         │
          │ DimPromotion   │   │             │ year            │
          ├────────────────┤   │             │ fiscal_year     │
          │ promo_key PK   ├───┘             │ is_holiday_week │
          │ deal_code      │  "time_key"     └─────────────────┘
          │ deal_type      │
          │ is_promoted    │
          └────────────────┘
```

### 8.2 FactCustomerTraffic Star Schema (Supplementary)

```
    ┌──────────────┐     ┌──────────────────────┐     ┌──────────┐
    │   DimStore   ├─────┤ FactCustomerTraffic  ├─────┤ DimTime  │
    └──────────────┘     ├──────────────────────┤     └──────────┘
     "store_key"         │ traffic_fact_id PK   │      "time_key"
                         │ store_key FK         │
                         │ time_key FK          │
                         │ total_customers      │
                         │ grocery_count        │
                         │ dairy_count          │
                         │ frozen_count         │
                         │ meat_count           │
                         │ produce_count        │
                         │ deli_count           │
                         │ bakery_count         │
                         │ pharmacy_count       │
                         │ beer_count           │
                         │ spirits_count        │
                         │ mvp_club_count       │
                         │ total_coupon_redemp  │
                         └──────────────────────┘
```

> **Note:** The Report 1 ER diagram (submitted and uploaded as an image) should be included in the final DOCX report as the official visual. The text diagrams above are a reference.

---

## 9. Data Source Summary

| Source | File Name(s) | Location | Description |
|:--|:--|:--|:--|
| Movement – Soft Drinks | wsdr.csv | DFF data/Movement/WSDR/ | Weekly item-level sales, 17.7M rows |
| Movement – Canned Soup | WCSO-Done.csv | DFF data/Movement/WCSO/ | Weekly item-level sales |
| Movement – Toothpaste | WTPA_done.csv | DFF data/Movement/WTPA/ | Weekly item-level sales |
| Movement – Crackers | Done-WCRA.csv | DFF data/Movement/WCRA/ | Weekly item-level sales |
| UPC – Soft Drinks | UPCSDR.csv | DFF data/UPC/ | Product master, ~2,200 UPCs |
| UPC – Canned Soup | UPCCSO.csv | DFF data/UPC/ | Product master |
| UPC – Toothpaste | UPCTPA.csv | DFF data/UPC/ | Product master |
| UPC – Crackers | UPCCRA.csv | DFF data/UPC/ | Product master |
| Demographics | DEMO.csv | DFF data/Demographics/ | 107 stores, 400+ attributes |
| Customer Counts | CCOUNT.csv | DFF data/Ccount/ | Store-level daily customer counts |
| DFF Codebook | Dominicks-Manual-and-Codebook.pdf | DFF data/ | Variable definitions and data dictionary |

---

*End of Report 2*
