"""
Punnett Squares Page
Draw genetic inheritance diagrams showing allele combinations.
"""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.patches import Rectangle

from shared_utils import (
    MY_COLORS,
    get_color_options,
    create_download_buttons,
    apply_figure_style,
    init_session_state,
    DEFAULT_WHITE_BG
)


# --- Session State Version Check ---
PS_VERSION = 1
if st.session_state.get("ps_version", 0) < PS_VERSION:
    for key in list(st.session_state.keys()):
        if key.startswith("ps_"):
            del st.session_state[key]
    st.session_state["ps_version"] = PS_VERSION

# --- Initialize Session State Defaults ---
PS_DEFAULTS = {
    # Sidebar
    "ps_line_weight": 2.0,
    "ps_label_size": 18,
    "ps_white_bg": DEFAULT_WHITE_BG,
    # Genetics
    "ps_preset": "Monohybrid (Aa × Aa)",
    "ps_parent1_allele1": "A",
    "ps_parent1_allele2": "a",
    "ps_parent2_allele1": "A",
    "ps_parent2_allele2": "a",
    # Style
    "ps_line_color": "grey",
    "ps_dominant_color": "blue",
    "ps_recessive_color": "pink",
    # Options
    "ps_show_labels": True,
    "ps_show_ratios": True,
    "ps_highlight_phenotypes": True,
}

init_session_state(PS_DEFAULTS)


def get_index(options, key):
    val = st.session_state.get(key, options[0])
    try:
        return options.index(val)
    except ValueError:
        return 0


COLOR_OPTIONS = get_color_options()

# Preset crosses
PUNNETT_PRESETS = {
    'Monohybrid (Aa × Aa)': {
        'parent1': ('A', 'a'),
        'parent2': ('A', 'a'),
        'description': 'Heterozygous × Heterozygous',
        'trait': 'e.g., Tall (A) vs Short (a)',
    },
    'Monohybrid (Aa × aa)': {
        'parent1': ('A', 'a'),
        'parent2': ('a', 'a'),
        'description': 'Heterozygous × Homozygous recessive',
        'trait': 'Test cross',
    },
    'Monohybrid (AA × aa)': {
        'parent1': ('A', 'A'),
        'parent2': ('a', 'a'),
        'description': 'Homozygous dominant × Homozygous recessive',
        'trait': 'F1 generation all heterozygous',
    },
    'Monohybrid (AA × Aa)': {
        'parent1': ('A', 'A'),
        'parent2': ('A', 'a'),
        'description': 'Homozygous dominant × Heterozygous',
        'trait': 'All offspring show dominant phenotype',
    },
    'Codominance (CR × CW)': {
        'parent1': ('Cᴿ', 'Cᵂ'),
        'parent2': ('Cᴿ', 'Cᵂ'),
        'description': 'Red × White flowers',
        'trait': 'e.g., Snapdragons: Red, Pink, White',
    },
    'Sex-linked (XᴬXᵃ × XᴬY)': {
        'parent1': ('Xᴬ', 'Xᵃ'),
        'parent2': ('Xᴬ', 'Y'),
        'description': 'Carrier female × Normal male',
        'trait': 'e.g., Colour blindness, Haemophilia',
    },
}


def draw_punnett_square(ax, parent1_alleles, parent2_alleles,
                        line_color='#4C5B64', line_width=2.0,
                        font_size=18, dominant_color='#82DCF2',
                        recessive_color='#F688C9',
                        show_labels=True, show_ratios=True,
                        highlight_phenotypes=True, bg_color='white'):
    """
    Draw a Punnett square.
    
    Args:
        parent1_alleles: tuple of (allele1, allele2) for parent 1 (top)
        parent2_alleles: tuple of (allele1, allele2) for parent 2 (left)
    """
    # Grid parameters
    cell_size = 1.0
    grid_left = -1
    grid_top = 1
    
    # Draw grid lines
    for i in range(3):
        # Horizontal lines
        y = grid_top - i * cell_size
        ax.plot([grid_left, grid_left + 2*cell_size], [y, y],
               color=line_color, linewidth=line_width, zorder=5)
        # Vertical lines
        x = grid_left + i * cell_size
        ax.plot([x, x], [grid_top, grid_top - 2*cell_size],
               color=line_color, linewidth=line_width, zorder=5)
    
    # Parent 1 alleles (top) - columns
    if show_labels:
        for i, allele in enumerate(parent1_alleles):
            x = grid_left + (i + 0.5) * cell_size
            y = grid_top + 0.4
            ax.text(x, y, allele, fontsize=font_size * 1.2, ha='center', va='center',
                   color=line_color, fontweight='bold')
        
        # Parent 2 alleles (left) - rows
        for i, allele in enumerate(parent2_alleles):
            x = grid_left - 0.4
            y = grid_top - (i + 0.5) * cell_size
            ax.text(x, y, allele, fontsize=font_size * 1.2, ha='center', va='center',
                   color=line_color, fontweight='bold')
    
    # Fill in offspring genotypes
    genotype_counts = {}
    phenotype_counts = {'dominant': 0, 'recessive': 0, 'heterozygous': 0}
    
    for row, p2_allele in enumerate(parent2_alleles):
        for col, p1_allele in enumerate(parent1_alleles):
            # Combine alleles (dominant first by convention)
            alleles = sorted([p1_allele, p2_allele], 
                           key=lambda x: (x.lower(), x.islower()))
            genotype = alleles[0] + alleles[1]
            
            # Count genotypes
            genotype_counts[genotype] = genotype_counts.get(genotype, 0) + 1
            
            # Determine phenotype (simplified)
            is_dominant = any(a.isupper() and a not in 'XY' for a in [p1_allele, p2_allele])
            is_recessive = all(a.islower() or a == 'Y' for a in [p1_allele, p2_allele])
            
            # Cell position
            cx = grid_left + (col + 0.5) * cell_size
            cy = grid_top - (row + 0.5) * cell_size
            
            # Highlight cell based on phenotype
            if highlight_phenotypes:
                if is_recessive:
                    color = recessive_color
                    phenotype_counts['recessive'] += 1
                else:
                    color = dominant_color
                    phenotype_counts['dominant'] += 1
                
                rect = Rectangle((grid_left + col * cell_size + 0.02, 
                                  grid_top - (row + 1) * cell_size + 0.02),
                                 cell_size - 0.04, cell_size - 0.04,
                                 facecolor=color, alpha=0.3, zorder=1)
                ax.add_patch(rect)
            
            # Draw genotype text
            ax.text(cx, cy, genotype, fontsize=font_size, ha='center', va='center',
                   color=line_color, fontweight='bold', zorder=10)
    
    # Show ratios below
    if show_ratios:
        # Genotype ratio
        ratio_parts = []
        for geno, count in sorted(genotype_counts.items()):
            ratio_parts.append(f"{count} {geno}")
        ratio_text = " : ".join(ratio_parts)
        
        ax.text(0, grid_top - 2*cell_size - 0.6, f"Genotype ratio: {ratio_text}",
               fontsize=font_size * 0.7, ha='center', va='top', color=line_color)
        
        # Phenotype ratio
        dom = phenotype_counts['dominant']
        rec = phenotype_counts['recessive']
        if rec > 0:
            pheno_text = f"Phenotype ratio: {dom} dominant : {rec} recessive"
        else:
            pheno_text = "Phenotype ratio: 4 dominant : 0 recessive"
        
        ax.text(0, grid_top - 2*cell_size - 1.0, pheno_text,
               fontsize=font_size * 0.7, ha='center', va='top', color=line_color)
    
    # Labels for parents
    if show_labels:
        ax.text(0, grid_top + 0.9, "Parent 1", fontsize=font_size * 0.8,
               ha='center', va='center', color=line_color, style='italic')
        ax.text(grid_left - 0.9, 0, "Parent 2", fontsize=font_size * 0.8,
               ha='center', va='center', color=line_color, style='italic',
               rotation=90)


# --- Sidebar ---
with st.sidebar:
    st.header("Appearance")
    
    line_weight = st.slider(
        "Line weight",
        min_value=1.0, max_value=4.0, step=0.5,
        key="ps_line_weight"
    )
    
    label_size = st.slider(
        "Label size",
        min_value=12, max_value=28, step=2,
        key="ps_label_size"
    )
    
    st.write("")
    white_background = st.toggle("White background", key="ps_white_bg")


fig_height = 6
fig_width = 7


# --- Main Layout ---
col_plot, col_controls = st.columns([1.5, 1])

with col_plot:
    plot_placeholder = st.empty()
    st.write("")
    download_cols = st.columns([1.2, 1, 1, 1])
    with download_cols[1]:
        svg_placeholder = st.empty()
    with download_cols[2]:
        png_placeholder = st.empty()

with col_controls:
    tab_cross, tab_style, tab_info = st.tabs(["Cross", "Style", "Info"])
    
    # === CROSS TAB ===
    with tab_cross:
        st.caption("Select cross type")
        
        preset_names = list(PUNNETT_PRESETS.keys())
        cols = st.columns(1)
        for name in preset_names:
            if st.button(name, key=f"ps_btn_{name}", use_container_width=True):
                st.session_state["ps_preset"] = name
                preset = PUNNETT_PRESETS[name]
                st.session_state["ps_parent1_allele1"] = preset['parent1'][0]
                st.session_state["ps_parent1_allele2"] = preset['parent1'][1]
                st.session_state["ps_parent2_allele1"] = preset['parent2'][0]
                st.session_state["ps_parent2_allele2"] = preset['parent2'][1]
        
        st.markdown("---")
        
        current = st.session_state.get("ps_preset", "Monohybrid (Aa × Aa)")
        if current in PUNNETT_PRESETS:
            preset = PUNNETT_PRESETS[current]
            st.markdown(f"**{current}**")
            st.caption(preset['description'])
            st.caption(preset['trait'])
        
        st.markdown("---")
        st.caption("Custom alleles")
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Parent 1 allele 1", key="ps_parent1_allele1", max_chars=3)
            st.text_input("Parent 1 allele 2", key="ps_parent1_allele2", max_chars=3)
        with col2:
            st.text_input("Parent 2 allele 1", key="ps_parent2_allele1", max_chars=3)
            st.text_input("Parent 2 allele 2", key="ps_parent2_allele2", max_chars=3)
    
    # === STYLE TAB ===
    with tab_style:
        st.caption("Colors")
        
        st.selectbox("Lines/text", options=COLOR_OPTIONS,
                    index=get_index(COLOR_OPTIONS, "ps_line_color"),
                    key="ps_line_color")
        
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Dominant", options=COLOR_OPTIONS,
                        index=get_index(COLOR_OPTIONS, "ps_dominant_color"),
                        key="ps_dominant_color")
        with col2:
            st.selectbox("Recessive", options=COLOR_OPTIONS,
                        index=get_index(COLOR_OPTIONS, "ps_recessive_color"),
                        key="ps_recessive_color")
    
    # === INFO TAB ===
    with tab_info:
        st.caption("Display options")
        st.checkbox("Show parent labels", key="ps_show_labels")
        st.checkbox("Show ratios", key="ps_show_ratios")
        st.checkbox("Highlight phenotypes", key="ps_highlight_phenotypes")
        
        st.markdown("---")
        st.caption("Key")
        st.markdown("""
        - **Capital letter** = Dominant allele
        - **Lowercase** = Recessive allele
        - Genotype = combination of alleles
        - Phenotype = physical characteristic
        """)


# --- Render ---
def render_punnett():
    # Get alleles
    p1 = (st.session_state.get("ps_parent1_allele1", "A"),
          st.session_state.get("ps_parent1_allele2", "a"))
    p2 = (st.session_state.get("ps_parent2_allele1", "A"),
          st.session_state.get("ps_parent2_allele2", "a"))
    
    # Create figure
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_aspect('equal')
    ax.axis('off')
    
    white_bg = st.session_state.get("ps_white_bg", True)
    apply_figure_style(fig, ax, white_bg)
    bg_color = 'white' if white_bg else 'none'
    
    # Get style settings
    lc = MY_COLORS[st.session_state.get("ps_line_color", "grey")]
    lw = st.session_state.get("ps_line_weight", 2.0)
    fs = st.session_state.get("ps_label_size", 18)
    dom_color = MY_COLORS[st.session_state.get("ps_dominant_color", "blue")]
    rec_color = MY_COLORS[st.session_state.get("ps_recessive_color", "pink")]
    show_labels = st.session_state.get("ps_show_labels", True)
    show_ratios = st.session_state.get("ps_show_ratios", True)
    highlight = st.session_state.get("ps_highlight_phenotypes", True)
    
    draw_punnett_square(
        ax, p1, p2,
        line_color=lc, line_width=lw, font_size=fs,
        dominant_color=dom_color, recessive_color=rec_color,
        show_labels=show_labels, show_ratios=show_ratios,
        highlight_phenotypes=highlight, bg_color=bg_color
    )
    
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-2.5, 2.5)
    
    fig.tight_layout()
    return fig


# --- Main ---
try:
    fig = render_punnett()
    
    if fig is not None:
        plot_placeholder.pyplot(fig)
        
        p1 = st.session_state.get("ps_parent1_allele1", "A") + st.session_state.get("ps_parent1_allele2", "a")
        p2 = st.session_state.get("ps_parent2_allele1", "A") + st.session_state.get("ps_parent2_allele2", "a")
        filename = f"punnett_{p1}x{p2}"
        
        create_download_buttons(fig, svg_placeholder, png_placeholder, filename)
        plt.close(fig)
except Exception as e:
    st.error(f"Error rendering: {e}")
    import traceback
    st.code(traceback.format_exc())

