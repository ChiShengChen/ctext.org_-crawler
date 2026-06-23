import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import pandas as pd
import numpy as np

# Set font
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['font.size'] = 10

# Data: English labels only (no Chinese characters)
# Numbers represent frequency ranking (lower = more frequent)

characters_data = {
    'Travel': {'male': 34, 'female': 77},
    'Road': {'male': 70, 'female': None},
    'Boat': {'male': 258, 'female': 328},
    'Horse': {'male': 96, 'female': None},
    'Frontier': {'male': 175, 'female': 139},
    'Pass': {'male': 209, 'female': 278},
    'Border Fortress': {'male': 448, 'female': 410},
    'Expedition': {'male': 377, 'female': None},
    'Lodging': {'male': 292, 'female': None},
    'Climb': {'male': 305, 'female': None},
    'Boudoir': {'male': None, 'female': 277},
    'Window': {'male': None, 'female': 162},
    'Mirror': {'male': None, 'female': 145},
    'Sleeve': {'male': None, 'female': 345},
    'Hand Fan': {'male': None, 'female': 358},
    'Pillow': {'male': None, 'female': 213}
}

# RANK ALGORITHM:
# Convert frequency rank to relative score (0-100 scale)
# Formula: score = (max_rank - rank) / max_rank * 100
# 
# - Lower rank number = higher frequency = higher score
# - Example: rank 34 -> score = (500-34)/500*100 = 93.2
# - Example: rank 448 -> score = (500-448)/500*100 = 10.4
# - None/missing -> score = 0

def rank_to_score(rank, max_rank=500):
    """
    Convert frequency ranking to normalized score.
    
    Parameters:
    -----------
    rank : int or None
        Frequency ranking (lower = more frequent)
    max_rank : int
        Maximum possible rank for normalization
        
    Returns:
    --------
    float : Normalized score (0-100)
    """
    if rank is None:
        return 0
    return (max_rank - rank) / max_rank * 100

# Create data matrix for scores and calculate differences
char_labels = list(characters_data.keys())
char_diff_map = {}

for char in char_labels:
    male_score = rank_to_score(characters_data[char]['male'])
    female_score = rank_to_score(characters_data[char]['female'])
    
    # Calculate gender preference difference
    # Positive = male-dominant, Negative = female-dominant
    # Use actual score differences instead of fixed ±100
    diff = male_score - female_score
    
    char_diff_map[char] = diff

# Sort characters by preference score (high to low: male-dominant to female-dominant)
char_labels_sorted = sorted(char_labels, key=lambda x: char_diff_map[x], reverse=True)

# Create data matrix with sorted order
data = []
for char in char_labels_sorted:
    male_score = rank_to_score(characters_data[char]['male'])
    female_score = rank_to_score(characters_data[char]['female'])
    data.append([male_score, female_score])

df = pd.DataFrame(data, columns=['Male Poets', 'Female Poets'], index=char_labels_sorted)

# Create diverging heatmap showing gender preference differences
fig, ax = plt.subplots(figsize=(9, 11))

# Create sorted difference data
difference_data = []
for char in char_labels_sorted:
    difference_data.append([char_diff_map[char]])

df_diff = pd.DataFrame(difference_data, columns=['Gender Preference'], index=char_labels_sorted)

# Calculate dynamic range based on actual data
max_abs_diff = max(abs(df_diff['Gender Preference'].min()), abs(df_diff['Gender Preference'].max()))

# Create diverging heatmap (Red=Male preference, Blue=Female preference)
sns.heatmap(df_diff, annot=True, fmt='.1f', cmap='RdBu_r', center=0,
            cbar_kws={'label': 'Preference Score (Red=Male, Blue=Female)'},
            linewidths=0.5, linecolor='gray',
            vmin=-max_abs_diff, vmax=max_abs_diff, ax=ax)

plt.title('Gender Preference in Character Usage\nTang Dynasty Poetry', 
          fontsize=14, fontweight='bold', pad=20)
plt.xlabel('', fontsize=11)
plt.ylabel('Character Theme', fontsize=11, fontweight='bold')

# Characters now sorted by preference score (no category labels needed)

plt.tight_layout()
plt.savefig('gender_diverging_heatmap_english_only.png', dpi=300, bbox_inches='tight', facecolor='white')
print("English-only diverging heatmap saved as 'gender_diverging_heatmap_english_only.png'")

# Print algorithm explanation
print("\n" + "="*70)
print("RANK ALGORITHM EXPLANATION")
print("="*70)
print("\nFormula: score = (max_rank - rank) / max_rank × 100")
print("\nWhere:")
print("  - rank: frequency ranking (lower number = more frequent use)")
print("  - max_rank: 500 (normalization constant)")
print("  - score: relative frequency score (0-100 scale)")
print("\nExamples:")
for i, (char, data) in enumerate(list(characters_data.items())[:3]):
    male_rank = data['male']
    female_rank = data['female']
    if male_rank:
        male_score = rank_to_score(male_rank)
        print(f"  {char} (Male): rank {male_rank} → score {male_score:.1f}")
    if female_rank:
        female_score = rank_to_score(female_rank)
        print(f"  {char} (Female): rank {female_rank} → score {female_score:.1f}")
    if i < 2:
        print()

print("\nGender Preference Calculation:")
print("  - difference = male_score - female_score")
print("  - Positive values: male-preferred")
print("  - Negative values: female-preferred")
print("  - If only one gender uses it: the other score is 0")
print("="*70)
