"""
Utility functions for drawing dot-and-cross diagrams.
Shows ionic and covalent bonding with electrons represented as dots and crosses.

GCSE Convention:
- Atom circles OVERLAP where bonds form
- Shared electrons appear in the overlapping region
- Lone pairs appear on the outer perimeter as pairs of electrons
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


# --- Element Data ---
ELEMENT_DATA = {
    'H': {'outer_electrons': 1, 'name': 'Hydrogen'},
    'He': {'outer_electrons': 2, 'name': 'Helium'},
    'Li': {'outer_electrons': 1, 'name': 'Lithium'},
    'Be': {'outer_electrons': 2, 'name': 'Beryllium'},
    'B': {'outer_electrons': 3, 'name': 'Boron'},
    'C': {'outer_electrons': 4, 'name': 'Carbon'},
    'N': {'outer_electrons': 5, 'name': 'Nitrogen'},
    'O': {'outer_electrons': 6, 'name': 'Oxygen'},
    'F': {'outer_electrons': 7, 'name': 'Fluorine'},
    'Ne': {'outer_electrons': 8, 'name': 'Neon'},
    'Na': {'outer_electrons': 1, 'name': 'Sodium'},
    'Mg': {'outer_electrons': 2, 'name': 'Magnesium'},
    'Al': {'outer_electrons': 3, 'name': 'Aluminium'},
    'Si': {'outer_electrons': 4, 'name': 'Silicon'},
    'P': {'outer_electrons': 5, 'name': 'Phosphorus'},
    'S': {'outer_electrons': 6, 'name': 'Sulphur'},
    'Cl': {'outer_electrons': 7, 'name': 'Chlorine'},
    'Ar': {'outer_electrons': 8, 'name': 'Argon'},
    'K': {'outer_electrons': 1, 'name': 'Potassium'},
    'Ca': {'outer_electrons': 2, 'name': 'Calcium'},
    'Br': {'outer_electrons': 7, 'name': 'Bromine'},
    'I': {'outer_electrons': 7, 'name': 'Iodine'},
}


# --- Preset Molecules ---
# Positions are set so circles OVERLAP where bonds form
# atom_radius is 0.6 by default, so atoms ~1.0 apart will overlap nicely

PRESET_MOLECULES = {
    'H₂': {
        'type': 'covalent',
        'description': 'Hydrogen molecule - single covalent bond',
        'atoms': [
            {'element': 'H', 'position': (-0.5, 0)},
            {'element': 'H', 'position': (0.5, 0)},
        ],
        'bonds': [(0, 1, 1)],  # (atom1_idx, atom2_idx, bond_order)
        'lone_pairs': {},
    },
    'Cl₂': {
        'type': 'covalent',
        'description': 'Chlorine molecule - single covalent bond, 6 lone pairs total',
        'atoms': [
            {'element': 'Cl', 'position': (-0.5, 0)},
            {'element': 'Cl', 'position': (0.5, 0)},
        ],
        'bonds': [(0, 1, 1)],
        'lone_pairs': {0: [90, 180, 270], 1: [90, 0, 270]},
    },
    'O₂': {
        'type': 'covalent',
        'description': 'Oxygen molecule - double covalent bond',
        'atoms': [
            {'element': 'O', 'position': (-0.5, 0)},
            {'element': 'O', 'position': (0.5, 0)},
        ],
        'bonds': [(0, 1, 2)],
        'lone_pairs': {0: [90, 270], 1: [90, 270]},
    },
    'N₂': {
        'type': 'covalent',
        'description': 'Nitrogen molecule - triple covalent bond',
        'atoms': [
            {'element': 'N', 'position': (-0.5, 0)},
            {'element': 'N', 'position': (0.5, 0)},
        ],
        'bonds': [(0, 1, 3)],
        'lone_pairs': {0: [180], 1: [0]},
    },
    'HCl': {
        'type': 'covalent',
        'description': 'Hydrogen chloride - single covalent bond',
        'atoms': [
            {'element': 'H', 'position': (-0.5, 0)},
            {'element': 'Cl', 'position': (0.5, 0)},
        ],
        'bonds': [(0, 1, 1)],
        'lone_pairs': {1: [90, 0, 270]},
    },
    'HF': {
        'type': 'covalent',
        'description': 'Hydrogen fluoride - single covalent bond',
        'atoms': [
            {'element': 'H', 'position': (-0.5, 0)},
            {'element': 'F', 'position': (0.5, 0)},
        ],
        'bonds': [(0, 1, 1)],
        'lone_pairs': {1: [90, 0, 270]},
    },
    'H₂O': {
        'type': 'covalent',
        'description': 'Water - bent molecule with 2 lone pairs on oxygen',
        'atoms': [
            {'element': 'O', 'position': (0, 0)},
            {'element': 'H', 'position': (-0.75, -0.6)},
            {'element': 'H', 'position': (0.75, -0.6)},
        ],
        'bonds': [(0, 1, 1), (0, 2, 1)],
        'lone_pairs': {0: [110, 70]},  # Two lone pairs at top, slightly spread
    },
    'H₂S': {
        'type': 'covalent',
        'description': 'Hydrogen sulphide - similar to water',
        'atoms': [
            {'element': 'S', 'position': (0, 0)},
            {'element': 'H', 'position': (-0.75, -0.6)},
            {'element': 'H', 'position': (0.75, -0.6)},
        ],
        'bonds': [(0, 1, 1), (0, 2, 1)],
        'lone_pairs': {0: [110, 70]},
    },
    'NH₃': {
        'type': 'covalent',
        'description': 'Ammonia - pyramidal with 1 lone pair on nitrogen',
        'atoms': [
            {'element': 'N', 'position': (0, 0)},
            {'element': 'H', 'position': (-0.8, -0.55)},
            {'element': 'H', 'position': (0, -0.9)},
            {'element': 'H', 'position': (0.8, -0.55)},
        ],
        'bonds': [(0, 1, 1), (0, 2, 1), (0, 3, 1)],
        'lone_pairs': {0: [90]},
    },
    'CH₄': {
        'type': 'covalent',
        'description': 'Methane - tetrahedral arrangement',
        'atoms': [
            {'element': 'C', 'position': (0, 0)},
            {'element': 'H', 'position': (0, 0.9)},
            {'element': 'H', 'position': (-0.8, -0.55)},
            {'element': 'H', 'position': (0.8, -0.55)},
            {'element': 'H', 'position': (0, -0.9)},
        ],
        'bonds': [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1)],
        'lone_pairs': {},
    },
    'CO₂': {
        'type': 'covalent',
        'description': 'Carbon dioxide - linear with double bonds',
        'atoms': [
            {'element': 'C', 'position': (0, 0)},
            {'element': 'O', 'position': (-0.9, 0)},
            {'element': 'O', 'position': (0.9, 0)},
        ],
        'bonds': [(0, 1, 2), (0, 2, 2)],
        'lone_pairs': {1: [90, 270], 2: [90, 270]},
    },
    # Ionic compounds
    'NaCl': {
        'type': 'ionic',
        'description': 'Sodium chloride - Na⁺ and Cl⁻ ions',
        'atoms': [
            {'element': 'Na', 'position': (-1.5, 0), 'charge': '+', 'show_electrons': 0},
            {'element': 'Cl', 'position': (1.5, 0), 'charge': '-', 
             'show_electrons': 8, 'transferred': 1},
        ],
    },
    'MgO': {
        'type': 'ionic',
        'description': 'Magnesium oxide - Mg²⁺ and O²⁻ ions',
        'atoms': [
            {'element': 'Mg', 'position': (-1.5, 0), 'charge': '2+', 'show_electrons': 0},
            {'element': 'O', 'position': (1.5, 0), 'charge': '2-',
             'show_electrons': 8, 'transferred': 2},
        ],
    },
    'MgCl₂': {
        'type': 'ionic',
        'description': 'Magnesium chloride - Mg²⁺ and 2×Cl⁻',
        'atoms': [
            {'element': 'Mg', 'position': (0, 0), 'charge': '2+', 'show_electrons': 0},
            {'element': 'Cl', 'position': (-1.8, 0), 'charge': '-',
             'show_electrons': 8, 'transferred': 1},
            {'element': 'Cl', 'position': (1.8, 0), 'charge': '-',
             'show_electrons': 8, 'transferred': 1},
        ],
    },
    'CaCl₂': {
        'type': 'ionic',
        'description': 'Calcium chloride - Ca²⁺ and 2×Cl⁻',
        'atoms': [
            {'element': 'Ca', 'position': (0, 0), 'charge': '2+', 'show_electrons': 0},
            {'element': 'Cl', 'position': (-1.8, 0), 'charge': '-',
             'show_electrons': 8, 'transferred': 1},
            {'element': 'Cl', 'position': (1.8, 0), 'charge': '-',
             'show_electrons': 8, 'transferred': 1},
        ],
    },
    'Na₂O': {
        'type': 'ionic',
        'description': 'Sodium oxide - 2×Na⁺ and O²⁻',
        'atoms': [
            {'element': 'Na', 'position': (-1.8, 0), 'charge': '+', 'show_electrons': 0},
            {'element': 'O', 'position': (0, 0), 'charge': '2-',
             'show_electrons': 8, 'transferred': 2},
            {'element': 'Na', 'position': (1.8, 0), 'charge': '+', 'show_electrons': 0},
        ],
    },
    'KBr': {
        'type': 'ionic',
        'description': 'Potassium bromide - K⁺ and Br⁻',
        'atoms': [
            {'element': 'K', 'position': (-1.5, 0), 'charge': '+', 'show_electrons': 0},
            {'element': 'Br', 'position': (1.5, 0), 'charge': '-',
             'show_electrons': 8, 'transferred': 1},
        ],
    },
    'LiF': {
        'type': 'ionic',
        'description': 'Lithium fluoride - Li⁺ and F⁻',
        'atoms': [
            {'element': 'Li', 'position': (-1.5, 0), 'charge': '+', 'show_electrons': 0},
            {'element': 'F', 'position': (1.5, 0), 'charge': '-',
             'show_electrons': 8, 'transferred': 1},
        ],
    },
}


def draw_atom_circle(ax, position, element, radius=0.6, color='#4C5B64', 
                     line_width=2.5, font_size=18, zorder=10, bg_color='white'):
    """Draw an atom as a circle with element symbol."""
    circle = Circle(position, radius, fill=False, edgecolor=color, 
                   linewidth=line_width, zorder=zorder)
    ax.add_patch(circle)
    
    # Draw label - with background if bg_color is set, otherwise transparent
    text_kwargs = dict(
        fontsize=font_size, ha='center', va='center', 
        color=color, fontweight='bold', zorder=100
    )
    if bg_color and bg_color != 'none':
        text_kwargs['bbox'] = dict(
            boxstyle='circle,pad=0.15', facecolor=bg_color, 
            edgecolor='none', alpha=0.9
        )
    ax.text(position[0], position[1], element, **text_kwargs)


def draw_electron_dot(ax, position, color='#4C5B64', size=45, zorder=20):
    """Draw an electron as a filled dot (●)."""
    ax.scatter([position[0]], [position[1]], s=size, c=color, 
               marker='o', zorder=zorder, edgecolors='none')


def draw_electron_cross(ax, position, color='#EF665F', size=0.12, 
                        line_width=2.0, zorder=20):
    """Draw an electron as a cross (×)."""
    x, y = position
    half = size / 2
    ax.plot([x - half, x + half], [y - half, y + half], 
            color=color, linewidth=line_width, zorder=zorder,
            solid_capstyle='round')
    ax.plot([x - half, x + half], [y + half, y - half], 
            color=color, linewidth=line_width, zorder=zorder,
            solid_capstyle='round')


def draw_bonding_pair(ax, pos1, pos2, elem1_marker,
                      dot_color, cross_color, electron_size, cross_line_width,
                      pair_spacing=0.12):
    """
    Draw a shared electron pair at the midpoint between two atoms.
    """
    # Midpoint (center of overlap region)
    mid_x = (pos1[0] + pos2[0]) / 2
    mid_y = (pos1[1] + pos2[1]) / 2
    
    # Direction perpendicular to bond for spacing electrons
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    length = np.sqrt(dx*dx + dy*dy)
    if length > 0:
        perp_x = -dy / length
        perp_y = dx / length
    else:
        perp_x, perp_y = 0, 1
    
    # Position the two electrons perpendicular to bond axis
    e1_pos = (mid_x + perp_x * pair_spacing / 2, mid_y + perp_y * pair_spacing / 2)
    e2_pos = (mid_x - perp_x * pair_spacing / 2, mid_y - perp_y * pair_spacing / 2)
    
    if elem1_marker == 'dot':
        draw_electron_dot(ax, e1_pos, color=dot_color, size=electron_size)
        draw_electron_cross(ax, e2_pos, color=cross_color, line_width=cross_line_width)
    else:
        draw_electron_cross(ax, e1_pos, color=cross_color, line_width=cross_line_width)
        draw_electron_dot(ax, e2_pos, color=dot_color, size=electron_size)


def draw_bonding_pair_at(ax, center, perp_dir, elem1_marker,
                         dot_color, cross_color, electron_size, cross_line_width,
                         pair_spacing=0.12):
    """
    Draw a shared electron pair at a specific center position.
    
    Args:
        center: (x, y) position for the center of the pair
        perp_dir: (px, py) perpendicular direction for spacing electrons
    """
    perp_x, perp_y = perp_dir
    
    e1_pos = (center[0] + perp_x * pair_spacing / 2, center[1] + perp_y * pair_spacing / 2)
    e2_pos = (center[0] - perp_x * pair_spacing / 2, center[1] - perp_y * pair_spacing / 2)
    
    if elem1_marker == 'dot':
        draw_electron_dot(ax, e1_pos, color=dot_color, size=electron_size)
        draw_electron_cross(ax, e2_pos, color=cross_color, line_width=cross_line_width)
    else:
        draw_electron_cross(ax, e1_pos, color=cross_color, line_width=cross_line_width)
        draw_electron_dot(ax, e2_pos, color=dot_color, size=electron_size)


def draw_lone_pair(ax, center, angle_deg, radius, marker_type,
                   dot_color, cross_color, electron_size, cross_line_width,
                   pair_spacing=0.12):
    """
    Draw a lone pair (2 electrons) at specified angle from atom center.
    
    Args:
        center: Atom center position
        angle_deg: Angle in degrees (0=right, 90=up)
        radius: Distance from atom center
        marker_type: 'dot' or 'cross'
        pair_spacing: Distance between the two electrons in the pair
    """
    angle_rad = np.radians(angle_deg)
    
    # Base position
    base_x = center[0] + radius * np.cos(angle_rad)
    base_y = center[1] + radius * np.sin(angle_rad)
    
    # Perpendicular direction for spacing the pair
    perp_angle = angle_rad + np.pi / 2
    offset_x = pair_spacing / 2 * np.cos(perp_angle)
    offset_y = pair_spacing / 2 * np.sin(perp_angle)
    
    e1_pos = (base_x - offset_x, base_y - offset_y)
    e2_pos = (base_x + offset_x, base_y + offset_y)
    
    if marker_type == 'dot':
        draw_electron_dot(ax, e1_pos, color=dot_color, size=electron_size)
        draw_electron_dot(ax, e2_pos, color=dot_color, size=electron_size)
    else:
        draw_electron_cross(ax, e1_pos, color=cross_color, line_width=cross_line_width)
        draw_electron_cross(ax, e2_pos, color=cross_color, line_width=cross_line_width)


def draw_ionic_brackets(ax, position, radius, charge, color='#4C5B64',
                        line_width=2.5, font_size=14, zorder=5):
    """Draw square brackets around an ion with charge."""
    x, y = position
    b = radius + 0.2
    hook = 0.12
    
    # Left bracket [
    ax.plot([x - b + hook, x - b, x - b, x - b + hook], 
            [y + b, y + b, y - b, y - b],
            color=color, linewidth=line_width, zorder=zorder,
            solid_capstyle='round', solid_joinstyle='round')
    
    # Right bracket ]
    ax.plot([x + b - hook, x + b, x + b, x + b - hook], 
            [y + b, y + b, y - b, y - b],
            color=color, linewidth=line_width, zorder=zorder,
            solid_capstyle='round', solid_joinstyle='round')
    
    # Charge superscript
    ax.text(x + b + 0.12, y + b, charge,
            fontsize=font_size, ha='left', va='bottom', color=color, 
            fontweight='bold', zorder=zorder)


def draw_covalent_molecule(ax, molecule_data, atom_radius=0.6,
                           dot_color='#4C5B64', cross_color='#EF665F',
                           line_color='#4C5B64', line_width=2.5,
                           font_size=18, electron_size=45,
                           show_all_electrons=True, bg_color='white'):
    """
    Draw a covalent molecule with dot-and-cross diagram.
    Circles overlap where bonds form, shared electrons in overlap region.
    """
    atoms = molecule_data['atoms']
    bonds = molecule_data.get('bonds', [])
    lone_pairs = molecule_data.get('lone_pairs', {})
    
    # Determine which element gets dots vs crosses
    element_markers = {}
    marker_idx = 0
    for atom in atoms:
        elem = atom['element']
        if elem not in element_markers:
            element_markers[elem] = 'dot' if marker_idx == 0 else 'cross'
            marker_idx += 1
    
    cross_line_width = line_width * 0.7
    
    # Draw atom circles
    for atom in atoms:
        draw_atom_circle(ax, atom['position'], atom['element'], 
                        radius=atom_radius, color=line_color,
                        line_width=line_width, font_size=font_size,
                        bg_color=bg_color)
    
    # Draw bonding pairs - always centered at midpoint between atoms
    for bond in bonds:
        idx1, idx2, order = bond
        pos1 = atoms[idx1]['position']
        pos2 = atoms[idx2]['position']
        elem1 = atoms[idx1]['element']
        elem1_marker = element_markers[elem1]
        
        # Midpoint between atoms (center of overlap)
        mid_x = (pos1[0] + pos2[0]) / 2
        mid_y = (pos1[1] + pos2[1]) / 2
        
        # Direction perpendicular to bond for spacing multiple pairs
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        length = np.sqrt(dx*dx + dy*dy)
        if length > 0:
            perp_x = -dy / length
            perp_y = dx / length
        else:
            perp_x, perp_y = 0, 1
        
        if order == 1:
            # Single bond - one pair at exact midpoint
            draw_bonding_pair(ax, pos1, pos2, elem1_marker,
                            dot_color, cross_color, electron_size, cross_line_width)
        elif order == 2:
            # Double bond - 4 electrons evenly spaced perpendicular to bond
            # Alternating: dot, cross, dot, cross (or vice versa)
            spacing = 0.11
            positions = [-1.5, -0.5, 0.5, 1.5]  # Evenly spaced
            markers = ['dot', 'cross', 'dot', 'cross'] if elem1_marker == 'dot' else ['cross', 'dot', 'cross', 'dot']
            for i, pos_mult in enumerate(positions):
                e_pos = (mid_x + perp_x * spacing * pos_mult, mid_y + perp_y * spacing * pos_mult)
                if markers[i] == 'dot':
                    draw_electron_dot(ax, e_pos, color=dot_color, size=electron_size * 0.9)
                else:
                    draw_electron_cross(ax, e_pos, color=cross_color, line_width=cross_line_width * 0.9)
        elif order == 3:
            # Triple bond - 6 electrons evenly spaced
            spacing = 0.09
            positions = [-2.5, -1.5, -0.5, 0.5, 1.5, 2.5]
            markers = ['dot', 'cross'] * 3 if elem1_marker == 'dot' else ['cross', 'dot'] * 3
            for i, pos_mult in enumerate(positions):
                e_pos = (mid_x + perp_x * spacing * pos_mult, mid_y + perp_y * spacing * pos_mult)
                if markers[i] == 'dot':
                    draw_electron_dot(ax, e_pos, color=dot_color, size=electron_size * 0.8)
                else:
                    draw_electron_cross(ax, e_pos, color=cross_color, line_width=cross_line_width * 0.8)
    
    # Draw lone pairs - ON the circle perimeter
    if show_all_electrons:
        lone_pair_radius = atom_radius  # ON the perimeter, not outside
        for atom_idx, angles in lone_pairs.items():
            atom = atoms[atom_idx]
            pos = atom['position']
            elem = atom['element']
            marker = element_markers[elem]
            
            for angle in angles:
                draw_lone_pair(ax, pos, angle, lone_pair_radius, marker,
                             dot_color, cross_color, electron_size, cross_line_width)


def draw_ionic_compound(ax, molecule_data, atom_radius=0.6,
                        dot_color='#4C5B64', cross_color='#EF665F',
                        line_color='#4C5B64', line_width=2.5,
                        font_size=18, electron_size=45,
                        show_brackets=True, bg_color='white'):
    """Draw an ionic compound with dot-and-cross diagram."""
    atoms = molecule_data['atoms']
    cross_line_width = line_width * 0.7
    
    for atom in atoms:
        pos = atom['position']
        elem = atom['element']
        charge = atom.get('charge', '')
        n_electrons = atom.get('show_electrons', 0)
        transferred = atom.get('transferred', 0)
        
        # Draw atom circle
        draw_atom_circle(ax, pos, elem, radius=atom_radius,
                        color=line_color, line_width=line_width, font_size=font_size,
                        bg_color=bg_color)
        
        # Draw brackets for ions
        if show_brackets and charge:
            draw_ionic_brackets(ax, pos, atom_radius, charge,
                              color=line_color, line_width=line_width,
                              font_size=font_size * 0.75)
        
        # Draw electrons as pairs around the perimeter
        if n_electrons > 0:
            # 8 electrons = 4 pairs at top, right, bottom, left
            pair_angles = [90, 0, 270, 180]
            radius = atom_radius + 0.2
            pair_spacing = 0.12
            
            original_count = n_electrons - transferred
            electron_idx = 0
            
            for pair_idx, angle in enumerate(pair_angles):
                if electron_idx >= n_electrons:
                    break
                
                angle_rad = np.radians(angle)
                base_x = pos[0] + radius * np.cos(angle_rad)
                base_y = pos[1] + radius * np.sin(angle_rad)
                
                perp_angle = angle_rad + np.pi / 2
                offset_x = pair_spacing / 2 * np.cos(perp_angle)
                offset_y = pair_spacing / 2 * np.sin(perp_angle)
                
                # First electron of pair
                if electron_idx < n_electrons:
                    e_pos = (base_x - offset_x, base_y - offset_y)
                    if electron_idx < original_count:
                        draw_electron_dot(ax, e_pos, color=dot_color, size=electron_size)
                    else:
                        draw_electron_cross(ax, e_pos, color=cross_color, line_width=cross_line_width)
                    electron_idx += 1
                
                # Second electron of pair
                if electron_idx < n_electrons:
                    e_pos = (base_x + offset_x, base_y + offset_y)
                    if electron_idx < original_count:
                        draw_electron_dot(ax, e_pos, color=dot_color, size=electron_size)
                    else:
                        draw_electron_cross(ax, e_pos, color=cross_color, line_width=cross_line_width)
                    electron_idx += 1


def auto_set_limits(ax, molecule_data, padding=1.2):
    """Set axis limits based on atom positions."""
    atoms = molecule_data.get('atoms', [])
    if not atoms:
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_aspect('equal')
        return
    
    positions = np.array([a['position'] for a in atoms])
    
    x_min, y_min = positions.min(axis=0)
    x_max, y_max = positions.max(axis=0)
    
    x_range = max(x_max - x_min, 1.5)
    y_range = max(y_max - y_min, 1.5)
    max_range = max(x_range, y_range)
    
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2
    
    half_range = max_range / 2 + padding
    
    ax.set_xlim(x_center - half_range, x_center + half_range)
    ax.set_ylim(y_center - half_range, y_center + half_range)
    ax.set_aspect('equal')


def parse_smiles(smiles_string, scale='auto', atom_radius=0.6, target_overlap=0.25):
    """
    Parse a SMILES string and return molecule_data for dot-and-cross diagram.
    
    Args:
        smiles_string: SMILES representation (e.g., "O=C=O" for CO2)
        scale: Scale factor for atom positions, or 'auto' to calculate automatically
        atom_radius: The radius used for drawing atoms (needed for auto-scaling)
        target_overlap: Target overlap as fraction of atom_radius (0.25 = 25% overlap)
    
    Returns:
        molecule_data dict or None if parsing fails
    """
    # Validate input
    if not smiles_string or not smiles_string.strip():
        return None, "Please enter a SMILES string"
    
    smiles_string = smiles_string.strip()
    
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
    except ImportError:
        return None, "RDKit not installed. Run: pip install rdkit"
    
    # Parse SMILES
    try:
        mol = Chem.MolFromSmiles(smiles_string)
    except Exception as e:
        return None, f"Error parsing SMILES: {e}"
    
    if mol is None:
        return None, f"Could not parse SMILES: {smiles_string}"
    
    # Add hydrogens (important for dot-and-cross diagrams)
    mol = Chem.AddHs(mol)
    
    if mol.GetNumAtoms() == 0:
        return None, "No atoms found in molecule"
    
    # Generate 2D coordinates
    AllChem.Compute2DCoords(mol)
    conf = mol.GetConformer()
    
    # Calculate scale factor
    if scale == 'auto':
        # Calculate average bond length from RDKit coordinates
        bond_lengths = []
        for bond in mol.GetBonds():
            idx1 = bond.GetBeginAtomIdx()
            idx2 = bond.GetEndAtomIdx()
            pos1 = conf.GetAtomPosition(idx1)
            pos2 = conf.GetAtomPosition(idx2)
            dist = np.sqrt((pos2.x - pos1.x)**2 + (pos2.y - pos1.y)**2)
            bond_lengths.append(dist)
        
        if bond_lengths:
            avg_bond_length = np.mean(bond_lengths)
            # For proper overlap: bond_distance = 2*radius - overlap_amount
            # overlap_amount = target_overlap * radius
            # So: bond_distance = 2*radius - target_overlap*radius = radius*(2 - target_overlap)
            target_bond_distance = atom_radius * (2 - target_overlap)
            scale = target_bond_distance / avg_bond_length
        else:
            scale = 0.6  # Fallback for single atoms
    
    # Extract atom info
    atoms = []
    for i, atom in enumerate(mol.GetAtoms()):
        pos = conf.GetAtomPosition(i)
        symbol = atom.GetSymbol()
        atoms.append({
            'element': symbol,
            'position': (pos.x * scale, pos.y * scale)
        })
    
    # Extract bond info
    bonds = []
    for bond in mol.GetBonds():
        idx1 = bond.GetBeginAtomIdx()
        idx2 = bond.GetEndAtomIdx()
        bond_type = bond.GetBondType()
        
        # Convert bond type to order
        if bond_type == Chem.BondType.SINGLE:
            order = 1
        elif bond_type == Chem.BondType.DOUBLE:
            order = 2
        elif bond_type == Chem.BondType.TRIPLE:
            order = 3
        else:
            order = 1  # Default to single
        
        bonds.append((idx1, idx2, order))
    
    # Calculate lone pairs for each atom
    lone_pairs = {}
    for i, atom in enumerate(mol.GetAtoms()):
        symbol = atom.GetSymbol()
        
        # H and He can NEVER have lone pairs - skip entirely
        if symbol in ('H', 'He'):
            continue
            
        valence = ELEMENT_DATA.get(symbol, {}).get('outer_electrons', 0)
        
        # Count bonding electrons (each bond uses 1 electron from this atom per bond order)
        bonding_electrons = 0
        bonded_directions = []
        
        for bond in mol.GetBonds():
            if bond.GetBeginAtomIdx() == i or bond.GetEndAtomIdx() == i:
                bond_type = bond.GetBondType()
                if bond_type == Chem.BondType.SINGLE:
                    bonding_electrons += 1
                elif bond_type == Chem.BondType.DOUBLE:
                    bonding_electrons += 2
                elif bond_type == Chem.BondType.TRIPLE:
                    bonding_electrons += 3
                
                # Calculate direction to bonded atom
                other_idx = bond.GetEndAtomIdx() if bond.GetBeginAtomIdx() == i else bond.GetBeginAtomIdx()
                my_pos = conf.GetAtomPosition(i)
                other_pos = conf.GetAtomPosition(other_idx)
                angle = np.degrees(np.arctan2(other_pos.y - my_pos.y, other_pos.x - my_pos.x))
                bonded_directions.append(angle)
        
        # Remaining electrons form lone pairs
        lone_electrons = valence - bonding_electrons
        num_lone_pairs = lone_electrons // 2
        
        if num_lone_pairs > 0:
            # Find angles away from bonds for lone pairs
            lone_pair_angles = []
            
            if len(bonded_directions) == 0:
                # No bonds - distribute evenly
                for j in range(num_lone_pairs):
                    lone_pair_angles.append(j * 360 / num_lone_pairs)
            else:
                # Find gaps between bonded directions
                bonded_directions.sort()
                
                # Calculate midpoints of gaps (opposite to bonds)
                if len(bonded_directions) == 1:
                    # One bond - lone pairs opposite
                    base_angle = bonded_directions[0] + 180
                    if num_lone_pairs == 1:
                        lone_pair_angles = [base_angle]
                    elif num_lone_pairs == 2:
                        lone_pair_angles = [base_angle - 30, base_angle + 30]
                    elif num_lone_pairs == 3:
                        lone_pair_angles = [base_angle - 45, base_angle, base_angle + 45]
                else:
                    # Multiple bonds - find largest gaps
                    gaps = []
                    for j in range(len(bonded_directions)):
                        next_j = (j + 1) % len(bonded_directions)
                        gap_start = bonded_directions[j]
                        gap_end = bonded_directions[next_j]
                        if gap_end < gap_start:
                            gap_end += 360
                        gap_mid = (gap_start + gap_end) / 2
                        gap_size = gap_end - gap_start
                        gaps.append((gap_size, gap_mid % 360))
                    
                    # Sort by gap size (largest first)
                    gaps.sort(reverse=True)
                    
                    # Place lone pairs in largest gaps
                    for j in range(min(num_lone_pairs, len(gaps))):
                        lone_pair_angles.append(gaps[j][1])
            
            if lone_pair_angles:
                lone_pairs[i] = lone_pair_angles
    
    molecule_data = {
        'type': 'covalent',
        'description': f'Generated from SMILES: {smiles_string}',
        'atoms': atoms,
        'bonds': bonds,
        'lone_pairs': lone_pairs,
    }
    
    return molecule_data, None


def get_preset_names():
    """Return list of preset molecule names."""
    return list(PRESET_MOLECULES.keys())


def get_preset_molecule(name):
    """Get preset molecule data by name."""
    return PRESET_MOLECULES.get(name, PRESET_MOLECULES['H₂O'])


def get_element_list():
    """Return list of available elements."""
    return list(ELEMENT_DATA.keys())
