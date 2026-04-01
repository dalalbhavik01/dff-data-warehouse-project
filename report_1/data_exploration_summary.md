# Data Exploration Summary — Dominick's Fine Foods (DFF)

> **Dataset**: Real retail grocery chain data from ~100 Dominick's stores in the Chicago metropolitan area (1989–1994), covering 3,500+ UPCs across 28 product categories.

---

## Introduction

Dominick's Finer Foods was a Chicago-area supermarket chain that operated approximately 100 stores throughout the metropolitan region. Between 1989 and 1994, the University of Chicago Booth School of Business (James M. Kilts Center for Marketing) partnered with Dominick's to conduct store-level research on shelf management and pricing. Randomized experiments were conducted in over 25 product categories across the 100-store chain. The resulting dataset — approximately 5 GB of store-level scanner data — is one of the most comprehensive publicly available retail datasets, covering weekly unit sales, retail prices, profit margins, deal codes, customer traffic, and store demographics (Kilts Center, 2013).

This data exploration summary documents our analysis of the OLTP source files that will serve as the foundation for the DFF data warehouse. The analysis covers all CSV files across four data categories: Movement (weekly sales), UPC (product master), Customer Counts, and Store Demographics.

### OLTP Source File Metadata

The DFF dataset consists of the following OLTP (Online Transaction Processing) source files, organized into two categories as described in the Dominick's Data Manual:

| Category | File Type | # Files | Total Rows | Description |
|----------|-----------|---------|------------|-------------|
| **General** | Customer Count (CCOUNT) | 1 | 327,045 | Store traffic and coupon usage by store and department |
| **General** | Demographics (DEMO) | 1 | 108 | Store-level demographics from 1990 US Census |
| **Category-Specific** | Movement (W*xxx*) | 24 | 134,881,958 | Weekly sales by UPC, store, and week for each product category |
| **Category-Specific** | UPC (UPC*xxx*) | 28 | ~14,000 | Product master data (name, size, brand) for each category |
| | **Total** | **54** | **~135,223,000** | |

---

## Directory Structure

```
DFF data - zipped/
├── Ccount/          → Customer count data (by store, by department, weekly)
├── Demographics/    → Store-level demographic & competitive data
├── Movement/        → Weekly store-level sales transactions (by UPC)
│   ├── WBJC/, WCHE/, WCIG/, WCOO/, WCRA/, WCSO/, WDID/, WFEC/,
│   │   WFRD/, WFRE/, WFRJ/, WFSF/, WGRO/, WLND/, WSDR/, WSOA/,
│   │   WTBR/, WTNA/, WTPA/, WTTI/
│   └── backup-Movement/ (WANA, WBAT, WBER, WCER)
└── UPC/             → Product master data (one file per category)
```

---

## 1. Movement Files (Weekly Store-UPC Sales)

**Purpose**: Weekly sales/movement data at the store-UPC level. Each file represents one product category.

| Column | Data Type | Description |
|--------|-----------|-------------|
| `UPC` | int64 | Universal Product Code (links to UPC files) |
| `STORE` | int64 | Store identifier (links to DEMO) |
| `WEEK` | int64 | Week number (DFF proprietary; week 1 ≈ mid-Sep 1989) |
| `MOVE` | int64 | Units sold (movement) during the week |
| `QTY` | int64 | Number of units for the listed price (e.g., 2-for-$3 → QTY=2) |
| `PRICE` | float64 | Shelf price during the week |
| `SALE` | object | Sale/deal flag: `B` = bonus buy, `C` = coupon, `S` = sale; NaN = no promotion |
| `PROFIT` | float64 | Gross profit for that week |
| `OK` | int64 | Data quality flag (1 = valid observation) |

**Sample (from WGRO – Grooming Products):**

| UPC | STORE | WEEK | MOVE | QTY | PRICE | SALE | PROFIT | OK |
|-----|-------|------|------|-----|-------|------|--------|----|
| 707300856 | 77 | 128 | 0 | 1 | 0.00 | NaN | 0.00 | 1 |
| 707300856 | 77 | 132 | 1 | 1 | 3.49 | NaN | 1.15 | 1 |
| 1204400005 | 77 | 131 | 2 | 1 | 2.29 | B | 0.66 | 1 |

### Movement Files Inventory (24 files, ~134.9 million rows total)

| File | Category | Rows |
|------|----------|------|
| DONE-WCOO.csv | Cookies | 13,447,807 |
| WFRE-Done.csv | Frozen Entrees | 11,663,663 |
| wsdr.csv | Soft Drinks | 17,730,501 |
| Done-WCHE.csv | Cheeses | 9,427,395 |
| DONE-WANA.csv | Analgesics | 7,339,217 |
| WCSO-Done.csv | Canned Soup | 7,011,243 |
| wlnd.csv | Laundry Detergents | 6,742,910 |
| DONE-WCER.csv | Cereals | 6,602,582 |
| WTPA_done.csv | Toothpaste | 6,310,896 |
| DONE-WBJC.csv | Bottled Juices | 6,222,797 |
| Done-WCIG.csv | Cigarettes | 5,398,197 |
| WTBR_done.csv | Toothbrushes | 4,529,484 |
| WFSF-done.csv | Fabric Softeners | 4,122,487 |
| DONE-WBER.csv | Beer | 3,990,672 |
| WDID-Done.csv | Dish Detergent | 3,838,182 |
| WTNA_done.csv | Canned Tuna | 3,763,229 |
| Done-WCRA.csv | Crackers | 3,624,688 |
| WSOA.csv | Soaps | 3,310,695 |
| WFRJ.csv | Frozen Juices | 3,156,545 |
| WGRO.csv | Grooming Products | 2,016,291 |
| DONE-WBAT.csv | Bath Soap | 1,644,557 |
| WTTI.csv | Toilet Tissue | 1,627,284 |
| WFEC.csv | Front End Candies | 797,921 |
| WFRD.csv | Frozen Dinners | 562,715 |

### Data Quality Issues — Movement
- **`SALE` column**: Mostly NaN (~90%+ of rows); valid values are `B`, `C`, `S`
- **`PRICE` = 0.00**: Some rows have zero price, indicating missing/unavailable pricing
- **`MOVE` = 0**: Many rows show zero movement (product stocked but not sold that week)
- **`OK` flag**: Should filter to `OK = 1` for reliable data
- **`WEEK` encoding**: Proprietary week IDs (range ~128–400+); requires mapping to calendar dates

---

## 2. UPC Files (Product Master Data)

**Purpose**: Product-level reference data. Each file matches a corresponding Movement file by category code.

| Column | Data Type | Description |
|--------|-----------|-------------|
| `COM_CODE` | int64 | Commodity/company code (manufacturer/brand grouping) |
| `UPC` | int64 | Universal Product Code (join key to Movement) |
| `DESCRIP` | object | Product description (e.g., "OLD SPICE PUMP ORIGI") |
| `SIZE` | object | Package size (e.g., "7 OZ", "12 OZ", "1 CT") |
| `CASE` | int64 | Case pack quantity |
| `NITEM` | int64 | Internal item number |

> **Note**: Column order varies slightly across UPC files (some have `NITEM` second, others last; one file `UPCPTW` includes an extra `WSTART` column).

**Sample (from UPCGRO – Grooming Products):**

| COM_CODE | NITEM | UPC | DESCRIP | SIZE | CASE |
|----------|-------|-----|---------|------|------|
| 972 | 6570051 | 707300856 | BRUT 33 SPLSH LOT W/ | 7 OZ | 6 |
| 969 | 6428441 | 1204400005 | OLD SPICE PUMP ORIGI | 1.75 O | 6 |

### UPC Files Inventory (28 files)

| File | Category | Rows (UPCs) |
|------|----------|-------------|
| UPCSHA.csv | Shampoos | 2,713 |
| UPCSDR.csv | Soft Drinks | 1,746 |
| UPCGRO.csv | Grooming Products | 1,599 |
| UPCCOO.csv | Cookies | 1,276 |
| UPCCHE.csv | Cheeses | 1,181 |
| UPCFRE.csv | Frozen Entrees | 900 |
| UPCCER.csv | Cereals | 871 |
| UPCCIG.csv | Cigarettes | 652 |
| UPCTPA.csv | Toothpaste | 608 |
| UPCLND.csv | Laundry Detergents | 582 |
| UPCANA.csv | Analgesics | 520 |
| UPCFEC.csv | Front End Candies | 505 |
| UPCCSO.csv | Canned Soup | 453 |
| UPCTBR.csv | Toothbrushes | 431 |
| UPCSNA.csv | Snack Crackers | 425 |
| UPCBJC.csv | Bottled Juices | 408 |
| UPCBER.csv | Beer | 384 |
| UPCBAT.csv | Bath Soap | 378 |
| UPCSOA.csv | Soaps | 337 |
| UPCFSF.csv | Fabric Softeners | 318 |
| UPCCRA.csv | Crackers | 305 |
| UPCDID.csv | Dish Detergent | 287 |
| UPCFRD.csv | Frozen Dinners | 283 |
| UPCTNA.csv | Canned Tuna | 278 |
| UPCFRJ.csv | Frozen Juices | 175 |
| UPCPTW.csv | Paper Towels | 164 |
| UPCTTI.csv | Toilet Tissue | 128 |
| UPCOAT.csv | Oatmeal | 96 |

### Data Quality Issues — UPC
- **Encoding**: Files require `latin-1` / `cp1252` encoding (not UTF-8)
- **`DESCRIP`**: Truncated product descriptions (max ~20 chars); some include leading `#` or `~`
- **`SIZE`**: Inconsistent formats (e.g., "7 OZ", "1.75 O", "13.5", "EACH", "24/12O")
- **Column order variability**: `NITEM` position varies; `UPCPTW` has extra `WSTART` column

---

## 3. CCOUNT File (Customer Counts)

**Purpose**: Daily customer transaction counts by store and department. 327,000+ rows × 61 columns.

| Key Columns | Description |
|-------------|-------------|
| `STORE` | Store number |
| `DATE` | Date of observation (corrupted in original; `#VALUE!` in Copy) |
| `WEEK` | Week number (range: -88 to 398; negative = pre-dataset period) |
| `GROCERY` | Customer count in Grocery dept |
| `DAIRY` | Customer count in Dairy dept |
| `FROZEN` | Customer count in Frozen dept |
| `MEAT` | Customer count in Meat dept |
| `PRODUCE` | Customer count in Produce dept |
| `BAKERY` | Customer count in Bakery dept |
| `DELI` | Customer count in Deli dept |
| `PHARMACY` | Customer count in Pharmacy dept |
| `BEER`, `WINE`, `SPIRITS` | Liquor department counts |
| `CUSTCOUN` | Total customer count |
| `MVPCLUB` | MVP Club member transactions |
| `*COUP` columns | Coupon redemptions by department (e.g., `GROCCOUP`, `MEATCOUP`) |

**Sample (valid data):**

| STORE | DATE | GROCERY | DAIRY | CUSTCOUN | WEEK |
|-------|------|---------|-------|----------|------|
| 1 | (corrupted) | 15255.79 | 3536.85 | 1505.28 | 179 |
| 1 | (corrupted) | 15457.80 | 3626.97 | 1630.26 | 189 |

### Data Quality Issues — CCOUNT
- **`DATE` column**: Corrupted/garbled encoding in original file; shows `#VALUE!` in the Copy version — **major quality gap**
- **`STORE = 0` rows**: Header/summary rows mixed with data (first ~500 rows have STORE = 0)
- **Dots (`.`) as placeholders**: Many columns use `.` instead of null/NaN for missing values
- **Negative WEEK values**: Weeks range from -88 to 398; negatives likely indicate pre-tracking period
- **Columns as `object` type**: Many numeric columns stored as strings due to `.` placeholders

---

## 4. DEMO File (Store Demographics)

**Purpose**: Store-level attributes including location, demographics, competition, and pricing tier. 108 rows (one per store) × 510 columns.

### Key Column Groups

| Group | Example Columns | Description |
|-------|----------------|-------------|
| **Identity** | `STORE`, `NAME`, `MMID` | Store number, name, market maker ID |
| **Location** | `CITY`, `ZIP`, `LAT`, `LONG` | Geographic data |
| **Operations** | `WEEKVOL`, `ZONE` | Weekly volume, pricing zone (1–10) |
| **Demographics** | `AGE9`, `AGE60`, `ETHNIC`, `EDUC`, `INCOME`, `POVERTY` | Census-area demographics |
| **Household** | `HSIZEAVG`, `HSIZE1`–`HSIZE567`, `HHSINGLE`, `HHLARGE` | Household composition |
| **Shopper Style** | `SHPCONS`, `SHPHURR`, `SHPAVID`, `SHPKSTR` | Shopper segment proportions |
| **Competition** | `CUBDIST`, `OMNIDIST`, `DDIST1`–`DDIST10` | Distance/volume of competitors |
| **Elasticities** | `SELAS1`–`SELAS24`, `NELAS1`–`NELAS18` | Price elasticity estimates |
| **Pricing Tier** | `PRICLOW`, `PRICMED`, `PRICHIGH` | Binary store pricing tier flags |
| **Urban/Density** | `URBAN`, `DENSITY` | Urban flag, population density |

**Sample:**

| STORE | NAME | CITY | ZIP | ZONE | WEEKVOL | INCOME | URBAN |
|-------|------|------|-----|------|---------|--------|-------|
| 2 | DOMINICKS 2 | RIVER FOREST | 60305 | 1 | 350 | 10.55 | 1 |
| 4 | DOMINICKS 4 | PARK RIDGE | 60068 | 2 | 300 | 10.65 | 0 |
| 5 | DOMINICKS 5 | PALATINE | 60067 | 2 | 550 | 10.92 | 0 |

### Data Quality Issues — DEMO
- **23 nulls in `NAME` and `CITY`**: Some stores lack name/city data
- **Dots (`.`) as placeholders**: First row uses `.` for all numeric fields (looks like a header/template row)
- **`STORE` as string/object**: Instead of integer, due to the `.` placeholder in first row
- **510 columns**: Many elasticity/competition columns; most are niche and may not be needed for the warehouse
- **`LAT`/`LONG` format**: Non-standard (e.g., 419081 instead of 41.9081) — scaled by 10,000

---

## 5. Category Code Mapping

The dataset is organized by 3-letter product category codes. Each category has a matching Movement file (`W<code>.csv`) and UPC file (`UPC<code>.csv`):

| Code | Category | Movement File | UPC File |
|------|----------|---------------|----------|
| ANA | Analgesics | DONE-WANA.csv | UPCANA.csv |
| BAT | Bath Soap | DONE-WBAT.csv | UPCBAT.csv |
| BER | Beer | DONE-WBER.csv | UPCBER.csv |
| BJC | Bottled Juices | DONE-WBJC.csv | UPCBJC.csv |
| CER | Cereals | DONE-WCER.csv | UPCCER.csv |
| CHE | Cheeses | Done-WCHE.csv | UPCCHE.csv |
| CIG | Cigarettes | Done-WCIG.csv | UPCCIG.csv |
| COO | Cookies | DONE-WCOO.csv | UPCCOO.csv |
| CRA | Crackers | Done-WCRA.csv | UPCCRA.csv |
| CSO | Canned Soup | WCSO-Done.csv | UPCCSO.csv |
| DID | Dish Detergent | WDID-Done.csv | UPCDID.csv |
| FEC | Front End Candies | WFEC.csv | UPCFEC.csv |
| FRD | Frozen Dinners | WFRD.csv | UPCFRD.csv |
| FRE | Frozen Entrees | WFRE-Done.csv | UPCFRE.csv |
| FRJ | Frozen Juices | WFRJ.csv | UPCFRJ.csv |
| FSF | Fabric Softeners | WFSF-done.csv | UPCFSF.csv |
| GRO | Grooming Products | WGRO.csv | UPCGRO.csv |
| LND | Laundry Detergents | wlnd.csv | UPCLND.csv |
| OAT | Oatmeal | *(not available)* | UPCOAT.csv |
| PTW | Paper Towels | *(not available)* | UPCPTW.csv |
| SDR | Soft Drinks | wsdr.csv | UPCSDR.csv |
| SHA | Shampoos | *(not available)* | UPCSHA.csv |
| SNA | Snack Crackers | *(not available)* | UPCSNA.csv |
| SOA | Soaps | WSOA.csv | UPCSOA.csv |
| TBR | Toothbrushes | WTBR_done.csv | UPCTBR.csv |
| TNA | Canned Tuna | WTNA_done.csv | UPCTNA.csv |
| TPA | Toothpaste | WTPA_done.csv | UPCTPA.csv |
| TTI | Toilet Tissue | WTTI.csv | UPCTTI.csv |

> **Gap**: 4 categories (OAT, PTW, SHA, SNA) have UPC files but **no matching Movement file** in the current dataset.

---

## 6. Key Relationships (Join Keys)

```
Movement.UPC ──────→ UPC.UPC        (product details)
Movement.STORE ────→ DEMO.STORE     (store demographics)
Movement.WEEK ─────→ CCOUNT.WEEK    (customer counts)
Movement.STORE + WEEK → CCOUNT.STORE + WEEK  (store-week customer traffic)
Category code is implicit from the filename (not a column in Movement/UPC)
```

---

## 7. Summary of Critical Data Quality Issues

| Issue | File(s) | Severity | Impact |
|-------|---------|----------|--------|
| `DATE` column corrupted | CCOUNT | **High** | Cannot derive calendar dates from CCOUNT directly; must use WEEK mapping |
| Dots (`.`) as missing values | CCOUNT, DEMO | Medium | Requires cleaning; columns read as `object` instead of numeric |
| `SALE` mostly NaN | Movement | Medium | Promotion analysis limited; only ~10% of rows have deal flags |
| `PRICE = 0` rows | Movement | Medium | Must filter or impute; skews revenue calculations |
| File encoding (non-UTF-8) | UPC, CCOUNT | Low | Use `latin-1` or `cp1252` encoding |
| Category not a column | Movement, UPC | Medium | Must derive from filename; needs engineering for the warehouse |
| 4 categories missing Movement data | OAT, PTW, SHA, SNA | Medium | No sales data for these; UPC info only |
| `WEEK` ↔ calendar date mapping | All | High | Proprietary week IDs; Week 1 ≈ 14-Sep-1989; need formula or lookup |
| `LAT`/`LONG` scaled × 10,000 | DEMO | Low | Transform to standard decimal degrees |
| 23 stores missing `NAME`/`CITY` | DEMO | Low | Minor; `ZIP` and coordinates still available |

---

## 8. Statistical Analysis of Key Categories

> Statistical summaries computed from a sample of the first 50,000 rows per category file to validate data quality and support business question feasibility.

### 8.1 Sales Volume & Pricing by Category

| Category | Avg Units Sold (MOVE) | Median Units | Max Units | Avg Price ($) | Median Price ($) | Avg Profit ($) |
|----------|----------------------|-------------|-----------|---------------|-----------------|----------------|
| Soft Drinks (SDR) | 17.07 | 0.0 | 4,637 | 6.63 | 6.99 | -8.28 |
| Cereals (CER) | 9.51 | 8.0 | 1,229 | 2.22 | 2.11 | 8.48 |
| Cheeses (CHE) | 5.74 | 3.0 | 295 | 2.48 | 2.45 | 22.66 |
| Beer (BER) | 4.79 | 2.0 | 124 | 3.20 | 3.49 | 16.44 |
| Canned Soup (CSO) | 1.68 | 0.0 | 41 | 1.33 | 1.09 | 12.92 |
| Grooming (GRO) | 0.21 | 0.0 | 21 | 2.97 | 2.59 | 4.45 |

### 8.2 Promotion Effectiveness Analysis

| Category | % Rows Promoted | Avg MOVE (Promoted) | Avg MOVE (Non-Promoted) | Sales Lift (x) | Dominant Deal Type |
|----------|----------------|---------------------|------------------------|----------------|-------------------|
| **Soft Drinks** | **23.1%** | **59.25** | **4.37** | **13.6×** | S (Sale) & B (Bonus) |
| Cheeses | 18.2% | 11.46 | 4.47 | 2.6× | B (Bonus Buy) |
| Canned Soup | 7.5% | 4.79 | 1.43 | 3.4× | B (Bonus Buy) |
| Cereals | 5.7% | 23.68 | 8.66 | 2.7× | B (Bonus Buy) |
| Grooming | 2.1% | 1.52 | 0.18 | 8.4× | B (Bonus Buy) |
| Beer | 0.2% | 2.42 | 4.79 | 0.5× | B (Bonus Buy) |

> **Key Finding**: Promotions dramatically increase unit sales in most categories. Soft Drinks show the highest promotion intensity (23.1%) and the largest absolute sales lift (13.6×). Beer is an anomaly — promotions are rare (0.2%) and promoted items actually sell fewer units, suggesting price-insensitive or differently-promoted products.

### 8.3 Store Demographics Summary

| Metric | Value |
|--------|-------|
| Total stores | 107 |
| Urban stores | 32 (30%) |
| Suburban stores | 75 (70%) |
| Pricing zones | 15 distinct zones |
| Avg weekly volume | 464.8 units |
| Weekly volume range | 250 – 875 |
| Avg area income (log) | 10.61 (σ = 0.28) |

### 8.4 Customer Traffic Summary (CCOUNT)

| Metric | Value |
|--------|-------|
| Total valid records | 326,235 |
| Unique stores | 132 |
| Avg total customer count (CUSTCOUN) | 2,848.4 |
| Median customer count | 2,703.0 |
| Week coverage | -88 to 398 (spanning ~9 years) |

### 8.5 Key Statistical Findings

1. **Promotions are highly effective**: Across all categories except Beer, promoted items sell 2.6× to 13.6× more units than non-promoted items. This validates the importance of promotion-related business questions (Q6, Q8).

2. **Soft Drinks dominate volume**: SDR has the highest average unit sales (17.07) and the largest single-week movement (4,637 units), making it ideal for trend analysis (Q1, Q8).

3. **Profit variance is significant**: Soft Drinks show *negative* average profit (-$8.28), suggesting loss-leader pricing strategies. Cheeses have the highest average profit ($22.66). This supports profit analysis questions (Q5, Q15).

4. **Store heterogeneity**: With 15 pricing zones, 30/70 urban-suburban split, and wide weekly volume range (250–875), there is rich variation for cross-store comparative analysis (Q7, Q13, Q15).

5. **Zero-movement rows are common**: Many rows show MOVE = 0 (medians of 0.0 for SDR, CSO, GRO), indicating products stocked but not sold — important for data cleaning in the warehouse.

6. **Deal types vary by category**: Bonus Buys (B) dominate most categories, but Soft Drinks have a nearly equal split between Sales (S) and Bonus Buys (B), enabling deal-type comparison analysis (Q6).
