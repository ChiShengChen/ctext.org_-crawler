import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Data for male and female poets' character preferences
# Numbers in parentheses represent ranking (lower = more frequent)

male_chars = {
    '行 (travel)': 34,
    '路 (road)': 70,
    '舟 (boat)': 258,
    '馬 (horse)': 96,
    '邊 (frontier)': 175,
    '關 (pass)': 209,
    '塞 (border fortress)': 448,
    '征 (expedition)': 377,
    '宿 (lodging)': 292,
    '登 (climb)': 305
}

female_chars = {
    '行 (travel)': 77,
    '邊 (frontier)': 139,
    '關 (pass)': 278,
    '塞 (border fortress)': 410,
    '舟 (boat)': 328,
    '閨 (boudoir)': 277,
    '窗 (window)': 162,
    '鏡 (mirror)': 145,
    '袖 (sleeve)': 345,
    '扇 (hand fan)': 358,
    '枕 (pillow)': 213
}

# Create a comprehensive list of all unique characters
all_chars = set()
for char in male_chars.keys():
    all_chars.add(char)
for char in female_chars.keys():
    all_chars.add(char)

# Sort characters by category
outdoor_chars = ['行 (travel)', '路 (road)', '舟 (boat)', '馬 (horse)', '邊 (frontier)', 
                 '關 (pass)', '塞 (border fortress)', '征 (expedition)', '宿 (lodging)', '登 (climb)']
indoor_chars = ['閨 (boudoir)', '窗 (window)', '鏡 (mirror)', '袖 (sleeve)', '扇 (hand fan)', '枕 (pillow)']

# Combine in logical order
sorted_chars = outdoor_chars + indoor_chars

# Convert rank to normalized frequency (inverse of rank, normalized)
# Lower rank = higher frequency, so we invert
def rank_to_score(rank, max_rank=500):
    if rank is None:
        return 0
    return (max_rank - rank) / max_rank * 100

# Create data matrix
data = []
for char in sorted_chars:
    male_score = rank_to_score(male_chars.get(char))
    female_score = rank_to_score(female_chars.get(char))
    data.append([male_score, female_score])

# Create DataFrame
df = pd.DataFrame(data, columns=['Male Poets', 'Female Poets'], index=sorted_chars)

# Create figure
fig, ax = plt.subplots(figsize=(10, 12))

# Create heatmap
sns.heatmap(df, annot=True, fmt='.1f', cmap='YlOrRd', 
            cbar_kws={'label': 'Relative Frequency Score'},
            linewidths=0.5, linecolor='gray',
            vmin=0, vmax=100, ax=ax)

# Customize
plt.title('Gender Differences in Character Usage\nTang Dynasty Poetry', 
          fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Poet Gender', fontsize=12, fontweight='bold')
plt.ylabel('Character (with English Translation)', fontsize=12, fontweight='bold')

# Add category labels
ax.text(-0.5, 5, 'Outdoor/Travel\nThemes', 
        fontsize=11, fontweight='bold', va='center', ha='right',
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
ax.text(-0.5, 13, 'Indoor/\nDomestic\nThemes', 
        fontsize=11, fontweight='bold', va='center', ha='right',
        bbox=dict(boxstyle='round', facecolor='lightpink', alpha=0.5))

plt.tight_layout()
plt.savefig('gender_character_heatmap.png', dpi=300, bbox_inches='tight')
print("Heatmap saved as 'gender_character_heatmap.png'")
plt.close()

# Create a second version with actual ranks displayed
fig, ax = plt.subplots(figsize=(10, 12))

# Create annotation matrix with ranks
annot_data = []
for char in sorted_chars:
    male_rank = male_chars.get(char, '-')
    female_rank = female_chars.get(char, '-')
    annot_data.append([
        f"{male_rank}" if male_rank != '-' else '-',
        f"{female_rank}" if female_rank != '-' else '-'
    ])

annot_df = pd.DataFrame(annot_data, columns=['Male Poets', 'Female Poets'], index=sorted_chars)

sns.heatmap(df, annot=annot_df, fmt='', cmap='YlOrRd', 
            cbar_kws={'label': 'Relative Frequency Score'},
            linewidths=0.5, linecolor='gray',
            vmin=0, vmax=100, ax=ax)

plt.title('Gender Differences in Character Usage (with Rankings)\nTang Dynasty Poetry', 
          fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Poet Gender', fontsize=12, fontweight='bold')
plt.ylabel('Character (with English Translation)', fontsize=12, fontweight='bold')

# Add note about rankings
plt.figtext(0.5, -0.02, 'Note: Numbers shown are frequency rankings (lower = more frequent)\nColor intensity represents relative frequency score', 
            ha='center', fontsize=10, style='italic')

# Add category labels
ax.text(-0.5, 5, 'Outdoor/Travel\nThemes', 
        fontsize=11, fontweight='bold', va='center', ha='right',
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
ax.text(-0.5, 13, 'Indoor/\nDomestic\nThemes', 
        fontsize=11, fontweight='bold', va='center', ha='right',
        bbox=dict(boxstyle='round', facecolor='lightpink', alpha=0.5))

plt.tight_layout()
plt.savefig('gender_character_heatmap_with_ranks.png', dpi=300, bbox_inches='tight')
print("Heatmap with ranks saved as 'gender_character_heatmap_with_ranks.png'")
