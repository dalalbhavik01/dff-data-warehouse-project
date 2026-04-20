#!/usr/bin/env python3
"""
Generate a formatted DOCX from Integrated_Report_4.md.

Design goals:
  - Clean, Google Docs-compatible output (no hard page breaks, no complex XML)
  - Times New Roman 12pt body, black text throughout
  - Minimal formatting that survives a round-trip through Google Docs
  - Placeholder boxes for BI screenshots 30-41 (clean gray-bordered tables)
  - All ETL screenshots (1-29) and diagrams embedded directly
"""

import re
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MD_PATH    = os.path.join(SCRIPT_DIR, "Integrated_Report_4.md")
OUT_PATH   = os.path.join(SCRIPT_DIR, "Integrated_Report_4.docx")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def set_cell_bg(cell, hex_color):
    """Set a table cell background color via OOXML shading."""
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    shd.set(qn("w:val"), "clear")
    cell._tc.get_or_add_tcPr().append(shd)


def add_table_borders(table, color="BBBBBB", sz="4"):
    """Add a uniform thin border around every edge of a table."""
    tbl   = table._tbl
    tblPr = tbl.find(qn("w:tblPr"))
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        tbl.insert(0, tblPr)
    # Remove any existing tblBorders first
    for old in tblPr.findall(qn("w:tblBorders")):
        tblPr.remove(old)
    tblBorders = OxmlElement("w:tblBorders")
    for side in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"),   "single")
        b.set(qn("w:sz"),    sz)
        b.set(qn("w:space"), "0")
        b.set(qn("w:color"), color)
        tblBorders.append(b)
    tblPr.append(tblBorders)


def set_row_min_height(row, twips=800):
    """Set a minimum row height (in twips, 1440 twips = 1 inch)."""
    trPr    = row._tr.get_or_add_trPr()
    trH     = OxmlElement("w:trHeight")
    trH.set(qn("w:val"),   str(twips))
    trH.set(qn("w:hRule"), "atLeast")
    trPr.append(trH)


# ---------------------------------------------------------------------------
# Content renderers
# ---------------------------------------------------------------------------

def add_placeholder_box(doc, label, instruction=""):
    """
    Render a clean gray-bordered 1-column table as a screenshot placeholder.
    Row 0 (gray bg):  bold label e.g.  '[Screenshot 30 Placeholder]'
    Row 1 (white bg): italic instruction describing exactly what to capture.
    Google Docs renders simple table borders perfectly.
    """
    rows  = 2 if instruction else 1
    table = doc.add_table(rows=rows, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_table_borders(table, color="AAAAAA", sz="6")

    # Label row
    c0 = table.cell(0, 0)
    c0.text = ""
    p0 = c0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r0 = p0.add_run(label)
    r0.bold = True
    r0.font.size = Pt(12)
    r0.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    set_cell_bg(c0, "EEEEEE")
    set_row_min_height(table.rows[0], 700)

    # Instruction row
    if instruction:
        c1 = table.cell(1, 0)
        c1.text = ""
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p1.add_run(instruction)
        r1.italic = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        set_cell_bg(c1, "FAFAFA")
        set_row_min_height(table.rows[1], 500)

    doc.add_paragraph("")   # one blank line after


def add_image(doc, image_path, caption=""):
    """Embed an image (centered, 5.5 in wide) with an optional italic caption."""
    if os.path.exists(image_path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(image_path, width=Inches(5.5))
        if caption:
            cp = doc.add_paragraph()
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cr = cp.add_run(caption)
            cr.italic = True
            cr.font.size = Pt(12)
            cr.font.name = "Times New Roman"
            cr.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        doc.add_paragraph("")
    else:
        add_placeholder_box(doc, f"[Image not found: {os.path.basename(image_path)}]")


def add_code_block(doc, code_text):
    """
    Render a code block as a single-cell table with a light-gray background.
    Using a table (instead of paragraph shading XML) is more stable in Google Docs.
    """
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    add_table_borders(table, color="CCCCCC", sz="4")
    cell = table.cell(0, 0)
    cell.text = ""
    set_cell_bg(cell, "F5F5F5")
    p = cell.paragraphs[0]
    p.paragraph_format.left_indent  = Cm(0.3)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(code_text)
    run.font.name  = "Courier New"
    run.font.size  = Pt(9)
    run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    doc.add_paragraph("")


def add_md_table(doc, header_line, data_lines):
    """Convert a markdown pipe table to a Word table."""
    def parse_row(line):
        return [c.strip() for c in line.strip().strip("|").split("|")]

    headers   = parse_row(header_line)
    rows_data = [parse_row(l) for l in data_lines]
    cols      = len(headers)

    table = doc.add_table(rows=1 + len(rows_data), cols=cols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(9)
        set_cell_bg(cell, "D9E2F3")

    for r_idx, row_data in enumerate(rows_data):
        for c_idx in range(min(cols, len(row_data))):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = ""
            run = cell.paragraphs[0].add_run(row_data[c_idx])
            run.font.name = "Times New Roman"
            run.font.size = Pt(9)

    doc.add_paragraph("")


def process_inline(paragraph, text):
    """Apply **bold**, *italic*, `inline_code` markdown to a paragraph."""
    parts = re.split(r"(\*\*.*?\*\*|\*.*?\*|`.*?`)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            r = paragraph.add_run(part[2:-2])
            r.bold = True
            r.font.name = "Times New Roman"
        elif part.startswith("*") and part.endswith("*") and not part.startswith("**"):
            r = paragraph.add_run(part[1:-1])
            r.italic = True
            r.font.name = "Times New Roman"
        elif part.startswith("`") and part.endswith("`"):
            r = paragraph.add_run(part[1:-1])
            r.font.name  = "Courier New"
            r.font.size  = Pt(12)
            r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        else:
            r = paragraph.add_run(part)
            r.font.name = "Times New Roman"


# ---------------------------------------------------------------------------
# Line-type detectors
# ---------------------------------------------------------------------------

def detect_screenshot_placeholder(line):
    """Legacy pattern: *[Screenshot X: ...]* → returns inner text or None."""
    s = line.strip()
    for pat in [r"^\*\[(Screenshot.*?)\]\*$", r"^\*\[\*?(Screenshot.*?)\*?\]\*$",
                r"^\*\[(INSERT:.*?)\]\*$"]:
        m = re.match(pat, s)
        if m:
            return m.group(1)
    return None


def detect_image_line(line):
    """![alt](path) → returns (alt, path) or None."""
    m = re.match(r"^!\[(.*?)\]\((.*?)\)$", line.strip())
    return (m.group(1), m.group(2)) if m else None


def detect_blockquote_placeholder(line):
    """
    '> **[Screenshot N Placeholder]** instruction...'
    Returns (label, instruction) or None.
    """
    s = line.strip()
    if not s.startswith("> "):
        return None
    content = s[2:].strip()
    m = re.match(r"\*\*(\[Screenshot \d+ Placeholder\])\*\* (.*)", content)
    if m:
        return m.group(1), m.group(2).strip()
    return None


# ---------------------------------------------------------------------------
# Pre-flight
# ---------------------------------------------------------------------------

def preflight_check():
    """Print a clear warning if BI screenshots 30-41 are missing."""
    ss_dir  = os.path.join(SCRIPT_DIR, "screenshots")
    missing = [
        f"screenshot_{n:02d}.png"
        for n in range(30, 42)
        if not os.path.exists(os.path.join(ss_dir, f"screenshot_{n:02d}.png"))
    ]
    if not missing:
        return   # all present — proceed silently

    print("=" * 60)
    print("⚠️  WARNING: BI screenshots missing")
    print("=" * 60)
    print(f"\n  {len(missing)} of 12 screenshots (30–41) not found:\n")
    for m in missing:
        print(f"    {m}")
    print("""
  DOCX will contain bordered placeholder boxes instead.

  When you have real screenshots:
    1. Save them as  screenshots/screenshot_30.png … screenshot_41.png
    2. Re-run:       python3 generate_docx.py
""")
    print("=" * 60)
    ans = input("  Continue with placeholder boxes? [y/N]: ").strip().lower()
    if ans != "y":
        print("  Aborted.")
        raise SystemExit(0)
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    preflight_check()

    with open(MD_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    doc = Document()

    # Standard 1-inch margins (Google Docs default — no custom XML needed)
    for section in doc.sections:
        section.top_margin    = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin   = Cm(2.54)
        section.right_margin  = Cm(2.54)

    # Body font: Times New Roman 12pt (academic standard)
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)

    # Heading fonts — Times New Roman, restrained sizes, plain black
    # Spacing matched to Report 3: H1 before=12/after=6, H2/H3 before=8/after=4
    heading_config = {
        "Heading 1": (Pt(16), Pt(12), Pt(6)),   # ## Section X
        "Heading 2": (Pt(14), Pt(8),  Pt(4)),   # ### subsection
        "Heading 3": (Pt(12), Pt(8),  Pt(4)),   # #### sub-subsection
    }
    for style_name, (size, sp_before, sp_after) in heading_config.items():
        try:
            h_style = doc.styles[style_name]
            h_style.font.name  = "Times New Roman"
            h_style.font.size  = size
            h_style.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
            h_style.paragraph_format.space_before = sp_before
            h_style.paragraph_format.space_after  = sp_after
        except KeyError:
            pass

    i            = 0
    in_code      = False
    code_lines   = []

    while i < len(lines):
        raw  = lines[i].rstrip("\n")
        line = raw   # keep original for prefix checks

        # ── Code block fence ──────────────────────────────────────────────
        if line.startswith("```"):
            if in_code:
                add_code_block(doc, "\n".join(code_lines))
                code_lines = []
                in_code    = False
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        # ── Horizontal rule  →  simple blank paragraph (no XML borders) ──
        if line.strip() == "---":
            doc.add_paragraph("")
            i += 1
            continue

        # ── Headings ──────────────────────────────────────────────────────
        if line.startswith("# ") and not line.startswith("## "):
            p = doc.add_heading(line[2:].strip(), level=0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            # Title: 18pt Times New Roman bold, black
            for run in p.runs:
                run.font.name  = "Times New Roman"
                run.font.size  = Pt(18)
                run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
            i += 1
            continue
        if line.startswith("## "):
            p = doc.add_heading(line[3:].strip(), level=1)
            for run in p.runs:
                run.font.name  = "Times New Roman"
                run.font.size  = Pt(16)
                run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
            i += 1
            continue
        if line.startswith("### "):
            p = doc.add_heading(line[4:].strip(), level=2)
            for run in p.runs:
                run.font.name  = "Times New Roman"
                run.font.size  = Pt(14)
                run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
            i += 1
            continue
        if line.startswith("#### "):
            p = doc.add_heading(line[5:].strip(), level=3)
            for run in p.runs:
                run.font.name  = "Times New Roman"
                run.font.size  = Pt(12)
                run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
            i += 1
            continue

        # ── Image embed  ![alt](path) ─────────────────────────────────────
        img = detect_image_line(line)
        if img:
            alt, path = img
            if not os.path.isabs(path):
                path = os.path.join(SCRIPT_DIR, path)
            add_image(doc, path, alt)
            i += 1
            continue

        # ── Legacy *[Screenshot…]* placeholder ───────────────────────────
        ph = detect_screenshot_placeholder(line)
        if ph:
            add_placeholder_box(doc, ph)
            i += 1
            continue

        # ── Blockquote  >  (inc. placeholder instructions) ─────────────
        if line.strip().startswith("> "):
            bq = detect_blockquote_placeholder(line)
            if bq:
                label, instruction = bq
                # label already contains brackets, e.g. "[Screenshot 30 Placeholder]"
                add_placeholder_box(doc, f"{label}", instruction)
            else:
                content = line.strip()[2:].strip()
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.8)
                r = p.add_run(content)
                r.italic = True
                r.font.name = "Times New Roman"
                r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
            i += 1
            continue

        # ── Markdown table ────────────────────────────────────────────────
        if "|" in line and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if re.match(r"^\|[\s:-]+\|", next_line):
                header = line
                j      = i + 2          # skip separator row
                data   = []
                while j < len(lines) and lines[j].strip().startswith("|"):
                    data.append(lines[j].rstrip("\n"))
                    j += 1
                add_md_table(doc, header, data)
                i = j
                continue

        # ── Bullet list ───────────────────────────────────────────────────
        stripped = line.strip()
        if stripped.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            process_inline(p, stripped[2:])
            i += 1
            continue

        # ── Numbered list ─────────────────────────────────────────────────
        m = re.match(r"^(\d+)\.\s+(.*)", stripped)
        if m:
            p = doc.add_paragraph(style="List Number")
            process_inline(p, m.group(2))
            i += 1
            continue

        # ── Empty line → small spacer (keeps paragraphs separated) ────────
        if stripped == "":
            p = doc.add_paragraph("")
            p.paragraph_format.space_after = Pt(2)
            i += 1
            continue

        # ── Tab-indented line (TOC subsections) ──────────────────────────
        if line.startswith("\t"):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(1.0)
            process_inline(p, line.strip())
            i += 1
            continue

        # ── Regular paragraph ─────────────────────────────────────────────
        p = doc.add_paragraph()
        process_inline(p, line)
        i += 1

    doc.save(OUT_PATH)
    kb = os.path.getsize(OUT_PATH) / 1024
    present  = sum(1 for n in range(1, 42)
                   if os.path.exists(os.path.join(SCRIPT_DIR, "screenshots",
                                                   f"screenshot_{n:02d}.png")))
    missing_bi = 42 - 1 - present   # 42 slots, 1-indexed, minus what exists

    print(f"✅ DOCX saved: {OUT_PATH}")
    print(f"   Size:           {kb:.1f} KB")
    print(f"   Screenshots:    {present} embedded  |  {12 - (41 - present + 1 if present < 30 else max(0, 41 - present + 1))} BI placeholders")


if __name__ == "__main__":
    main()
