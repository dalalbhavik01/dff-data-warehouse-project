"""Generate all charts for the Consulting Report-1 from real DFF data."""
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, warnings
warnings.filterwarnings('ignore')

BASE = '/Users/bhavikdalal/Documents/data warehouse/project/DFF data - zipped'
OUT = '/Users/bhavikdalal/Documents/data warehouse/project/report_charts'
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({'font.size': 11, 'figure.figsize': (10, 6), 'figure.dpi': 150})

# ── Helper ──
def read_csv(path, nrows=500000):
    for enc in ['utf-8', 'latin-1', 'cp1252']:
        try: return pd.read_csv(path, encoding=enc, nrows=nrows)
        except: continue
    return None

# ── Category file map ──
CAT_FILES = {
    'Soft Drinks': 'Movement/WSDR/wsdr.csv',
    'Canned Soup': 'Movement/WCSO/WCSO-Done.csv',
    'Frozen Entrees': 'Movement/WFRE/WFRE-Done.csv',
    'Cheeses': 'Movement/WCHE/Done-WCHE.csv',
    'Cookies': 'Movement/WCOO/DONE-WCOO.csv',
    'Crackers': 'Movement/WCRA/Done-WCRA.csv',
    'Cigarettes': 'Movement/WCIG/Done-WCIG.csv',
    'Toothpaste': 'Movement/WTPA/WTPA_done.csv',
    'Grooming': 'Movement/WGRO/WGRO.csv',
    'Beer': 'Movement/backup-Movement/DONE-WBER.csv',
    'Cereals': 'Movement/backup-Movement/DONE-WCER.csv',
    'Bottled Juices': 'Movement/WBJC/DONE-WBJC.csv',
}

print("=== CHART 1: Category Volume Comparison ===")
cat_totals = {}
for cat, fpath in CAT_FILES.items():
    df = read_csv(os.path.join(BASE, fpath), nrows=200000)
    if df is not None and 'MOVE' in df.columns:
        valid = df[df.get('OK', 1) == 1]
        cat_totals[cat] = valid['MOVE'].sum()
        print(f"  {cat}: {cat_totals[cat]:,.0f} units (200K sample)")

cats = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)
fig, ax = plt.subplots()
ax.barh([c[0] for c in cats], [c[1] for c in cats], color='#4472C4')
ax.set_xlabel('Total Units Sold (Sample: 200K rows)')
ax.set_title('Total Units Sold by Product Category')
for i, (_, v) in enumerate(cats):
    ax.text(v + max(cat_totals.values())*0.01, i, f'{v:,.0f}', va='center', fontsize=9)
plt.tight_layout()
plt.savefig(f'{OUT}/chart1_category_volume.png')
plt.close()
print("  ✅ Saved chart1_category_volume.png")

print("\n=== CHART 2: Weekly SDR Sales Trend ===")
sdr = read_csv(os.path.join(BASE, 'Movement/WSDR/wsdr.csv'), nrows=500000)
sdr = sdr[sdr['OK'] == 1]
weekly = sdr.groupby('WEEK')['MOVE'].sum().reset_index()
fig, ax = plt.subplots()
ax.plot(weekly['WEEK'], weekly['MOVE'], color='#4472C4', linewidth=1.2)
ax.set_xlabel('Week Number')
ax.set_ylabel('Total Units Sold')
ax.set_title('Weekly Unit Sales — Soft Drinks (SDR)')
ax.set_xlim(weekly['WEEK'].min(), weekly['WEEK'].max())
plt.tight_layout()
plt.savefig(f'{OUT}/chart2_weekly_sdr_trend.png')
plt.close()
print("  ✅ Saved chart2_weekly_sdr_trend.png")

print("\n=== CHART 3: Promotion vs Non-Promotion ===")
sdr['Promo'] = sdr['SALE'].apply(lambda x: 'Promoted' if pd.notna(x) and x != '' else 'Not Promoted')
promo_avg = sdr.groupby('Promo')['MOVE'].agg(['mean', 'sum', 'count']).reset_index()
fig, ax = plt.subplots()
colors = ['#ED7D31', '#4472C4']
bars = ax.bar(promo_avg['Promo'], promo_avg['mean'], color=colors)
ax.set_ylabel('Average Units Sold (MOVE)')
ax.set_title('Promotion vs Non-Promotion — Avg Units Sold (Soft Drinks)')
for bar, val in zip(bars, promo_avg['mean']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{val:.2f}', ha='center', fontsize=11)
plt.tight_layout()
plt.savefig(f'{OUT}/chart3_promo_vs_nonpromo.png')
plt.close()
print(f"  Promoted avg: {promo_avg.set_index('Promo').loc['Promoted','mean']:.2f}")
print(f"  Not Promoted avg: {promo_avg.set_index('Promo').loc['Not Promoted','mean']:.2f}")
print("  ✅ Saved chart3_promo_vs_nonpromo.png")

print("\n=== CHART 4: Store Demographics ===")
demo = read_csv(os.path.join(BASE, 'Demographics/DEMO.csv'))
demo = demo[demo['STORE'].apply(lambda x: str(x) != '.')]
demo['STORE'] = pd.to_numeric(demo['STORE'], errors='coerce')
demo = demo.dropna(subset=['STORE'])
demo['URBAN'] = pd.to_numeric(demo['URBAN'], errors='coerce')
urban_counts = demo['URBAN'].value_counts().sort_index()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
labels = ['Suburban', 'Urban']
vals = [urban_counts.get(0, 0), urban_counts.get(1, 0)]
ax1.pie(vals, labels=labels, autopct='%1.1f%%', colors=['#4472C4', '#ED7D31'], startangle=90)
ax1.set_title('Urban vs Suburban Stores')
demo['ZONE'] = pd.to_numeric(demo['ZONE'], errors='coerce')
zone_counts = demo['ZONE'].dropna().value_counts().sort_index()
ax2.bar(zone_counts.index.astype(int).astype(str), zone_counts.values, color='#4472C4')
ax2.set_xlabel('Pricing Zone')
ax2.set_ylabel('Number of Stores')
ax2.set_title('Store Distribution by Pricing Zone')
plt.tight_layout()
plt.savefig(f'{OUT}/chart4_demographics.png')
plt.close()
print(f"  Urban: {vals[1]}, Suburban: {vals[0]}")
print("  ✅ Saved chart4_demographics.png")

print("\n=== CHART 5: Descriptive Statistics ===")
stats_data = {}
for cat in ['Soft Drinks', 'Canned Soup', 'Cereals', 'Beer', 'Cheeses', 'Grooming']:
    df = read_csv(os.path.join(BASE, CAT_FILES[cat]), nrows=100000)
    if df is not None:
        valid = df[df.get('OK', 1) == 1]
        stats_data[cat] = {
            'Mean': valid['MOVE'].mean(),
            'Median': valid['MOVE'].median(),
            'Std Dev': valid['MOVE'].std(),
            'Max': valid['MOVE'].max(),
            'Min': valid['MOVE'].min(),
            'Avg Price': valid['PRICE'].mean() if 'PRICE' in valid.columns else 0,
            'Avg Profit': valid['PROFIT'].mean() if 'PROFIT' in valid.columns else 0,
        }
stats_df = pd.DataFrame(stats_data).T
stats_df.to_csv(f'{OUT}/descriptive_stats.csv')
fig, ax = plt.subplots(figsize=(10, 4))
ax.axis('off')
table = ax.table(cellText=[[f'{v:.2f}' for v in row] for row in stats_df.values],
                 rowLabels=stats_df.index, colLabels=stats_df.columns,
                 cellLoc='center', loc='center')
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1.2, 1.5)
ax.set_title('Descriptive Statistics by Category (Sample: 100K rows)', pad=20, fontsize=12)
plt.tight_layout()
plt.savefig(f'{OUT}/chart5_descriptive_stats.png')
plt.close()
print("  ✅ Saved chart5_descriptive_stats.png")

print("\n=== CHART 6: Price Distribution (Beer) ===")
beer = read_csv(os.path.join(BASE, 'Movement/backup-Movement/DONE-WBER.csv'), nrows=300000)
beer = beer[(beer['OK'] == 1) & (beer['PRICE'] > 0) & (beer['QTY'] > 0)]
beer['UnitPrice'] = beer['PRICE'] / beer['QTY']
price_by_upc = beer.groupby('UPC')['UnitPrice'].agg(['mean', 'min', 'max', 'std']).reset_index()
price_by_upc['spread'] = price_by_upc['max'] - price_by_upc['min']
price_by_upc = price_by_upc.nlargest(10, 'spread')
fig, ax = plt.subplots()
ax.barh(price_by_upc['UPC'].astype(str), price_by_upc['spread'], color='#ED7D31')
ax.set_xlabel('Price Spread ($)')
ax.set_title('Top 10 Beer Products by Price Spread Across Stores')
ax.set_ylabel('UPC')
for i, (_, row) in enumerate(price_by_upc.iterrows()):
    ax.text(row['spread'] + 0.1, i, f'${row["spread"]:.2f}', va='center', fontsize=9)
plt.tight_layout()
plt.savefig(f'{OUT}/chart6_beer_price_spread.png')
plt.close()
print("  ✅ Saved chart6_beer_price_spread.png")

# ──── BQ Evidence Charts ────
print("\n=== BQ-M1: Promo Lift by Deal Type (Canned Soup) ===")
cso = read_csv(os.path.join(BASE, 'Movement/WCSO/WCSO-Done.csv'), nrows=500000)
cso = cso[cso['OK'] == 1]
deal_avg = cso.groupby(cso['SALE'].fillna('No Promo'))['MOVE'].mean().reset_index()
deal_avg.columns = ['Deal', 'Avg_MOVE']
fig, ax = plt.subplots()
colors_deal = {'No Promo': '#A5A5A5', 'B': '#4472C4', 'S': '#ED7D31', 'C': '#70AD47', 'G': '#FFC000'}
ax.bar(deal_avg['Deal'], deal_avg['Avg_MOVE'], color=[colors_deal.get(d, '#4472C4') for d in deal_avg['Deal']])
ax.set_ylabel('Avg Units Sold')
ax.set_title('BQ M1: Promotion Lift by Deal Type — Canned Soup')
ax.set_xlabel('Deal Type (B=Bonus Buy, C=Coupon, S=Sale)')
for i, row in deal_avg.iterrows():
    ax.text(i, row['Avg_MOVE'] + 0.5, f'{row["Avg_MOVE"]:.1f}', ha='center', fontsize=10)
plt.tight_layout()
plt.savefig(f'{OUT}/bq_m1_promo_lift.png')
plt.close()
print("  ✅ Saved bq_m1_promo_lift.png")

print("\n=== BQ-M2: Urban vs Suburban Revenue (Frozen Entrees) ===")
fre = read_csv(os.path.join(BASE, 'Movement/WFRE/WFRE-Done.csv'), nrows=500000)
fre = fre[(fre['OK'] == 1) & (fre['PRICE'] > 0) & (fre['QTY'] > 0)]
fre['Revenue'] = fre['MOVE'] * (fre['PRICE'] / fre['QTY'])
fre['Quarter'] = (fre['WEEK'] // 13).astype(int)
demo_urban = demo[['STORE', 'URBAN']].copy()
demo_urban['STORE'] = pd.to_numeric(demo_urban['STORE'], errors='coerce')
fre = fre.merge(demo_urban, on='STORE', how='left')
fre = fre.dropna(subset=['URBAN'])
qtr_rev = fre.groupby(['Quarter', 'URBAN'])['Revenue'].sum().unstack(fill_value=0)
qtr_rev.columns = ['Suburban', 'Urban']
fig, ax = plt.subplots()
qtr_rev.plot(kind='bar', ax=ax, color=['#4472C4', '#ED7D31'])
ax.set_xlabel('Quarter')
ax.set_ylabel('Revenue ($)')
ax.set_title('BQ M2: Quarterly Revenue — Urban vs Suburban (Frozen Entrees)')
ax.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{OUT}/bq_m2_urban_suburban.png')
plt.close()
print("  ✅ Saved bq_m2_urban_suburban.png")

print("\n=== BQ-H1: Store Revenue Quartiles (Toothpaste) ===")
tpa = read_csv(os.path.join(BASE, 'Movement/WTPA/WTPA_done.csv'), nrows=500000)
tpa = tpa[(tpa['OK'] == 1) & (tpa['PRICE'] > 0) & (tpa['QTY'] > 0)]
tpa['Revenue'] = tpa['MOVE'] * (tpa['PRICE'] / tpa['QTY'])
store_rev = tpa.groupby('STORE')['Revenue'].sum().reset_index()
store_rev['Quartile'] = pd.qcut(store_rev['Revenue'], 4, labels=['Bottom 25%', 'Lower Mid', 'Upper Mid', 'Top 25%'])
store_rev['STORE'] = pd.to_numeric(store_rev['STORE'], errors='coerce')
store_rev = store_rev.merge(demo[['STORE', 'URBAN', 'INCOME', 'ZONE']], on='STORE', how='left')
for col in ['URBAN', 'INCOME']:
    store_rev[col] = pd.to_numeric(store_rev[col], errors='coerce')
qsummary = store_rev.groupby('Quartile').agg(
    Stores=('STORE', 'count'),
    Avg_Revenue=('Revenue', 'mean'),
    Pct_Urban=('URBAN', 'mean'),
    Avg_Income=('INCOME', 'mean')
).reset_index()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.bar(qsummary['Quartile'], qsummary['Avg_Revenue'], color='#4472C4')
ax1.set_ylabel('Avg Revenue ($)')
ax1.set_title('Avg Revenue by Quartile')
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=30, ha='right')
ax2.bar(qsummary['Quartile'], qsummary['Pct_Urban']*100, color='#ED7D31')
ax2.set_ylabel('% Urban Stores')
ax2.set_title('Urban % by Revenue Quartile')
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=30, ha='right')
plt.suptitle('BQ H1: Store Revenue Quartiles + Demographics (Toothpaste)', fontsize=13)
plt.tight_layout()
plt.savefig(f'{OUT}/bq_h1_quartiles.png')
plt.close()
print("  ✅ Saved bq_h1_quartiles.png")

print("\n=== BQ-H3: Profit by Zone (Cigarettes) ===")
cig = read_csv(os.path.join(BASE, 'Movement/WCIG/Done-WCIG.csv'), nrows=500000)
cig = cig[cig['OK'] == 1]
cig['STORE'] = pd.to_numeric(cig['STORE'], errors='coerce')
cig = cig.merge(demo[['STORE', 'ZONE']], on='STORE', how='left')
cig['ZONE'] = pd.to_numeric(cig['ZONE'], errors='coerce')
cig = cig.dropna(subset=['ZONE'])
store_profit = cig.groupby(['ZONE', 'STORE'])['PROFIT'].mean().reset_index()
zone_summary = store_profit.groupby('ZONE')['PROFIT'].agg(['mean', 'min', 'max', 'count']).reset_index()
fig, ax = plt.subplots()
ax.bar(zone_summary['ZONE'].astype(int).astype(str), zone_summary['mean'], color='#4472C4')
ax.errorbar(range(len(zone_summary)), zone_summary['mean'],
            yerr=[zone_summary['mean']-zone_summary['min'], zone_summary['max']-zone_summary['mean']],
            fmt='none', ecolor='#ED7D31', capsize=4)
ax.set_xlabel('Pricing Zone')
ax.set_ylabel('Avg Store Profit ($)')
ax.set_title('BQ H3: Average Store Profit by Pricing Zone (Cigarettes)')
plt.tight_layout()
plt.savefig(f'{OUT}/bq_h3_zone_profit.png')
plt.close()
print("  ✅ Saved bq_h3_zone_profit.png")

# ──── ERD Diagram ────
print("\n=== ERD Diagram ===")
fig, ax = plt.subplots(figsize=(12, 8))
ax.axis('off')
boxes = {
    'Movement Files\n(24 files, ~134.9M rows)\n─────────\nUPC | STORE | WEEK\nMOVE | QTY | PRICE\nSALE | PROFIT | OK': (0.5, 0.5),
    'UPC Files\n(28 files, ~14K UPCs)\n─────────\nCOM_CODE | UPC\nDESCRIP | SIZE\nCASE | NITEM': (0.15, 0.85),
    'DEMO\n(107 stores, 510 cols)\n─────────\nSTORE | NAME | CITY\nZONE | URBAN | INCOME\nDENSITY | WEEKVOL': (0.85, 0.85),
    'CCOUNT\n(327K rows, 61 cols)\n─────────\nSTORE | WEEK | DATE\nCUSTCOUN | GROCERY\nDAIRY | FROZEN | MEAT': (0.85, 0.15),
}
for txt, (x, y) in boxes.items():
    ax.add_patch(plt.Rectangle((x-0.14, y-0.12), 0.28, 0.24, fill=True,
                 facecolor='#D6E4F0', edgecolor='#2F5496', linewidth=2, zorder=2))
    ax.text(x, y, txt, ha='center', va='center', fontsize=9, family='monospace', zorder=3)
# Arrows
ax.annotate('', xy=(0.36, 0.62), xytext=(0.29, 0.73), arrowprops=dict(arrowstyle='->', color='#2F5496', lw=2))
ax.text(0.28, 0.68, 'UPC', fontsize=10, color='#C00000', fontweight='bold')
ax.annotate('', xy=(0.64, 0.62), xytext=(0.71, 0.73), arrowprops=dict(arrowstyle='->', color='#2F5496', lw=2))
ax.text(0.68, 0.68, 'STORE', fontsize=10, color='#C00000', fontweight='bold')
ax.annotate('', xy=(0.64, 0.38), xytext=(0.71, 0.27), arrowprops=dict(arrowstyle='->', color='#2F5496', lw=2))
ax.text(0.62, 0.29, 'STORE+WEEK', fontsize=10, color='#C00000', fontweight='bold')
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_title('Entity Relationship Diagram — DFF OLTP Source Files', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(f'{OUT}/erd_diagram.png')
plt.close()
print("  ✅ Saved erd_diagram.png")

print("\n✅ ALL CHARTS GENERATED SUCCESSFULLY")
print(f"Charts saved to: {OUT}/")
for f in sorted(os.listdir(OUT)):
    if f.endswith('.png'):
        print(f"  📊 {f}")
