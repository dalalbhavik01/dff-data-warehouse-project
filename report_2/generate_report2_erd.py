import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


TITLE_BG = "#173F73"
TITLE_FG = "white"
ROW_EVEN = "#F6F8FC"
ROW_ODD = "#FFFFFF"
BORDER = "#2A5CAA"
PK_COLOR = "#C62828"
FK_COLOR = "#EF6C00"
TEXT = "#1F2937"
SUBTEXT = "#4B5563"


def draw_table(ax, x, y, width, title, subtitle, columns):
    """Draw a simple dimensional-model table box."""
    title_h = 0.52
    subtitle_h = 0.30
    row_h = 0.30
    body_h = len(columns) * row_h
    total_h = title_h + subtitle_h + body_h

    # Outer shell
    ax.add_patch(
        FancyBboxPatch(
            (x, y - total_h),
            width,
            total_h,
            boxstyle="round,pad=0.02,rounding_size=0.03",
            linewidth=1.6,
            edgecolor=BORDER,
            facecolor="white",
        )
    )

    # Title
    ax.add_patch(
        FancyBboxPatch(
            (x, y - title_h),
            width,
            title_h,
            boxstyle="round,pad=0.02,rounding_size=0.03",
            linewidth=0,
            facecolor=TITLE_BG,
        )
    )
    ax.text(
        x + width / 2,
        y - title_h / 2,
        title,
        ha="center",
        va="center",
        color=TITLE_FG,
        fontsize=11,
        fontweight="bold",
    )

    # Subtitle
    subtitle_y = y - title_h
    ax.add_patch(
        plt.Rectangle(
            (x, subtitle_y - subtitle_h),
            width,
            subtitle_h,
            facecolor="#E9EFFA",
            edgecolor="none",
        )
    )
    ax.text(
        x + width / 2,
        subtitle_y - subtitle_h / 2,
        subtitle,
        ha="center",
        va="center",
        color=SUBTEXT,
        fontsize=8.5,
        style="italic",
    )

    # Rows
    current_y = subtitle_y - subtitle_h
    for i, (name, dtype, key) in enumerate(columns):
        ax.add_patch(
            plt.Rectangle(
                (x, current_y - row_h),
                width,
                row_h,
                facecolor=ROW_EVEN if i % 2 == 0 else ROW_ODD,
                edgecolor="#D6DFEF",
                linewidth=0.5,
            )
        )

        if key:
            key_color = PK_COLOR if key == "PK" else FK_COLOR
            ax.text(
                x + 0.18,
                current_y - row_h / 2,
                key,
                ha="left",
                va="center",
                fontsize=8.5,
                color=key_color,
                fontweight="bold",
            )

        ax.text(
            x + 0.58,
            current_y - row_h / 2,
            name,
            ha="left",
            va="center",
            fontsize=8.7,
            color=TEXT,
            family="monospace",
        )
        ax.text(
            x + width - 0.14,
            current_y - row_h / 2,
            dtype,
            ha="right",
            va="center",
            fontsize=8.2,
            color=SUBTEXT,
        )
        current_y -= row_h

    return {
        "x": x,
        "y": y,
        "width": width,
        "height": total_h,
        "left": (x, y - total_h / 2),
        "right": (x + width, y - total_h / 2),
        "top": (x + width / 2, y),
        "bottom": (x + width / 2, y - total_h),
    }


def connect(ax, p1, p2, label, rad=0.0):
    arrow = FancyArrowPatch(
        p1,
        p2,
        arrowstyle="-|>",
        mutation_scale=14,
        linewidth=2.0,
        color=BORDER,
        connectionstyle=f"arc3,rad={rad}",
    )
    ax.add_patch(arrow)
    mid_x = (p1[0] + p2[0]) / 2
    mid_y = (p1[1] + p2[1]) / 2
    ax.text(
        mid_x,
        mid_y + 0.14,
        label,
        ha="center",
        va="center",
        fontsize=8.5,
        color=TITLE_BG,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#B5C7E8", lw=1),
    )


fig, ax = plt.subplots(figsize=(18, 12))
ax.axis("off")

boxes = {}
boxes["fact"] = draw_table(
    ax,
    6.9,
    7.6,
    4.8,
    "FactWeeklySales",
    "Grain: 1 UPC x 1 Store x 1 Week | ~134.9M rows",
    [
        ("sales_fact_id", "INT", "PK"),
        ("product_key", "INT", "FK"),
        ("store_key", "INT", "FK"),
        ("time_key", "INT", "FK"),
        ("category_key", "INT", "FK"),
        ("promotion_key", "INT", "FK"),
        ("units_sold", "INT", ""),
        ("unit_price", "DEC(8,2)", ""),
        ("shelf_price", "DEC(8,2)", ""),
        ("price_qty", "INT", ""),
        ("revenue", "DEC(12,2)", ""),
        ("gross_profit", "DEC(10,2)", ""),
        ("profit_margin_pct", "DEC(5,2)", ""),
    ],
)

boxes["product"] = draw_table(
    ax,
    1.0,
    9.8,
    4.0,
    "DimProduct",
    "One row per UPC | ~14K rows",
    [
        ("product_key", "INT", "PK"),
        ("upc", "BIGINT", ""),
        ("description", "VARCHAR(100)", ""),
        ("size", "VARCHAR(20)", ""),
        ("case_pack", "INT", ""),
        ("commodity_code", "INT", ""),
        ("item_number", "BIGINT", ""),
        ("category_key", "INT", "FK"),
    ],
)

boxes["store"] = draw_table(
    ax,
    13.4,
    9.8,
    4.2,
    "DimStore",
    "One row per store | ~107 rows",
    [
        ("store_key", "INT", "PK"),
        ("store_id", "INT", ""),
        ("store_name", "VARCHAR(50)", ""),
        ("city", "VARCHAR(40)", ""),
        ("zone", "INT", ""),
        ("is_urban", "BIT", ""),
        ("weekly_volume", "INT", ""),
        ("avg_income", "DEC(10,2)", ""),
        ("education_pct", "DEC(5,2)", ""),
        ("poverty_pct", "DEC(5,2)", ""),
        ("price_tier", "VARCHAR(10)", ""),
    ],
)

boxes["time"] = draw_table(
    ax,
    6.2,
    11.4,
    3.8,
    "DimTime",
    "One row per week | ~400 rows",
    [
        ("time_key", "INT", "PK"),
        ("week_id", "INT", ""),
        ("week_start_date", "DATE", ""),
        ("week_end_date", "DATE", ""),
        ("month", "INT", ""),
        ("quarter", "INT", ""),
        ("year", "INT", ""),
        ("is_holiday_week", "BIT", ""),
    ],
)

boxes["category"] = draw_table(
    ax,
    6.3,
    2.8,
    3.6,
    "DimCategory",
    "One row per category | 28 rows",
    [
        ("category_key", "INT", "PK"),
        ("category_code", "CHAR(3)", ""),
        ("category_name", "VARCHAR(30)", ""),
        ("department", "VARCHAR(20)", ""),
    ],
)

boxes["promotion"] = draw_table(
    ax,
    11.8,
    4.5,
    3.9,
    "DimPromotion",
    "One row per promotion type | 4 rows",
    [
        ("promotion_key", "INT", "PK"),
        ("deal_code", "CHAR(1)", ""),
        ("deal_type", "VARCHAR(20)", ""),
        ("is_promoted", "BIT", ""),
    ],
)

connect(ax, boxes["product"]["right"], boxes["fact"]["left"], "product_key", rad=-0.06)
connect(ax, boxes["store"]["left"], boxes["fact"]["right"], "store_key", rad=0.05)
connect(ax, boxes["time"]["bottom"], boxes["fact"]["top"], "time_key", rad=0.0)
connect(ax, boxes["category"]["top"], boxes["fact"]["bottom"], "category_key", rad=0.0)
connect(ax, boxes["promotion"]["left"], (boxes["fact"]["right"][0], boxes["fact"]["bottom"][1] + 1.0), "promotion_key", rad=0.08)
connect(ax, boxes["category"]["left"], boxes["product"]["bottom"], "category_key", rad=-0.22)

ax.text(
    9.0,
    11.9,
    "DFF Report 2 Star Schema ERD",
    ha="center",
    va="center",
    fontsize=20,
    fontweight="bold",
    color=TITLE_BG,
)
ax.text(
    9.0,
    11.45,
    "Current implemented mart for professor-selected BQs: BQ2, BQ3, BQ4, BQ8, BQ9",
    ha="center",
    va="center",
    fontsize=10,
    color=SUBTEXT,
)

ax.text(
    9.0,
    0.55,
    "All relationships are 1:N from dimension to fact. DimProduct also carries category_key for category lookup/supporting semantics.",
    ha="center",
    va="center",
    fontsize=9,
    color=SUBTEXT,
)

ax.set_xlim(0, 18.5)
ax.set_ylim(0, 12.5)

out = "/Users/bhavikdalal/Documents/data warehouse/project/report_2/report2_star_schema_erd.png"
plt.tight_layout()
plt.savefig(out, dpi=300, bbox_inches="tight")
print(f"Saved {out}")
