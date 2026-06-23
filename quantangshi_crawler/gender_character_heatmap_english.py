import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import pandas as pd
import numpy as np

# Set font to handle potential issues
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['font.size'] = 10

# Data for male and female poets' character preferences
# Numbers represent ranking (lower = more frequent)

# Organize data by character with both gender rankings
characters_data = {
    'Travel (行)': {'male': 34, 'female': 77},
    'Road (路)': {'male': 70, 'female': None},
    'Boat (舟)': {'male': 258, 'female': 328},
    'Horse (馬)': {'male': 96, 'female': None},
    'Frontier (邊)': {'male': 175, 'female': 139},
    'Pass (關)': {'male': 209, 'female': 278},
    'Border Fortress (塞)': {'male': 448, 'female': 410},
    'Expedition (征)': {'male': 377, 'female': None},
    'Lodging (宿)': {'male': 292, 'female': None},
    'Climb (登)': {'male': 305, 'female': None},
    'Boudoir (閨)': {'male': None, 'female': 277},
    'Window (窗)': {'male': None, 'female': 162},
    'Mirror (鏡)': {'male': None, 'female': 145},
    'Sleeve (袖)': {'male': None, 'female': 345},
    'Hand Fan (扇)': {'male': None, 'female': 358},
    'Pillow (枕)': {'male': None, 'female': 213}
}

# Convert rank to normalized frequency (inverse of rank, normalized)
def rank_to_score(rank, max_rank=500):
    if rank is None:
        return 0
    return (max_rank - rank) / max_rank * 100

# Create data matrix
char_labels = list(characters_data.keys())
data = []
for char in char_labels:
    male_score = rank_to_score(characters_data[char]['male'])
    female_score = rank_to_score(characters_data[char]['female'])
    data.append([male_score, female_score])

# Create DataFrame
df = pd.DataFrame(data, columns=['Male Poets', 'Female Poets'], index=char_labels)

# Create figure with relative frequency scores
fig, ax = plt.subplots(figsize=(8, 11))

# Create heatmap
sns.heatmap(df, annot=True, fmt='.1f', cmap='YlOrRd', 
            cbar_kws={'label': 'Relative Frequency Score'},
            linewidths=0.5, linecolor='gray',
            vmin=0, vmax=100, ax=ax)

# Customize
plt.title('Gender Differences in Character Usage\nTang Dynasty Poetry', 
          fontsize=14, fontweight='bold', pad=20)
plt.xlabel('Poet Gender', fontsize=11, fontweight='bold')
plt.ylabel('Character Theme', fontsize=11, fontweight='bold')

# Add category labels with background
ax.axhline(y=10, color='black', linestyle='--', linewidth=0.8, alpha=0.3)
ax.text(-0.1, 5, 'OUTDOOR/TRAVEL', 
        fontsize=10, fontweight='bold', va='center', ha='right',
        rotation=0, color='darkblue')
ax.text(-0.1, 13, 'INDOOR/DOMESTIC', 
        fontsize=10, fontweight='bold', va='center', ha='right',
        rotation=0, color='darkred')

plt.tight_layout()
plt.savefig('gender_character_heatmap_english.png', dpi=300, bbox_inches='tight', facecolor='white')
print("English heatmap saved as 'gender_character_heatmap_english.png'")
plt.close()

# Create a second version with actual ranks displayed
fig, ax = plt.subplots(figsize=(8, 11))

# Create annotation matrix with ranks
annot_data = []
for char in char_labels:
    male_rank = characters_data[char]['male']
    female_rank = characters_data[char]['female']
    annot_data.append([
        f"#{male_rank}" if male_rank is not None else "-",
        f"#{female_rank}" if female_rank is not None else "-"
    ])

annot_df = pd.DataFrame(annot_data, columns=['Male Poets', 'Female Poets'], index=char_labels)

sns.heatmap(df, annot=annot_df, fmt='', cmap='YlOrRd', 
            cbar_kws={'label': 'Relative Frequency Score'},
            linewidths=0.5, linecolor='gray',
            vmin=0, vmax=100, ax=ax)

plt.title('Gender Differences in Character Usage (with Rankings)\nTang Dynasty Poetry', 
          fontsize=14, fontweight='bold', pad=20)
plt.xlabel('Poet Gender', fontsize=11, fontweight='bold')
plt.ylabel('Character Theme', fontsize=11, fontweight='bold')

# Add note about rankings
plt.figtext(0.5, 0.02, 'Note: Numbers shown are frequency rankings (lower # = more frequent use)\nColor intensity represents relative frequency score (0-100)', 
            ha='center', fontsize=9, style='italic', wrap=True)

# Add category labels
ax.axhline(y=10, color='black', linestyle='--', linewidth=0.8, alpha=0.3)
ax.text(-0.1, 5, 'OUTDOOR/TRAVEL', 
        fontsize=10, fontweight='bold', va='center', ha='right',
        rotation=0, color='darkblue')
ax.text(-0.1, 13, 'INDOOR/DOMESTIC', 
        fontsize=10, fontweight='bold', va='center', ha='right',
        rotation=0, color='darkred')

plt.tight_layout()
plt.savefig('gender_character_heatmap_english_ranks.png', dpi=300, bbox_inches='tight', facecolor='white')
print("English heatmap with ranks saved as 'gender_character_heatmap_english_ranks.png'")
plt.close()

# Create a comparison/diverging heatmap showing differences
fig, ax = plt.subplots(figsize=(10, 11))

# Calculate the difference in relative preference
# Positive = more male-dominant, Negative = more female-dominant
difference_data = []
for char in char_labels:
    male_score = rank_to_score(characters_data[char]['male'])
    female_score = rank_to_score(characters_data[char]['female'])
    # If only one gender uses it, show strong preference
    if male_score > 0 and female_score == 0:
        diff = 100  # Male-dominant
    elif female_score > 0 and male_score == 0:
        diff = -100  # Female-dominant
    else:
        diff = male_score - female_score
    difference_data.append([diff])

df_diff = pd.DataFrame(difference_data, columns=['Gender Preference'], index=char_labels)

# Create diverging heatmap
sns.heatmap(df_diff, annot=True, fmt='.1f', cmap='RdBu_r', center=0,
            cbar_kws={'label': 'Preference Score (Red=Male, Blue=Female)'},
            linewidths=0.5, linecolor='gray',
            vmin=-100, vmax=100, ax=ax)

plt.title('Gender Preference in Character Usage\nTang Dynasty Poetry', 
          fontsize=14, fontweight='bold', pad=20)
plt.xlabel('', fontsize=11)
plt.ylabel('Character Theme', fontsize=11, fontweight='bold')

# Add category labels
ax.axhline(y=10, color='black', linestyle='--', linewidth=1.5, alpha=0.5)
ax.text(-0.1, 5, 'OUTDOOR/TRAVEL', 
        fontsize=10, fontweight='bold', va='center', ha='right',
        rotation=0, color='darkblue')
ax.text(-0.1, 13, 'INDOOR/DOMESTIC', 
        fontsize=10, fontweight='bold', va='center', ha='right',
        rotation=0, color='darkred')

plt.tight_layout()
plt.savefig('gender_character_diverging_heatmap.png', dpi=300, bbox_inches='tight', facecolor='white')
print("Diverging heatmap saved as 'gender_character_diverging_heatmap.png'")

print("\nAll three heatmaps have been created successfully!")
print("1. gender_character_heatmap_english.png - Shows relative frequency scores")
print("2. gender_character_heatmap_english_ranks.png - Shows actual rankings")
print("3. gender_character_diverging_heatmap.png - Shows gender preference differences")
