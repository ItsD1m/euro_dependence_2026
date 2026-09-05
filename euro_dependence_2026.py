import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import Normalize
import warnings

warnings.filterwarnings('ignore')

def generate_institutional_map():
    # 1. Δεδομένα
    data = {
        'Country': ['Croatia', 'Greece', 'Slovakia', 'Poland', 'Italy', 'Spain', 'Cyprus',
                    'Bulgaria', 'Portugal', 'Slovenia', 'Ireland', 'Malta', 'Romania',
                    'Hungary', 'Latvia', 'Belgium', 'Luxembourg', 'Czechia', 'Austria',
                    'Lithuania', 'France', 'Estonia', 'Germany', 'Netherlands', 'Sweden',
                    'Finland', 'Denmark'],
        'Percentage': [62, 56, 54, 51, 51, 50, 43, 43, 42, 40, 38, 37, 37, 
                       34, 30, 25, 23, 22, 17, 16, 15, 14, 14, 11, 8, 4, 4]
    }
    df = pd.DataFrame(data)

    # 2. Λήψη & Διαχείριση Γεωμετρίας (EPSG:3035 - Προβολή Eurostat)
    print("Λήψη γεωγραφικών δεδομένων υψηλής ανάλυσης...")
    url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson"
    world = gpd.read_file(url)
    world.columns = world.columns.str.lower()
    world['name'] = world['name'].replace({'Czechia': 'Czechia', 'Bosnia and Herz.': 'Bosnia and Herzegovina'})
    world = world.to_crs(epsg=3035)
    merged = world.merge(df, how='left', left_on='name', right_on='Country')

    # 3. Setup Καμβά
    bg_color = '#F3F4F6'
    fig, ax = plt.subplots(1, 1, figsize=(16, 14), facecolor=bg_color)
    ax.set_facecolor(bg_color)

    # 4. Σχεδίαση Χάρτη
    # Layer 1: Χώρες χωρίς δεδομένα (Ανοιχτό Γκρι)
    europe_bounds = world[(world['continent'] == 'Europe') | (world['name'] == 'Turkey')]
    europe_bounds.plot(ax=ax, color='#E2E8F0', edgecolor='#FFFFFF', linewidth=1.2)

    # Layer 2: Χώρες με δεδομένα - ΒΑΘΥ ΝΑΥΤΙΚΟ ΜΠΛΕ (PuBu)
    merged_data = merged.dropna(subset=['Percentage'])
    merged_data.plot(
        column='Percentage', 
        ax=ax, 
        cmap='PuBu',  # <--- Η αλλαγή: Purple-Blue για πιο βαθιές, σκούρες αποχρώσεις
        linewidth=1.2, 
        edgecolor='#FFFFFF',
        legend=False 
    )

    # 5. Τυπογραφία & Data Labels
    for idx, row in merged_data.iterrows():
        if row['name'] not in ['Luxembourg', 'Malta', 'Cyprus']: 
            pt = row['geometry'].representative_point()
            ax.annotate(
                text=f"{int(row['Percentage'])}", 
                xy=(pt.x, pt.y),
                ha='center', va='center',
                fontsize=11, 
                color='#111827', 
                weight='heavy',
                # Το λευκό περίγραμμα κάνει τέλεια αντίθεση πάνω στο βαθύ μπλε
                path_effects=[pe.withStroke(linewidth=3.5, foreground="white")]
            )

    # 6. Όρια Χάρτη
    ax.set_xlim(2.5e6, 7.5e6)
    ax.set_ylim(1.4e6, 5.5e6)
    ax.set_axis_off()

    # 7. Custom Legend
    sm = plt.cm.ScalarMappable(cmap='PuBu', norm=Normalize(vmin=df['Percentage'].min(), vmax=df['Percentage'].max()))
    cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', shrink=0.3, pad=0.02, aspect=30, anchor=(0.1, 1.5))
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(size=0, labelsize=10, color='#4B5563')
    cbar.set_label('Ποσοστό Οικονομικής Εξάρτησης (%)', fontsize=11, color='#4B5563', weight='bold', labelpad=10)

    # 8. Τίτλοι
    plt.text(0.5, 0.95, 'Νέοι που εξαρτώνται οικονομικά από γονείς', 
             fontsize=24, weight='black', color='#111827', ha='center', transform=fig.transFigure)
    plt.text(0.5, 0.91, 'Ως ποσοστό του συνόλου των νέων ηλικίας 25-34 στην Ευρώπη', 
             fontsize=14, color='#6B7280', ha='center', transform=fig.transFigure)
    
    # Metadata
    plt.text(0.15, 0.15, 'Πηγή Δεδομένων: Eurostat (2026) | Greekonomics\nΟπτικοποίηση: Python / Geopandas', 
             fontsize=10, color='#9CA3AF', transform=fig.transFigure)

    # 9. Αποθήκευση
    output_path = 'final_eurostat_navy_map.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"\n[ΕΤΟΙΜΟ] Ο χάρτης αποθηκεύτηκε στο: {output_path}")

if __name__ == "__main__":
    generate_institutional_map()