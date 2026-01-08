"""
Utility functions for drawing chemical formulae.
- Displayed formulae: shows all atoms and bonds explicitly
- Skeletal formulae: carbon backbone with implied hydrogens
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def parse_smiles_for_formula(smiles_string, add_hydrogens=True):
    """
    Parse a SMILES string and return atom/bond data for formula drawing.
    
    Args:
        smiles_string: SMILES representation
        add_hydrogens: Whether to add explicit hydrogens (True for displayed, False for skeletal)
    
    Returns:
        dict with atoms, bonds, positions or (None, error_message)
    """
    if not smiles_string or not smiles_string.strip():
        return None, "Please enter a SMILES string"
    
    smiles_string = smiles_string.strip()
    
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
    except ImportError:
        return None, "RDKit not installed. Run: pip install rdkit"
    
    try:
        mol = Chem.MolFromSmiles(smiles_string)
    except Exception as e:
        return None, f"Error parsing SMILES: {e}"
    
    if mol is None:
        return None, f"Could not parse SMILES: {smiles_string}"
    
    # Add hydrogens for displayed formula
    if add_hydrogens:
        mol = Chem.AddHs(mol)
    
    if mol.GetNumAtoms() == 0:
        return None, "No atoms found in molecule"
    
    # Generate 2D coordinates
    AllChem.Compute2DCoords(mol)
    conf = mol.GetConformer()
    
    # Extract atom info
    atoms = []
    for i, atom in enumerate(mol.GetAtoms()):
        pos = conf.GetAtomPosition(i)
        symbol = atom.GetSymbol()
        atoms.append({
            'element': symbol,
            'position': (pos.x, pos.y),
            'index': i
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
        elif bond_type == Chem.BondType.AROMATIC:
            order = 1.5
        else:
            order = 1
        
        bonds.append({
            'atom1': idx1,
            'atom2': idx2,
            'order': order
        })
    
    return {
        'atoms': atoms,
        'bonds': bonds,
        'smiles': smiles_string
    }, None


def draw_displayed_formula(ax, mol_data, line_color='#4C5B64', line_width=2.5,
                           font_size=14, show_carbons=True, show_hydrogens=True,
                           bg_color='white'):
    """
    Draw a displayed formula showing all atoms and bonds.
    
    Args:
        ax: matplotlib axes
        mol_data: dict from parse_smiles_for_formula
        line_color: color for bonds and text
        line_width: width of bond lines
        font_size: size of atom labels
        show_carbons: whether to show C labels (False for semi-skeletal)
        show_hydrogens: whether to show H labels
        bg_color: background color for labels
    """
    atoms = mol_data['atoms']
    bonds = mol_data['bonds']
    
    bond_offset = 0.08  # Offset for double/triple bonds
    
    # Draw bonds first (behind atoms)
    for bond in bonds:
        pos1 = np.array(atoms[bond['atom1']]['position'])
        pos2 = np.array(atoms[bond['atom2']]['position'])
        order = bond['order']
        
        # Direction vector
        direction = pos2 - pos1
        length = np.linalg.norm(direction)
        if length > 0:
            direction = direction / length
        
        # Perpendicular for multiple bonds
        perp = np.array([-direction[1], direction[0]])
        
        # Shorten bonds slightly so they don't overlap with atom labels
        shorten = 0.25
        start = pos1 + direction * shorten
        end = pos2 - direction * shorten
        
        if order == 1:
            ax.plot([start[0], end[0]], [start[1], end[1]], 
                   color=line_color, linewidth=line_width, zorder=1,
                   solid_capstyle='round')
        elif order == 2:
            # Double bond - two parallel lines
            offset = perp * bond_offset
            ax.plot([start[0] + offset[0], end[0] + offset[0]], 
                   [start[1] + offset[1], end[1] + offset[1]], 
                   color=line_color, linewidth=line_width, zorder=1,
                   solid_capstyle='round')
            ax.plot([start[0] - offset[0], end[0] - offset[0]], 
                   [start[1] - offset[1], end[1] - offset[1]], 
                   color=line_color, linewidth=line_width, zorder=1,
                   solid_capstyle='round')
        elif order == 3:
            # Triple bond - three parallel lines
            ax.plot([start[0], end[0]], [start[1], end[1]], 
                   color=line_color, linewidth=line_width, zorder=1,
                   solid_capstyle='round')
            offset = perp * bond_offset * 1.2
            ax.plot([start[0] + offset[0], end[0] + offset[0]], 
                   [start[1] + offset[1], end[1] + offset[1]], 
                   color=line_color, linewidth=line_width * 0.8, zorder=1,
                   solid_capstyle='round')
            ax.plot([start[0] - offset[0], end[0] - offset[0]], 
                   [start[1] - offset[1], end[1] - offset[1]], 
                   color=line_color, linewidth=line_width * 0.8, zorder=1,
                   solid_capstyle='round')
        elif order == 1.5:
            # Aromatic - solid + dashed
            ax.plot([start[0], end[0]], [start[1], end[1]], 
                   color=line_color, linewidth=line_width, zorder=1,
                   solid_capstyle='round')
            offset = perp * bond_offset
            ax.plot([start[0] + offset[0], end[0] + offset[0]], 
                   [start[1] + offset[1], end[1] + offset[1]], 
                   color=line_color, linewidth=line_width * 0.6, 
                   linestyle='--', zorder=1)
    
    # Draw atom labels
    for atom in atoms:
        element = atom['element']
        pos = atom['position']
        
        # Skip based on settings
        if element == 'C' and not show_carbons:
            continue
        if element == 'H' and not show_hydrogens:
            continue
        
        # Draw atom label with optional background
        text_kwargs = dict(fontsize=font_size, ha='center', va='center', 
                          color=line_color, fontweight='bold', zorder=10)
        if bg_color and bg_color != 'none':
            text_kwargs['bbox'] = dict(boxstyle='round,pad=0.15', 
                                       facecolor=bg_color, edgecolor='none')
        ax.text(pos[0], pos[1], element, **text_kwargs)


def draw_skeletal_formula(ax, mol_data, line_color='#4C5B64', line_width=2.5,
                          font_size=14, bg_color='white'):
    """
    Draw a skeletal formula (carbon backbone, heteroatoms shown).
    Carbon and hydrogen atoms bonded to carbon are not shown.
    
    Args:
        ax: matplotlib axes
        mol_data: dict from parse_smiles_for_formula (should NOT have explicit H)
        line_color: color for bonds and text
        line_width: width of bond lines
        font_size: size of atom labels
        bg_color: background color for labels
    """
    atoms = mol_data['atoms']
    bonds = mol_data['bonds']
    
    bond_offset = 0.08
    
    # Draw bonds
    for bond in bonds:
        pos1 = np.array(atoms[bond['atom1']]['position'])
        pos2 = np.array(atoms[bond['atom2']]['position'])
        elem1 = atoms[bond['atom1']]['element']
        elem2 = atoms[bond['atom2']]['element']
        order = bond['order']
        
        # Direction vector
        direction = pos2 - pos1
        length = np.linalg.norm(direction)
        if length > 0:
            direction = direction / length
        
        # Perpendicular for multiple bonds
        perp = np.array([-direction[1], direction[0]])
        
        # Shorten bonds if atom label will be shown (heteroatoms)
        shorten1 = 0.2 if elem1 not in ('C',) else 0
        shorten2 = 0.2 if elem2 not in ('C',) else 0
        
        start = pos1 + direction * shorten1
        end = pos2 - direction * shorten2
        
        if order == 1:
            ax.plot([start[0], end[0]], [start[1], end[1]], 
                   color=line_color, linewidth=line_width, zorder=1,
                   solid_capstyle='round')
        elif order == 2:
            offset = perp * bond_offset
            ax.plot([start[0] + offset[0], end[0] + offset[0]], 
                   [start[1] + offset[1], end[1] + offset[1]], 
                   color=line_color, linewidth=line_width, zorder=1,
                   solid_capstyle='round')
            ax.plot([start[0] - offset[0], end[0] - offset[0]], 
                   [start[1] - offset[1], end[1] - offset[1]], 
                   color=line_color, linewidth=line_width, zorder=1,
                   solid_capstyle='round')
        elif order == 3:
            ax.plot([start[0], end[0]], [start[1], end[1]], 
                   color=line_color, linewidth=line_width, zorder=1,
                   solid_capstyle='round')
            offset = perp * bond_offset * 1.2
            ax.plot([start[0] + offset[0], end[0] + offset[0]], 
                   [start[1] + offset[1], end[1] + offset[1]], 
                   color=line_color, linewidth=line_width * 0.8, zorder=1,
                   solid_capstyle='round')
            ax.plot([start[0] - offset[0], end[0] - offset[0]], 
                   [start[1] - offset[1], end[1] - offset[1]], 
                   color=line_color, linewidth=line_width * 0.8, zorder=1,
                   solid_capstyle='round')
        elif order == 1.5:
            ax.plot([start[0], end[0]], [start[1], end[1]], 
                   color=line_color, linewidth=line_width, zorder=1,
                   solid_capstyle='round')
            offset = perp * bond_offset
            ax.plot([start[0] + offset[0], end[0] + offset[0]], 
                   [start[1] + offset[1], end[1] + offset[1]], 
                   color=line_color, linewidth=line_width * 0.6, 
                   linestyle='--', zorder=1)
    
    # Draw heteroatom labels only (not C)
    for atom in atoms:
        element = atom['element']
        pos = atom['position']
        
        # Only show heteroatoms (not C)
        if element == 'C':
            continue
        
        text_kwargs = dict(fontsize=font_size, ha='center', va='center', 
                          color=line_color, fontweight='bold', zorder=10)
        if bg_color and bg_color != 'none':
            text_kwargs['bbox'] = dict(boxstyle='round,pad=0.15', 
                                       facecolor=bg_color, edgecolor='none')
        ax.text(pos[0], pos[1], element, **text_kwargs)


def auto_set_limits_formula(ax, mol_data, padding=0.8):
    """Set axis limits based on atom positions."""
    atoms = mol_data.get('atoms', [])
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


# Common molecule presets for quick access
FORMULA_PRESETS = {
    # Alkanes
    'Methane': 'C',
    'Ethane': 'CC',
    'Propane': 'CCC',
    'Butane': 'CCCC',
    # Alkenes
    'Ethene': 'C=C',
    'Propene': 'CC=C',
    # Alkynes
    'Ethyne': 'C#C',
    # Alcohols
    'Methanol': 'CO',
    'Ethanol': 'CCO',
    'Propan-1-ol': 'CCCO',
    'Propan-2-ol': 'CC(O)C',
    # Carboxylic acids
    'Methanoic acid': 'C(=O)O',
    'Ethanoic acid': 'CC(=O)O',
    # Aldehydes/Ketones
    'Methanal': 'C=O',
    'Ethanal': 'CC=O',
    'Propanone': 'CC(=O)C',
    # Others
    'Water': 'O',
    'Carbon dioxide': 'O=C=O',
    'Ammonia': 'N',
    # Aromatics
    'Benzene': 'c1ccccc1',
}

