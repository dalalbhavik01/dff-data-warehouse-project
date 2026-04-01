# Data Warehouse Schema — Dominick's Fine Foods

> Star schema design based on DFF dataset exploration and 15 OLAP business questions. Optimized for weekly store-level sales analysis across product categories, stores, time, and promotions.

---

## Overview

```
                  ┌─────────────┐
                  │  DimProduct  │
                  └──────┬──────┘
                         │
┌──────────┐    ┌────────┴────────┐    ┌──────────────┐
│ DimStore  ├────┤  FactWeekly     ├────┤ DimPromotion │
└──────────┘    │  Sales          │    └──────────────┘
                └────────┬────────┘
                         │
                  ┌──────┴──────┐     ┌──────────────┐
                  │  DimTime     │     │ DimCategory  │
                  └─────────────┘     └──────────────┘
                                            │
                  ┌─────────────┐           │
                  │ FactCustomer├───────────┘
                  │ Traffic     │
                  └─────────────┘
```

---

## Fact Tables

### Fact Table 1: `FactWeeklySales`

The central fact table containing weekly store-UPC-level sales transactions. One row per UPC × Store × Week.

| Column | Data Type | Description | Source |
|--------|-----------|-------------|--------|
| `sales_fact_id` | INT (PK, surrogate) | Auto-generated surrogate key | Generated |
| `product_key` | INT (FK → DimProduct) | Product dimension key | Mapped from `UPC` |
| `store_key` | INT (FK → DimStore) | Store dimension key | Mapped from `STORE` |
| `time_key` | INT (FK → DimTime) | Time dimension key | Mapped from `WEEK` |
| `category_key` | INT (FK → DimCategory) | Category dimension key | Derived from source filename |
| `promotion_key` | INT (FK → DimPromotion) | Promotion dimension key | Mapped from `SALE` |
| `units_sold` | INT | Units moved/sold | `MOVE` from Movement files |
| `unit_price` | DECIMAL(8,2) | Price per unit (`PRICE / QTY`) | Computed: `PRICE / QTY` |
| `shelf_price` | DECIMAL(8,2) | Listed shelf price | `PRICE` from Movement files |
| `price_qty` | INT | Quantity for listed price | `QTY` from Movement files |
| `revenue` | DECIMAL(12,2) | Computed revenue (`MOVE × PRICE / QTY`) | Computed |
| `gross_profit` | DECIMAL(10,2) | Gross profit | `PROFIT` from Movement files |
| `profit_margin_pct` | DECIMAL(5,2) | Profit margin % (`PROFIT / revenue × 100`) | Computed |
| `is_valid` | BOOLEAN | Data quality flag | `OK` from Movement files |

**Primary Key**: `sales_fact_id`
**Grain**: One row per UPC × Store × Week × Category
**Source**: All 24 Movement CSV files (134.9M total rows)

---

### Fact Table 2: `FactCustomerTraffic`

Store-level weekly customer traffic counts by department.

| Column | Data Type | Description | Source |
|--------|-----------|-------------|--------|
| `traffic_fact_id` | INT (PK, surrogate) | Auto-generated surrogate key | Generated |
| `store_key` | INT (FK → DimStore) | Store dimension key | `STORE` from CCOUNT |
| `time_key` | INT (FK → DimTime) | Time dimension key | `WEEK` from CCOUNT |
| `grocery_count` | DECIMAL(10,2) | Customer count – Grocery | `GROCERY` from CCOUNT |
| `dairy_count` | DECIMAL(10,2) | Customer count – Dairy | `DAIRY` from CCOUNT |
| `frozen_count` | DECIMAL(10,2) | Customer count – Frozen | `FROZEN` from CCOUNT |
| `meat_count` | DECIMAL(10,2) | Customer count – Meat | `MEAT` from CCOUNT |
| `produce_count` | DECIMAL(10,2) | Customer count – Produce | `PRODUCE` from CCOUNT |
| `deli_count` | DECIMAL(10,2) | Customer count – Deli | `DELI` from CCOUNT |
| `bakery_count` | DECIMAL(10,2) | Customer count – Bakery | `BAKERY` from CCOUNT |
| `pharmacy_count` | DECIMAL(10,2) | Customer count – Pharmacy | `PHARMACY` from CCOUNT |
| `beer_count` | DECIMAL(10,2) | Customer count – Beer | `BEER` from CCOUNT |
| `wine_count` | DECIMAL(10,2) | Customer count – Wine | `WINE` from CCOUNT |
| `spirits_count` | DECIMAL(10,2) | Customer count – Spirits | `SPIRITS` from CCOUNT |
| `total_customers` | DECIMAL(10,2) | Total customer count | `CUSTCOUN` from CCOUNT |
| `mvp_club_count` | DECIMAL(10,2) | MVP loyalty program transactions | `MVPCLUB` from CCOUNT |
| `total_coupon_redemptions` | DECIMAL(10,2) | Sum of all coupon columns | Computed from `*COUP` columns |

**Primary Key**: `traffic_fact_id`
**Grain**: One row per Store × Week
**Source**: `Ccount/CCOUNT.csv` (327K rows)

---

## Dimension Tables

### DimProduct

Product master information. One row per UPC.

| Column | Data Type | Description | Source |
|--------|-----------|-------------|--------|
| `product_key` | INT (PK, surrogate) | Auto-generated surrogate key | Generated |
| `upc` | BIGINT (NK) | Universal Product Code (natural key) | `UPC` from UPC files |
| `description` | VARCHAR(100) | Product description | `DESCRIP` from UPC files |
| `size` | VARCHAR(20) | Package size | `SIZE` from UPC files |
| `case_pack` | INT | Case pack quantity | `CASE` from UPC files |
| `commodity_code` | INT | Manufacturer/company code | `COM_CODE` from UPC files |
| `item_number` | BIGINT | Internal DFF item number | `NITEM` from UPC files |
| `category_key` | INT (FK → DimCategory) | Category dimension key | Derived from source filename |

**Primary Key**: `product_key`
**Natural Key**: `upc`
**Source**: All 28 UPC CSV files (~14,000 total UPCs)

**Cleaning/Transformations**:
- Remove leading `#` and `~` from `DESCRIP`
- Standardize `SIZE` format (e.g., "1.75 O" → "1.75 OZ")
- Assign `category_key` based on source filename (e.g., UPCCER.csv → Cereals)

---

### DimStore

Store-level attributes and demographics. One row per store.

| Column | Data Type | Description | Source |
|--------|-----------|-------------|--------|
| `store_key` | INT (PK, surrogate) | Auto-generated surrogate key | Generated |
| `store_id` | INT (NK) | Original store number (natural key) | `STORE` from DEMO |
| `store_name` | VARCHAR(50) | Store name | `NAME` from DEMO |
| `city` | VARCHAR(50) | City name | `CITY` from DEMO |
| `zip_code` | VARCHAR(10) | ZIP code | `ZIP` from DEMO |
| `latitude` | DECIMAL(8,4) | Latitude (decimal degrees) | `LAT / 10000` from DEMO |
| `longitude` | DECIMAL(8,4) | Longitude (decimal degrees) | `LONG / 10000` from DEMO |
| `zone` | INT | Pricing zone (1–10) | `ZONE` from DEMO |
| `weekly_volume` | INT | Average weekly volume | `WEEKVOL` from DEMO |
| `is_urban` | BOOLEAN | Urban location flag | `URBAN` from DEMO |
| `avg_income` | DECIMAL(6,2) | Average area income (log scale) | `INCOME` from DEMO |
| `education_pct` | DECIMAL(5,4) | % with higher education | `EDUC` from DEMO |
| `poverty_pct` | DECIMAL(5,4) | % below poverty line | `POVERTY` from DEMO |
| `avg_household_size` | DECIMAL(4,2) | Average household size | `HSIZEAVG` from DEMO |
| `ethnic_diversity` | DECIMAL(5,4) | Ethnic diversity index | `ETHNIC` from DEMO |
| `population_density` | DECIMAL(10,7) | Population density | `DENSITY` from DEMO |
| `price_tier` | VARCHAR(10) | Price tier: Low / Medium / High | Derived from `PRICLOW`, `PRICMED`, `PRICHIGH` |
| `age_under_9_pct` | DECIMAL(5,4) | % population under 9 | `AGE9` from DEMO |
| `age_over_60_pct` | DECIMAL(5,4) | % population over 60 | `AGE60` from DEMO |
| `working_women_pct` | DECIMAL(5,4) | % working women | `WORKWOM` from DEMO |

**Primary Key**: `store_key`
**Natural Key**: `store_id`
**Source**: `Demographics/DEMO.csv` (107 valid rows)

**Cleaning/Transformations**:
- Filter out the header/template row (STORE = `.`)
- Convert `LAT` and `LONG` by dividing by 10,000
- Derive `price_tier` from binary flags: if `PRICLOW = 1` → 'Low', `PRICMED = 1` → 'Medium', `PRICHIGH = 1` → 'High'
- Cast all demographic percentages from string to DECIMAL
- Handle 23 null `NAME`/`CITY` values (fill with 'UNKNOWN' or derive from ZIP)

---

### DimTime

Time dimension derived from the proprietary DFF week numbering. One row per week.

| Column | Data Type | Description | Source |
|--------|-----------|-------------|--------|
| `time_key` | INT (PK, surrogate) | Auto-generated surrogate key | Generated |
| `week_id` | INT (NK) | DFF proprietary week number | `WEEK` from Movement files |
| `week_start_date` | DATE | Calculated start date of the week | Engineered: `1989-09-14 + (week_id - 1) × 7 days` |
| `week_end_date` | DATE | End date of the week | `week_start_date + 6 days` |
| `month` | INT | Month number (1–12) | Derived from `week_start_date` |
| `month_name` | VARCHAR(15) | Month name | Derived from `week_start_date` |
| `quarter` | INT | Quarter (1–4) | Derived from `week_start_date` |
| `year` | INT | Year (1989–1997) | Derived from `week_start_date` |
| `fiscal_year` | INT | DFF fiscal year | Engineered (if applicable) |
| `is_holiday_week` | BOOLEAN | Holiday week flag | Engineered (Thanksgiving, Christmas, etc.) |

**Primary Key**: `time_key`
**Natural Key**: `week_id`
**Source**: Derived/engineered from WEEK values in Movement files (range ~1–400)

**Cleaning/Transformations**:
- Week 1 ≈ September 14, 1989 (per DFF codebook)
- Calculate `week_start_date = DATE('1989-09-14') + (week_id - 1) * 7`
- Derive month, quarter, year from the computed date
- Flag known US retail holiday weeks (Thanksgiving, Christmas, July 4th, Memorial Day, Labor Day)

---

### DimPromotion

Promotion/deal type dimension. One row per promotion type.

| Column | Data Type | Description | Source |
|--------|-----------|-------------|--------|
| `promotion_key` | INT (PK, surrogate) | Auto-generated surrogate key | Generated |
| `deal_code` | CHAR(1) | Original deal flag | `SALE` from Movement files |
| `deal_type` | VARCHAR(20) | Descriptive name | Mapped from `SALE` values |
| `is_promoted` | BOOLEAN | Whether any deal was active | `SALE IS NOT NULL` |

**Primary Key**: `promotion_key`
**Source**: `SALE` column from Movement files

**Reference Mapping**:

| deal_code | deal_type | is_promoted |
|-----------|-----------|-------------|
| NULL | No Promotion | FALSE |
| B | Bonus Buy | TRUE |
| C | Coupon | TRUE |
| S | Sale/Discount | TRUE |

---

### DimCategory

Product category dimension, derived from the file naming convention. One row per product category.

| Column | Data Type | Description | Source |
|--------|-----------|-------------|--------|
| `category_key` | INT (PK, surrogate) | Auto-generated surrogate key | Generated |
| `category_code` | CHAR(3) (NK) | 3-letter category code | Derived from Movement/UPC filenames |
| `category_name` | VARCHAR(50) | Full category name | Mapped from codebook |
| `department` | VARCHAR(30) | High-level department grouping | Engineered |

**Primary Key**: `category_key`
**Natural Key**: `category_code`
**Source**: Derived from file naming convention (28 categories)

**Full Category Reference**:

| category_code | category_name | department |
|---------------|--------------|------------|
| ANA | Analgesics | Health & Beauty |
| BAT | Bath Soap | Health & Beauty |
| BER | Beer | Beverages |
| BJC | Bottled Juices | Beverages |
| CER | Cereals | Grocery |
| CHE | Cheeses | Dairy |
| CIG | Cigarettes | Tobacco |
| COO | Cookies | Snacks |
| CRA | Crackers | Snacks |
| CSO | Canned Soup | Grocery |
| DID | Dish Detergent | Household |
| FEC | Front End Candies | Snacks |
| FRD | Frozen Dinners | Frozen |
| FRE | Frozen Entrees | Frozen |
| FRJ | Frozen Juices | Beverages |
| FSF | Fabric Softeners | Household |
| GRO | Grooming Products | Health & Beauty |
| LND | Laundry Detergents | Household |
| OAT | Oatmeal | Grocery |
| PTW | Paper Towels | Household |
| SDR | Soft Drinks | Beverages |
| SHA | Shampoos | Health & Beauty |
| SNA | Snack Crackers | Snacks |
| SOA | Soaps | Health & Beauty |
| TBR | Toothbrushes | Health & Beauty |
| TNA | Canned Tuna | Grocery |
| TPA | Toothpaste | Health & Beauty |
| TTI | Toilet Tissue | Household |

---

## Data Cleaning & Transformation Summary

| Step | Description | Applies To |
|------|-------------|------------|
| 1 | Read all CSV files with `latin-1` encoding | All files |
| 2 | Filter `OK = 1` rows from Movement files | FactWeeklySales |
| 3 | Derive `category_code` from source filenames | FactWeeklySales, DimProduct |
| 4 | Compute `revenue = MOVE × (PRICE / QTY)` | FactWeeklySales |
| 5 | Compute `unit_price = PRICE / QTY` | FactWeeklySales |
| 6 | Compute `profit_margin_pct = PROFIT / revenue × 100` | FactWeeklySales |
| 7 | Map SALE values to DimPromotion keys | FactWeeklySales |
| 8 | Map WEEK to calendar dates (`1989-09-14 + (WEEK-1) × 7`) | DimTime |
| 9 | Clean DEMO: filter header row, cast numeric columns | DimStore |
| 10 | Transform `LAT/10000`, `LONG/10000` to decimal degrees | DimStore |
| 11 | Derive `price_tier` from `PRICLOW/PRICMED/PRICHIGH` | DimStore |
| 12 | Clean UPC `DESCRIP`: strip leading `#` and `~` | DimProduct |
| 13 | Standardize UPC `SIZE` format | DimProduct |
| 14 | Replace `.` placeholders with NULL in CCOUNT | FactCustomerTraffic |
| 15 | Sum coupon columns to get `total_coupon_redemptions` | FactCustomerTraffic |
| 16 | Handle PRICE = 0 rows (filter or flag) | FactWeeklySales |

---

## Feasibility Validation

### FactWeeklySales — Measures

| Attribute | Source File | Column | Status |
|-----------|-----------|--------|--------|
| `units_sold` | Movement files | `MOVE` | ✅ Available |
| `shelf_price` | Movement files | `PRICE` | ✅ Available |
| `price_qty` | Movement files | `QTY` | ✅ Available |
| `unit_price` | Movement files | `PRICE / QTY` | 🔧 Engineered (division of two available columns) |
| `revenue` | Movement files | `MOVE × PRICE / QTY` | 🔧 Engineered (multiplication of available columns) |
| `gross_profit` | Movement files | `PROFIT` | ✅ Available |
| `profit_margin_pct` | Movement files | `PROFIT / revenue × 100` | 🔧 Engineered (ratio of available/engineered columns) |
| `is_valid` | Movement files | `OK` | ✅ Available |

### FactCustomerTraffic — Measures

| Attribute | Source File | Column | Status |
|-----------|-----------|--------|--------|
| `grocery_count` | CCOUNT.csv | `GROCERY` | ✅ Available (clean `.` → NULL) |
| `dairy_count` | CCOUNT.csv | `DAIRY` | ✅ Available (clean `.` → NULL) |
| `frozen_count` | CCOUNT.csv | `FROZEN` | ✅ Available (clean `.` → NULL) |
| `meat_count` | CCOUNT.csv | `MEAT` | ✅ Available (clean `.` → NULL) |
| `produce_count` | CCOUNT.csv | `PRODUCE` | ✅ Available (clean `.` → NULL) |
| `deli_count` | CCOUNT.csv | `DELI` | ✅ Available (clean `.` → NULL) |
| `bakery_count` | CCOUNT.csv | `BAKERY` | ✅ Available (clean `.` → NULL) |
| `pharmacy_count` | CCOUNT.csv | `PHARMACY` | ✅ Available (clean `.` → NULL) |
| `beer_count` | CCOUNT.csv | `BEER` | ✅ Available (clean `.` → NULL) |
| `wine_count` | CCOUNT.csv | `WINE` | ✅ Available (clean `.` → NULL) |
| `spirits_count` | CCOUNT.csv | `SPIRITS` | ✅ Available (clean `.` → NULL) |
| `total_customers` | CCOUNT.csv | `CUSTCOUN` | ✅ Available |
| `mvp_club_count` | CCOUNT.csv | `MVPCLUB` | ✅ Available (clean `.` → NULL) |
| `total_coupon_redemptions` | CCOUNT.csv | `*COUP` columns | 🔧 Engineered (sum of 15+ coupon columns) |

### DimProduct — Attributes

| Attribute | Source File | Column | Status |
|-----------|-----------|--------|--------|
| `upc` | UPC files | `UPC` | ✅ Available |
| `description` | UPC files | `DESCRIP` | ✅ Available (clean leading `#`/`~`) |
| `size` | UPC files | `SIZE` | ✅ Available (standardize format) |
| `case_pack` | UPC files | `CASE` | ✅ Available |
| `commodity_code` | UPC files | `COM_CODE` | ✅ Available |
| `item_number` | UPC files | `NITEM` | ✅ Available |
| `category_key` | UPC files | — | 🔧 Engineered (derived from source filename) |

### DimStore — Attributes

| Attribute | Source File | Column | Status |
|-----------|-----------|--------|--------|
| `store_id` | DEMO.csv | `STORE` | ✅ Available |
| `store_name` | DEMO.csv | `NAME` | ✅ Available (23 nulls) |
| `city` | DEMO.csv | `CITY` | ✅ Available (23 nulls) |
| `zip_code` | DEMO.csv | `ZIP` | ✅ Available |
| `latitude` | DEMO.csv | `LAT` | 🔧 Engineered (divide by 10,000) |
| `longitude` | DEMO.csv | `LONG` | 🔧 Engineered (divide by 10,000) |
| `zone` | DEMO.csv | `ZONE` | ✅ Available |
| `weekly_volume` | DEMO.csv | `WEEKVOL` | ✅ Available |
| `is_urban` | DEMO.csv | `URBAN` | ✅ Available |
| `avg_income` | DEMO.csv | `INCOME` | ✅ Available |
| `education_pct` | DEMO.csv | `EDUC` | ✅ Available |
| `poverty_pct` | DEMO.csv | `POVERTY` | ✅ Available |
| `avg_household_size` | DEMO.csv | `HSIZEAVG` | ✅ Available |
| `ethnic_diversity` | DEMO.csv | `ETHNIC` | ✅ Available |
| `population_density` | DEMO.csv | `DENSITY` | ✅ Available |
| `price_tier` | DEMO.csv | `PRICLOW/MED/HIGH` | 🔧 Engineered (map 3 binary flags → single label) |
| `age_under_9_pct` | DEMO.csv | `AGE9` | ✅ Available |
| `age_over_60_pct` | DEMO.csv | `AGE60` | ✅ Available |
| `working_women_pct` | DEMO.csv | `WORKWOM` | ✅ Available |

### DimTime — Attributes

| Attribute | Source File | Column | Status |
|-----------|-----------|--------|--------|
| `week_id` | Movement files | `WEEK` | ✅ Available |
| `week_start_date` | — | — | 🔧 Engineered (`1989-09-14 + (week_id - 1) × 7`) |
| `week_end_date` | — | — | 🔧 Engineered (`week_start_date + 6`) |
| `month` | — | — | 🔧 Engineered (from `week_start_date`) |
| `month_name` | — | — | 🔧 Engineered (from `week_start_date`) |
| `quarter` | — | — | 🔧 Engineered (from `week_start_date`) |
| `year` | — | — | 🔧 Engineered (from `week_start_date`) |
| `fiscal_year` | — | — | ⚠️ Gap (DFF fiscal calendar unknown; can approximate) |
| `is_holiday_week` | — | — | 🔧 Engineered (US federal holidays lookup) |

### DimPromotion — Attributes

| Attribute | Source File | Column | Status |
|-----------|-----------|--------|--------|
| `deal_code` | Movement files | `SALE` | ✅ Available |
| `deal_type` | Movement files | `SALE` | 🔧 Engineered (map B→Bonus Buy, C→Coupon, S→Sale) |
| `is_promoted` | Movement files | `SALE` | 🔧 Engineered (`SALE IS NOT NULL`) |

### DimCategory — Attributes

| Attribute | Source File | Column | Status |
|-----------|-----------|--------|--------|
| `category_code` | Filenames | — | 🔧 Engineered (extracted from Movement/UPC filenames) |
| `category_name` | Codebook | — | 🔧 Engineered (mapped from codebook/manual) |
| `department` | — | — | 🔧 Engineered (logical grouping of categories) |

### Feasibility Summary Counts

| Status | Count |
|--------|-------|
| ✅ Available (direct column) | 39 |
| 🔧 Engineered (derived/computed) | 21 |
| ⚠️ Gap (missing, requires assumption) | 1 (`fiscal_year`) |

> **Conclusion**: 98.4% of schema attributes are either directly available or can be reliably engineered from existing data. The only gap is `fiscal_year`, which can be approximated using calendar year or omitted.

---

## Schema–Business Question Traceability

This traceability matrix confirms every business question can be answered using the designed schema:

| BQ | Fact Table | Dimensions Needed | Key Measures | Key Attributes |
|----|-----------|-------------------|-------------|----------------|
| Q1 | FactWeeklySales | DimTime, DimCategory | units_sold | week_id, category_code='SDR' |
| Q2 | FactWeeklySales | DimStore, DimTime, DimCategory | revenue | store_id, week_id |
| Q3 | FactWeeklySales | DimCategory | units_sold | category_name |
| Q4 | FactWeeklySales | DimProduct, DimTime, DimCategory | units_sold | upc, week_id |
| Q5 | FactWeeklySales | DimStore, DimCategory | gross_profit | store_id |
| Q6 | FactWeeklySales | DimPromotion, DimCategory | units_sold | deal_type, is_promoted |
| Q7 | FactWeeklySales | DimStore, DimTime, DimCategory | revenue | is_urban, quarter |
| Q8 | FactWeeklySales + FactCustomerTraffic | DimStore, DimTime, DimPromotion | units_sold, total_customers | store_id, week_id, is_promoted |
| Q9 | FactWeeklySales | DimProduct, DimTime, DimCategory | units_sold | commodity_code, month |
| Q10 | FactWeeklySales | DimProduct, DimStore, DimTime, DimCategory | unit_price | upc, description, store_id |
| Q11 | FactWeeklySales | DimStore, DimTime, DimCategory | units_sold | store_id, week_id (running total) |
| Q12 | FactWeeklySales | DimStore, DimTime, DimCategory | revenue | store_id, week_id (ratio) |
| Q13 | FactWeeklySales | DimStore, DimCategory | revenue | store_id, avg_income, is_urban, zone |
| Q14 | FactWeeklySales | DimProduct, DimTime, DimCategory | units_sold | upc, description, week_id |
| Q15 | FactWeeklySales | DimStore, DimCategory | gross_profit | store_id, zone |

> **All 15 business questions are fully answerable** from the designed star schema without any additional data sources or structural changes.

---

## Notes for Future Reports (Reports 2–4)

This schema is designed as the foundation for the 3 upcoming implementation reports:

| Report | Focus | Schema Components Used |
|--------|-------|----------------------|
| **Report 2** — ETL & Physical Implementation | Build tables in SQL Server; load data via ETL | All dimension + fact table CREATE TABLE scripts; Data Cleaning & Transformation Summary (16 steps above) |
| **Report 3** — OLAP Queries & Analysis | Execute the 15 business questions as SQL queries | FactWeeklySales + all 5 dimensions; SQL sketches in `business_questions.md` |
| **Report 4** — Visualization & Reporting | Create dashboards and OLAP cubes | All tables; pivot/drill/slice operations per the OLAP operation types |
