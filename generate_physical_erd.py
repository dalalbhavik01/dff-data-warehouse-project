import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

# Physical ERD with Indexing and Partitioning specific annotations as per Task 3B slides
fig, ax = plt.subplots(figsize=(16, 11))
ax.axis('off')

# Colors
TITLE_BG = '#1F497D' # Darker blue
TITLE_FG = 'white'
ROW_ALT1 = '#F2F2F2'
ROW_ALT2 = '#FFFFFF'
BORDER = '#2F5496'
PK_COLOR = '#C00000'
FK_COLOR = '#E36C09'
IDX_COLOR = '#385723' # Green for indices

def create_table(ax, x, y, width, title, columns, partition_info=None):
    """Draws a physical database table with index annotations"""
    # Title bar
    ax.add_patch(Rectangle((x, y), width, 0.45, facecolor=TITLE_BG, edgecolor=BORDER))
    ax.text(x + width/2, y + 0.225, title, color=TITLE_FG, weight='bold', 
            ha='center', va='center', size=11, family='sans-serif')
    
    # Columns
    current_y = y
    box_height = len(columns) * 0.35
    
    # Background for columns
    ax.add_patch(Rectangle((x, current_y - box_height), width, box_height, 
                           facecolor=ROW_ALT2, edgecolor=BORDER, zorder=0))
    
    for i, (col_name, col_type, key_type, idx_type) in enumerate(columns):
        current_y -= 0.35
        
        # Alternating row background
        if i % 2 == 0:
            ax.add_patch(Rectangle((x, current_y), width, 0.35, 
                                   facecolor=ROW_ALT1, edgecolor='none', zorder=1))
        
        # Key indicator (PK/FK)
        if key_type:
            color = PK_COLOR if key_type == 'PK' else (FK_COLOR if key_type == 'FK' else '#595959')
            ax.text(x + 0.25, current_y + 0.175, key_type, color=color, 
                    weight='bold', ha='center', va='center', size=9)
            
        # Column Name
        font_weight = 'bold' if 'PK' in key_type or 'FK' in key_type else 'normal'
        ax.text(x + 0.6, current_y + 0.175, col_name, weight=font_weight,
                ha='left', va='center', size=10, family='monospace', zorder=2)
                
        # Data Type
        ax.text(x + width - 1.5, current_y + 0.175, col_type, color='#595959',
                ha='right', va='center', size=9, zorder=2)
                
        # Index indicator (from slide 25/26 etc)
        if idx_type:
            ax.text(x + width - 0.1, current_y + 0.175, idx_type, color=IDX_COLOR,
                    ha='right', va='center', size=8, style='italic', weight='bold', zorder=2)
            
    # Partitioning info box at the bottom if provided (Slide 11/12)
    final_bottom = y - box_height
    if partition_info:
        part_height = 0.4
        ax.add_patch(Rectangle((x, final_bottom - part_height), width, part_height, 
                               facecolor='#FFF2CC', edgecolor='#D6B656', zorder=0))
        ax.text(x + width/2, final_bottom - part_height/2, partition_info, color='#A67C00',
                ha='center', va='center', size=9, style='italic')
        final_bottom -= part_height
    
    return {
        'top': (x + width/2, y + 0.45),
        'bottom': (x + width/2, final_bottom),
        'left': (x, y - box_height/2),
        'right': (x + width, y - box_height/2),
        'x': x,
        'y': y,
        'width': width,
        'height': y + 0.45 - final_bottom
    }

# --- Define Physical Tables (Annotated based on Task 3B slides) ---
tables = {
    'FactWeeklySales': { # Renamed to reflect physical star schema fact table (Slide 31/32)
        'pos': (6, 5),
        'title': 'FactWeeklySales (Movement)\n~134.9M rows | Physical Size: ~5GB',
        'cols': [
            ('STORE_ID', 'INT', 'PK/FK', '[B-Tree Clustered]'),
            ('UPC', 'INT', 'PK/FK', '[B-Tree Clustered]'),
            ('WEEK_ID', 'INT', 'PK/FK', '[B-Tree Clustered]'),
            ('MOVE', 'INT', '', ''),
            ('QTY', 'INT', '', ''),
            ('PRICE', 'DECIMAL', '', ''),
            ('SALE', 'VARCHAR(1)', '', '[Bitmap]'),  # Low selectivity -> Bitmap (Slide 21)
            ('PROFIT', 'DECIMAL', '', ''),
            ('OK', 'INT', '', '[Bitmap]')   # Low selectivity
        ],
        'partition': 'Horizontally Partitioned by CATEGORY (24 files)\n(Reduces I/O during queries)' # Slide 11/12
    },
    'DimProduct': {
        'pos': (1, 8),
        'title': 'DimProduct (UPC)\n~14K rows',
        'cols': [
            ('UPC', 'INT', 'PK', '[Unique B-Tree]'), # Slide 25
            ('COM_CODE', 'INT', '', '[B-Tree]'),
            ('DESCRIP', 'VARCHAR(30)', '', ''),
            ('SIZE', 'VARCHAR(10)', '', ''),
            ('CASE', 'INT', '', ''),
            ('NITEM', 'INT', '', '')
        ],
        'partition': None
    },
    'DimStore': {
        'pos': (11.5, 8),
        'title': 'DimStore (DEMO)\n108 rows | 510 cols',
        'cols': [
            ('STORE_ID', 'INT', 'PK', '[Unique B-Tree]'),
            ('NAME', 'VARCHAR(50)', '', ''),
            ('CITY', 'VARCHAR(50)', '', '[Bitmap]'), # Low selectivity
            ('ZONE', 'INT', '', '[Bitmap]'), # 15 zones -> low selectivity -> Bitmap
            ('URBAN', 'INT', '', '[Bitmap]'), # Binary -> Bitmap
            ('INCOME', 'DECIMAL', '', ''),
            ('... (504 more cols)', 'MIXED', '', '')
        ],
        'partition': None
    },
    'FactTraffic': {
        'pos': (11.5, 3),
        'title': 'FactTraffic (CCOUNT)\n327K rows',
        'cols': [
            ('STORE_ID', 'INT', 'PK/FK', '[B-Tree]'),
            ('WEEK_ID', 'INT', 'PK/FK', '[B-Tree]'),
            ('CUSTCOUN', 'INT', '', ''),
            ('GROCERY', 'INT', '', ''),
            ('DAIRY', 'INT', '', ''),
            ('FROZEN', 'INT', '', ''),
            ('... (55 more cols)', 'INT', '', '')
        ],
        'partition': None
    }
}

# --- Draw Tables ---
boxes = {}
for name, data in tables.items():
    boxes[name] = create_table(ax, data['pos'][0], data['pos'][1], 4.2, data['title'], data['cols'], data['partition'])

# --- Draw Relationships ---
def draw_line(p1, p2, label, connectionstyle='arc3,rad=0.1'):
    patch = FancyArrowPatch(p1, p2, connectionstyle=connectionstyle, 
                            arrowstyle='<-', color=BORDER, lw=2.5, mutation_scale=15)
    ax.add_patch(patch)
    
    mid_x = (p1[0] + p2[0]) / 2
    mid_y = (p1[1] + p2[1]) / 2
    
    bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec=BORDER, lw=1)
    ax.text(mid_x, mid_y, label, ha="center", va="center", size=9.5, 
            weight='bold', color=TITLE_BG, bbox=bbox_props, zorder=5)

# FactWeeklySales -> DimProduct
draw_line(
    (boxes['FactWeeklySales']['left'][0], boxes['FactWeeklySales']['y'] - 0.9),
    (boxes['DimProduct']['right'][0], boxes['DimProduct']['y'] - 0.5),
    '1    :    N\n(UPC)',
    connectionstyle='bar,angle=180,fraction=-0.15'
)

# FactWeeklySales -> DimStore
draw_line(
    (boxes['FactWeeklySales']['right'][0], boxes['FactWeeklySales']['y'] - 0.5),
    (boxes['DimStore']['left'][0], boxes['DimStore']['y'] - 0.5),
    '1    :    N\n(STORE_ID)',
    connectionstyle='bar,angle=0,fraction=-0.15'
)

# FactWeeklySales -> FactTraffic (Shared Dimensions logical link)
draw_line(
    (boxes['FactWeeklySales']['right'][0], boxes['FactWeeklySales']['y'] - 1.25),
    (boxes['FactTraffic']['left'][0], boxes['FactTraffic']['y'] - 0.9),
    '1    :    N\n(STORE_ID + WEEK_ID)',
    connectionstyle='bar,angle=0,fraction=-0.25'
)

# Legend for Physical Design Elements
legend_x = 1
legend_y = 2.5
ax.add_patch(Rectangle((legend_x, legend_y), 3.5, 1.8, facecolor='#F8FAFC', edgecolor='#BDD7EE'))
ax.text(legend_x + 1.75, legend_y + 1.5, 'Physical Design Notes (Task 3B)', 
        weight='bold', ha='center', size=10, color=TITLE_BG)
ax.text(legend_x + 0.2, legend_y + 1.1, '• B-Tree Index: High selectivity keys (UPC)', size=9)
ax.text(legend_x + 0.2, legend_y + 0.8, '• Bitmap Index: Low selectivity (SALE, URBAN)', size=9)
ax.text(legend_x + 0.2, legend_y + 0.5, '• Clustered Index: Fact table composite PK', size=9)
ax.text(legend_x + 0.2, legend_y + 0.2, '• Partitioning: Fact table split by category', size=9)


plt.suptitle("Dominick's Finer Foods (DFF) — Physical Data Warehouse Design", 
             fontsize=20, weight='bold', color=TITLE_BG, y=0.96)
plt.figtext(0.5, 0.04, "* Physical model incorporates Star Schema design, indexing strategies, and partitioning as per Task 3B requirements.", 
            ha="center", fontsize=11, style='italic', color='#595959')

ax.set_xlim(0, 16)
ax.set_ylim(0, 10.5)

plt.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.savefig('/Users/bhavikdalal/Documents/data warehouse/project/physical_erd_task3b.png', dpi=300, bbox_inches='tight')
print("High-quality physical ERD generated: physical_erd_task3b.png")
