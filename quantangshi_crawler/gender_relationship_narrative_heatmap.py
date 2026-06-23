import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import pandas as pd
import numpy as np

# Set font
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['font.size'] = 10

# Data: Relationship and Narrative Perspective Characters
# Numbers represent frequency ranking (lower = more frequent)

characters_data = {
    # Relationship terms (both genders)
    'You/My Lord': {'male': 23, 'female': 21},  # 君
    'Lover': {'male': 453, 'female': 43},  # 郎
    'Concubine/I (humble)': {'male': None, 'female': 73},  # 妾
    'King': {'male': 173, 'female': 170},  # 王
    'Woman': {'male': None, 'female': 200},  # 女
    'Pillow': {'male': None, 'female': 213},  # 枕
    'Husband': {'male': None, 'female': 255},  # 夫
    'Boudoir': {'male': None, 'female': 277},  # 閨
    'Sleeve': {'male': None, 'female': 345},  # 袖
    'Hand Fan': {'male': None, 'female': 358},  # 扇
    
    # Narrative perspective & public spheres
    'I': {'male': 79, 'female': None},  # 我
    'Official': {'male': 287, 'female': None},  # 官
    'Emperor': {'male': 351, 'female': None},  # 帝
    'General/Teacher': {'male': 489, 'female': None},  # 師
}

# RANK ALGORITHM
def rank_to_score(rank, max_rank=500):
    """Convert frequency ranking to normalized score (0-100)"""
    if rank is None:
        return 0
    return (max_rank - rank) / max_rank * 100

# Calculate differences and sort
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

# Sort by preference score (high to low: male-dominant to female-dominant)
char_labels_sorted = sorted(char_labels, key=lambda x: char_diff_map[x], reverse=True)

# Create data matrix
data = []
for char in char_labels_sorted:
    male_score = rank_to_score(characters_data[char]['male'])
    female_score = rank_to_score(characters_data[char]['female'])
    data.append([male_score, female_score])

df = pd.DataFrame(data, columns=['Male Poets', 'Female Poets'], index=char_labels_sorted)

# Create diverging heatmap
fig, ax = plt.subplots(figsize=(9, 10))

# Create sorted difference data
difference_data = []
for char in char_labels_sorted:
    difference_data.append([char_diff_map[char]])

df_diff = pd.DataFrame(difference_data, columns=['Gender Preference'], index=char_labels_sorted)

# Calculate dynamic range based on actual data
max_abs_diff = max(abs(df_diff['Gender Preference'].min()), abs(df_diff['Gender Preference'].max()))

# Create heatmap
sns.heatmap(df_diff, annot=True, fmt='.1f', cmap='RdBu_r', center=0,
            cbar_kws={'label': 'Preference Score (Red=Male, Blue=Female)'},
            linewidths=0.5, linecolor='gray',
            vmin=-max_abs_diff, vmax=max_abs_diff, ax=ax)

plt.title('Gender Preference in Relationship & Narrative Terms\nTang Dynasty Poetry', 
          fontsize=14, fontweight='bold', pad=20)
plt.xlabel('', fontsize=11)
plt.ylabel('Character Theme', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('gender_relationship_narrative_heatmap.png', dpi=300, bbox_inches='tight', facecolor='white')
print("Relationship & Narrative heatmap saved as 'gender_relationship_narrative_heatmap.png'")

# Print summary
print("\n" + "="*70)
print("GENDER DIFFERENCES IN RELATIONSHIP & NARRATIVE TERMS")
print("="*70)
print("\nMale-Preferred Terms (Political/Military/Public):")
for char in char_labels_sorted[:7]:
    if characters_data[char]['male'] is not None:
        rank = characters_data[char]['male']
        score = rank_to_score(rank)
        print(f"  {char:25} rank {rank:3d} → score {score:5.1f}")

print("\nFemale-Preferred Terms (Intimate/Romantic Relationships):")
for char in char_labels_sorted[7:]:
    if characters_data[char]['female'] is not None:
        rank = characters_data[char]['female']
        score = rank_to_score(rank)
        print(f"  {char:25} rank {rank:3d} → score {score:5.1f}")
        
print("\nKey Findings:")
print("  - Male poets: self-centered narration (我 'I' at rank 79)")
print("  - Female poets: relational narration (君 'you', 郎 'lover', 妾 'I-humble')")
print("  - Male focus: political/military sphere (emperor, king, official, army)")
print("  - Female focus: intimate relationships (lover, husband, woman)")
print("="*70)

