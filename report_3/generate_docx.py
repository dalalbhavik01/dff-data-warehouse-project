#!/usr/bin/env python3
"""
Generate a professionally formatted DOCX from Integrated_Report_3.md.

Matches the formatting and theme used in Reports 1 & 2:
  - Times New Roman 12pt body text
  - Heading 1: 16pt bold black
  - Heading 2: 14pt bold black
  - Heading 3: 12pt bold black
  - 1-inch margins
  - Centered title page with team info
  - Table Grid style with blue header shading (D9E2F3)
  - Yellow placeholder boxes for screenshots/ERDs
  - Consolas 8.5pt code blocks with light gray background
"""

import re
from docx import Document
from docx.shared import Inches, Pt, Cm, Emu, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(SCRIPT_DIR, "Integrated_Report_3.md")
OUT_PATH = os.path.join(SCRIPT_DIR, "Integrated_Report_3.docx")


# ================================================================
# Helper Functions
# ================================================================

def set_cell_shading(cell, color):
    """Set cell background color."""
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), color)
    shading.set(qn("w:val"), "clear")
    cell._tc.get_or_add_tcPr().append(shading)


def add_page_break(doc):
    """Add a page break."""
    p = doc.add_paragraph()
    run = p.add_run()
    run.add_break(docx.enum.text.WD_BREAK.PAGE)


def add_bottom_border(paragraph, color="999999", size="6"):
    """Add a horizontal line under a paragraph."""
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), size)
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)
    pBdr.append(bottom)
    pPr.append(pBdr)


def add_placeholder_box(doc, text):
    """Add a yellow placeholder box for screenshots/ERDs."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x66, 0x33, 0x00)
    run.font.italic = True
    set_cell_shading(cell, "FFFFCC")
    # Set minimum cell height
    tr = table.rows[0]._tr
    trPr = tr.get_or_add_trPr()
    trHeight = OxmlElement("w:trHeight")
    trHeight.set(qn("w:val"), "1200")
    trHeight.set(qn("w:hRule"), "atLeast")
    trPr.append(trHeight)
    doc.add_paragraph("")


def add_code_block(doc, code_text):
    """Add a formatted code block with light gray background."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.5)
    pf.right_indent = Cm(0.5)
    pf.space_before = Pt(4)
    pf.space_after = Pt(4)
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
    # Gray background
    pPr = p._p.get_or_add_pPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), "F5F5F5")
    shading.set(qn("w:val"), "clear")
    pPr.append(shading)
    run = p.add_run(code_text)
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)


def add_md_table(doc, header_line, separator_line, data_lines):
    """Add a markdown table as a formatted Word table."""
    def parse_row(line):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        return cells

    headers = parse_row(header_line)
    cols = len(headers)
    rows_data = [parse_row(l) for l in data_lines]

    table = doc.add_table(rows=1 + len(rows_data), cols=cols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row - blue background
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(9)
        set_cell_shading(cell, "D9E2F3")

    # Data rows
    for r_idx, row_data in enumerate(rows_data):
        for c_idx in range(min(cols, len(row_data))):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = ""
            p = cell.paragraphs[0]
            run = p.add_run(row_data[c_idx])
            run.font.name = "Times New Roman"
            run.font.size = Pt(9)

    doc.add_paragraph("")


def process_inline(paragraph, text):
    """Process inline markdown formatting: **bold**, *italic*, `code`."""
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
        elif part.startswith("*") and part.endswith("*") and not part.startswith("**"):
            run = paragraph.add_run(part[1:-1])
            run.italic = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
        elif part.startswith("`") and part.endswith("`"):
            run = paragraph.add_run(part[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0xC0, 0x39, 0x2B)
        else:
            run = paragraph.add_run(part)
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)


# ================================================================
# Title Page
# ================================================================

def create_title_page(doc):
    """Create a professional title page matching Reports 1 & 2."""
    # Add vertical spacing at top
    for _ in range(5):
        p = doc.add_paragraph("")
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)

    # Report Title
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("INTEGRATED REPORT - 3")
    run.font.name = "Times New Roman"
    run.font.size = Pt(18)
    run.bold = True
    p.paragraph_format.space_after = Pt(6)

    # Subtitle
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Requirements Analysis, Data Design and\nETL Design using SSIS")
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)
    run.bold = True
    p.paragraph_format.space_after = Pt(12)

    # Project title
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Design and Implementation of a Data Warehouse\nfor a Retail Store with Store-level Data")
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.bold = True
    p.paragraph_format.space_after = Pt(24)

    # Course info
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("ISTM 637 - Data Warehousing\nTexas A&M University\nSpring 2026")
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    p.paragraph_format.space_after = Pt(18)

    # Team
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Team 1:")
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.bold = True
    p.paragraph_format.space_after = Pt(4)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Nisarg Sonar\nBhavik Dalal\nYifei Wang")
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    p.paragraph_format.space_after = Pt(18)

    # Date
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Date: April 8, 2026")
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    p.paragraph_format.space_after = Pt(0)

    # Page break after title page
    doc.add_page_break()


# ================================================================
# Table of Contents Page
# ================================================================

def create_toc_page(doc):
    """Create a Table of Contents page (matching Report 2 format)."""
    p = doc.add_heading("Table of Contents", level=1)
    p.runs[0].font.name = "Times New Roman"

    toc_items = [
        ("1.", "Introduction", 1),
        ("1.1", "About Dominick's Fine Foods", 2),
        ("1.2", "Project Design Specifications", 2),
        ("1.3", "Understanding of the Data", 2),
        ("1.4", "Key Data Quality Issues", 2),
        ("1.5", "Source Data Relationships (ERD)", 2),
        ("2.", "Subject Area Understanding", 1),
        ("2.1", "Literature Review", 2),
        ("2.2", "Business Questions", 2),
        ("2.3", "Prioritization of Business Questions", 2),
        ("2.4", "Data Evidence Supporting Selected BQs", 2),
        ("3.", "Overview of Kimball's Methodology", 1),
        ("4.", "Data Warehouse Logical Design (Star Schema Design)", 1),
        ("4.1", "Selected Business Questions", 2),
        ("4.2", "Star Schema Table Definitions", 2),
        ("4.3", "Schema Justification", 2),
        ("4.4", "Star Schema Diagram", 2),
        ("4.5", "Mapping Table #1", 2),
        ("4.6", "Mapping Table #2", 2),
        ("4.7", "Physical Design Plan", 2),
        ("5.", "Development of the ETL Plan", 1),
        ("5.1", "All Target Data in the Data Warehouse", 2),
        ("5.2", "All Data Sources", 2),
        ("5.3", "Data Mappings", 2),
        ("5.4", "Comprehensive Data Extraction Rules", 2),
        ("5.5", "Data Transformation and Cleansing Rules", 2),
        ("5.6", "Plan for Aggregate Tables", 2),
        ("5.7", "Organization of Data Staging Area", 2),
        ("5.8", "Procedures for All Data Extractions and Loadings", 2),
        ("5.9", "ETL for Dimension Table", 2),
        ("5.10", "ETL for Fact Table", 2),
        ("6.", "Implementation of the ETL Plan", 1),
        ("6.1", "Database Creation", 2),
        ("6.2", "Staging Table Creation", 2),
        ("6.3", "Data Mart Table Creation", 2),
        ("6.4", "SSIS Package 1: Extract to Staging", 2),
        ("6.5", "SSIS Package 2: Transform Staging", 2),
        ("6.6", "SSIS Package 3: Load Data Mart", 2),
        ("6.7", "Temporary Table Cleanup", 2),
        ("6.8", "Granularity Discussion", 2),
        ("6.9", "Business Question Verification", 2),
        ("6.10", "Final Data Mart Summary", 2),
        ("7.", "References", 1),
        ("8.", "Appendix", 1),
    ]

    for num, title, level in toc_items:
        style_name = "toc 1" if level == 1 else "toc 2"
        # Use a custom approach since toc styles may not exist
        p = doc.add_paragraph()
        indent = Cm(0) if level == 1 else Cm(1)
        p.paragraph_format.left_indent = indent
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(f"{num}\t{title}")
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)
        if level == 1:
            run.bold = True

    doc.add_page_break()


# ================================================================
# Configure Document Styles
# ================================================================

def configure_styles(doc):
    """Set up document styles to match Reports 1 & 2."""
    # Page margins: 1 inch all around
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Normal style: Times New Roman 12pt
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.paragraph_format.space_after = Pt(4)

    # Heading 1: 16pt bold black
    h1 = doc.styles["Heading 1"]
    h1.font.name = "Times New Roman"
    h1.font.size = Pt(16)
    h1.font.bold = True
    h1.font.color.rgb = RGBColor(0, 0, 0)
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(6)

    # Heading 2: 14pt bold black
    h2 = doc.styles["Heading 2"]
    h2.font.name = "Times New Roman"
    h2.font.size = Pt(14)
    h2.font.bold = True
    h2.font.color.rgb = RGBColor(0, 0, 0)
    h2.paragraph_format.space_before = Pt(8)
    h2.paragraph_format.space_after = Pt(4)

    # Heading 3: 12pt bold black
    h3 = doc.styles["Heading 3"]
    h3.font.name = "Times New Roman"
    h3.font.size = Pt(12)
    h3.font.bold = True
    h3.font.color.rgb = RGBColor(0, 0, 0)
    h3.paragraph_format.space_before = Pt(8)
    h3.paragraph_format.space_after = Pt(4)

    # List Bullet
    try:
        lb = doc.styles["List Bullet"]
        lb.font.name = "Times New Roman"
        lb.font.size = Pt(12)
    except:
        pass

    # List Number
    try:
        ln = doc.styles["List Number"]
        ln.font.name = "Times New Roman"
        ln.font.size = Pt(12)
    except:
        pass


# ================================================================
# Main Processing
# ================================================================

def main():
    import docx.enum.text

    with open(MD_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    doc = Document()
    configure_styles(doc)

    # --- Title Page ---
    create_title_page(doc)

    # --- Table of Contents ---
    create_toc_page(doc)

    # --- Process Markdown Body ---
    i = 0
    in_code_block = False
    code_lines = []

    # Skip the markdown header (title, metadata, TOC) since we built our own
    # Find where Section 1 starts
    start_idx = 0
    for idx, line in enumerate(lines):
        if line.strip().startswith("## Section 1"):
            start_idx = idx
            break
    i = start_idx

    while i < len(lines):
        line = lines[i].rstrip("\n")

        # --- Code blocks ---
        if line.startswith("```"):
            if in_code_block:
                code_text = "\n".join(code_lines)
                add_code_block(doc, code_text)
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # --- Horizontal rule ---
        if line.strip() == "---":
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            add_bottom_border(p)
            i += 1
            continue

        # --- Headings ---
        # ## Section X -> Heading 1
        if line.startswith("## "):
            heading_text = line[3:].strip()
            p = doc.add_heading(heading_text, level=1)
            for run in p.runs:
                run.font.name = "Times New Roman"
                run.font.color.rgb = RGBColor(0, 0, 0)
            i += 1
            continue

        # ### -> Heading 2
        if line.startswith("### "):
            heading_text = line[4:].strip()
            p = doc.add_heading(heading_text, level=2)
            for run in p.runs:
                run.font.name = "Times New Roman"
                run.font.color.rgb = RGBColor(0, 0, 0)
            i += 1
            continue

        # #### -> Heading 3
        if line.startswith("#### "):
            heading_text = line[5:].strip()
            p = doc.add_heading(heading_text, level=3)
            for run in p.runs:
                run.font.name = "Times New Roman"
                run.font.color.rgb = RGBColor(0, 0, 0)
            i += 1
            continue

        # --- Screenshot / ERD placeholders ---
        # Match patterns like *[Screenshot 1: ...]* or *[INSERT: ...]*
        # Also match *[*Screenshot 15: ...*]*
        placeholder_match = re.match(
            r'^\*\[\*?(Screenshot.*?|INSERT:.*?)\*?\]\*$', line.strip()
        )
        if placeholder_match:
            add_placeholder_box(doc, placeholder_match.group(1))
            i += 1
            continue

        # Also catch *[Insert Excel ...]* placeholders
        placeholder_match2 = re.match(
            r'^\*\[(Insert.*?)\]\*$', line.strip(), re.IGNORECASE
        )
        if placeholder_match2:
            add_placeholder_box(doc, placeholder_match2.group(1))
            i += 1
            continue

        # --- Tables ---
        if "|" in line and i + 1 < len(lines) and re.match(
            r'^\|[\s:-]+\|', lines[i + 1].strip()
        ):
            header_line = line
            sep_line = lines[i + 1].rstrip("\n")
            data_lines = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                data_lines.append(lines[j].rstrip("\n"))
                j += 1
            add_md_table(doc, header_line, sep_line, data_lines)
            i = j
            continue

        # --- Bullet points ---
        if line.strip().startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            text = line.strip()[2:]
            process_inline(p, text)
            i += 1
            continue

        # --- Numbered lists ---
        num_match = re.match(r'^(\d+)\.\s+(.*)', line.strip())
        if num_match:
            p = doc.add_paragraph(style="List Number")
            process_inline(p, num_match.group(2))
            i += 1
            continue

        # --- Empty lines - skip ---
        if line.strip() == "":
            i += 1
            continue

        # --- Regular paragraph ---
        p = doc.add_paragraph()
        process_inline(p, line)
        i += 1

    # Save
    doc.save(OUT_PATH)
    print(f"  DOCX saved to: {OUT_PATH}")
    print(f"   File size: {os.path.getsize(OUT_PATH) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
