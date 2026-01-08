"""
Utility functions for drawing electron shell diagrams.
Shows electrons arranged in shells (2, 8, 8, etc.) around a nucleus.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


# Element data with electron configurations
ELECTRON_CONFIG = {
    'H':  {'shells': [1], 'name': 'Hydrogen', 'symbol': 'H', 'protons': 1},
    'He': {'shells': [2], 'name': 'Helium', 'symbol': 'He', 'protons': 2},
    'Li': {'shells': [2, 1], 'name': 'Lithium', 'symbol': 'Li', 'protons': 3},
    'Be': {'shells': [2, 2], 'name': 'Beryllium', 'symbol': 'Be', 'protons': 4},
    'B':  {'shells': [2, 3], 'name': 'Boron', 'symbol': 'B', 'protons': 5},
    'C':  {'shells': [2, 4], 'name': 'Carbon', 'symbol': 'C', 'protons': 6},
    'N':  {'shells': [2, 5], 'name': 'Nitrogen', 'symbol': 'N', 'protons': 7},
    'O':  {'shells': [2, 6], 'name': 'Oxygen', 'symbol': 'O', 'protons': 8},
    'F':  {'shells': [2, 7], 'name': 'Fluorine', 'symbol': 'F', 'protons': 9},
    'Ne': {'shells': [2, 8], 'name': 'Neon', 'symbol': 'Ne', 'protons': 10},
    'Na': {'shells': [2, 8, 1], 'name': 'Sodium', 'symbol': 'Na', 'protons': 11},
    'Mg': {'shells': [2, 8, 2], 'name': 'Magnesium', 'symbol': 'Mg', 'protons': 12},
    'Al': {'shells': [2, 8, 3], 'name': 'Aluminium', 'symbol': 'Al', 'protons': 13},
    'Si': {'shells': [2, 8, 4], 'name': 'Silicon', 'symbol': 'Si', 'protons': 14},
    'P':  {'shells': [2, 8, 5], 'name': 'Phosphorus', 'symbol': 'P', 'protons': 15},
    'S':  {'shells': [2, 8, 6], 'name': 'Sulphur', 'symbol': 'S', 'protons': 16},
    'Cl': {'shells': [2, 8, 7], 'name': 'Chlorine', 'symbol': 'Cl', 'protons': 17},
    'Ar': {'shells': [2, 8, 8], 'name': 'Argon', 'symbol': 'Ar', 'protons': 18},
    'K':  {'shells': [2, 8, 8, 1], 'name': 'Potassium', 'symbol': 'K', 'protons': 19},
    'Ca': {'shells': [2, 8, 8, 2], 'name': 'Calcium', 'symbol': 'Ca', 'protons': 20},
}


def draw_electron_shell_diagram(ax, element, center=(0, 0), 
                                 nucleus_radius=0.4, shell_spacing=0.5,
                                 line_color='#4C5B64', line_width=2.0,
                                 electron_size=60, font_size=16,
                                 show_nucleus_label=True, show_config=True,
                                 bg_color='white'):
    """
    Draw an electron shell diagram for an element.
    
    Args:
        ax: matplotlib axes
        element: element symbol (e.g., 'Na')
        center: center position of diagram
        nucleus_radius: radius of the nucleus circle
        shell_spacing: spacing between shells
        line_color: color for circles and electrons
        line_width: width of shell circles
        electron_size: size of electron dots
        font_size: size of labels
        show_nucleus_label: whether to show element symbol in nucleus
        show_config: whether to show electron configuration below
        bg_color: background color
    """
    if element not in ELECTRON_CONFIG:
        raise ValueError(f"Unknown element: {element}")
    
    config = ELECTRON_CONFIG[element]
    shells = config['shells']
    symbol = config['symbol']
    
    cx, cy = center
    
    # Draw nucleus
    nucleus = Circle(center, nucleus_radius, fill=True, 
                    facecolor=bg_color, edgecolor=line_color,
                    linewidth=line_width, zorder=10)
    ax.add_patch(nucleus)
    
    if show_nucleus_label:
        ax.text(cx, cy, symbol, fontsize=font_size * 1.2,
                ha='center', va='center', color=line_color,
                fontweight='bold', zorder=11)
    
    # Draw shells and electrons
    for shell_idx, n_electrons in enumerate(shells):
        shell_radius = nucleus_radius + (shell_idx + 1) * shell_spacing
        
        # Draw shell circle
        shell_circle = Circle(center, shell_radius, fill=False,
                             edgecolor=line_color, linewidth=line_width,
                             linestyle='-', zorder=5)
        ax.add_patch(shell_circle)
        
        # Draw electrons evenly distributed on shell
        if n_electrons > 0:
            # Start from top and go clockwise
            start_angle = np.pi / 2
            angle_step = 2 * np.pi / n_electrons
            
            for e_idx in range(n_electrons):
                angle = start_angle - e_idx * angle_step
                ex = cx + shell_radius * np.cos(angle)
                ey = cy + shell_radius * np.sin(angle)
                
                # Draw electron as filled circle
                ax.scatter([ex], [ey], s=electron_size, c=line_color,
                          marker='o', zorder=15, edgecolors='none')
    
    # Draw electron configuration label below
    if show_config:
        config_str = '.'.join(str(n) for n in shells)
        total_radius = nucleus_radius + len(shells) * shell_spacing
        ax.text(cx, cy - total_radius - 0.4, config_str,
                fontsize=font_size * 0.9, ha='center', va='top',
                color=line_color)


def draw_ion_shell_diagram(ax, element, charge, center=(0, 0),
                           nucleus_radius=0.4, shell_spacing=0.5,
                           line_color='#4C5B64', line_width=2.0,
                           electron_size=60, font_size=16,
                           show_nucleus_label=True, show_config=True,
                           bg_color='white'):
    """
    Draw an electron shell diagram for an ion.
    
    Args:
        element: element symbol
        charge: ion charge (e.g., +1, -1, +2, -2)
    """
    if element not in ELECTRON_CONFIG:
        raise ValueError(f"Unknown element: {element}")
    
    config = ELECTRON_CONFIG[element]
    shells = list(config['shells'])  # Make a copy
    symbol = config['symbol']
    
    # Modify electron count based on charge
    electrons_to_change = abs(charge)
    
    if charge > 0:
        # Remove electrons (start from outermost shell)
        for i in range(len(shells) - 1, -1, -1):
            if electrons_to_change <= 0:
                break
            remove = min(shells[i], electrons_to_change)
            shells[i] -= remove
            electrons_to_change -= remove
        # Remove empty shells
        while shells and shells[-1] == 0:
            shells.pop()
    elif charge < 0:
        # Add electrons to outermost shell
        if shells:
            shells[-1] += electrons_to_change
        else:
            shells = [electrons_to_change]
    
    cx, cy = center
    
    # Draw nucleus
    nucleus = Circle(center, nucleus_radius, fill=True,
                    facecolor=bg_color, edgecolor=line_color,
                    linewidth=line_width, zorder=10)
    ax.add_patch(nucleus)
    
    if show_nucleus_label:
        # Show symbol with charge
        charge_str = ""
        if charge > 0:
            charge_str = f"$^{{{'+' if charge == 1 else str(charge) + '+'}}}$"
        elif charge < 0:
            charge_str = f"$^{{{'−' if charge == -1 else str(abs(charge)) + '−'}}}$"
        
        ax.text(cx, cy, f"{symbol}{charge_str}", fontsize=font_size * 1.1,
                ha='center', va='center', color=line_color,
                fontweight='bold', zorder=11)
    
    # Draw shells and electrons
    for shell_idx, n_electrons in enumerate(shells):
        shell_radius = nucleus_radius + (shell_idx + 1) * shell_spacing
        
        shell_circle = Circle(center, shell_radius, fill=False,
                             edgecolor=line_color, linewidth=line_width,
                             linestyle='-', zorder=5)
        ax.add_patch(shell_circle)
        
        if n_electrons > 0:
            start_angle = np.pi / 2
            angle_step = 2 * np.pi / n_electrons
            
            for e_idx in range(n_electrons):
                angle = start_angle - e_idx * angle_step
                ex = cx + shell_radius * np.cos(angle)
                ey = cy + shell_radius * np.sin(angle)
                
                ax.scatter([ex], [ey], s=electron_size, c=line_color,
                          marker='o', zorder=15, edgecolors='none')
    
    if show_config:
        config_str = '.'.join(str(n) for n in shells) if shells else "0"
        total_radius = nucleus_radius + max(len(shells), 1) * shell_spacing
        ax.text(cx, cy - total_radius - 0.4, config_str,
                fontsize=font_size * 0.9, ha='center', va='top',
                color=line_color)


def get_element_list():
    """Return list of available elements."""
    return list(ELECTRON_CONFIG.keys())


def get_element_info(element):
    """Return info about an element."""
    return ELECTRON_CONFIG.get(element, None)


def auto_set_limits_shell(ax, element, nucleus_radius=0.4, shell_spacing=0.5, padding=0.5):
    """Set axis limits based on element's electron shells."""
    if element not in ELECTRON_CONFIG:
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.set_aspect('equal')
        return
    
    n_shells = len(ELECTRON_CONFIG[element]['shells'])
    total_radius = nucleus_radius + n_shells * shell_spacing + padding
    
    ax.set_xlim(-total_radius, total_radius)
    ax.set_ylim(-total_radius - 0.5, total_radius)  # Extra space at bottom for label
    ax.set_aspect('equal')

