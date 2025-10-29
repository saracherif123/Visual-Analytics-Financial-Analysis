#!/usr/bin/env python3
"""
Multiple visualization alternatives for financial transaction data
using Palette 1 colors from the color palette assignment.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import seaborn as sns
from matplotlib.patches import Circle, Wedge
from datetime import datetime
import os

# Get project root directory (parent of scripts/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# Read the data
df = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', 'financial_data_SaraSaad_final.csv'))

# Create a date column from Year and Month
df['Date'] = pd.to_datetime(df[['Year', 'Month']].assign(Day=1))

# Define Palette 1 colors
palette1 = {
    'Financial_Management': '#1E90FF',  # Dodger Blue
    'Essential_Living': '#008000',      # Green
    'Income_Receipts': '#F4A460',       # Sandy Brown
    'Lifestyle_Spending': '#D95318',    # Orange Red
    'Other': '#8B4513'                  # Saddle Brown
}

category_order = ['Financial_Management', 'Essential_Living', 'Income_Receipts', 'Lifestyle_Spending', 'Other']
colors_list = [palette1[cat] for cat in category_order]

# Helper function for saving figures
def save_figure(filename):
    """Save figure to figures/visualizations/ directory."""
    output_file = os.path.join(PROJECT_ROOT, 'figures', 'visualizations', filename)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    return output_file

# ============================================
# Visualization 1: Stacked Bar Chart (Monthly)
# ============================================
def create_stacked_bar_chart():
    """Stacked bar chart showing monthly transaction counts per category."""
    monthly_counts = df.groupby(['Date', 'Super_Category']).size().unstack(fill_value=0)
    monthly_counts = monthly_counts[category_order]
    
    fig, ax = plt.subplots(figsize=(14, 8))
    monthly_counts.plot(kind='bar', stacked=True, ax=ax, color=colors_list, alpha=0.85, width=0.8)
    
    ax.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Transactions', fontsize=12, fontweight='bold')
    ax.set_title('Monthly Transaction Distribution by Category\nStacked Bar Chart', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(title='Super Category', loc='upper left', fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Format x-axis
    ax.set_xticklabels([d.strftime('%b %Y') if isinstance(d, pd.Timestamp) else d 
                        for d in monthly_counts.index], rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(save_figure('visualization_1_stacked_bar.png'), dpi=300, bbox_inches='tight')
    print("✅ Saved: visualization_1_stacked_bar.png")
    plt.close()

# ============================================
# Visualization 2: Grouped Bar Chart
# ============================================
def create_grouped_bar_chart():
    """Grouped bar chart comparing categories side-by-side."""
    monthly_counts = df.groupby(['Date', 'Super_Category']).size().unstack(fill_value=0)
    monthly_counts = monthly_counts[category_order]
    
    # Select every other month for readability
    monthly_counts_sel = monthly_counts.iloc[::2] if len(monthly_counts) > 6 else monthly_counts
    
    fig, ax = plt.subplots(figsize=(14, 8))
    x = np.arange(len(monthly_counts_sel.index))
    width = 0.15
    
    for i, cat in enumerate(category_order):
        offset = (i - 2) * width
        ax.bar(x + offset, monthly_counts_sel[cat], width, label=cat, 
               color=colors_list[i], alpha=0.85)
    
    ax.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Transactions', fontsize=12, fontweight='bold')
    ax.set_title('Monthly Transaction Comparison by Category\nGrouped Bar Chart', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels([d.strftime('%b %Y') if isinstance(d, pd.Timestamp) else d 
                        for d in monthly_counts_sel.index], rotation=45, ha='right')
    ax.legend(title='Super Category', fontsize=9)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(save_figure('visualization_2_grouped_bar.png'), dpi=300, bbox_inches='tight')
    print("✅ Saved: visualization_2_grouped_bar.png")
    plt.close()

# ============================================
# Visualization 3: Donut Chart (Proportions)
# ============================================
def create_donut_chart():
    """Donut chart showing overall category proportions."""
    category_counts = df['Super_Category'].value_counts()
    category_counts = category_counts.reindex(category_order, fill_value=0)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Create donut chart
    wedges, texts, autotexts = ax.pie(category_counts.values, 
                                      labels=[cat.replace('_', ' ') for cat in category_order],
                                      colors=colors_list,
                                      autopct='%1.1f%%',
                                      startangle=90,
                                      pctdistance=0.85,
                                      textprops={'fontsize': 10, 'fontweight': 'bold'})
    
    # Draw circle for donut effect
    centre_circle = Circle((0, 0), 0.70, fc='white')
    ax.add_artist(centre_circle)
    
    # Add total in center
    total = category_counts.sum()
    ax.text(0, 0, f'Total:\n{total}\nTransactions', 
            ha='center', va='center', fontsize=14, fontweight='bold')
    
    ax.set_title('Overall Transaction Distribution by Category\nDonut Chart', 
                 fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(save_figure('visualization_3_donut.png'), dpi=300, bbox_inches='tight')
    print("✅ Saved: visualization_3_donut.png")
    plt.close()

# ============================================
# Visualization 4: Heatmap (Month × Category)
# ============================================
def create_heatmap():
    """Heatmap showing transaction patterns across months and categories."""
    monthly_counts = df.groupby(['Date', 'Super_Category']).size().unstack(fill_value=0)
    monthly_counts = monthly_counts[category_order]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create custom color map from palette
    sns.heatmap(monthly_counts.T, 
                annot=True, 
                fmt='d',
                cmap='YlOrRd',  # Alternative: use custom colors
                cbar_kws={'label': 'Transaction Count'},
                linewidths=0.5,
                linecolor='gray',
                ax=ax)
    
    ax.set_ylabel('Super Category', fontsize=12, fontweight='bold')
    ax.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax.set_title('Transaction Count Heatmap\nMonth × Category', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Format labels
    ax.set_yticklabels([cat.replace('_', ' ') for cat in category_order], rotation=0)
    ax.set_xticklabels([d.strftime('%b %Y') if isinstance(d, pd.Timestamp) else str(d) 
                        for d in monthly_counts.index], rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(save_figure('visualization_4_heatmap.png'), dpi=300, bbox_inches='tight')
    print("✅ Saved: visualization_4_heatmap.png")
    plt.close()

# ============================================
# Visualization 5: Horizontal Bar Chart
# ============================================
def create_horizontal_bar():
    """Horizontal bar chart showing total transactions per category."""
    category_counts = df['Super_Category'].value_counts()
    category_counts = category_counts.reindex(category_order, fill_value=0)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.barh(range(len(category_order)), 
                   category_counts.values,
                   color=colors_list,
                   alpha=0.85,
                   edgecolor='black',
                   linewidth=1)
    
    # Add value labels
    for i, (idx, val) in enumerate(category_counts.items()):
        ax.text(val + 5, i, f'{val} ({val/category_counts.sum()*100:.1f}%)',
                va='center', fontsize=11, fontweight='bold')
    
    ax.set_yticks(range(len(category_order)))
    ax.set_yticklabels([cat.replace('_', ' ') for cat in category_order])
    ax.set_xlabel('Number of Transactions', fontsize=12, fontweight='bold')
    ax.set_title('Total Transactions by Category\nHorizontal Bar Chart', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(save_figure('visualization_5_horizontal_bar.png'), dpi=300, bbox_inches='tight')
    print("✅ Saved: visualization_5_horizontal_bar.png")
    plt.close()

# ============================================
# Visualization 6: Line Chart (Over Time)
# ============================================
def create_line_chart():
    """Line chart showing category trends over time."""
    monthly_counts = df.groupby(['Date', 'Super_Category']).size().unstack(fill_value=0)
    monthly_counts = monthly_counts[category_order]
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    for i, cat in enumerate(category_order):
        ax.plot(monthly_counts.index, monthly_counts[cat], 
                marker='o', 
                linewidth=2.5,
                markersize=6,
                label=cat.replace('_', ' '),
                color=colors_list[i],
                alpha=0.85)
    
    ax.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Transactions', fontsize=12, fontweight='bold')
    ax.set_title('Transaction Trends by Category Over Time\nLine Chart', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(title='Super Category', loc='best', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Format x-axis
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(save_figure('visualization_6_line_chart.png'), dpi=300, bbox_inches='tight')
    print("✅ Saved: visualization_6_line_chart.png")
    plt.close()

# ============================================
# Visualization 7: Circular Bar Chart
# ============================================
def create_circular_bar():
    """Modern circular bar chart showing category proportions."""
    category_counts = df['Super_Category'].value_counts()
    category_counts = category_counts.reindex(category_order, fill_value=0)
    
    fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection='polar'))
    
    # Compute angles
    N = len(category_order)
    theta = np.linspace(0, 2 * np.pi, N, endpoint=False)
    width = 2 * np.pi / N * 0.8
    
    # Normalize values
    max_val = category_counts.max()
    heights = category_counts.values / max_val * 100  # Scale to percentage of max
    
    bars = ax.bar(theta, heights, width=width, 
                  color=colors_list, alpha=0.85, edgecolor='black', linewidth=2)
    
    # Add labels
    for angle, height, label, count in zip(theta, heights, category_order, category_counts.values):
        ax.text(angle, height + 5, f'{label.replace("_", " ")}\n({count})',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xticks(theta)
    ax.set_xticklabels([])  # Remove radial labels
    ax.set_ylim(0, max(heights) * 1.2)
    ax.set_title('Transaction Distribution by Category\nCircular Bar Chart', 
                 fontsize=14, fontweight='bold', pad=30, y=1.1)
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig(save_figure('visualization_7_circular_bar.png'), dpi=300, bbox_inches='tight')
    print("✅ Saved: visualization_7_circular_bar.png")
    plt.close()

# ============================================
# Visualization 8: Small Multiples (Faceted)
# ============================================
def create_small_multiples():
    """Small multiples showing each category's monthly pattern."""
    monthly_counts = df.groupby(['Date', 'Super_Category']).size().unstack(fill_value=0)
    monthly_counts = monthly_counts[category_order]
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()
    
    for i, cat in enumerate(category_order):
        ax = axes[i]
        ax.fill_between(monthly_counts.index, 0, monthly_counts[cat],
                        color=colors_list[i], alpha=0.7, edgecolor='black', linewidth=1)
        ax.plot(monthly_counts.index, monthly_counts[cat],
                color=colors_list[i], linewidth=2.5, marker='o', markersize=4)
        ax.set_title(cat.replace('_', ' '), fontsize=11, fontweight='bold', color=colors_list[i])
        ax.set_ylabel('Transactions', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Hide extra subplot
    axes[-1].axis('off')
    
    fig.suptitle('Monthly Transaction Patterns by Category\nSmall Multiples', 
                 fontsize=14, fontweight='bold', y=0.995)
    
    plt.tight_layout()
    plt.savefig(save_figure('visualization_8_small_multiples.png'), dpi=300, bbox_inches='tight')
    print("✅ Saved: visualization_8_small_multiples.png")
    plt.close()

# ============================================
# Main Execution
# ============================================
if __name__ == "__main__":
    print("="*60)
    print("GENERATING MULTIPLE VISUALIZATION ALTERNATIVES")
    print("="*60)
    
    visualizations = [
        ("Stacked Bar Chart", create_stacked_bar_chart),
        ("Grouped Bar Chart", create_grouped_bar_chart),
        ("Donut Chart", create_donut_chart),
        ("Heatmap", create_heatmap),
        ("Horizontal Bar Chart", create_horizontal_bar),
        ("Line Chart", create_line_chart),
        ("Circular Bar Chart", create_circular_bar),
        ("Small Multiples", create_small_multiples),
    ]
    
    for name, func in visualizations:
        print(f"\n📊 Creating {name}...")
        try:
            func()
        except Exception as e:
            print(f"❌ Error creating {name}: {e}")
    
    print("\n" + "="*60)
    print("✅ ALL VISUALIZATIONS GENERATED!")
    print("="*60)
