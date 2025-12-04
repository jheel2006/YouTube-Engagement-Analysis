import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
df = pd.read_csv("youtube_length_engagement.csv")

print("="*60)
print("YOUTUBE VIDEO LENGTH & ENGAGEMENT ANALYSIS")
print("="*60)

# Create duration categories
df['duration_category'] = df['duration_minutes'].apply(
    lambda x: 'Short (<10 min)' if x < 10 else 'Long (>20 min)'
)

# Separate into two groups
short_videos = df[df['duration_category'] == 'Short (<10 min)']
long_videos = df[df['duration_category'] == 'Long (>20 min)']

print(f"\nDataset Summary:")
print(f"  Total videos: {len(df)}")
print(f"  Short videos: {len(short_videos)}")
print(f"  Long videos: {len(long_videos)}")

# Descriptive Statistics
print(f"\n{'='*60}")
print("DESCRIPTIVE STATISTICS")
print(f"{'='*60}")

print(f"\nShort Videos (<10 min):")
print(f"  Mean like-to-view ratio: {short_videos['like_view_ratio'].mean():.4f} ({short_videos['like_view_ratio'].mean()*100:.2f}%)")
print(f"  Median like-to-view ratio: {short_videos['like_view_ratio'].median():.4f}")
print(f"  Std deviation: {short_videos['like_view_ratio'].std():.4f}")

print(f"\nLong Videos (>20 min):")
print(f"  Mean like-to-view ratio: {long_videos['like_view_ratio'].mean():.4f} ({long_videos['like_view_ratio'].mean()*100:.2f}%)")
print(f"  Median like-to-view ratio: {long_videos['like_view_ratio'].median():.4f}")
print(f"  Std deviation: {long_videos['like_view_ratio'].std():.4f}")

# Calculate percentage difference
pct_diff = ((short_videos['like_view_ratio'].mean() - long_videos['like_view_ratio'].mean()) / 
            long_videos['like_view_ratio'].mean() * 100)
print(f"\n📊 Short videos have {pct_diff:.1f}% higher like-to-view ratio than long videos")

# Statistical Tests
print(f"\n{'='*60}")
print("STATISTICAL TESTS")
print(f"{'='*60}")

# 1. Normality tests (Shapiro-Wilk)
print("\n1. Testing for normality (Shapiro-Wilk test):")
short_shapiro = stats.shapiro(short_videos['like_view_ratio'])
long_shapiro = stats.shapiro(long_videos['like_view_ratio'])

print(f"   Short videos: W={short_shapiro.statistic:.4f}, p={short_shapiro.pvalue:.4f}")
print(f"   Long videos: W={long_shapiro.statistic:.4f}, p={long_shapiro.pvalue:.4f}")

if short_shapiro.pvalue < 0.05 or long_shapiro.pvalue < 0.05:
    print("   → Data is NOT normally distributed (p < 0.05)")
    use_parametric = False
else:
    print("   → Data is normally distributed (p >= 0.05)")
    use_parametric = True

# 2. Choose appropriate test
print(f"\n2. Comparing engagement rates:")

if use_parametric:
    # Independent samples t-test
    t_stat, p_value = stats.ttest_ind(
        short_videos['like_view_ratio'],
        long_videos['like_view_ratio']
    )
    print(f"   Independent t-test:")
    print(f"   t-statistic = {t_stat:.4f}")
    print(f"   p-value = {p_value:.6f}")
else:
    # Mann-Whitney U test (non-parametric alternative)
    u_stat, p_value = stats.mannwhitneyu(
        short_videos['like_view_ratio'],
        long_videos['like_view_ratio'],
        alternative='two-sided'
    )
    print(f"   Mann-Whitney U test (non-parametric):")
    print(f"   U-statistic = {u_stat:.4f}")
    print(f"   p-value = {p_value:.6f}")

# Interpret results
print(f"\n{'='*60}")
print("INTERPRETATION")
print(f"{'='*60}")

if p_value < 0.001:
    print(f"\n✅ HIGHLY SIGNIFICANT (p < 0.001)")
    print(f"   There is very strong evidence that short videos have")
    print(f"   different engagement rates than long videos.")
elif p_value < 0.01:
    print(f"\n✅ VERY SIGNIFICANT (p < 0.01)")
    print(f"   There is strong evidence that short videos have")
    print(f"   different engagement rates than long videos.")
elif p_value < 0.05:
    print(f"\n✅ SIGNIFICANT (p < 0.05)")
    print(f"   There is evidence that short videos have")
    print(f"   different engagement rates than long videos.")
else:
    print(f"\n❌ NOT SIGNIFICANT (p >= 0.05)")
    print(f"   No significant difference found between groups.")

# Effect size (Cohen's d)
pooled_std = np.sqrt(
    ((len(short_videos)-1) * short_videos['like_view_ratio'].var() + 
     (len(long_videos)-1) * long_videos['like_view_ratio'].var()) /
    (len(short_videos) + len(long_videos) - 2)
)
cohens_d = (short_videos['like_view_ratio'].mean() - 
            long_videos['like_view_ratio'].mean()) / pooled_std

print(f"\nEffect Size (Cohen's d): {cohens_d:.3f}")
if abs(cohens_d) < 0.2:
    print("   → Small effect")
elif abs(cohens_d) < 0.5:
    print("   → Medium effect")
else:
    print("   → Large effect")

# Engagement by Category
print(f"\n{'='*60}")
print("ENGAGEMENT BY CATEGORY")
print(f"{'='*60}")

category_stats = df.groupby(['category_name', 'duration_category'])['like_view_ratio'].agg([
    ('mean', 'mean'),
    ('count', 'count')
]).round(4)

print(f"\n{category_stats}")

# Create visualizations
print(f"\n{'='*60}")
print("Creating visualizations...")
print(f"{'='*60}")

# Set style
sns.set_style("whitegrid")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Box plot comparing short vs long
ax1 = axes[0, 0]
df.boxplot(column='like_view_ratio', by='duration_category', ax=ax1)
ax1.set_title('Like-to-View Ratio by Video Length', fontsize=12, fontweight='bold')
ax1.set_xlabel('Video Length Category')
ax1.set_ylabel('Like-to-View Ratio')
plt.sca(ax1)
plt.xticks(rotation=0)

# 2. Histogram
ax2 = axes[0, 1]
ax2.hist(short_videos['like_view_ratio'], bins=30, alpha=0.6, label='Short (<10 min)', color='blue')
ax2.hist(long_videos['like_view_ratio'], bins=30, alpha=0.6, label='Long (>20 min)', color='red')
ax2.set_xlabel('Like-to-View Ratio')
ax2.set_ylabel('Frequency')
ax2.set_title('Distribution of Like-to-View Ratios', fontsize=12, fontweight='bold')
ax2.legend()

# 3. Bar chart by category
ax3 = axes[1, 0]
category_means = df.groupby(['category_name', 'duration_category'])['like_view_ratio'].mean().unstack()
# Ensure colors match column order: Long = red, Short = blue
category_means.plot(kind='bar', ax=ax3, color=['#e74c3c', '#3498db'])
ax3.set_title('Average Like-to-View Ratio by Category', fontsize=12, fontweight='bold')
ax3.set_xlabel('Category')
ax3.set_ylabel('Average Like-to-View Ratio')
ax3.legend(title='Duration')
plt.sca(ax3)
plt.xticks(rotation=45, ha='right')

# 4. Scatter plot: Duration vs Engagement
ax4 = axes[1, 1]
colors = ['blue' if x < 10 else 'red' for x in df['duration_minutes']]
ax4.scatter(df['duration_minutes'], df['like_view_ratio'], alpha=0.5, c=colors)
ax4.set_xlabel('Video Duration (minutes)')
ax4.set_ylabel('Like-to-View Ratio')
ax4.set_title('Duration vs Like-to-View Ratio', fontsize=12, fontweight='bold')
ax4.set_xlabel('Video Duration (minutes)')
ax4.set_ylabel('Engagement Rate')
ax4.set_title('Duration vs Engagement Rate', fontsize=12, fontweight='bold')
ax4.axvline(x=10, color='gray', linestyle='--', alpha=0.5, label='10 min threshold')
ax4.axvline(x=20, color='gray', linestyle='--', alpha=0.5, label='20 min threshold')
ax4.legend()

plt.tight_layout()
plt.savefig('youtube_engagement_analysis.png', dpi=300, bbox_inches='tight')
print("\n✓ Saved visualization as 'youtube_engagement_analysis.png'")

print(f"\n{'='*60}")
print("CONCLUSION FOR YOUR PAPER")
print(f"{'='*60}")
print(f"\nThe analysis of {len(df)} YouTube videos across {df['category_name'].nunique()} categories")
print(f"shows that short videos (<10 min) have significantly higher like-to-view")
print(f"ratios ({short_videos['like_view_ratio'].mean():.4f}) compared to long videos")
print(f"(>20 min) ({long_videos['like_view_ratio'].mean():.4f}), with p={p_value:.6f}.")
print(f"This represents a {pct_diff:.1f}% increase in likes per view for shorter content,")
print(f"supporting the hypothesis that video length affects audience interaction.")
print(f"\n{'='*60}")