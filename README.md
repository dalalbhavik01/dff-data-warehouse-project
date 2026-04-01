# DFF Data Warehouse Project

**Course:** ISTM 637 — Data Warehousing | **Spring 2026** | **Team 1**

> Design and implementation of a data warehouse for Dominick's Fine Foods (DFF), a Chicago-area supermarket chain with ~100 stores. Built on the University of Chicago Booth School's Kilts Center retail scanner dataset (1989–1994).

---

## 📁 Project Structure

```
dff-data-warehouse-project/
│
├── README.md                          ← You are here
├── .gitignore
│
├── DFF data - zipped/                 ← Raw OLTP source data
│   ├── Ccount/                        │   CCOUNT.csv (327K rows — store traffic)
│   ├── Demographics/                  │   DEMO.csv (108 stores)
│   ├── Movement/                      │   24 category folders (wsdr, wcso, etc.)
│   └── UPC/                           │   28 product lookup files
│
├── report_1/                          ← Report 1: Requirements Analysis
│   ├── CONSULTING_REPORT_1_Team_1.docx    Final submission (42/50)
│   ├── dominick-project-report-one-*.doc  Assignment instructions
│   ├── business_questions.md              All business questions
│   ├── top_10_business_questions.md       Curated top 10 BQs
│   ├── data_exploration_summary.md        EDA findings
│   ├── charts/                            BQ visualization charts
│   └── report_charts/                     EDA charts & ERDs
│
├── report_2/                          ← Report 2: Logical & Physical Design
│   ├── CONSULTING_REPORT_2_Team_1_v8.docx Final submission (73/75)
│   ├── Report_2_Final.md                  Report content (markdown)
│   ├── data_warehouse_schema.md           Star schema specification
│   ├── ER_Diagram_Reference.md            ERD specifications
│   ├── ERD_Final.jpeg                     Star schema ERD
│   ├── hybrid_data_pipeline.png           Architecture diagram
│   └── modules for reference/             Course slide decks
│
└── report_3/                          ← Report 3: ETL Design & Implementation
    ├── Integrated_Report_3.md             Full integrated report (§1-§8)
    ├── IMPLEMENTATION_STEPS.md            Step-by-step SSIS execution guide
    ├── dominick-project-report-three-*.doc Assignment instructions
    ├── feedback of report 1 and 2/        Professor annotations (PDFs)
    ├── sql/                               ETL SQL scripts
    │   ├── 01_create_databases.sql
    │   ├── 02_create_staging_tables.sql
    │   ├── 03_create_dw_tables.sql
    │   ├── 04_transform_staging.sql
    │   ├── 05_load_dimensions.sql
    │   ├── 06_load_facts.sql
    │   ├── 07_drop_temp_tables.sql
    │   └── 08_verify_bq_queries.sql
    ├── etl_1_text.txt                     ETL lecture notes (extracted)
    └── etl_2_text.txt                     ETL lecture notes (extracted)
```

---

## 🏗️ Architecture

| Component | Choice |
|:--|:--|
| Implementation Architecture | Hybrid Data Pipeline |
| Warehouse Architecture | Independent Data Marts |
| Modeling Scheme | Dimensional Modeling (Star Schema) |
| OLAP Style | HOLAP (Hybrid Online Analytical Processing) |
| Target Infrastructure | SQL Server 2016 + SSIS |

---

## ⭐ Star Schema

```
                    ┌──────────────┐
                    │  DimProduct  │
                    └──────┬───────┘
                           │
┌──────────────┐   ┌───────┴────────┐   ┌──────────────┐
│   DimStore   ├───┤FactWeeklySales ├───┤  DimCategory  │
└──────────────┘   └───────┬────────┘   └──────────────┘
                           │
┌──────────────┐           │            ┌──────────────┐
│   DimTime    ├───────────┘────────────┤ DimPromotion │
└──────────────┘                        └──────────────┘
```

**Grain:** One row per UPC × Store × Week | **~34.6M fact rows** across 4 categories

---

## 📊 Business Questions (5 Selected)

| # | Question | Difficulty | OLAP Op |
|:--|:--|:--|:--|
| BQ2 | Weekly Soft Drink unit sales across all stores | 🟢 Easy | Roll-up |
| BQ3 | Promotion vs non-promotion sales comparison | 🟢 Easy | Slice |
| BQ4 | Which promo type has highest lift in Canned Soup? | 🟡 Medium | Dice |
| BQ8 | Store quartile tiers by Toothpaste revenue | 🔴 Hard | NTILE |
| BQ9 | Top 10 weekly Cracker products with WoW change | 🔴 Hard | RANK + LAG |

---

## 🔄 ETL Pipeline

```
CSV Files ──→ [SSIS Package 1] ──→ Staging Area ──→ [SSIS Package 2] ──→ Clean Staging
                                                                              │
                                                                              ▼
BQ Queries ←── Data Mart ←────── [SSIS Package 3] ←──────────────────── Load DW
```

| Phase | SSIS Package | SQL Script | What It Does |
|:--|:--|:--|:--|
| Extract | `01_Extract_to_Staging.dtsx` | `01`, `02` | Load 10 CSVs into staging tables |
| Transform | `02_Transform_Staging.dtsx` | `04` | Clean, derive category codes, fix NULLs |
| Load | `03_Load_DataMart.dtsx` | `03`, `05`, `06`, `07` | Create schema → Load dimensions → Load facts → Cleanup |
| Verify | — | `08` | Run 5 BQ verification queries |

---

## 📈 Grades

| Report | Score | Key Feedback |
|:--|:--|:--|
| Report 1 | 42/50 | -3 wrong ERD (used star schema instead of source data), -3 no BQ prioritization |
| Report 2 | 73/75 | -2 ERD not from proper tool (Visio/LucidChart required) |
| Report 3 | TBD | Due April 8, 2026 |

---

## 🛠️ How to Run the ETL

> Requires SQL Server 2016 + SSIS (Visual Studio with SSDT)

1. Connect to SQL Server in SSMS
2. Execute scripts in order: `01` → `02` → `03`
3. Build 3 SSIS packages in Visual Studio (see `IMPLEMENTATION_STEPS.md`)
4. Execute packages: Extract → Transform → Load
5. Execute `04` → `05` → `06` → `07` (via SSIS or directly in SSMS)
6. Verify with `08_verify_bq_queries.sql`

See [`report_3/IMPLEMENTATION_STEPS.md`](report_3/IMPLEMENTATION_STEPS.md) for detailed step-by-step instructions with screenshot checklist.

---

## 👥 Team 1

ISTM 637 — Data Warehousing, Spring 2026  
Texas A&M University, Mays Business School
