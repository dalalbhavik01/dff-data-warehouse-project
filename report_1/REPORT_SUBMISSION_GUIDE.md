# 📋 Consulting Report-1 — Submission Guide

> **Due:** February 25, 2026 | **Points:** 50 | **Team:** 3 members
> **Title:** Requirements Gathering to Create Business Questions and Domain Understanding

---

## Rubric Breakdown & Points Map

| Section                            | Weight | Points           | What the Grader Wants                                                             |
| ---------------------------------- | ------ | ---------------- | --------------------------------------------------------------------------------- |
| **A. Metadata + ERD**        | 10%    | **4 pts**  | Describe ALL OLTP source files' metadata; draw ERD in Visio showing relationships |
| **B. Data Understanding**    | 25%    | **10 pts** | Excel analysis, charts, pivot tables proving you explored the data                |
| **C. Subject Area Research** | 25%    | **10 pts** | 3–5 cited research papers on retail domain; list relevant problems for DFF       |
| **D. Business Questions**    | 40%    | **16 pts** | 10 BQs with data evidence (Excel/pivots), prioritization with rationale           |
| **Presentation Quality**     | —     | *implicit*     | Professional formatting, proper citations, clear structure                        |
|                                    |        | **50 pts** |                                                                                   |

---

## Report Structure (Follow EXACTLY)

Your Word document must follow this order:

```
1. Cover Page
2. Table of Contents
3. Section 1: Introduction
4. Section 2: Details About the Data
   2.1 Metadata for ALL OLTP Source Files
   2.2 ERD (Visio diagram)
5. Section 3: Retail Subject Area Understanding
   3.1 Literature Review (3–5 papers)
   3.2 Relevant Problems for DFF
   3.3 References
6. Section 4: Business Questions
   4.1 List of 10 Business Questions
   4.2 Data Evidence (Excel charts, pivot tables, statistics)
   4.3 Prioritization with Rationale
7. Appendix (optional: extra charts, raw data screenshots)
```

---

## 🔵 PART 1 — Nisarg: Intro + Metadata + Data Understanding (Sections 1 + 2) → 14 pts

**Estimated Time: 5–6 hours**

### Section 1: Introduction (0.5 pages)

Write a brief intro about DFF:

- Dominick's Finer Foods — Chicago-area supermarket chain, ~100 stores
- Between 1989–1994, partnered with University of Chicago Booth School for store-level research
- Dataset: ~5 GB, 3,500+ UPCs across 28 product categories, weekly scanner data
- Project goal: Design a data warehouse for DFF using this historical retail data

**Must cite:**

- Kilts Center (2013) — the dataset source
- Company history URL: `https://www.company-histories.com/Dominicks-Finer-Foods-Inc-Company-History.html`

### Section 2.1: Metadata for ALL OLTP Source Files (2–3 pages) → 4 pts

Describe **every** source file type. Use the table format below for each:

#### Movement Files (24 files — one per category)

| Column     | Data Type | Description                                                |
| ---------- | --------- | ---------------------------------------------------------- |
| `UPC`    | Integer   | Universal Product Code — links to UPC files               |
| `STORE`  | Integer   | Store identifier — links to DEMO                          |
| `WEEK`   | Integer   | Proprietary week number (Week 1 ≈ Sep 14, 1989)           |
| `MOVE`   | Integer   | Units sold during the week                                 |
| `QTY`    | Integer   | Number of units for listed price (e.g., 2-for-$3 → QTY=2) |
| `PRICE`  | Decimal   | Shelf price during the week                                |
| `SALE`   | Text      | Deal flag: B=Bonus Buy, C=Coupon, S=Sale, blank=No promo   |
| `PROFIT` | Decimal   | Gross profit                                               |
| `OK`     | Integer   | Data quality flag (1=valid)                                |

**Include a table listing all 24 Movement files with category names and row counts.**

> 📌 Use the inventory from `data_exploration_summary.md` → Section 1 (Movement Files Inventory)

#### UPC Files (28 files)

| Column       | Data Type | Description                                   |
| ------------ | --------- | --------------------------------------------- |
| `COM_CODE` | Integer   | Commodity/company code (brand grouping)       |
| `UPC`      | Integer   | Universal Product Code (join key to Movement) |
| `DESCRIP`  | Text      | Product description                           |
| `SIZE`     | Text      | Package size                                  |
| `CASE`     | Integer   | Case pack quantity                            |
| `NITEM`    | Integer   | Internal item number                          |

**Include a table listing all 28 UPC files with category names and UPC counts.**

#### CCOUNT File (Customer Counts)

- 327K rows × 61 columns
- Key columns: `STORE`, `WEEK`, `CUSTCOUN`, department-level counts, coupon columns
- Note the `DATE` column is corrupted

#### DEMO File (Demographics)

- 108 rows × 510 columns (one per store)
- Key columns: `STORE`, `NAME`, `CITY`, `ZIP`, `ZONE`, `URBAN`, `INCOME`, `DENSITY`
- Note the 23 null NAME/CITY values

#### Key Relationships

Document the join keys:

```
Movement.UPC      → UPC.UPC        (product details)
Movement.STORE    → DEMO.STORE     (store demographics)
Movement.WEEK     → CCOUNT.WEEK    (customer counts)
Movement.STORE+WEEK → CCOUNT.STORE+WEEK (traffic by store-week)
```

### Section 2.2: Data Understanding via Excel (2–3 pages) → 10 pts

**This is 25% of your grade. The professor wants to SEE Excel screenshots.**

Create these 6 Excel visuals (pivot tables + charts), screenshot into the report:

| # | What to Create                                                                                            | Data File                              | Excel Method                                                                       |
| - | --------------------------------------------------------------------------------------------------------- | -------------------------------------- | ---------------------------------------------------------------------------------- |
| 1 | **Category Volume Comparison** — Bar chart of total units sold by category (at least 6 categories) | Multiple Movement CSVs                 | Open each CSV → filter OK=1 → SUM(MOVE) → compile in summary sheet → bar chart |
| 2 | **Sales Distribution** — Show the range of MOVE values for 2–3 categories                         | `wsdr.csv`, `WCSO-Done.csv`        | Histogram or descriptive stats (mean, median, max, min, stdev)                     |
| 3 | **Promotion Effectiveness** — Compare promoted vs non-promoted avg sales                           | `wsdr.csv` or any Movement file      | Pivot Table: Rows=SALE (B,C,S,blank), Values=Average of MOVE                       |
| 4 | **Store Demographics Overview** — Chart of urban vs suburban stores, zone distribution             | `DEMO.csv`                           | Pivot Table: Rows=URBAN, Values=Count; or Rows=ZONE, Values=Count → pie/bar chart |
| 5 | **Price Distribution** — Show price variation across a category                                    | `DONE-WBER.csv` or `DONE-WCER.csv` | Compute UnitPrice=PRICE/QTY → Pivot: Rows=UPC, Values=Avg/Min/Max of UnitPrice    |
| 6 | **Weekly Trend** — Line chart of total weekly sales for Soft Drinks                                | `wsdr.csv`                           | Pivot Table: Rows=WEEK, Values=SUM(MOVE) → Line chart                             |

**How to present in the report:**

- Screenshot each pivot table AND its chart
- Below each, write 2–3 sentences about what the data shows
- Example: *"Soft Drinks lead all categories with 1.41M units (sample), followed by Canned Soup at 1.26M. The SDR category also shows the highest promotion lift at 13.6×, confirming its importance for DFF."*

> 📌 Use statistics/data from `data_exploration_summary.md` Sections 8.1–8.5 to guide your analysis. The numbers are already validated.

> ⚠️ **Large files tip:** Excel handles max ~1M rows. For `wsdr.csv` (17.7M rows), import only the first 500K–1M rows. Note in the report: *"Analysis performed on a representative sample of X rows."*

### Checklist for Nisarg

- [ ] Cover page with team members, date, course
- [ ] Table of contents
- [ ] Introduction with DFF background (cite 2+ sources)
- [ ] Metadata tables for Movement, UPC, CCOUNT, DEMO
- [ ] File inventory tables (24 Movement + 28 UPC files with row counts)
- [ ] Data quality issues noted (corrupted dates, dots as nulls, PRICE=0)
- [ ] Join key relationships documented
- [ ] 6 Excel screenshots (pivot tables + charts) with captions
- [ ] 2–3 sentence interpretation under each visual
- [ ] Proper citations for DFF website and codebook

---

## 🟡 PART 2 — Bhavik: ERD + Subject Area Research (Section 2.2 + 3) → 14 pts

**Estimated Time: 4–5 hours**

### Section 2.2: ERD (1 page) → Part of 4 pts

**Draw in Visio, draw.io, or any diagramming tool.** Show the OLTP source file relationships:

```
┌──────────────────┐         ┌──────────────┐
│  Movement File   │───UPC──→│   UPC File   │
│  (Weekly Sales)  │         │  (Product)   │
│                  │         └──────────────┘
│  UPC, STORE,     │
│  WEEK, MOVE,     │         ┌──────────────┐
│  PRICE, QTY,     │──STORE─→│  DEMO File   │
│  SALE, PROFIT,OK │         │ (Demographics)│
│                  │         └──────────────┘
│                  │         ┌──────────────┐
│                  │─STORE+──→│ CCOUNT File  │
│                  │  WEEK   │(Customer Cnt) │
└──────────────────┘         └──────────────┘
```

> 📌 Use the Mermaid ERD from `erd.md` as reference — redraw it in your diagramming tool.

### Section 3: Retail Subject Area Understanding (2–3 pages) → 10 pts

**This is 25% of your grade. Must cite 3–5 research papers.**

#### 3.1 Literature Review — Use these papers (already identified):

| # | Paper                                                                                                                                   | Key Finding                                                                                 | Relevant BQs |
| - | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------ |
| 1 | Hoch, Kim, Montgomery & Rossi (1995), "Determinants of Store-Level Price Elasticity,"*Journal of Marketing Research*, 32(1), 17–29.  | DFF used zone pricing; optimizing by category-level elasticity could increase profits 3–5% | M2, H1, H3   |
| 2 | Chevalier, Kashyap & Rossi (2003), "Why Don't Prices Rise During Periods of Peak Demand?,"*American Economic Review*, 93(1), 15–37.  | Retail margins decrease during peak demand while volume increases                           | E3, M1       |
| 3 | Chintagunta (2002), "Investigating Category Pricing Behavior at a Retail Chain,"*Journal of Marketing Research*, 39(2), 141–154.     | Brand promotional activity significantly impacts competitor market share                    | M3           |
| 4 | Montgomery (1997), "Creating Micro-Marketing Pricing Strategies Using Supermarket Scanner Data,"*Marketing Science*, 16(4), 315–337. | Store demographics predict demand elasticity and category performance                       | M2, H1       |
| 5 | Pesendorfer (2002), "Retail Sales: A Study of Pricing Behavior in Supermarkets,"*Journal of Business*, 75(1), 33–66.                 | Consumers strategically time purchases around promotional cycles                            | E2, H2       |

**How to write this section:**

1. For each paper, write 1 paragraph summarizing the key finding
2. Connect it to DFF's data: *"Our analysis confirms this finding — SDR promotions show a 13.6× sales lift..."*
3. End with a table of "Relevant Retail Problems for DFF" (see below)

#### 3.2 Relevant Problems for DFF

| # | Retail Problem                    | Relevance to DFF                                     | Related BQs |
| - | --------------------------------- | ---------------------------------------------------- | ----------- |
| 1 | Promotion ROI measurement         | DFF runs B, C, S deals across 24 categories          | E3, M1      |
| 2 | Zone pricing optimization         | DFF uses 15 pricing zones across 107 stores          | H1, H3      |
| 3 | Category management & shelf space | 24+ categories with vastly different profit profiles | E1, M3      |
| 4 | Trend detection & seasonality     | 5+ years of weekly data for time-series analysis     | E2, H2      |
| 5 | Store performance benchmarking    | Demographics + sales data enables attribution        | M2, H1      |

#### 3.3 References (APA format in-text citations)

Cite as: `(Hoch et al., 1995, Journal of Marketing Research, Vol. 32, No. 1, pp. 17-29)`

**Put a full References section at the end of the report.**

### Checklist for Bhavik

- [ ] ERD drawn in diagramming tool showing all 4 file types + relationships
- [ ] Literature review — 3–5 papers summarized with DFF connections
- [ ] In-text citations in correct format
- [ ] "Relevant Problems for DFF" table
- [ ] Full References list in APA format
- [ ] Report formatting: consistent fonts/headings, page numbers, figure captions, spell check

---

## 🔴 PART 3 — Yifei: Business Questions (Section 4) → 16 pts

**Estimated Time: 5–6 hours**

### This is 40% of your grade — the most important section.

#### Section 4.1: List of 10 Business Questions (3–4 pages)

Use the 10 questions from `top_10_business_questions.md`. For each question, present:

**Template for each BQ:**

```
BQ [#]: [Question text]

Difficulty: Easy / Medium / Hard
OLAP Operation: [Roll-up / Slice / Dice / Drill-down / Ranking / etc.]
Files Needed: [exact file names]
Key Columns: [list columns used]

Business Value:
[2-3 sentences on why this is important for DFF]

SQL Query:
[include the SQL from top_10_business_questions.md]
```

#### Section 4.2: Data Evidence via Excel (4–5 pages) → Critical for full marks

**For each of the 10 BQs, create an Excel visual to prove it is implementable.**

Use the Pivot Table instructions from `top_10_business_questions.md`:

| BQ           | What to Show in Excel                                                       | File to Open                                       |
| ------------ | --------------------------------------------------------------------------- | -------------------------------------------------- |
| **E1** | Bar chart of total units by category (at least 6)                           | Multiple Movement CSVs                             |
| **E2** | Line chart of weekly SDR sales                                              | `WSDR/wsdr.csv`                                  |
| **E3** | Pivot: Rows=SALE, Values=Avg(MOVE) → clustered bar                         | `WSDR/wsdr.csv`                                  |
| **M1** | Pivot: Rows=SALE, Values=Avg(MOVE) for Canned Soup → lift calc             | `WCSO/WCSO-Done.csv`                             |
| **M2** | VLOOKUP URBAN from DEMO → Pivot by Quarter×Urban → clustered bar         | `WFRE/WFRE-Done.csv` + `DEMO.csv`              |
| **M3** | VLOOKUP COM_CODE from UPC → Pivot by COM_CODE×Month → % of column        | `backup-Movement/DONE-WCER.csv` + `UPCCER.csv` |
| **M4** | Compute UnitPrice → Pivot by UPC×STORE → calc spread → bar chart top 10 | `backup-Movement/DONE-WBER.csv` + `UPCBER.csv` |
| **H1** | Revenue per store → assign quartiles → VLOOKUP demographics → summary    | `WTPA/WTPA_done.csv` + `DEMO.csv`              |
| **H2** | Pivot by WEEK×UPC → rank → add WoW formula → conditional formatting     | `WCRA/Done-WCRA.csv` + `UPCCRA.csv`            |
| **H3** | VLOOKUP ZONE → Avg profit per store → PERCENTRANK per zone → box plot    | `WCIG/Done-WCIG.csv` + `DEMO.csv`              |

> ⚠️ **Important:** Some files are very large (17M+ rows). Excel can only handle ~1M rows. For large files, **use only the first 500K–1M rows** as a sample and note this in your report: *"Analysis performed on a representative sample of [X] rows from [file]."*

**For each BQ screenshot:**

1. Show the Pivot Table setup (rows, columns, values, filters)
2. Show the chart it produces
3. Write 2–3 sentences interpreting the result
4. Connect the finding back to the business question

#### Section 4.3: Prioritization with Rationale (1 page)

Present the 10 BQs in priority order with justification:

| Priority | BQ                                   | Rationale                                                                                                                             |
| -------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| 1        | M1 — Promo lift by deal type        | Highest ROI impact — directly affects DFF's promotional budget (millions). Data confirms 9.4× lift for Sale vs 2.2× for Bonus Buy. |
| 2        | E1 — Total units by category        | Category management foundation — baseline for shelf space, supply chain, and merchandising.                                          |
| 3        | H1 — Store quartiles + demographics | Zone pricing validation — Hoch et al. (1995) showed 3–5% profit improvement opportunity. Top stores are 73.9% urban.                |
| 4        | M3 — Brand market share             | Competitive intelligence for manufacturer negotiation. Aligned with Chintagunta (2002).                                               |
| 5        | E2 — Weekly SDR trend               | Largest category — demand forecasting and inventory optimization.                                                                    |
| 6        | M2 — Urban vs suburban revenue      | Location strategy — 60/40 suburban-urban revenue split informs store openings.                                                       |
| 7        | H3 — Percentile rank by zone        | Profit optimization — Cigarettes high-margin ($16.44 avg); Zone 1 spread $7–$40 shows improvement opportunity.                      |
| 8        | E3 — Promo vs non-promo             | Validates promotional ROI — 13.6× lift proves promotions are worth the investment.                                                  |
| 9        | H2 — Top 10 products + WoW          | Product velocity — enables rapid assortment adjustment based on weekly trends.                                                       |
| 10       | M4 — Price variance (Beer)          | Pricing audit — Busch Beer $6.30 spread across 69 stores reveals inconsistency.                                                      |

**Rationale summary (include this paragraph):**

> *"Prioritization follows four principles: (1) Revenue & profit impact first — questions that directly inform pricing and promotion decisions rank highest. (2) Research alignment — questions supported by published DFF studies receive higher priority. (3) Data richness — questions leveraging the most complete data rank higher. (4) Actionability — questions producing immediately actionable insights outrank descriptive ones."*

### Checklist for Yifei

- [ ] 10 business questions, each with difficulty, OLAP operation, files, columns, business value, SQL
- [ ] 10 Excel screenshots (one per BQ) — pivot table + chart + interpretation
- [ ] Prioritization table with all 10 BQs ranked
- [ ] Rationale paragraph explaining prioritization principles
- [ ] Each BQ links back to research papers where applicable
- [ ] Note sample sizes for large files

---

## ⏰ Timeline (Due Tomorrow)

| Time Block                  | Nisarg (A)                                                                    | Bhavik (B)                                     | Yifei (C)                               |
| --------------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------- | --------------------------------------- |
| **Tonight 6–8 PM**   | Write Intro + Metadata tables                                                 | Draw ERD + start literature review             | Write BQ 1–5 with SQL + descriptions   |
| **Tonight 8–10 PM**  | Create 6 Excel pivot tables + screenshots                                     | Summarize papers 3–5 + problems table          | Write BQ 6–10 + create Excel evidence  |
| **Tonight 10–11 PM** | Write interpretations under each visual                                       | Write References list, finalize formatting     | Create prioritization table + rationale |
| **Morning**           | **ALL THREE:** Merge into one Word doc, final review, consistency check |                                                |                                         |

---

## 🎯 Full-Marks Checklist

### Content Completeness

- [ ] **Introduction** mentions DFF, Chicago, 1989–1994, Kilts Center, 100 stores, 5GB data
- [ ] **ALL 4 file types** described (Movement, UPC, CCOUNT, DEMO) with column-level metadata
- [ ] **File inventories** — 24 Movement files + 28 UPC files listed with row counts
- [ ] **ERD** drawn in Visio (not hand-drawn, not just text)
- [ ] **Data quality issues** documented (corrupted dates, dots, PRICE=0, encoding)
- [ ] **Join keys** explicitly stated
- [ ] **6+ Excel charts/pivot tables** in Data Understanding section
- [ ] **3–5 research papers** cited with in-text citations
- [ ] **Retail problems table** connecting research to DFF
- [ ] **10 business questions** with OLAP operations identified
- [ ] **Excel evidence** for each BQ (pivot table + chart)
- [ ] **Prioritization** with rationale for each rank
- [ ] **References** section in APA format

### Presentation Quality

- [ ] Professional formatting (consistent fonts, headings, margins)
- [ ] Page numbers
- [ ] Figure/table captions numbered (Figure 1, Table 1, etc.)
- [ ] No spelling/grammar errors
- [ ] All images are clear and readable
- [ ] All citations are in-text AND in the References list

---

## 📂 Files You Already Have (Use These)

| Resource               | Path                                      | What It Contains                                      |
| ---------------------- | ----------------------------------------- | ----------------------------------------------------- |
| Data exploration stats | `data_exploration_summary.md`           | All metadata, row counts, statistics, quality issues  |
| ERD reference          | `erd.md`                                | Mermaid ERD diagram — redraw in Visio                |
| Schema design          | `data_warehouse_schema.md`              | Schema, join keys, transformations                    |
| Business questions     | `top_10_business_questions.md`          | 10 curated BQs with SQL + Excel Pivot instructions    |
| Visual evidence        | `business_questions_visual_evidence.md` | Data tables + chart descriptions for each BQ          |
| Full question pool     | `business_questions.md`                 | All 15 original BQs with research papers + references |
