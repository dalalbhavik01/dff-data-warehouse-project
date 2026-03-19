from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT_PATH = Path(
    "/Users/bhavikdalal/Documents/data warehouse/project/report_2/hybrid_etl_pipeline_diagram_v2.png"
)

WIDTH = 2400
HEIGHT = 1350
BG = "#f8fafc"
TEXT = "#0f172a"
SUBTEXT = "#475569"
LINE = "#334155"


def load_font(size, bold=False):
    candidates = []
    if bold:
        candidates.extend(
            [
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/System/Library/Fonts/Supplemental/Helvetica.ttc",
            ]
        )
    candidates.extend(
        [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Tahoma.ttf",
        ]
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


FONT_TITLE = load_font(54, bold=True)
FONT_SUBTITLE = load_font(24)
FONT_BOX_TITLE = load_font(27, bold=True)
FONT_BODY = load_font(19)
FONT_LABEL = load_font(22, bold=True)
FONT_FOOT = load_font(20)


def rounded_box(draw, xy, radius, fill, outline, width=4):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def wrap_line(draw, text, font, max_width):
    if not text:
        return [""]
    words = text.split()
    if not words:
        return [text]

    wrapped = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = candidate
        else:
            wrapped.append(current)
            current = word
    wrapped.append(current)
    return wrapped


def wrap_lines(draw, lines, font, max_width):
    wrapped = []
    for line in lines:
        if not line:
            wrapped.append("")
            continue
        leading = line[: len(line) - len(line.lstrip(" "))]
        for idx, segment in enumerate(wrap_line(draw, line.strip(), font, max_width)):
            wrapped.append(f"{leading}{segment}" if idx == 0 else f"{leading}{segment}")
    return wrapped


def draw_multiline(draw, pos, lines, font, fill, line_gap=8):
    x, y = pos
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, y), line, font=font)
        y = bbox[3] + line_gap


def draw_box(draw, xy, title, lines, fill, outline):
    x1, y1, x2, y2 = xy
    inner_width = (x2 - x1) - 56
    rounded_box(draw, xy, radius=28, fill=fill, outline=outline, width=4)
    title_lines = wrap_lines(draw, [title], FONT_BOX_TITLE, inner_width)
    draw_multiline(draw, (x1 + 28, y1 + 24), title_lines, FONT_BOX_TITLE, TEXT, line_gap=6)
    title_height = 0
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=FONT_BOX_TITLE)
        title_height += (bbox[3] - bbox[1]) + 6
    wrapped_body = wrap_lines(draw, lines, FONT_BODY, inner_width)
    draw_multiline(
        draw,
        (x1 + 28, y1 + 30 + title_height + 18),
        wrapped_body,
        FONT_BODY,
        "#1f2937",
        line_gap=8,
    )


def draw_arrow(draw, start, end, label):
    sx, sy = start
    ex, ey = end
    draw.line((sx, sy, ex, ey), fill=LINE, width=6)
    arrow_size = 18
    draw.polygon(
        [
            (ex, ey),
            (ex - arrow_size * 2, ey - arrow_size),
            (ex - arrow_size * 2, ey + arrow_size),
        ],
        fill=LINE,
    )
    text_bbox = draw.textbbox((0, 0), label, font=FONT_LABEL)
    tx = (sx + ex - (text_bbox[2] - text_bbox[0])) / 2
    ty = sy - 58
    rounded_box(
        draw,
        (tx - 16, ty - 8, tx + (text_bbox[2] - text_bbox[0]) + 16, ty + 36),
        radius=16,
        fill="#ffffff",
        outline="#cbd5e1",
        width=2,
    )
    draw.text((tx, ty), label, font=FONT_LABEL, fill=LINE)


def main():
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    draw.text((90, 55), "DFF Hybrid ETL Pipeline Architecture", font=FONT_TITLE, fill=TEXT)
    draw.text(
        (90, 125),
        "Report 2 flow from operational CSV files to staging, star schema presentation server, and OLAP-ready analysis.",
        font=FONT_SUBTITLE,
        fill=SUBTEXT,
    )

    boxes = {
        "source": (90, 300, 450, 980),
        "extract": (560, 300, 1010, 980),
        "stage": (1120, 300, 1570, 980),
        "mart": (1680, 300, 2290, 980),
    }

    draw_box(
        draw,
        boxes["source"],
        "Source System Files",
        [
            "- Movement CSVs (24)",
            "- UPC CSVs (28)",
            "- DEMO.csv",
            "- CCOUNT.csv",
            "",
            "Operational flat-file inputs",
            "from the DFF source system",
        ],
        "#dbeafe",
        "#2563eb",
    )

    draw_box(
        draw,
        boxes["extract"],
        "Batch Extraction and Cleansing",
        [
            "- read raw CSV files",
            "- derive CATEGORY_CODE",
            "  from filenames",
            "- filter invalid rows",
            "  (OK = 0, PRICE = 0)",
            "- standardize text fields",
            "- preserve SALE values",
        ],
        "#e0f2fe",
        "#0284c7",
    )

    draw_box(
        draw,
        boxes["stage"],
        "Relational Staging Area",
        [
            "- stg_Movement",
            "- stg_Product",
            "- stg_Store",
            "",
            "Temporary relational layer for",
            "validation, traceability, and",
            "controlled transformations",
        ],
        "#dcfce7",
        "#16a34a",
    )

    draw_box(
        draw,
        boxes["mart"],
        "Presentation Server / Data Mart",
        [
            "- FactWeeklySales",
            "- DimTime",
            "- DimStore",
            "- DimProduct",
            "- DimCategory",
            "- DimPromotion",
            "",
            "Star schema for HOLAP analysis",
            "and professor-selected BQs",
        ],
        "#fce7f3",
        "#db2777",
    )

    mid_y = 720
    draw_arrow(draw, (boxes["source"][2] + 18, mid_y), (boxes["extract"][0] - 18, mid_y), "Extraction")
    draw_arrow(draw, (boxes["extract"][2] + 18, mid_y), (boxes["stage"][0] - 18, mid_y), "Mapping Table #1")
    draw_arrow(draw, (boxes["stage"][2] + 18, mid_y), (boxes["mart"][0] - 18, mid_y), "Mapping Table #2")

    rounded_box(
        draw,
        (690, 1070, 1710, 1195),
        radius=24,
        fill="#fef3c7",
        outline="#d97706",
        width=4,
    )
    draw.text((730, 1095), "Business Rules Applied Across the Pipeline", font=FONT_LABEL, fill="#7c2d12")
    rules_lines = wrap_lines(
        draw,
        [
            "- surrogate key generation   - foreign key lookups   - derived facts: revenue, unit_price, profit_margin_pct"
        ],
        FONT_BODY,
        1710 - 690 - 80,
    )
    draw_multiline(draw, (730, 1138), rules_lines, FONT_BODY, "#7c2d12", line_gap=8)

    rounded_box(
        draw,
        (1760, 120, 2310, 245),
        radius=24,
        fill="#ffffff",
        outline="#94a3b8",
        width=3,
    )
    draw.text((1810, 150), "Future Independent Mart", font=FONT_LABEL, fill=SUBTEXT)
    draw.text((1810, 188), "FactCustomerTraffic (optional later phase)", font=FONT_BODY, fill=SUBTEXT)
    draw.line((2035, 245, 2035, 290), fill="#94a3b8", width=4)
    draw.polygon([(2035, 290), (2020, 265), (2050, 265)], fill="#94a3b8")

    draw.text(
        (1815, 1030),
        "Supports BQ2, BQ3, BQ4,\nBQ8, and BQ9",
        font=FONT_LABEL,
        fill="#9d174d",
        spacing=10,
    )

    draw.text(
        (90, 1275),
        "Architecture in Report 2: Hybrid Data Pipeline + Independent Data Marts + Star Schema + SQL Server 2016",
        font=FONT_FOOT,
        fill=SUBTEXT,
    )

    image.save(OUT_PATH, format="PNG")


if __name__ == "__main__":
    main()
