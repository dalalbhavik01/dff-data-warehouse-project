# Prompt for Antigravity Claude Opus 4.6

You are working in this local project:

`/Users/bhavikdalal/Documents/data warehouse/project`

Act as a strict senior data-warehouse report reviewer and final-document editor. The goal is to make **Report 4** submission-ready for the ISTM 637 / Data Warehouse project without changing the implementation completion workflow that has already started.

## Non-Negotiable Constraint

Do **not** rewrite or reorder the BI completion workflow, screenshot plan, implementation sequence, or completion guide. The team has already started those steps.

Preserve these unless there is a clearly proven factual error:

- `report_4/COMPLETION_GUIDE.md`
- screenshot numbering, especially placeholders `screenshot_30.png` through `screenshot_41.png`
- the BI tool assignment plan: SSRS, SSAS, Redshift Query v2, Power BI
- the five professor-selected BQs and their current tool mapping
- the current SQL execution order in `report_4/sql`

Your role is final QA, consistency repair, wording cleanup, and report-structure alignment.

## Primary Files To Inspect

Read these first:

- Assignment brief: `report_4/dominick-project-report-four-spring 2026.doc`
- Current Report 4 source: `report_4/Integrated_Report_4.md`
- Current Report 4 Word doc: `report_4/Integrated_Report_4.docx`
- Report 4 generator: `report_4/generate_docx.py`
- SQL scripts: `report_4/sql/*.sql`
- Existing evidence screenshots: `report_4/screenshots/*.png`
- Star schema diagram: `report_4/star_schema_erd.png`
- Report 3 professor feedback: `report_4/feedback_annotated-CONSULTING_REPORT_3_Team_1-1.pdf`
- Report 1 and 2 professor feedback: `report_3/feedback of report 1 and 2/`
- Final Report 1: `report_1/CONSULTING_REPORT_1_Team_1.docx`
- Final Report 2: `report_2/CONSULTING_REPORT_2_Team_1.docx`
- Final Report 3: `report_3/Integrated_Report_3.docx`

## Assignment Requirements To Verify

Confirm Report 4 is an integrated final report, not a pasted collection of earlier reports. It must follow this frame:

1. Introduction
2. Business Questions and substantiations from Report 1, including all BQs and clear marking of implemented BQs
3. Independent Data Marts design using Kimball methodology, including detailed steps and a diagramming-tool star schema
4. Data Cleaning and Integration from Report 3, including data quality issues, ETL plan, ETL scripts, screenshots/evidence, data loading, and actual ETL for the fact table
5. BI Reporting, including reporting plan, target reports, mappings from data marts to report attributes, report templates, screenshots, and use of SSRS, SSAS, Redshift Query v2, and ReportBuilder/Power BI/Tableau

Also verify that the report explicitly states where the data warehouse, staging database, SSRS reports, SSAS cube, Redshift work, and Power BI artifacts are stored.

## Professor Feedback That Must Be Addressed

Report 3 feedback:

- Clearly state where the DW and staging databases are stored.
- Avoid any fact-table foreign key issue or unexplained strange FK values.
- Use summary-style citation placement instead of dumping citations awkwardly into body text.
- Do not call the star schema an ERD.

Report 2 feedback:

- Do not include irrelevant discussion about conformed dimensions/marts unless multiple marts genuinely require it.
- Do not label dimensional star schema diagrams as ERDs.
- In diagrams, keep relationship lines clean and unlabeled; put key/type information inside table boxes.

Report 1 feedback:

- Prioritize the BQs clearly.
- Do not claim an ERD “becomes” a star schema.
- Make sure figures are directly relevant to DFF data and the selected analytics problem.

## Current Known Facts To Preserve

- `FactWeeklySales` verified actual loaded row count is `11,976,442`, matching `report_4/screenshots/screenshot_23.png`.
- `DimProduct` verified actual loaded row count is `3,127`, matching `report_4/screenshots/screenshot_22.png`.
- Raw movement source volume is approximately 34.6M rows across the four selected categories; do not present that as the final loaded fact count.
- The difference between raw rows and loaded fact rows should be explained by ETL quality filters plus inner joins that enforce valid dimension references.
- BI screenshots `30` through `41` are intentionally placeholders until the team completes the already-started BI implementation steps.
- The visible diagram title should say **Retail Data Warehouse Star Schema**, not ERD.

## What To Check Carefully

Check the current Report 4 for:

- section order and naming matching the assignment
- title page, table of contents, numbering, captions, and references matching the style of final Reports 1, 2, and 3
- no stale row counts such as `14,921,365`
- no visible use of `ERD` to label the star schema
- no unsupported claims that aggregate tables, indexes, partitions, dashboards, reports, cubes, or cloud deployments are complete unless backed by SQL/scripts/screenshots
- all BQs are prioritized and the professor-selected BQs are clearly marked as implemented
- every selected BQ maps to dimensions, fact measures, SQL logic, and BI output
- Appendix SQL matches the actual files in `report_4/sql`
- citations are clean, summarized, and not awkwardly inserted
- screenshot placeholders are clear and professional, not mistaken for completed evidence
- grammar, formatting, and consistency issues that could cost easy marks

## Editing Rules

Make only minimal, high-confidence edits. Do not invent evidence, screenshots, execution results, row counts, or tool outputs.

Allowed edits:

- wording cleanup
- section/caption fixes
- factual consistency corrections
- adding short bridging paragraphs where the assignment requires explicit explanation
- regenerating `Integrated_Report_4.docx` from `Integrated_Report_4.md` using `generate_docx.py`
- tiny SQL/report consistency fixes only if they prevent a proven contradiction

Avoid:

- changing the implementation completion steps
- changing screenshot numbering
- replacing the current BI plan
- adding large new sections that make the report feel stitched together
- claiming work is complete when the report only has placeholders

## Expected Output

When finished, provide:

1. A concise checklist of assignment requirements and whether each is satisfied.
2. A list of professor-feedback items and exactly where/how each is addressed.
3. A list of files changed.
4. Any remaining risks before submission, especially missing screenshots `30-41`.
5. Confirmation that `Integrated_Report_4.docx` was regenerated after edits.

If you find an issue that requires changing the already-started completion workflow, stop and explain the issue instead of changing that workflow.
