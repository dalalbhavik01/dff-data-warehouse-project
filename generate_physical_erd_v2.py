import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, ConnectionPatch

# More elaborate Physical ERD with precise types, partition strategies, and indexing
fig, ax = plt.subplots(figsize=(18, 13))
ax.axis('off')

# Custom Colors
TITLE_BG = '#002060' # Deep navy blue
TITLE_FG = 'white'
ROW_ALT1 = '#E8EBF5'
ROW_ALT2 = '#FFFFFF'
BORDER = '#4472C4'
PK_COLOR = '#C00000'
FK_COLOR = '#E36C09'
IDX_COLOR = '#00B050' # Vibrant green for indices
PART_BG = '#FFF2CC'
PART_FG = '#C65911'

def create_table(ax, x, y, width, title, subtitle, columns, partition_info=None):
    """Draws a detailed physical database table with precision annotations"""
    # Title bar (Table Name)
    ax.add_patch(Rectangle((x, y), width, 0.45, facecolor=TITLE_BG, edgecolor=BORDER))
    ax.text(x + width/2, y + 0.225, title, color=TITLE_FG, weight='bold', 
            ha='center', va='center', size=12, family='sans-serif')
            
    # Subtitle bar (Metadata)
    ax.add_patch(Rectangle((x, y - 0.3), width, 0.3, facecolor='#D9E1F2', edgecolor=BORDER))
    ax.text(x + width/2, y - 0.15, subtitle, color='black', style='italic',
            ha='center', va='center', size=9.5)
    
    # Columns
    current_y = y - 0.3
    box_height = len(columns) * 0.35 + 0.1 # slight padding
    
    # Background for columns
    ax.add_patch(Rectangle((x, current_y - box_height), width, box_height, 
                           facecolor=ROW_ALT2, edgecolor=BORDER, zorder=0))
    
    for i, (col_name, col_type, key_type, idx_type) in enumerate(columns):
        current_y -= 0.35
        
        # Alternating row background
        if i % 2 == 0:
            ax.add_patch(Rectangle((x, current_y), width, 0.35, 
                                   facecolor=ROW_ALT1, edgecolor='none', zorder=1))
        
        # Key indicator (PK/FK/PFK)
        if key_type:
            color = PK_COLOR if 'PK' in key_type else (FK_COLOR if 'FK' in key_type else '#595959')
            ax.text(x + 0.4, current_y + 0.175, key_type, color=color, 
                    weight='bold', ha='center', va='center', size=9.5)
            
        # Column Name
        font_weight = 'bold' if key_type in ['PK', 'FK', 'PFK'] else 'normal'
        ax.text(x + 0.9, current_y + 0.175, col_name, weight=font_weight,
                ha='left', va='center', size=10.5, family='monospace', zorder=2)
                
        # Data Type (Precise)
        ax.text(x + width - 1.8, current_y + 0.175, col_type, color='#3B3838',
                ha='right', va='center', size=9.5, zorder=2)
                
        # Index indicator
        if idx_type:
            ax.text(x + width - 0.1, current_y + 0.175, idx_type, color=IDX_COLOR,
                    ha='right', va='center', size=8.5, style='italic', weight='bold', zorder=2)
            
    # Partitioning info box at the bottom
    final_bottom = y - 0.3 - box_height
    if partition_info:
        part_height = 0.5
        ax.add_patch(Rectangle((x, final_bottom - part_height), width, part_height, 
                               facecolor=PART_BG, edgecolor=PART_FG, zorder=0))
        # Handle multiline Partition warning
        lines = partition_info.split('\n')
        for idx, line in enumerate(lines):
            ax.text(x + width/2, final_bottom - 0.15 - (idx*0.2), line, color=PART_FG,
                    ha='center', va='center', size=9.5, weight='bold')
        final_bottom -= part_height
    
    return {
        'top': (x + width/2, y + 0.45),
        'bottom': (x + width/2, final_bottom),
        'left': (x, y - (0.3 + box_height)/2),
        'right': (x + width, y - (0.3 + box_height)/2),
        'x': x,
        'y': y,
        'width': width,
        'height': y + 0.45 - final_bottom
    }

# --- Detailed Physical Definitions ---
tables = {
    'FactWeeklySales': { 
        'pos': (6.5, 6),
        'title': 'FactWeeklySales (Movement Data)',
        'subtitle': '134,929,320 Rows | Size: ~5.2 GB | Record Length: 42 Bytes',
        'cols': [
            ('STORE_ID', 'INT(4)', 'PFK', '[Clustered Idx 1]'),
            ('WEEK_ID', 'INT(4)', 'PFK', '[Clustered Idx 2]'),
            ('UPC', 'BIGINT(12)', 'PFK', '[Clustered Idx 3]'),
            ('MOVE', 'INT(6)', '', ''),
            ('QTY', 'INT(2)', '', ''),
            ('PRICE', 'DECIMAL(6,2)', '', ''),
            ('PROFIT', 'DECIMAL(6,2)', '', ''),
            ('SALE', 'CHAR(1)', '', '[Bitmap Idx]'),  
            ('OK', 'TINYINT(1)', '', '[Bitmap Idx]')   
        ],
        'partition': 'PARTITION BY LIST (Category)\n24 Partitions (SDR, CSO, FRE, etc.)'
    },
    'DimProduct': {
        'pos': (1, 9),
        'title': 'DimProduct (UPC Master)',
        'subtitle': '14,249 Rows | Size: ~2 MB | Record Length: 78 Bytes',
        'cols': [
            ('UPC', 'BIGINT(12)', 'PK', '[Unique B-Tree]'),
            ('COM_CODE', 'INT(4)', '', '[NCI B-Tree]'),
            ('DESCRIP', 'VARCHAR(29)', '', ''),
            ('SIZE', 'VARCHAR(12)', '', ''),
            ('CASE', 'INT(4)', '', ''),
            ('NITEM', 'INT(6)', '', '')
        ],
        'partition': None
    },
    'DimStore': {
        'pos': (12.5, 9),
        'title': 'DimStore (DEMO / Demographics)',
        'subtitle': '108 Rows | Size: ~400 KB | Record Length: 2048 Bytes',
        'cols': [
            ('STORE_ID', 'INT(4)', 'PK', '[Unique B-Tree]'),
            ('NAME', 'VARCHAR(50)', '', ''),
            ('CITY', 'VARCHAR(40)', '', '[Bitmap Idx]'), 
            ('ZIP', 'INT(5)', '', '[NCI B-Tree]'),
            ('ZONE', 'TINYINT(2)', '', '[Bitmap Idx]'), 
            ('URBAN', 'TINYINT(1)', '', '[Bitmap Idx]'), 
            ('INCOME', 'DECIMAL(10,4)', '', ''),
            ('HSIZEAVG', 'DECIMAL(4,2)', '', ''),
            ('PRICLOW', 'TINYINT(1)', '', '[Bitmap Idx]'),
            ('... (501 more census cols)', 'MIXED', '', '')
        ],
        'partition': None
    },
    'FactTraffic': {
        'pos': (12.5, 3),
        'title': 'FactCustomerTraffic (CCOUNT)',
        'subtitle': '327,045 Rows | Size: ~80 MB | Record Length: 244 Bytes',
        'cols': [
            ('STORE_ID', 'INT(4)', 'PFK', '[Clustered Idx 1]'),
            ('WEEK_ID', 'INT(4)', 'PFK', '[Clustered Idx 2]'),
            ('CUSTCOUN', 'INT(6)', '', ''),
            ('GROCERY', 'INT(6)', '', ''),
            ('DAIRY', 'INT(6)', '', ''),
            ('FROZEN', 'INT(6)', '', ''),
            ('MEAT', 'INT(6)', '', ''),
            ('... (54 dept/coupon cols)', 'INT(6)', '', '')
        ],
        'partition': None
    }
}

# --- Draw Tables ---
boxes = {}
for name, data in tables.items():
    boxes[name] = create_table(ax, data['pos'][0], data['pos'][1], 4.8, 
                               data['title'], data['subtitle'], data['cols'], data['partition'])

# --- Draw Relationships (Crow's Foot Style) ---
def draw_line(p1, p2, label, connectionstyle='arc3,rad=0.1'):
    patch = FancyArrowPatch(p1, p2, connectionstyle=connectionstyle, 
                            arrowstyle='<-', color=BORDER, lw=3, mutation_scale=20)
    ax.add_patch(patch)
    
    mid_x = (p1[0] + p2[0]) / 2
    mid_y = (p1[1] + p2[1]) / 2
    
    bbox_props = dict(boxstyle="round,pad=0.4", fc="white", ec=BORDER, lw=1.5)
    ax.text(mid_x, mid_y, label, ha="center", va="center", size=10.5, 
            weight='bold', color=TITLE_BG, bbox=bbox_props, zorder=5)

# FactWeeklySales -> DimProduct
draw_line(
    (boxes['FactWeeklySales']['left'][0], boxes['FactWeeklySales']['y'] - 1.1),
    (boxes['DimProduct']['right'][0], boxes['DimProduct']['y'] - 0.7),
    '1    :    N\n(UPC = UPC)',
    connectionstyle='bar,angle=180,fraction=-0.1'
)

# FactWeeklySales -> DimStore
draw_line(
    (boxes['FactWeeklySales']['right'][0], boxes['FactWeeklySales']['y'] - 0.5),
    (boxes['DimStore']['left'][0], boxes['DimStore']['y'] - 0.7),
    '1    :    N\n(STORE_ID = STORE_ID)',
    connectionstyle='bar,angle=0,fraction=-0.15'
)

# FactWeeklySales -> FactTraffic (Shared Dimensions logical link)
draw_line(
    (boxes['FactWeeklySales']['right'][0], boxes['FactWeeklySales']['y'] - 0.8),
    (boxes['FactTraffic']['left'][0], boxes['FactTraffic']['y'] - 0.7),
    '1    :    N\n(STORE_ID, WEEK_ID)',
    connectionstyle='bar,angle=0,fraction=-0.3'
)

# Legend Context Box
legend_x = 0.5
legend_y = 2.5
ax.add_patch(Rectangle((legend_x, legend_y), 5.5, 2.5, facecolor='#F8FAFC', edgecolor='#BDD7EE'))
ax.add_patch(Rectangle((legend_x, legend_y+2.1), 5.5, 0.4, facecolor=TITLE_BG))
ax.text(legend_x + 2.75, legend_y + 2.3, 'Physical Implementation Notes (Task 3B)', 
        weight='bold', ha='center', size=11, color='white')

legend_text = """
• Composite Primary Keys (PFK): Fact tables utilize
  composite keys (STORE_ID + WEEK_ID + UPC) to establish
  grain. Built with B-Tree Clustered Indexes to optimize
  range queries on time and location.
• Bitmap Indexing: Applied to low-selectivity columns 
  found in DFF data (SALE flags: B/C/S/null, URBAN: 0/1, 
  ZONE: 1-15, OK quality flags).
• Partitioning Strategy: The 134.9M row movement
  Fact table is horizontally partitioned by Category
  (Soft Drinks, Cereals, etc.) matching the 24 source CSVs
  to drastically reduce I/O during single-category OLAP scans.
• Storage Calculations: Explicit data types (INT(4), 
  DECIMAL(6,2)) optimized to minimize row length overhead.
"""
ax.text(legend_x + 0.2, legend_y + 0.1, legend_text.strip(), size=10, family='sans-serif', va='bottom')


plt.suptitle("Dominick's Finer Foods (DFF) — Elaborate Physical Star Schema ERD", 
             fontsize=24, weight='bold', color=TITLE_BG, y=0.96)
plt.figtext(0.5, 0.03, "* Highly-detailed physical model derived from DFF academic dataset constraints, incorporating indexing strategies, row sizes, and table partitioning paradigms.", 
            ha="center", fontsize=12, style='italic', color='#595959')

ax.set_xlim(0, 18)
ax.set_ylim(0, 12)

plt.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.savefig('report_charts/physical_erd_detailed_v2.png', dpi=400, bbox_inches='tight')
print("High-quality precise physical ERD generated: report_charts/physical_erd_detailed_v2.png")
