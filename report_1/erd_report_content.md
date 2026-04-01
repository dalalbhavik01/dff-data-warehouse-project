# 2.2 Entity Relationship Diagram (ERD)

## Entities

The DFF dataset consists of four primary source entities: Movement, UPC, Store Demographics (DEMO), and Customer Count (CCOUNT). In the warehouse star schema, these source entities are transformed into seven entities — two fact tables and five dimension tables — to support multidimensional OLAP analysis.

The Movement source files capture weekly scanner data at the UPC × Store × Week level and are consolidated into the central fact table, FactWeeklySales. Each Movement record contains the number of units sold, shelf price, price quantity, gross profit, a promotional deal flag (SALE), and a data quality indicator (OK). The UPC source files provide product master data — description, package size, case pack, and commodity code — which populates DimProduct. The DEMO source file provides store-level demographics including city, zone, urban/rural classification, household income, education levels, and age distribution, mapped into DimStore. The CCOUNT source file records weekly customer traffic counts by department and is loaded into a secondary fact table, FactCustomerTraffic, at the Store × Week grain.

Two additional dimensions are derived during the ETL process rather than sourced directly from files. DimTime is constructed from the WEEK numbers in the source data, providing calendar attributes such as week start/end dates, month, quarter, year, and holiday flags. DimCategory is derived from the source Movement filenames, classifying products into categories such as Soft Drinks (SDR), Cereals (CER), and Beer (BER). DimPromotion is derived from the SALE flag, encoding the four promotion types: Bonus Buy (B), Coupon (C), Markdown Sale (S), and No Promotion (null).

## Relationships and Cardinalities

Each Store Demographics row maps to exactly one DimStore row (1:1). Each UPC row maps to exactly one DimProduct row (1:1). Store has many Movement rows (1:N), and Movement has many rows per UPC (N:1) and per Week (N:1). Similarly, Store has many CCOUNT rows (1:N) and Week has many CCOUNT rows (1:N). These cardinality rules dictate the foreign key placement in the star schema: the many-side entity (the fact table) carries the foreign keys referencing each dimension, consistent with the translation rules for 1:N relationships covered in Sen (2026).

Specifically, FactWeeklySales holds five foreign keys: product_key referencing DimProduct, store_key referencing DimStore, time_key referencing DimTime, category_key referencing DimCategory, and promotion_key referencing DimPromotion. DimProduct additionally holds a foreign key category_key referencing DimCategory, forming an outrigger relationship. FactCustomerTraffic holds two foreign keys: store_key referencing DimStore and time_key referencing DimTime. The shared DimStore and DimTime dimensions between both fact tables enable analysts to correlate sales performance with customer traffic patterns across identical stores and time periods.

Figure 1 shows the complete Star Schema ERD for the DFF data warehouse. The diagram was generated from the entity and relationship definitions in the DFF data codebook and course materials.

## Figure 1: Star Schema ERD — Dominick's Finer Foods Data Warehouse

**[Insert ERD Diagram Here]**

*Figure 1. Star Schema ERD for the Dominick's Finer Foods (DFF) Data Warehouse. The schema consists of two fact tables (FactWeeklySales and FactCustomerTraffic) surrounded by five dimension tables (DimProduct, DimStore, DimTime, DimCategory, and DimPromotion). All relationships are one-to-many (1:N), with foreign keys placed on the many-side (fact tables) per standard relational translation rules. Crow's foot notation indicates the "many" side of each relationship.*

## Legend

- **PK** — Primary Key: uniquely identifies each row in the entity.
- **FK** — Foreign Key: references the primary key of a related dimension table.
- **INT, BIGINT, DECIMAL, VARCHAR, CHAR, BIT, DATE** — Physical data types specifying storage format and precision.
- **Unique** — Column enforces a uniqueness constraint (e.g., upc in DimProduct, store_id in DimStore).
- **Crow's Foot (fork symbol)** — Indicates the "many" side of a 1:N relationship; the single line indicates the "one" side.
- **Solid connecting line** — Represents a mandatory foreign key relationship between two entities.

### Reference

Sen, A. (2026). *Task 3B: Physical Design of Data Warehouse.* Department of Information & Operations Management, Mays Business School, Texas A&M University.
