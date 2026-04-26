#!/usr/bin/env python3
"""
Generate Report 4 DOCX by cloning the submitted Report 3 DOCX,
applying professor feedback fixes, renumbering sections, and
appending Section 5 (BI Reporting).
"""

import copy, re, os
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DOCX  = os.path.join(os.path.dirname(SCRIPT_DIR), "CONSULTING_REPORT_3_Team_1.docx")
OUT_DOCX   = os.path.join(SCRIPT_DIR, "Integrated_Report_4_v2.docx")
SS_DIR     = os.path.join(SCRIPT_DIR, "screenshots")

# ── Section renumbering map (old → new) ──
HEADING1_RENAME = {
    "Section 1: Introduction": "Section 1: Introduction",
    "Section 2: Subject Area Understanding": "Section 2: Business Questions and Substantiations",
    "Section 3: Overview of Kimball's Methodology": "Section 3: Independent Data Marts Design Using Kimball's Approach",
    "Section 4: Data Warehouse Logical Design (Star Schema Design)": None,  # MERGE into Section 3
    "Section 5: Development of the ETL Plan": "Section 4: Data Cleaning and Integration",
    "Section 6: Implementation of the ETL Plan": None,  # MERGE into Section 4
    "Section 7: References": "Section 6: References",
    "Section 8: Appendix": "Section 7: Appendix",
}

# Sub-section renumbering: old prefix → new prefix
SUBSECTION_MAP = {
    # Section 3+4 merge into Section 3
    "3.": "3.", "4.1": "3.2", "4.2": "3.3", "4.3": "3.4",
    "4.4": "3.5", "4.5": "3.6", "4.6": "3.7", "4.7": "3.8",
    # Section 5+6 merge into Section 4
    "5.1": "4.1", "5.2": "4.2", "5.3": "4.3", "5.4": "4.4",
    "5.5": "4.5", "5.6": "4.6", "5.7": "4.7", "5.8": "4.8",
    "5.9": "4.9", "5.10": "4.10",
    "6.1": "4.12", "6.2": "4.13", "6.3": "4.14", "6.4": "4.15",
    "6.5": "4.16", "6.6": "4.17", "6.7": "4.18", "6.8": "4.19",
    "6.9": "4.20", "6.10": "4.21",
}


def set_run_font(run, name="Times New Roman", size=12, bold=False, italic=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)


def add_heading_paragraph(doc, text, level, element_before=None):
    """Add a heading paragraph at the end of the document."""
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        run.font.name = "Times New Roman"
        run.font.color.rgb = RGBColor(0, 0, 0)
        if level == 1:
            run.font.size = Pt(16)
        elif level == 2:
            run.font.size = Pt(14)
        elif level == 3:
            run.font.size = Pt(12)
    return p


def add_body_paragraph(doc, text, bold=False, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    set_run_font(r, bold=bold, italic=italic)
    return p


def add_inline_paragraph(doc, parts):
    """Add a paragraph with mixed formatting. parts = [(text, bold, italic), ...]"""
    p = doc.add_paragraph()
    for text, bold, italic in parts:
        r = p.add_run(text)
        set_run_font(r, bold=bold, italic=italic)
    return p


def add_table(doc, headers, rows):
    """Add a properly formatted table with borders."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    # Apply borders via XML
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement('w:tblPr')
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        el = OxmlElement(f'w:{edge}')
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), '4')
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), '000000')
        borders.append(el)
    tblPr.append(borders)
    # Header row
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        r = cell.paragraphs[0].add_run(h)
        set_run_font(r, bold=True, size=10)
    # Data rows
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.rows[ri + 1].cells[ci]
            cell.text = ""
            r = cell.paragraphs[0].add_run(str(val))
            set_run_font(r, size=10)
    doc.add_paragraph("")
    return table


def add_placeholder(doc, num, description):
    """Add a clean text placeholder for a screenshot."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"[INSERT: Screenshot {num} — {description}]")
    set_run_font(r, italic=True, size=11)
    doc.add_paragraph("")


def add_image_or_placeholder(doc, num, description):
    """Embed screenshot if it exists, otherwise add text placeholder."""
    path = os.path.join(SS_DIR, f"screenshot_{num:02d}.png")
    if os.path.exists(path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(path, width=Inches(5.5))
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cap.add_run(f"Screenshot {num}: {description}")
        set_run_font(r, italic=True, size=10)
    else:
        add_placeholder(doc, num, description)


def add_code_block(doc, code):
    """Add code as a separate paragraph with Courier New font."""
    p = doc.add_paragraph()
    r = p.add_run(code)
    r.font.name = "Courier New"
    r.font.size = Pt(9)
    doc.add_paragraph("")


# ── Phase 1: Load and fix ──

def main():
    print(f"Loading base: {BASE_DOCX}")
    doc = Document(BASE_DOCX)

    print(f"  Paragraphs: {len(doc.paragraphs)}")
    print(f"  Tables: {len(doc.tables)}")
    print(f"  Images: {len(doc.inline_shapes)}")

    # ── Fix 1: Title page ──
    for p in doc.paragraphs[:15]:
        if "INTEGRATED REPORT - 3" in p.text:
            for run in p.runs:
                run.text = run.text.replace("INTEGRATED REPORT - 3", "INTEGRATED REPORT - 4")
            print("  ✅ Title: Report 3 → Report 4")
            break
        if "INTEGRATED REPORT" in p.text and "3" in p.text:
            for run in p.runs:
                if "3" in run.text:
                    run.text = run.text.replace("3", "4", 1)
            print("  ✅ Title: Report 3 → Report 4")
            break

    # ── Fix 1b: Rewrite Section 2.1 Literature Review ──
    lit_h2 = None
    lit_h2_idx = None
    next_h2_idx = None
    for i, p in enumerate(doc.paragraphs):
        if p.style.name == "Heading 2" and "2.1" in p.text and "Literature" in p.text:
            lit_h2 = p
            lit_h2_idx = i
        elif lit_h2_idx is not None and p.style.name == "Heading 2" and i > lit_h2_idx:
            next_h2_idx = i
            break
    if lit_h2 is not None and next_h2_idx is not None:
        # Remove all paragraphs between 2.1 heading and next H2
        paras_to_remove = doc.paragraphs[lit_h2_idx + 1 : next_h2_idx]
        for p in paras_to_remove:
            p._element.getparent().remove(p._element)
        print(f"  ✅ Removed {len(paras_to_remove)} old 2.1 paragraphs")
        # Insert new content after the 2.1 heading
        summary_text = (
            "The Dominick\u2019s Fine Foods scanner dataset has been used extensively in "
            "retail analytics research, and prior studies converge on three findings "
            "that directly motivate our business questions. First, store-level pricing "
            "strategy materially affects profitability: Hoch, Dr\u00e8ze, and Purk (1994) "
            "demonstrated that DFF\u2019s zone-based pricing could increase profits by "
            "3\u20135%, and Montgomery (1997) extended this with micro-marketing models "
            "that exploit demographic segmentation at the store level \u2014 together "
            "validating our store-tier and demographic analysis (BQ8). Second, "
            "promotional pricing produces measurable but heterogeneous lifts: "
            "Chevalier, Kashyap, and Rossi (2003) showed that DFF used loss-leader "
            "pricing counter-cyclically during peak demand, and Chintagunta (2002) "
            "documented brand-level competitive responses within categories \u2014 both "
            "motivating our promotion-versus-baseline analysis (BQ3, BQ4). Third, "
            "the dataset\u2019s UPC-week-store granularity supports high-dimensional "
            "analyses for category management and demand forecasting (Mehta and "
            "Ma, 2012), which underpins our weekly trend and product-ranking "
            "questions (BQ2, BQ9). Collectively, this body of work confirms that "
            "the DFF data is well-suited to the decision-support questions we "
            "selected, and that our star schema must preserve store, time, product, "
            "category, and promotion dimensions to remain consistent with "
            "established analytical practice."
        )
        citations = [
            "Hoch, S. J., Dr\u00e8ze, X., & Purk, M. E. (1994). EDLP, Hi-Lo, and Margin Arithmetic. Journal of Marketing, 58(4), 16\u201327.",
            "Chevalier, J. A., Kashyap, A. K., & Rossi, P. E. (2003). Why Don\u2019t Prices Rise During Periods of Peak Demand? Evidence from Scanner Data. American Economic Review, 93(1), 15\u201337.",
            "Chintagunta, P. K. (2002). Investigating Category Pricing Behavior at a Retail Chain. Journal of Marketing Research, 39(2), 141\u2013154.",
            "Mehta, S., & Ma, P. (2012). A High Dimensional Data Analysis Approach for Retail Data. Proceedings of the ACM SIGKDD.",
            "Montgomery, A. L. (1997). Creating Micro-Marketing Pricing Strategies Using Supermarket Scanner Data. Marketing Science, 16(4), 315\u2013337.",
        ]
        # Build XML elements to insert after the 2.1 heading
        insert_after = lit_h2._element
        # Summary paragraph
        sp = OxmlElement("w:p")
        sr = OxmlElement("w:r")
        srpr = OxmlElement("w:rPr")
        sfont = OxmlElement("w:rFonts")
        sfont.set(qn("w:ascii"), "Times New Roman")
        sfont.set(qn("w:hAnsi"), "Times New Roman")
        srpr.append(sfont)
        ssz = OxmlElement("w:sz")
        ssz.set(qn("w:val"), "24")  # 12pt
        srpr.append(ssz)
        sr.append(srpr)
        st = OxmlElement("w:t")
        st.set(qn("xml:space"), "preserve")
        st.text = summary_text
        sr.append(st)
        sp.append(sr)
        insert_after.addnext(sp)
        insert_after = sp
        # Sub-heading: "References cited in this section"
        rh = OxmlElement("w:p")
        rhr = OxmlElement("w:r")
        rhrpr = OxmlElement("w:rPr")
        rhfont = OxmlElement("w:rFonts")
        rhfont.set(qn("w:ascii"), "Times New Roman")
        rhfont.set(qn("w:hAnsi"), "Times New Roman")
        rhrpr.append(rhfont)
        rhb = OxmlElement("w:b")
        rhrpr.append(rhb)
        rhsz = OxmlElement("w:sz")
        rhsz.set(qn("w:val"), "24")
        rhrpr.append(rhsz)
        rhr.append(rhrpr)
        rht = OxmlElement("w:t")
        rht.set(qn("xml:space"), "preserve")
        rht.text = "References cited in this section:"
        rhr.append(rht)
        rh.append(rhr)
        insert_after.addnext(rh)
        insert_after = rh
        # Citation paragraphs
        for cite in citations:
            cp = OxmlElement("w:p")
            cr = OxmlElement("w:r")
            crpr = OxmlElement("w:rPr")
            cfont = OxmlElement("w:rFonts")
            cfont.set(qn("w:ascii"), "Times New Roman")
            cfont.set(qn("w:hAnsi"), "Times New Roman")
            crpr.append(cfont)
            csz = OxmlElement("w:sz")
            csz.set(qn("w:val"), "22")  # 11pt
            crpr.append(csz)
            cr.append(crpr)
            ct = OxmlElement("w:t")
            ct.set(qn("xml:space"), "preserve")
            ct.text = cite
            cr.append(ct)
            cp.append(cr)
            insert_after.addnext(cp)
            insert_after = cp
        print("  ✅ Section 2.1 rewritten as synthesized summary with inline citations")
    else:
        print("  ⚠️  Could not find Section 2.1 heading")

    # ── Fix 2: ERD label — catch ALL occurrences ──
    for p in doc.paragraphs:
        if "ERD" in p.text:
            for run in p.runs:
                if "Star Schema ERD" in run.text:
                    run.text = run.text.replace("Star Schema ERD", "Star Schema Diagram")
                elif "ERD" in run.text:
                    run.text = run.text.replace("ERD", "Star Schema Diagram")
            print(f"  ✅ ERD fix: '{p.text[:80]}...'")
    # Also check table cells for ERD
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if "ERD" in cell.text:
                    for p in cell.paragraphs:
                        for run in p.runs:
                            if "Star Schema ERD" in run.text:
                                run.text = run.text.replace("Star Schema ERD", "Star Schema Diagram")
                            elif "ERD" in run.text:
                                run.text = run.text.replace("ERD", "Star Schema Diagram")
                    print(f"  ✅ ERD fix in table cell")

    # ── Fix 2b: Row count correction ──
    for p in doc.paragraphs:
        if "14921365" in p.text or "14,921,365" in p.text:
            for run in p.runs:
                run.text = run.text.replace("14921365", "11,976,442")
                run.text = run.text.replace("14,921,365", "11,976,442")
            print(f"  ✅ Row count fixed: '{p.text[:80]}...'")
    # Also fix in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if "14921365" in cell.text or "14,921,365" in cell.text:
                    for p in cell.paragraphs:
                        for run in p.runs:
                            run.text = run.text.replace("14921365", "11,976,442")
                            run.text = run.text.replace("14,921,365", "11,976,442")
                    print(f"  ✅ Row count fixed in table cell")

    # ── Fix 2c: Report 3 → Report 4 in appendix SQL headers ──
    for p in doc.paragraphs:
        if "Report 3" in p.text and ("DFF" in p.text or "Script" in p.text or "sql" in p.text.lower()):
            for run in p.runs:
                run.text = run.text.replace("Report 3", "Report 4")
            print(f"  ✅ Appendix header: Report 3 → Report 4: '{p.text[:80]}...'")

    # ── Fix 3: Add storage location after database creation heading ──
    storage_added = False
    for i, p in enumerate(doc.paragraphs):
        if p.style.name.startswith("Heading") and "6.1" in p.text and "Database" in p.text:
            # Find the next paragraph and check if storage is already mentioned
            if i + 1 < len(doc.paragraphs):
                next_text = doc.paragraphs[i + 1].text
                if "infodata16" not in next_text:
                    # Insert a new paragraph after the heading
                    new_p = OxmlElement("w:p")
                    run_el = OxmlElement("w:r")
                    rpr = OxmlElement("w:rPr")
                    rfont = OxmlElement("w:rFonts")
                    rfont.set(qn("w:ascii"), "Times New Roman")
                    rfont.set(qn("w:hAnsi"), "Times New Roman")
                    rpr.append(rfont)
                    run_el.append(rpr)
                    t = OxmlElement("w:t")
                    t.set(qn("xml:space"), "preserve")
                    t.text = "The staging database (team1_staging_area) and data mart database (team1_dw_area) are both hosted on SQL Server at infodata16.mbs.tamu.edu in the TAMU ISTM Lab. All SSIS packages, SSRS reports, and SSAS cubes are deployed on the same server instance."
                    run_el.append(t)
                    new_p.append(run_el)
                    p._element.addnext(new_p)
                    storage_added = True
                    print("  ✅ Storage location added after Section 6.1")
                else:
                    print("  ℹ️  Storage location already present")
            break
    if not storage_added:
        print("  ⚠️  Could not find Section 6.1 heading to add storage location")

    # ── Fix 4: Renumber Heading 1 sections ──
    merge_targets = set()
    for p in doc.paragraphs:
        if p.style.name == "Heading 1":
            old = p.text.strip()
            if old in HEADING1_RENAME:
                new_name = HEADING1_RENAME[old]
                if new_name is None:
                    merge_targets.add(old)
                    if "Section 4:" in old:
                        # DELETE this heading entirely — Section 3 H1 covers it
                        p._element.getparent().remove(p._element)
                        print(f"  ✅ Deleted redundant: '{old}'")
                    elif "Section 6:" in old:
                        for run in p.runs:
                            run.text = ""
                        p.runs[0].text = "4.11 Implementation of the ETL Plan"
                        p.style = doc.styles["Heading 2"]
                        print(f"  ✅ Merged: '{old}' → '4.11 Implementation of the ETL Plan'")
                else:
                    for run in p.runs:
                        run.text = ""
                    p.runs[0].text = new_name
                    print(f"  ✅ Renamed: '{old}' → '{new_name}'")

    # ── Fix 4b: Number the Bus Matrix heading ──
    for p in doc.paragraphs:
        if p.style.name == "Heading 2" and p.text.strip() == "Data Mart / Dimension Bus Matrix":
            for run in p.runs:
                run.text = ""
            p.runs[0].text = "3.1 Data Mart / Dimension Bus Matrix"
            print("  ✅ Bus Matrix → '3.1 Data Mart / Dimension Bus Matrix'")
            break

    # ── Fix 5: Renumber sub-section headings (with digit-guard) ──
    for p in doc.paragraphs:
        if p.style.name in ("Heading 2", "Heading 3"):
            text = p.text.strip()
            for old_prefix, new_prefix in sorted(SUBSECTION_MAP.items(), key=lambda x: -len(x[0])):
                if text.startswith(old_prefix):
                    # Defensive: don't match if next char is a digit (e.g. "4.1" vs "4.11")
                    next_char = text[len(old_prefix):len(old_prefix)+1]
                    if next_char.isdigit():
                        continue
                    new_text = text.replace(old_prefix, new_prefix, 1)
                    for run in p.runs:
                        run.text = ""
                    p.runs[0].text = new_text
                    break

    # ── Phase 2: Insert Section 5 BEFORE References ──
    print("\n  Adding Section 5: BI Reporting...")

    # Find the References heading element so we can insert before it
    ref_element = None
    for p in doc.paragraphs:
        if p.style.name == "Heading 1" and "References" in p.text:
            ref_element = p._element
            break

    # Append Section 5 content to end of doc, then move it before References
    body = doc.element.body
    elements_before_section5 = list(body)  # snapshot of current elements

    add_heading_paragraph(doc, "Section 5: BI Reporting", level=1)

    add_body_paragraph(doc, (
        "This section presents the final phase of the data warehousing lifecycle: delivering BI reports "
        "that transform raw data into actionable business knowledge. Using four distinct reporting tools — "
        "SSRS, SSAS, Redshift Query v.2, and Power BI — we built decision-support reports that answer the "
        "five professor-approved Business Questions (BQ2, BQ3, BQ4, BQ8, BQ9)."
    ))

    add_body_paragraph(doc, (
        "Our BI architecture follows a three-layer model: (1) Data Layer — the team1_dw_area star schema on "
        "SQL Server 2016; (2) Application/Analytical Layer — SSAS cube engine, SSRS report server, Redshift "
        "query engine, Power BI data model; (3) Presentation Layer — rendered reports, cube browser pivots, "
        "Redshift result panes, and Power BI interactive dashboards."
    ))

    # 5.1 Reporting Plan
    add_heading_paragraph(doc, "5.1 Reporting Plan", level=2)

    add_heading_paragraph(doc, "5.1.1 Target Reports for Business Questions", level=3)

    add_table(doc,
        ["BQ", "Business Question", "BI Tool", "Report Type"],
        [
            ["BQ2", "Total weekly unit sales of Soft Drinks across all stores", "SSRS", "Tabular report with weekly trend chart"],
            ["BQ3", "Promotion vs non-promotion sales volume comparison", "SSAS", "Cube-based pivot with drill-down"],
            ["BQ4", "Highest incremental sales lift by promotion type (Canned Soup)", "Redshift Query v.2", "Query results with lift multiplier"],
            ["BQ8", "Store quartile tiers by Toothpaste revenue with demographics", "Power BI", "Interactive dashboard"],
            ["BQ9", "Weekly top 10 Cracker products with week-over-week change", "SSRS", "Parameterized report with ranking"],
        ]
    )

    add_heading_paragraph(doc, "5.1.2 Data Mappings from Data Marts to Report Attributes", level=3)

    add_table(doc,
        ["Report Attribute", "Source Table", "Source Column(s)", "Usage"],
        [
            ["Weekly sales trend", "FactWeeklySales + DimTime", "units_sold, week_start_date", "X=week, Y=SUM(units_sold)"],
            ["Promotion segmentation", "FactWeeklySales + DimPromotion", "deal_type, is_promoted", "Group-by / filter"],
            ["Sales lift calculation", "Fact + DimPromotion + DimCategory", "units_sold, deal_type, category_code", "AVG(promoted) − AVG(baseline)"],
            ["Store quartile tiers", "Fact + DimStore + DimCategory", "revenue, avg_income, is_urban", "NTILE(4), demographics"],
            ["Product ranking", "Fact + DimProduct + DimTime", "units_sold, upc, description, week_id", "RANK(), LAG()"],
        ]
    )

    add_heading_paragraph(doc, "5.1.3 Tool Assignment and Justification", level=3)

    add_inline_paragraph(doc, [
        ("1. SSRS (SQL Server Reporting Services): ", True, False),
        ("Used for BQ2 and BQ9. SSRS follows a three-phase workflow: Authoring (designing report layout and queries in Visual Studio), Management (configuring data sources and parameters), and Delivery (previewing or deploying). A shared data source (DFF_DataSource) provides a reusable connection to team1_dw_area.", False, False),
    ])
    add_inline_paragraph(doc, [
        ("2. SSAS (SQL Server Analysis Services): ", True, False),
        ("Used for BQ3. An OLAP cube was built over FactWeeklySales with MOLAP storage mode, which pre-calculates aggregations for fast query response. The cube enables slicing, dicing, and drill-down operations.", False, False),
    ])
    add_inline_paragraph(doc, [
        ("3. Redshift Query v.2: ", True, False),
        ("Used for BQ4. Tables were exported from SQL Server as CSV and loaded into a Redshift cluster in the AWS Academy environment, demonstrating cross-platform portability.", False, False),
    ])
    add_inline_paragraph(doc, [
        ("4. Power BI: ", True, False),
        ("Used for BQ8. The store quartile analysis with demographic overlays is best served by an interactive dashboard with cross-filtering capabilities.", False, False),
    ])

    add_heading_paragraph(doc, "5.1.4 Report Templates", level=3)

    add_table(doc,
        ["Template", "Tool", "Layout", "Decision-Support Purpose"],
        [
            ["Weekly trend", "SSRS", "Line chart + table", "Identifies demand spikes for inventory planning"],
            ["Top-10 parameterized", "SSRS", "Week selector + ranked table", "Inspect product velocity for any week"],
            ["Cube pivot", "SSAS", "Pivot with drill-down", "Compare promoted vs non-promoted sales"],
            ["Cloud query", "Redshift v.2", "SQL editor + result grid", "Auditable lift calculations"],
            ["Quartile dashboard", "Power BI", "Bar chart + matrix + map", "Store tiers with demographic context"],
        ]
    )

    # 5.2 Report Implementation
    add_heading_paragraph(doc, "5.2 Report Implementation", level=2)

    # 5.2.1 SSRS
    add_heading_paragraph(doc, "5.2.1 Reports from Independent Data Marts Using SSRS", level=3)

    add_body_paragraph(doc, (
        "Both SSRS reports follow the authoring, management, and delivery lifecycle. A shared data source "
        "(DFF_DataSource) was configured to connect to team1_dw_area, and report parameters were defined."
    ))

    add_inline_paragraph(doc, [
        ("BQ2 — Weekly Soft Drink Unit Sales (SSRS Tabular Report)", True, False),
    ])
    add_body_paragraph(doc, (
        "The SSRS report executes the BQ2 verification query. The report displays a time-series chart with "
        "week_start_date on the X-axis and SUM(units_sold) on the Y-axis, filtered to category_code = 'SDR'."
    ))

    add_image_or_placeholder(doc, 30, "SSRS Report Designer — BQ2 Weekly SDR Sales trend report layout")
    add_image_or_placeholder(doc, 31, "SSRS Report Preview — BQ2 line chart showing weekly Soft Drink unit sales")

    add_body_paragraph(doc, (
        "The BQ2 report helps DFF identify weekly peaks and dips in Soft Drink unit sales across all stores. "
        "This supports inventory planning and promotion timing by showing which weeks require higher stock "
        "levels or management attention."
    ))

    add_inline_paragraph(doc, [
        ("BQ9 — Weekly Top 10 Cracker Products (SSRS Parameterized Report)", True, False),
    ])
    add_body_paragraph(doc, (
        "This parameterized SSRS report allows the user to select a week_id and see the top 10 Cracker "
        "products by units sold, along with the previous week's units and the week-over-week change "
        "(computed via LAG). The report uses the RANK + LAG query."
    ))

    add_image_or_placeholder(doc, 32, "SSRS Report Designer — BQ9 parameterized Cracker ranking report layout")
    add_image_or_placeholder(doc, 33, "SSRS Report Preview — BQ9 table showing top 10 products for selected week")

    add_body_paragraph(doc, (
        "The BQ9 parameterized report identifies the top-selling Cracker products for a selected week and "
        "compares each product against the previous week. This helps DFF monitor product velocity, detect "
        "sudden demand changes, and adjust shelf space or replenishment priorities."
    ))

    # 5.2.2 SSAS
    add_heading_paragraph(doc, "5.2.2 Report from Cubes Using SSAS", level=3)

    add_inline_paragraph(doc, [
        ("BQ3 — Promotion vs Non-Promotion Sales Volume (SSAS Cube)", True, False),
    ])
    add_body_paragraph(doc, (
        "An SSAS multidimensional project was created in Visual Studio: (1) Data Source connected to "
        "team1_dw_area; (2) Data Source View built from the star schema; (3) DFF_Sales_Cube defined with "
        "measures SUM(units_sold) and SUM(revenue); (4) Dimensions configured with attribute relationships; "
        "(5) Cube deployed and processed with MOLAP storage; (6) Cube browsed for BQ3 analysis."
    ))
    add_body_paragraph(doc, (
        "The BQ3 analysis slices by category_code = 'SDR', then pivots on deal_type with units_sold in "
        "Values. A drill-down by year shows how the promotional effect varies across 1989–1997."
    ))

    add_image_or_placeholder(doc, 34, "Visual Studio — SSAS Cube structure in Solution Explorer")
    add_image_or_placeholder(doc, 35, "SSAS Cube Browser — BQ3 pivot: deal_type vs AVG(units_sold)")
    add_image_or_placeholder(doc, 36, "SSAS Cube Browser — drill-down by year and quarter")

    # 5.2.3 Redshift
    add_heading_paragraph(doc, "5.2.3 Reports from Redshift Query v.2", level=3)

    add_inline_paragraph(doc, [
        ("BQ4 — Promotion Lift by Deal Type in Canned Soup (Redshift Query v.2)", True, False),
    ])
    add_body_paragraph(doc, (
        "The BQ4 analysis was executed in Redshift Query v.2. The FactWeeklySales, DimPromotion, and "
        "DimCategory tables were exported from SQL Server and loaded into a Redshift cluster. The query "
        "computes the average units sold for each promotion type and compares against the non-promotion "
        "baseline to determine the incremental lift and lift multiplier."
    ))

    add_code_block(doc, """-- BQ4: Promotion Lift by Deal Type - Canned Soup (Redshift Query v.2)
WITH baseline AS (
    SELECT AVG(CAST(f.units_sold AS FLOAT)) AS avg_baseline
    FROM FactWeeklySales f
    JOIN DimPromotion dp ON f.promotion_key = dp.promotion_key
    JOIN DimCategory dc ON f.category_key = dc.category_key
    WHERE dc.category_code = 'CSO' AND dp.is_promoted = 0
)
SELECT dp.deal_type,
       COUNT(*) AS num_promoted_records,
       AVG(CAST(f.units_sold AS FLOAT)) AS avg_units_promoted,
       b.avg_baseline,
       AVG(CAST(f.units_sold AS FLOAT)) - b.avg_baseline AS incremental_lift,
       ROUND(AVG(CAST(f.units_sold AS FLOAT)) / b.avg_baseline, 2) AS lift_multiplier
FROM FactWeeklySales f
JOIN DimPromotion dp ON f.promotion_key = dp.promotion_key
JOIN DimCategory dc ON f.category_key = dc.category_key
CROSS JOIN baseline b
WHERE dc.category_code = 'CSO' AND dp.is_promoted = 1
GROUP BY dp.deal_type, b.avg_baseline
ORDER BY incremental_lift DESC;""")

    add_image_or_placeholder(doc, 37, "Redshift Query v.2 — query editor showing BQ4 promotion lift SQL")
    add_image_or_placeholder(doc, 38, "Redshift Query v.2 — BQ4 results: lift by deal type")

    add_body_paragraph(doc, (
        "The BQ4 Redshift output compares promoted Canned Soup records against the non-promotion baseline. "
        "The deal type with the highest incremental lift provides evidence for which promotion mechanism "
        "DFF should prioritize for future Canned Soup campaigns."
    ))

    # 5.2.4 Power BI
    add_heading_paragraph(doc, "5.2.4 Reports Using Power BI", level=3)

    add_inline_paragraph(doc, [
        ("BQ8 — Store Quartile Tiers by Toothpaste Revenue with Demographics (Power BI Dashboard)", True, False),
    ])
    add_body_paragraph(doc, (
        "A Power BI dashboard was built by connecting directly to the team1_dw_area database. The dashboard "
        "contains: (1) a bar chart showing total Toothpaste revenue by store quartile tier; (2) a demographic "
        "comparison table with avg_income, education_pct, poverty_pct, price_tier, and is_urban across "
        "tiers; (3) a geographic map of store locations sized by revenue and colored by tier."
    ))
    add_body_paragraph(doc, (
        "The dashboard confirms that Top 25% Toothpaste stores tend to have higher average income, lower "
        "poverty rates, and are more likely to be in higher price tiers — validating the hypothesis that "
        "demographic and economic factors influence category performance."
    ))

    add_image_or_placeholder(doc, 39, "Power BI — Data model view showing star schema connections")
    add_image_or_placeholder(doc, 40, "Power BI — BQ8 dashboard: store quartile bar chart + demographic table")
    add_image_or_placeholder(doc, 41, "Power BI — BQ8 dashboard: map view of stores by revenue tier")

    # 5.3 Storage Locations
    add_heading_paragraph(doc, "5.3 BI Tool Deployment and Storage Locations", level=2)

    add_table(doc,
        ["Component", "Location"],
        [
            ["Staging Database", "team1_staging_area on SQL Server, infodata16.mbs.tamu.edu"],
            ["Data Mart Database", "team1_dw_area on SQL Server, infodata16.mbs.tamu.edu"],
            ["SSIS Packages (.dtsx)", "Visual Studio 2015 project folder on lab machine"],
            ["SSRS Reports (.rdl)", "SSRS Report Server on infodata16.mbs.tamu.edu"],
            ["SSAS Cube", "SSAS instance on infodata16.mbs.tamu.edu, database: DFF_Sales_Cube"],
            ["Power BI Dashboard", "Local file: DFF_BQ8_Dashboard.pbix"],
            ["Redshift Queries", "Amazon Redshift Query Editor v.2 (AWS Academy)"],
            ["SQL Scripts", "report_4/sql/ directory — 8 scripts"],
        ]
    )

    # 5.4 Summary
    add_heading_paragraph(doc, "5.4 Summary: All Business Questions Supported", level=2)

    add_table(doc,
        ["BQ", "Question", "Tool", "Report Delivered", "Charts", "Analysis"],
        [
            ["BQ2", "Weekly SDR unit sales", "SSRS", "Tabular + trend chart", "✅", "✅"],
            ["BQ3", "Promo vs non-promo sales", "SSAS", "Cube pivot + drill-down", "✅", "✅"],
            ["BQ4", "Promo lift by type (CSO)", "Redshift v.2", "Analytical result set", "Table", "✅"],
            ["BQ8", "Store quartile tiers (TPA)", "Power BI", "Interactive dashboard", "✅", "✅"],
            ["BQ9", "Top 10 weekly CRA products", "SSRS", "Parameterized report", "✅", "✅"],
        ]
    )

    # ── Move Section 5 elements before References ──
    if ref_element is not None:
        new_elements = [el for el in body if el not in elements_before_section5]
        for el in new_elements:
            ref_element.addprevious(el)
        print("  ✅ Section 5 inserted before References")
    else:
        print("  ⚠️  References heading not found — Section 5 appended at end")

    # ── Save ──
    doc.save(OUT_DOCX)
    kb = os.path.getsize(OUT_DOCX) / 1024
    ss_count = sum(1 for n in range(30, 42) if os.path.exists(os.path.join(SS_DIR, f"screenshot_{n:02d}.png")))
    print(f"\n✅ Saved: {OUT_DOCX}")
    print(f"   Size: {kb:.1f} KB")
    print(f"   BI screenshots embedded: {ss_count}/12")
    if ss_count < 12:
        print(f"   Remaining: {12-ss_count} placeholders (add screenshots and re-run)")


if __name__ == "__main__":
    main()
