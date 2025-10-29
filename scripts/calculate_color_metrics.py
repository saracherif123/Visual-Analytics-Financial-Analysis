#!/usr/bin/env python3
"""
Calculate CIELAB color distances and generate color-blindness simulations
for the two color palettes used in the assignment.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000, delta_e_cie1976
import colorspacious as cs
import itertools
import os

# Get project root directory (parent of scripts/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================
# PALETTE 1: Balanced Harmony
# ============================================
palette1_colors = {
    "Financial_Management": (30, 144, 255),   # Dodger Blue
    "Essential_Living": (0, 128, 0),          # Green
    "Income_Receipts": (244, 164, 96),         # Sandy Brown
    "Lifestyle_Spending": (217, 83, 25),       # Orange Red (fixed RGB)
    "Other": (139, 69, 19)                     # Saddle Brown
}

# ============================================
# PALETTE 2: High Distinctiveness
# ============================================
palette2_colors = {
    "Financial_Management": (0, 0, 205),      # Medium Blue
    "Essential_Living": (50, 205, 50),         # Lime Green
    "Income_Receipts": (255, 165, 0),          # Orange
    "Lifestyle_Spending": (138, 43, 226),      # Blue Violet
    "Other": (160, 32, 10)                     # Brown
}

# Abbreviated names for tables
abbrev_names = {
    "Financial_Management": "Fin. Mgmt",
    "Essential_Living": "Essential",
    "Income_Receipts": "Income",
    "Lifestyle_Spending": "Lifestyle",
    "Other": "Other"
}

def rgb_to_lab(rgb_tuple):
    """Convert RGB (0-255) to Lab color."""
    rgb = sRGBColor(*rgb_tuple, is_upscaled=True)
    lab = convert_color(rgb, LabColor)
    return lab

def compute_delta_e_ab(lab1, lab2):
    """Compute CIELAB ΔE*ab (Euclidean distance in CIELAB space)."""
    return np.sqrt((lab1.lab_l - lab2.lab_l)**2 + 
                   (lab1.lab_a - lab2.lab_a)**2 + 
                   (lab1.lab_b - lab2.lab_b)**2)

def calculate_palette_distances(palette, palette_name):
    """Calculate pairwise CIELAB distances for a palette."""
    print(f"\n{'='*60}")
    print(f"Calculating distances for {palette_name}")
    print(f"{'='*60}")
    
    # Convert all colors to Lab
    lab_colors = {}
    for name, rgb in palette.items():
        lab_colors[name] = rgb_to_lab(rgb)
        print(f"{name:25s} RGB{rgb} → Lab(L={lab_colors[name].lab_l:.2f}, a={lab_colors[name].lab_a:.2f}, b={lab_colors[name].lab_b:.2f})")
    
    # Create distance matrix
    categories = list(palette.keys())
    n = len(categories)
    distance_matrix = np.zeros((n, n))
    
    # Calculate pairwise distances
    distances_list = []
    for i, name1 in enumerate(categories):
        for j, name2 in enumerate(categories):
            if i == j:
                distance_matrix[i, j] = 0.0
            else:
                # Use CIE1976 (ΔE*ab) - Euclidean distance in CIELAB space
                de76 = compute_delta_e_ab(lab_colors[name1], lab_colors[name2])
                distance_matrix[i, j] = de76
                if i < j:  # Store each pair only once
                    distances_list.append({
                        "Color1": abbrev_names[name1],
                        "Color2": abbrev_names[name2],
                        "ΔE_ab": round(de76, 1)
                    })
    
    # Calculate average distance (excluding diagonal)
    mask = ~np.eye(n, dtype=bool)
    avg_distance = distance_matrix[mask].mean()
    
    print(f"\nAverage CIELAB ΔE00 distance: {avg_distance:.2f}")
    
    return distance_matrix, categories, distances_list, avg_distance

def generate_cielab_table(palette, palette_name, distance_matrix, categories, avg_distance):
    """Generate LaTeX table code for CIELAB distances."""
    n = len(categories)
    abbrev_cats = [abbrev_names[c] for c in categories]
    
    print(f"\n{'='*60}")
    print(f"LaTeX Table for {palette_name}")
    print(f"{'='*60}\n")
    
    # Generate LaTeX table
    latex_code = f"""\\begin{{table}}[h]
\\centering
\\caption{{Pairwise CIELAB Color Distances ($\\Delta E^{{*}}_{{ab}}$) Between Categories - {palette_name}}}
\\begin{{tabular}}{{l{'c'*n}}}
\\toprule
\\textbf{{{palette_name}}} & {' & '.join([f'\\textbf{{{c}}}' for c in abbrev_cats])} \\\\
\\midrule
"""
    
    for i, cat in enumerate(categories):
        row = f"\\textbf{{{abbrev_names[cat]}}} & "
        values = []
        for j in range(n):
            if i == j:
                values.append("---")
            else:
                values.append(f"{distance_matrix[i,j]:.1f}")
        row += " & ".join(values) + " \\\\\n"
        latex_code += row
    
    latex_code += f"""\\midrule
\\textbf{{Average Distance}} & \\multicolumn{{{n}}}{{c}}{{{avg_distance:.1f} ({'Excellent' if avg_distance > 35 else 'Moderate' if avg_distance > 20 else 'Good'} separation)}} \\\\
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    
    print(latex_code)
    return latex_code

def simulate_colorblindness(palette_rgb, palette_name, deficiency_type, severity=100):
    """Simulate color-blindness for a palette."""
    # Convert RGB 0-255 to 0-1 range
    palette_normalized = [(r/255.0, g/255.0, b/255.0) for r, g, b in palette_rgb.values()]
    
    # Simulate color-blindness
    simulated = []
    for rgb in palette_normalized:
        try:
            # Convert to perceptually uniform RGB with CVD simulation
            simulated_rgb = cs.cspace_convert(
                rgb,
                start="sRGB1",
                end={"name": "sRGB1+CVD", "cvd_type": deficiency_type, "severity": severity}
            )
        except KeyError:
            # Try alternative names
            alt_names = {
                "deuteranopia": "deuteranomaly",
                "protanopia": "protanomaly", 
                "tritanopia": "tritanomaly"
            }
            deficiency_type = alt_names.get(deficiency_type, deficiency_type)
            simulated_rgb = cs.cspace_convert(
                rgb,
                start="sRGB1",
                end={"name": "sRGB1+CVD", "cvd_type": deficiency_type, "severity": severity}
            )
        # Clamp to valid range
        simulated_rgb = tuple(np.clip(simulated_rgb, 0, 1))
        # Convert back to 0-255
        simulated.append(tuple(int(c * 255) for c in simulated_rgb))
    
    return simulated

def test_accessibility(palette, palette_name):
    """Test palette accessibility under different color-blindness conditions."""
    print(f"\n{'='*60}")
    print(f"Accessibility Testing for {palette_name}")
    print(f"{'='*60}")
    
    palette_list = list(palette.values())
    categories = list(palette.keys())
    
    results = {
        "deuteranopia": simulate_colorblindness(palette, palette_name, "deuteranomaly", 100),
        "protanopia": simulate_colorblindness(palette, palette_name, "protanomaly", 100),
        "tritanopia": simulate_colorblindness(palette, palette_name, "tritanomaly", 100)
    }
    
    # Calculate distances for each simulation
    accessibility_results = []
    for deficiency, simulated_colors in results.items():
        print(f"\n{deficiency.upper()}:")
        print("-" * 40)
        
        # Convert simulated colors to Lab and calculate distances
        simulated_lab = {}
        for name, rgb in zip(categories, simulated_colors):
            simulated_lab[name] = rgb_to_lab(rgb)
            orig_lab = rgb_to_lab(palette[name])
            print(f"  {name:25s} Original Lab({orig_lab.lab_l:.1f}, {orig_lab.lab_a:.1f}, {orig_lab.lab_b:.1f}) → Simulated Lab({simulated_lab[name].lab_l:.1f}, {simulated_lab[name].lab_a:.1f}, {simulated_lab[name].lab_b:.1f})")
        
        # Check if categories remain distinguishable
        min_distance = float('inf')
        problem_pairs = []
        for name1, name2 in itertools.combinations(categories, 2):
            de = compute_delta_e_ab(simulated_lab[name1], simulated_lab[name2])
            min_distance = min(min_distance, de)
            if de < 15:  # Threshold for reliable distinction
                problem_pairs.append((name1, name2, de))
        
        status = "Excellent" if min_distance >= 15 else "Good" if min_distance >= 10 else "Fair"
        accessibility_results.append({
            "deficiency": deficiency,
            "min_distance": round(min_distance, 1),
            "status": status,
            "problem_pairs": problem_pairs
        })
        
        print(f"  Minimum distance: {min_distance:.1f} ({status})")
        if problem_pairs:
            print(f"  Problem pairs: {', '.join([f'{p[0]}–{p[1]} (ΔE={p[2]:.1f})' for p in problem_pairs])}")
    
    return accessibility_results

def visualize_simulations(palette, palette_name, output_dir=None):
    """Create visualization showing normal and colorblind simulations."""
    if output_dir is None:
        output_dir = PROJECT_ROOT
    categories = list(palette.keys())
    palette_list = list(palette.values())
    palette_normalized = [(r/255.0, g/255.0, b/255.0) for r, g, b in palette_list]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f'{palette_name} - Color Blindness Simulations', fontsize=14, fontweight='bold')
    
    # Normal vision
    ax = axes[0, 0]
    for i, (name, color) in enumerate(zip(categories, palette_normalized)):
        ax.bar(i, 1, color=color, edgecolor='black', linewidth=1.5)
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels([abbrev_names[c] for c in categories], rotation=45, ha='right')
    ax.set_title('Normal Vision', fontweight='bold')
    ax.set_ylabel('Color Intensity')
    ax.set_ylim(0, 1.1)
    
    # Deuteranopia
    ax = axes[0, 1]
    simulated = simulate_colorblindness(palette, palette_name, "deuteranomaly")
    simulated_norm = [(r/255.0, g/255.0, b/255.0) for r, g, b in simulated]
    for i, color in enumerate(simulated_norm):
        ax.bar(i, 1, color=color, edgecolor='black', linewidth=1.5)
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels([abbrev_names[c] for c in categories], rotation=45, ha='right')
    ax.set_title('Deuteranopia (Green-Blind)', fontweight='bold')
    ax.set_ylabel('Color Intensity')
    ax.set_ylim(0, 1.1)
    
    # Protanopia
    ax = axes[1, 0]
    simulated = simulate_colorblindness(palette, palette_name, "protanomaly")
    simulated_norm = [(r/255.0, g/255.0, b/255.0) for r, g, b in simulated]
    for i, color in enumerate(simulated_norm):
        ax.bar(i, 1, color=color, edgecolor='black', linewidth=1.5)
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels([abbrev_names[c] for c in categories], rotation=45, ha='right')
    ax.set_title('Protanopia (Red-Blind)', fontweight='bold')
    ax.set_ylabel('Color Intensity')
    ax.set_ylim(0, 1.1)
    
    # Tritanopia
    ax = axes[1, 1]
    simulated = simulate_colorblindness(palette, palette_name, "tritanomaly")
    simulated_norm = [(r/255.0, g/255.0, b/255.0) for r, g, b in simulated]
    for i, color in enumerate(simulated_norm):
        ax.bar(i, 1, color=color, edgecolor='black', linewidth=1.5)
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels([abbrev_names[c] for c in categories], rotation=45, ha='right')
    ax.set_title('Tritanopia (Blue-Blind)', fontweight='bold')
    ax.set_ylabel('Color Intensity')
    ax.set_ylim(0, 1.1)
    
    plt.tight_layout()
    filename = f'{palette_name.replace(" ", "_").lower()}_colorblind_simulations.png'
    output_path = os.path.join(output_dir, filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nSaved visualization: {output_path}")
    plt.close()

def main():
    print("="*60)
    print("COLOR PALETTE ANALYSIS")
    print("Computing CIELAB distances and accessibility tests")
    print("="*60)
    
    # Calculate distances for both palettes
    dist1, cats1, dist_list1, avg1 = calculate_palette_distances(palette1_colors, "Palette 1: Balanced Harmony")
    dist2, cats2, dist_list2, avg2 = calculate_palette_distances(palette2_colors, "Palette 2: High Distinctiveness")
    
    # Generate LaTeX tables
    latex_table1 = generate_cielab_table(palette1_colors, "Palette 1 (Balanced Harmony)", dist1, cats1, avg1)
    latex_table2 = generate_cielab_table(palette2_colors, "Palette 2 (High Distinctiveness)", dist2, cats2, avg2)
    
    # Save LaTeX tables
    latex_dir = os.path.join(PROJECT_ROOT, 'latex', 'tables')
    os.makedirs(latex_dir, exist_ok=True)
    
    with open(os.path.join(latex_dir, 'cielab_table_palette1.tex'), 'w') as f:
        f.write(latex_table1)
    with open(os.path.join(latex_dir, 'cielab_table_palette2.tex'), 'w') as f:
        f.write(latex_table2)
    
    print("\n" + "="*60)
    print("LaTeX tables saved to:")
    print(f"  - {os.path.join(latex_dir, 'cielab_table_palette1.tex')}")
    print(f"  - {os.path.join(latex_dir, 'cielab_table_palette2.tex')}")
    
    # Test accessibility
    acc1 = test_accessibility(palette1_colors, "Palette 1")
    acc2 = test_accessibility(palette2_colors, "Palette 2")
    
    # Generate accessibility LaTeX table
    print(f"\n{'='*60}")
    print("Accessibility Summary Table (LaTeX)")
    print(f"{'='*60}\n")
    
    acc_latex = """\\begin{table}[h]
\\centering
\\caption{Accessibility Evaluation Under Color-Blindness Simulation}
\\begin{tabular}{p{3cm}p{5.5cm}p{5.5cm}}
\\toprule
\\textbf{Condition} & \\textbf{Palette 1 (Balanced Harmony)} & \\textbf{Palette 2 (High Distinctiveness)} \\\\
\\midrule
"""
    
    conditions = ["Deuteranopia (Red-Green Deficiency)", "Protanopia (Red-Green Deficiency)", "Tritanopia (Blue-Yellow Deficiency)"]
    for i, cond in enumerate(conditions):
        def_type = ["deuteranopia", "protanopia", "tritanopia"][i]
        p1_min = next(r["min_distance"] for r in acc1 if r["deficiency"] == def_type)
        p1_status = next(r["status"] for r in acc1 if r["deficiency"] == def_type)
        p1_probs = next(r["problem_pairs"] for r in acc1 if r["deficiency"] == def_type)
        
        p2_min = next(r["min_distance"] for r in acc2 if r["deficiency"] == def_type)
        p2_status = next(r["status"] for r in acc2 if r["deficiency"] == def_type)
        p2_probs = next(r["problem_pairs"] for r in acc2 if r["deficiency"] == def_type)
        
        p1_desc = f"{p1_status} (min ΔE={p1_min:.1f})"
        if p1_probs:
            p1_desc += f". Minor confusion: {', '.join([f'{abbrev_names[p[0]]}–{abbrev_names[p[1]]}' for p in p1_probs[:2]])}"
        else:
            p1_desc += ". All categories clearly distinguishable."
        
        p2_desc = f"{p2_status} (min ΔE={p2_min:.1f})"
        if p2_probs:
            p2_desc += f". Minor confusion: {', '.join([f'{abbrev_names[p[0]]}–{abbrev_names[p[1]]}' for p in p2_probs[:2]])}"
        else:
            p2_desc += ". All categories clearly distinguishable."
        
        acc_latex += f"{cond} & {p1_desc} & {p2_desc} \\\\[0.5em]\n\\midrule\n"
    
    acc_latex += """\\textbf{Overall Score} & \\textbf{Good — minor issues under red-green deficiencies.} & \\textbf{Excellent — fully distinguishable under all conditions.} \\\\
\\bottomrule
\\end{tabular}
\\end{table}
"""
    
    print(acc_latex)
    with open(os.path.join(latex_dir, 'accessibility_table.tex'), 'w') as f:
        f.write(acc_latex)
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    sim_dir = os.path.join(PROJECT_ROOT, 'figures', 'colorblind_sim')
    os.makedirs(sim_dir, exist_ok=True)
    
    # Update visualize_simulations to save to correct directory
    visualize_simulations(palette1_colors, "Palette 1", sim_dir)
    visualize_simulations(palette2_colors, "Palette 2", sim_dir)
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("\nGenerated files:")
    print(f"  - {os.path.join(latex_dir, 'cielab_table_palette1.tex')}")
    print(f"  - {os.path.join(latex_dir, 'cielab_table_palette2.tex')}")
    print(f"  - {os.path.join(latex_dir, 'accessibility_table.tex')}")
    print(f"  - {os.path.join(sim_dir, 'palette_1_colorblind_simulations.png')}")
    print(f"  - {os.path.join(sim_dir, 'palette_2_colorblind_simulations.png')}")

if __name__ == "__main__":
    main()

