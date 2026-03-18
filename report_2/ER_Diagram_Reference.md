# ER Diagram Reference — Report 2 (matches Report 1 submitted ERD)

Use this document to verify the star schema structure for your Visio/LucidChart diagrams.
The schema below matches the ER diagram already submitted in Report 1.

---

## Table Structures

### FactWeeklySales (Central Fact Table)
```
┌──────────────────────────────────────────┐
│           FactWeeklySales                │
├──────────────────────────────────────────┤
│ sales_fact_id  PK       INT             │
│ product_key    FK       INT   → DimProduct│
│ store_key      FK       INT   → DimStore  │
│ time_key       FK       INT   → DimTime   │
│ category_key   FK       INT   → DimCategory│
│ promotion_key  FK       INT   → DimPromo  │
│ units_sold               INT             │
│ unit_price               DECIMAL(8,2)    │
│ shelf_price              DECIMAL(8,2)    │
│ price_qty                INT             │
│ revenue                  DECIMAL(12,2)   │
│ gross_profit             DECIMAL(10,2)   │
│ profit_margin_pct        DECIMAL(5,2)    │
├──────────────────────────────────────────┤
│ Grain: 1 UPC × 1 Store × 1 Week        │
└──────────────────────────────────────────┘
```

### FactCustomerTraffic
```
┌──────────────────────────────────────────┐
│         FactCustomerTraffic              │
├──────────────────────────────────────────┤
│ traffic_fact_id PK      INT             │
│ store_key       FK      INT   → DimStore │
│ time_key        FK      INT   → DimTime  │
│ total_customers          DECIMAL(10,2)   │
│ grocery_count            DECIMAL(10,2)   │
│ dairy_count              DECIMAL(10,2)   │
│ frozen_count             DECIMAL(10,2)   │
│ meat_count               DECIMAL(10,2)   │
│ produce_count            DECIMAL(10,2)   │
│ deli_count               DECIMAL(10,2)   │
│ bakery_count             DECIMAL(10,2)   │
│ pharmacy_count           DECIMAL(10,2)   │
│ beer_count               DECIMAL(10,2)   │
│ spirits_count            DECIMAL(10,2)   │
│ mvp_club_count           DECIMAL(10,2)   │
│ total_coupon_redemptions DECIMAL(10,2)   │
├──────────────────────────────────────────┤
│ Grain: 1 Store × 1 Week                │
└──────────────────────────────────────────┘
```

### DimProduct
```
┌──────────────────────────────────────────┐
│              DimProduct                  │
├──────────────────────────────────────────┤
│ product_key   PK        INT             │
│ upc           Unique    BIGINT          │
│ description              VARCHAR(100)    │
│ size                     VARCHAR(20)     │
│ case_pack                INT             │
│ commodity_code           INT             │
│ item_number              BIGINT          │
│ category_key  FK         INT  → DimCat   │
├──────────────────────────────────────────┤
│ Cardinality: ~14,000 rows               │
└──────────────────────────────────────────┘
```

### DimStore
```
┌──────────────────────────────────────────┐
│               DimStore                   │
├──────────────────────────────────────────┤
│ store_key      PK       INT             │
│ store_id       Unique   INT             │
│ store_name               VARCHAR(50)     │
│ city                     VARCHAR(40)     │
│ zip_code                 VARCHAR(10)     │
│ zone                     INT             │
│ is_urban                 INT             │
│ weekly_volume            INT             │
│ avg_income               DECIMAL(10,2)   │
│ education_pct            DECIMAL(5,2)    │
│ poverty_pct              DECIMAL(5,2)    │
│ avg_household_size       DECIMAL(4,2)    │
│ ethnic_diversity         DECIMAL(5,2)    │
│ population_density       DECIMAL(10,2)   │
│ price_tier               VARCHAR(10)     │
│ age_under_9_pct          DECIMAL(5,2)    │
│ age_over_60_pct          DECIMAL(5,2)    │
│ working_women_pct        DECIMAL(5,2)    │
├──────────────────────────────────────────┤
│ Cardinality: ~107 rows                  │
└──────────────────────────────────────────┘
```

### DimTime
```
┌──────────────────────────────────────────┐
│               DimTime                    │
├──────────────────────────────────────────┤
│ time_key       PK       INT             │
│ week_id                  INT             │
│ week_start_date          DATE            │
│ week_end_date            DATE            │
│ month                    INT             │
│ month_name               VARCHAR(10)     │
│ quarter                  INT             │
│ year                     INT             │
│ fiscal_year              INT             │
│ is_holiday_week          BIT             │
├──────────────────────────────────────────┤
│ Cardinality: ~400 rows                  │
└──────────────────────────────────────────┘
```

### DimCategory
```
┌──────────────────────────────────────────┐
│             DimCategory                  │
├──────────────────────────────────────────┤
│ category_key    PK      INT             │
│ category_code   Unique  CHAR(3)         │
│ category_name            VARCHAR(30)     │
│ department               VARCHAR(20)     │
├──────────────────────────────────────────┤
│ Cardinality: 28 rows                    │
└──────────────────────────────────────────┘
```

### DimPromotion
```
┌──────────────────────────────────────────┐
│            DimPromotion                  │
├──────────────────────────────────────────┤
│ promotion_key  PK       INT             │
│ deal_code                CHAR(1)         │
│ deal_type                VARCHAR(20)     │
│ is_promoted              BIT             │
├──────────────────────────────────────────┤
│ Cardinality: 4 rows                     │
│ NULL → No Promotion                     │
│ B    → Bonus Buy                        │
│ C    → Coupon                           │
│ S    → Sale/Discount                    │
└──────────────────────────────────────────┘
```

---

## Relationship Diagram

```
                        DimCategory
                            │
               "category_key" FK
                            │
   DimProduct ──────── FactWeeklySales ──────── DimStore
   (has category_key   │         │              (has demographics)
    FK to DimCategory) │         │
                       │         │
                  DimTime    DimPromotion

   DimStore ──────── FactCustomerTraffic ──────── DimTime
```

All FK relationships are many-to-one (fact → dimension).
