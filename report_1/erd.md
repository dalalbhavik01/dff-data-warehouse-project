# Entity Relationship Diagram — DFF Data Warehouse

> Star Schema ERD for the Dominick's Fine Foods Data Warehouse. Two fact tables surrounded by five dimension tables.

---

## Star Schema ERD

```mermaid
erDiagram
    FactWeeklySales {
        INT sales_fact_id PK
        INT product_key FK
        INT store_key FK
        INT time_key FK
        INT category_key FK
        INT promotion_key FK
        INT units_sold
        DECIMAL unit_price
        DECIMAL shelf_price
        INT price_qty
        DECIMAL revenue
        DECIMAL gross_profit
        DECIMAL profit_margin_pct
        BOOLEAN is_valid
    }

    FactCustomerTraffic {
        INT traffic_fact_id PK
        INT store_key FK
        INT time_key FK
        DECIMAL grocery_count
        DECIMAL dairy_count
        DECIMAL frozen_count
        DECIMAL meat_count
        DECIMAL produce_count
        DECIMAL deli_count
        DECIMAL bakery_count
        DECIMAL pharmacy_count
        DECIMAL beer_count
        DECIMAL wine_count
        DECIMAL spirits_count
        DECIMAL total_customers
        DECIMAL mvp_club_count
        DECIMAL total_coupon_redemptions
    }

    DimProduct {
        INT product_key PK
        BIGINT upc
        VARCHAR description
        VARCHAR size
        INT case_pack
        INT commodity_code
        BIGINT item_number
        INT category_key FK
    }

    DimStore {
        INT store_key PK
        INT store_id
        VARCHAR store_name
        VARCHAR city
        VARCHAR zip_code
        DECIMAL latitude
        DECIMAL longitude
        INT zone
        INT weekly_volume
        BOOLEAN is_urban
        DECIMAL avg_income
        DECIMAL education_pct
        DECIMAL poverty_pct
        DECIMAL avg_household_size
        DECIMAL ethnic_diversity
        DECIMAL population_density
        VARCHAR price_tier
        DECIMAL age_under_9_pct
        DECIMAL age_over_60_pct
        DECIMAL working_women_pct
    }

    DimTime {
        INT time_key PK
        INT week_id
        DATE week_start_date
        DATE week_end_date
        INT month
        VARCHAR month_name
        INT quarter
        INT year
        INT fiscal_year
        BOOLEAN is_holiday_week
    }

    DimPromotion {
        INT promotion_key PK
        CHAR deal_code
        VARCHAR deal_type
        BOOLEAN is_promoted
    }

    DimCategory {
        INT category_key PK
        CHAR category_code
        VARCHAR category_name
        VARCHAR department
    }

    DimProduct ||--o{ FactWeeklySales : "product_key"
    DimStore ||--o{ FactWeeklySales : "store_key"
    DimTime ||--o{ FactWeeklySales : "time_key"
    DimCategory ||--o{ FactWeeklySales : "category_key"
    DimPromotion ||--o{ FactWeeklySales : "promotion_key"
    DimCategory ||--o{ DimProduct : "category_key"
    DimStore ||--o{ FactCustomerTraffic : "store_key"
    DimTime ||--o{ FactCustomerTraffic : "time_key"
```

---

## Relationship Summary

| Relationship | Cardinality | Join Key | Description |
|-------------|-------------|----------|-------------|
| DimProduct → FactWeeklySales | 1:N | `product_key` | Each product appears in many weekly sales rows |
| DimStore → FactWeeklySales | 1:N | `store_key` | Each store has sales data across many weeks/products |
| DimTime → FactWeeklySales | 1:N | `time_key` | Each week contains sales for many store-product combos |
| DimCategory → FactWeeklySales | 1:N | `category_key` | Each category contains many product-store-week sales |
| DimPromotion → FactWeeklySales | 1:N | `promotion_key` | Each promo type (B/C/S/None) applies to many sales rows |
| DimCategory → DimProduct | 1:N | `category_key` | Each category contains many products |
| DimStore → FactCustomerTraffic | 1:N | `store_key` | Each store has weekly traffic counts |
| DimTime → FactCustomerTraffic | 1:N | `time_key` | Each week has traffic data for many stores |

---

## Source-to-Target Data Flow

```mermaid
flowchart LR
    subgraph Source["Source CSV Files"]
        M["Movement Files<br/>(24 files, 134.9M rows)"]
        U["UPC Files<br/>(28 files, ~14K rows)"]
        D["DEMO.csv<br/>(107 stores)"]
        C["CCOUNT.csv<br/>(327K rows)"]
    end

    subgraph Transform["ETL Transformations"]
        T1["Derive category<br/>from filename"]
        T2["Compute revenue<br/>unit_price, margin"]
        T3["Map WEEK to<br/>calendar dates"]
        T4["Clean demographics<br/>LAT/LONG, price_tier"]
        T5["Replace dots with<br/>NULL, sum coupons"]
        T6["Map SALE flags<br/>to promo types"]
    end

    subgraph Target["Star Schema"]
        F1["FactWeeklySales"]
        F2["FactCustomerTraffic"]
        DP["DimProduct"]
        DS["DimStore"]
        DT["DimTime"]
        DPR["DimPromotion"]
        DC["DimCategory"]
    end

    M --> T1 --> F1
    M --> T2 --> F1
    M --> T6 --> DPR
    M --> T3 --> DT
    U --> DP
    U --> T1 --> DC
    D --> T4 --> DS
    C --> T5 --> F2
```
