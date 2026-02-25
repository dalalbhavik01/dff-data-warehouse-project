import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, ConnectionPatch

fig, ax = plt.subplots(figsize=(14, 10))
ax.axis('off')

# Colors
TITLE_BG = '#2F5496'
TITLE_FG = 'white'
ROW_ALT1 = '#EDF2F9'
ROW_ALT2 = '#FFFFFF'
BORDER = '#4472C4'
PK_COLOR = '#C00000'
FK_COLOR = '#E36C09'

def create_table(ax, x, y, width, title, columns):
    """Draws a detailed database table"""
    # Title bar
    ax.add_patch(Rectangle((x, y), width, 0.4, facecolor=TITLE_BG, edgecolor=BORDER))
    ax.text(x + width/2, y + 0.2, title, color=TITLE_FG, weight='bold', 
            ha='center', va='center', size=11, family='sans-serif')
    
    # Columns
    current_y = y
    box_height = len(columns) * 0.3
    
    # Background for columns
    ax.add_patch(Rectangle((x, current_y - box_height), width, box_height, 
                           facecolor=ROW_ALT2, edgecolor=BORDER, zorder=0))
    
    for i, (col_name, col_type, key_type) in enumerate(columns):
        current_y -= 0.3
        
        # Alternating row background
        if i % 2 == 0:
            ax.add_patch(Rectangle((x, current_y), width, 0.3, 
                                   facecolor=ROW_ALT1, edgecolor='none', zorder=1))
        
        # Key indicator (PK/FK)
        if key_type:
            color = PK_COLOR if key_type == 'PK' else FK_COLOR
            ax.text(x + 0.2, current_y + 0.15, key_type, color=color, 
                    weight='bold', ha='center', va='center', size=9)
            
        # Column Name
        font_weight = 'bold' if key_type else 'normal'
        ax.text(x + 0.5, current_y + 0.15, col_name, weight=font_weight,
                ha='left', va='center', size=10, family='monospace', zorder=2)
                
        # Data Type
        ax.text(x + width - 0.2, current_y + 0.15, col_type, color='#595959',
                ha='right', va='center', size=9, style='italic', zorder=2)
    
    return {
        'top': (x + width/2, y + 0.4),
        'bottom': (x + width/2, y - box_height),
        'left': (x, y - box_height/2),
        'right': (x + width, y - box_height/2),
        'x': x,
        'y': y,
        'width': width,
        'height': box_height + 0.4
    }

# --- Define Tables ---
tables = {
    'Movement': {
        'pos': (5, 4.5),
        'title': 'Movement (Weekly Sales)\n~134.9M rows | 24 files',
        'cols': [
            ('STORE', 'INT', 'FK'),
            ('UPC', 'INT', 'FK'),
            ('WEEK', 'INT', 'FK'),
            ('MOVE', 'INT', ''),
            ('QTY', 'INT', ''),
            ('PRICE', 'DECIMAL', ''),
            ('SALE', 'VARCHAR(1)', ''),
            ('PROFIT', 'DECIMAL', ''),
            ('OK', 'INT', '')
        ]
    },
    'UPC': {
        'pos': (1, 7.5),
        'title': 'UPC (Product Master)\n~14K rows | 28 files',
        'cols': [
            ('UPC', 'INT', 'PK'),
            ('COM_CODE', 'INT', ''),
            ('DESCRIP', 'VARCHAR(30)', ''),
            ('SIZE', 'VARCHAR(10)', ''),
            ('CASE', 'INT', ''),
            ('NITEM', 'INT', '')
        ]
    },
    'DEMO': {
        'pos': (9.5, 7.5),
        'title': 'DEMO (Store Demographics)\n108 rows | 510 cols',
        'cols': [
            ('STORE', 'INT', 'PK'),
            ('NAME', 'VARCHAR(50)', ''),
            ('CITY', 'VARCHAR(50)', ''),
            ('ZIP', 'INT', ''),
            ('ZONE', 'INT', ''),
            ('URBAN', 'INT', ''),
            ('INCOME', 'DECIMAL', ''),
            ('... (503 more)', 'MIXED', '')
        ]
    },
    'CCOUNT': {
        'pos': (9.5, 2.5),
        'title': 'CCOUNT (Customer Traffic)\n327K rows | 61 cols',
        'cols': [
            ('STORE', 'INT', 'PK'),
            ('WEEK', 'INT', 'PK'),
            ('DATE', 'VARCHAR(20)', ''),
            ('CUSTCOUN', 'INT', ''),
            ('GROCERY', 'INT', ''),
            ('DAIRY', 'INT', ''),
            ('FROZEN', 'INT', ''),
            ('... (54 more)', 'INT', '')
        ]
    }
}

# --- Draw Tables ---
boxes = {}
for name, data in tables.items():
    boxes[name] = create_table(ax, data['pos'][0], data['pos'][1], 3.8, data['title'], data['cols'])

# --- Draw Relationships (Crow's Foot style approximation) ---
def draw_line(p1, p2, label, connectionstyle='arc3,rad=0.1'):
    patch = FancyArrowPatch(p1, p2, connectionstyle=connectionstyle, 
                            arrowstyle='<-', color=BORDER, lw=2.5, mutation_scale=15)
    ax.add_patch(patch)
    
    # Calculate midpoint for label
    mid_x = (p1[0] + p2[0]) / 2
    mid_y = (p1[1] + p2[1]) / 2
    
    # Background for label
    bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec=BORDER, lw=1)
    ax.text(mid_x, mid_y, label, ha="center", va="center", size=9, 
            weight='bold', color=TITLE_BG, bbox=bbox_props, zorder=5)

# 1. Movement -> UPC
draw_line(
    (boxes['Movement']['left'][0], boxes['Movement']['y'] - 0.7), # From Movement.UPC
    (boxes['UPC']['right'][0], boxes['UPC']['y'] - 0.4),          # To UPC.UPC
    '1    :    N\n(UPC)',
    connectionstyle='bar,angle=180,fraction=-0.2'
)

# 2. Movement -> DEMO
draw_line(
    (boxes['Movement']['right'][0], boxes['Movement']['y'] - 0.4), # From Movement.STORE
    (boxes['DEMO']['left'][0], boxes['DEMO']['y'] - 0.4),          # To DEMO.STORE
    '1    :    N\n(STORE)',
    connectionstyle='bar,angle=0,fraction=-0.2'
)

# 3. Movement -> CCOUNT (Composite)
draw_line(
    (boxes['Movement']['right'][0], boxes['Movement']['y'] - 1.0),     # From Movement.WEEK/STORE
    (boxes['CCOUNT']['left'][0], boxes['CCOUNT']['y'] - 0.55),         # To CCOUNT.STORE/WEEK
    '1    :    N\n(STORE + WEEK)',
    connectionstyle='bar,angle=0,fraction=-0.3'
)

# Optional: Header/Footer
plt.suptitle("Dominick's Finer Foods (DFF) Database Schema", fontsize=18, weight='bold', color=TITLE_BG, y=0.95)
plt.figtext(0.5, 0.05, "* This represents the source OLTP files provided in the academic dataset.", 
            ha="center", fontsize=10, style='italic', color='#595959')

ax.set_xlim(0, 14)
ax.set_ylim(0, 10)

plt.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.savefig('/Users/bhavikdalal/Documents/data warehouse/project/report_charts/elaborate_erd.png', dpi=300, bbox_inches='tight')
print("High-quality ERD generated: report_charts/elaborate_erd.png")
