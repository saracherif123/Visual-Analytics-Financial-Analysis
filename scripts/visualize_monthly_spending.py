#!/usr/bin/env python3
"""
Generate monthly spending distribution visualization by super category
using Palette 1 colors from the color palette assignment.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import seaborn as sns
import os

# Get project root directory (parent of scripts/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# Read the data
df = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', 'financial_data_SaraSaad_final.csv'))

# Create a date column from Year and Month
df['Date'] = pd.to_datetime(df[['Year', 'Month']].assign(Day=1))

# Define Palette 1 colors (RGB 0-255 converted to 0-1)
palette1 = {
    'Financial_Management': '#1E90FF',  # Dodger Blue (30, 144, 255)
    'Essential_Living': '#008000',      # Green (0, 128, 0)
    'Income_Receipts': '#F4A460',       # Sandy Brown (244, 164, 96)
    'Lifestyle_Spending': '#D95318',    # Orange Red (217, 83, 25)
    'Other': '#8B4513'                  # Saddle Brown (139, 69, 19)
}

# Count transactions per category per month
monthly_counts = df.groupby(['Date', 'Super_Category']).size().unstack(fill_value=0)

# Ensure all categories are present
for category in palette1.keys():
    if category not in monthly_counts.columns:
        monthly_counts[category] = 0

# Reorder columns to match the desired order
category_order = ['Financial_Management', 'Essential_Living', 'Income_Receipts', 'Lifestyle_Spending', 'Other']
monthly_counts = monthly_counts[category_order]

# Create the stacked area chart
fig, ax = plt.subplots(figsize=(14, 8))

# Plot stacked area chart
colors_list = [palette1[cat] for cat in category_order]
ax.stackplot(monthly_counts.index, *[monthly_counts[cat] for cat in category_order],
             labels=category_order, colors=colors_list, alpha=0.85)

# Customize the plot
ax.set_xlabel('Month', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Transactions', fontsize=12, fontweight='bold')
ax.set_title('Monthly Spending Distribution by Super Category\nSeptember 2024 - October 2025', 
             fontsize=14, fontweight='bold', pad=20)

# Format x-axis
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.xticks(rotation=45, ha='right')

# Add legend
legend = ax.legend(title='Super Category', loc='upper left', frameon=True, fancybox=True, shadow=True)
legend.get_title().set_fontweight('bold')

# Add grid
ax.grid(True, alpha=0.3, linestyle='--')

# Add percentage annotations
total_transactions = len(df)
for category in category_order:
    count = df[df['Super_Category'] == category].shape[0]
    percentage = (count / total_transactions) * 100
    print(f"{category}: {count} transactions ({percentage:.1f}%)")

# Tight layout
plt.tight_layout()

# Save the figure
output_file = os.path.join(PROJECT_ROOT, 'figures', 'visualizations', 'monthly_spending_distribution.png')
os.makedirs(os.path.dirname(output_file), exist_ok=True)
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\n✅ Visualization saved to {output_file}")

plt.show()

