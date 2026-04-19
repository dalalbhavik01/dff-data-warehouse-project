# Report 4 — Completion Guide (FINAL)

> **Status: ✅ COMPLETE — All rubric requirements satisfied. Report is submission-ready.**
>
> Last updated: April 19, 2026

---

## What Was Done

All content from Reports 1–4 has been integrated into a single unified document
(`Integrated_Report_4.docx`, 17.3 MB) following the professor's exact section structure.

### Content Integration Summary

| Source Report | Content | Integrated Into |
|:--|:--|:--|
| Report 1 | Intro, EDA, Literature Review, 10 BQs, Prioritization, Data Evidence | Sections 1 + 2 |
| Report 2 | Kimball methodology, Bus Matrix, Star Schema, ERD, Mapping Tables, Physical Design | Section 3 |
| Report 3 | Data Quality, ETL Plan, SSIS Implementation, SQL Scripts, 29 ETL Screenshots | Section 4 |
| Report 4 (NEW) | BI Reporting Plan, SSRS/SSAS/Redshift/Power BI Implementation, 12 BI Screenshots | Section 5 |

### Visual Evidence Embedded

| # Range | Tool/Source | Description | Count |
|:--|:--|:--|:--|
| — | LucidChart | ETL Pipeline diagram (R3 page 6) | 1 |
| — | LucidChart | Star Schema ERD (R3 page 13) | 1 |
| 1–29 | SSIS/SSMS | ETL implementation evidence (extracted from R3 PDF) | 29 |
| 30–31 | SSRS | BQ2 — Weekly SDR Sales trend (Designer + Preview) | 2 |
| 32–33 | SSRS | BQ9 — Top 10 Crackers ranking (Designer + Preview) | 2 |
| 34–36 | SSAS | BQ3 — Cube structure, pivot, drill-down | 3 |
| 37–38 | Redshift v.2 | BQ4 — Query editor + promotion lift results | 2 |
| 39–41 | Power BI | BQ8 — Model view, dashboard, map | 3 |
| **Total** | | | **43 images** |

---

## Final File Inventory

```
report_4/
├── Integrated_Report_4.md          ← Source markdown (113 KB)
├── Integrated_Report_4.docx        ← FINAL SUBMISSION FILE (17.3 MB, 42 embedded images)
├── generate_docx.py                ← DOCX generator script
├── COMPLETION_GUIDE.md             ← This file
├── etl_pipeline_diagram.png        ← Pipeline diagram (from R3)
├── star_schema_erd.png             ← Star Schema ERD (from R3)
├── MappingTables.xlsx              ← Excel mapping tables
├── dominick-project-report-four-spring 2026.doc  ← Professor's rubric
├── CONSULTING_REPORT_3_Team_1-1.pdf              ← Submitted R3 (reference)
├── sql/                            ← 8 SQL scripts
│   ├── 01_create_databases.sql
│   ├── 02_create_staging_tables.sql
│   ├── 03_create_dw_tables.sql
│   ├── 04_transform_staging.sql
│   ├── 05_load_dimensions.sql
│   ├── 06_load_facts.sql
│   ├── 07_drop_temp_tables.sql
│   └── 08_verify_bq_queries.sql
└── screenshots/                    ← All 41 screenshots
    ├── screenshot_01.png ... screenshot_29.png   (ETL evidence from R3)
    └── screenshot_30.png ... screenshot_41.png   (BI tool evidence)
```

---

## Rubric Compliance Checklist

### Structure (must follow exactly)

- [x] Section 1: Introduction
- [x] Section 2: BQs and substantiations (from Report 1)
- [x] Section 3: Independent Data Marts using Kimball (from Report 2)
- [x] Section 4: Data Cleaning and Integration (from Report 3)
- [x] Section 5: BI Reporting (NEW — SSRS, SSAS, Redshift v.2, Power BI)
- [x] Section 6: References
- [x] Section 7: Appendix (SQL scripts + Mapping Tables + Screenshot Index)

### Grading Criteria (50 points)

- [x] **Presentation, English, clean writing (10 pts)** — Professional prose, consistent numbering, no template/placeholder text
- [x] **SSAS (15 pts)** — Cube built over FactWeeklySales, browsed with BQ3 pivot + year drill-down (Screenshots 34-36)
- [x] **SSRS (15 pts)** — BQ2 weekly trend report + BQ9 parameterized ranking report (Screenshots 30-33)
- [x] **Redshift Query v.2 (15 pts)** — BQ4 promotion lift query with data export explanation (Screenshots 37-38)
- [x] **Power BI (15 pts)** — BQ8 store quartile dashboard with demographic table + map view (Screenshots 39-41)
- [x] **Integration of Reports 1-4 (5 pts)** — Single flowing narrative, no "Report X:" headers

### Additional Requirements

- [x] Storage locations documented (Section 5.3)
- [x] Title page: project title, member names, group number, email
- [x] Reports read as ONE document, not a collection of four
- [x] All BQs listed with implemented ones clearly identified
- [x] Charts and discussions provided for each BQ
- [x] Screenshots provide evidence that reports were built
- [x] No placeholder brackets remaining (`[INSERT]`, `[SERVER_NAME]`, etc.)
- [x] Appendix C covers all 41 screenshots (ETL 1-29 + BI 30-41)

---

## How to Submit

1. Open `report_4/Integrated_Report_4.docx` in Word
2. Verify images render correctly
3. Submit the `.docx` file

### If You Need to Regenerate

If you make any text changes to `Integrated_Report_4.md`:
```bash
cd "/Users/bhavikdalal/Documents/data warehouse/project/report_4"
python3 generate_docx.py
```

This will regenerate the DOCX with all 42 images re-embedded (~17 MB).

---

## Quick Verification (2 minutes)

Open the DOCX and check these 5 things:

1. **Title page** — DFF name, 3 member names, Group 1, email, date
2. **Section 3.6** — Star Schema ERD image visible
3. **Section 4.2** — ETL screenshots visible (scroll through — should see ~29 SSMS/SSIS images)
4. **Section 5.2** — BI screenshots visible:
   - 5.2.1: SSRS designer + preview (2×2 = 4 images)
   - 5.2.2: SSAS cube structure + browser (3 images)
   - 5.2.3: Redshift query editor + results (2 images)
   - 5.2.4: Power BI model + dashboard + map (3 images)
5. **Appendix C** — Screenshot index lists 1-41 (not just 1-29)

If all 5 check: **submit.**
