"""
Transport Diagrams Page
Diffusion, osmosis, and active transport visualizations.
"""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, FancyBboxPatch

from shared_utils import (
    MY_COLORS,
    get_color_options,
    create_download_buttons,
    apply_figure_style,
    init_session_state,
    DEFAULT_WHITE_BG
)


# --- Session State Version Check ---
TR_VERSION = 1
if st.session_state.get("tr_version", 0) < TR_VERSION:
    for key in list(st.session_state.keys()):
        if key.startswith("tr_"):
            del st.session_state[key]
    st.session_state["tr_version"] = TR_VERSION

# --- Initialize Session State Defaults ---
TR_DEFAULTS = {
    # Sidebar
    "tr_line_weight": 2.0,
    "tr_label_size": 14,
    "tr_white_bg": DEFAULT_WHITE_BG,
    # Transport
    "tr_preset": "Diffusion (high to low)",
    # Style
    "tr_line_color": "grey",
    "tr_particle_color": "blue",
    "tr_membrane_color": "green",
    # Options
    "tr_show_labels": True,
    "tr_show_arrows": True,
    "tr_show_concentrations": True,
}

init_session_state(TR_DEFAULTS)


def get_index(options, key):
    val = st.session_state.get(key, options[0])
    try:
        return options.index(val)
    except ValueError:
        return 0


COLOR_OPTIONS = get_color_options()

# Transport presets
TRANSPORT_PRESETS = {
    'Diffusion (high to low)': {
        'type': 'diffusion',
        'description': 'Particles move from high to low concentration',
        'left_particles': 12,
        'right_particles': 3,
        'arrow_direction': 'right',
        'left_label': 'High\nconcentration',
        'right_label': 'Low\nconcentration',
    },
    'Diffusion (equilibrium)': {
        'type': 'diffusion',
        'description': 'Equal concentration on both sides',
        'left_particles': 6,
        'right_particles': 6,
        'arrow_direction': 'both',
        'left_label': 'Equal\nconcentration',
        'right_label': 'Equal\nconcentration',
    },
    'Osmosis (into cell)': {
        'type': 'osmosis',
        'description': 'Water moves into cell (hypotonic solution)',
        'left_particles': 3,  # solute outside
        'right_particles': 10,  # solute inside
        'water_direction': 'right',
        'left_label': 'Hypotonic\n(dilute)',
        'right_label': 'Cell\n(concentrated)',
        'show_water': True,
    },
    'Osmosis (out of cell)': {
        'type': 'osmosis',
        'description': 'Water moves out of cell (hypertonic solution)',
        'left_particles': 10,  # solute outside
        'right_particles': 3,  # solute inside
        'water_direction': 'left',
        'left_label': 'Hypertonic\n(concentrated)',
        'right_label': 'Cell\n(dilute)',
        'show_water': True,
    },
    'Active transport': {
        'type': 'active',
        'description': 'Particles pumped against concentration gradient (uses ATP)',
        'left_particles': 3,
        'right_particles': 10,
        'arrow_direction': 'right',
        'left_label': 'Low\nconcentration',
        'right_label': 'High\nconcentration',
        'show_protein': True,
        'show_atp': True,
    },
    'Facilitated diffusion': {
        'type': 'facilitated',
        'description': 'Particles move through channel proteins (no ATP)',
        'left_particles': 10,
        'right_particles': 3,
        'arrow_direction': 'right',
        'left_label': 'High\nconcentration',
        'right_label': 'Low\nconcentration',
        'show_protein': True,
    },
}


def draw_transport_diagram(ax, preset_data, line_color='#4C5B64',
                           particle_color='#82DCF2', membrane_color='#8FE384',
                           line_width=2.0, font_size=14,
                           show_labels=True, show_arrows=True,
                           show_concentrations=True, bg_color='white'):
    """Draw a transport diagram."""
    
    # Dimensions
    box_width = 2.0
    box_height = 2.5
    membrane_width = 0.15
    gap = membrane_width + 0.1
    
    # Draw left region
    left_box = FancyBboxPatch((-box_width - gap/2, -box_height/2), 
                               box_width, box_height,
                               boxstyle="round,pad=0.05",
                               facecolor='none', edgecolor=line_color,
                               linewidth=line_width, zorder=5)
    ax.add_patch(left_box)
    
    # Draw right region
    right_box = FancyBboxPatch((gap/2, -box_height/2),
                                box_width, box_height,
                                boxstyle="round,pad=0.05",
                                facecolor='none', edgecolor=line_color,
                                linewidth=line_width, zorder=5)
    ax.add_patch(right_box)
    
    # Draw membrane
    membrane = Rectangle((-membrane_width/2, -box_height/2 - 0.1),
                        membrane_width, box_height + 0.2,
                        facecolor=membrane_color, edgecolor=line_color,
                        linewidth=line_width, alpha=0.7, zorder=10)
    ax.add_patch(membrane)
    
    # Membrane label
    if show_labels:
        ax.text(0, -box_height/2 - 0.4, 'Membrane', fontsize=font_size*0.8,
               ha='center', va='top', color=line_color)
    
    # Draw channel protein if needed
    if preset_data.get('show_protein'):
        # Draw protein channel in membrane
        protein_y = 0
        protein_height = 0.8
        protein_width = 0.4
        
        # Protein body
        protein = FancyBboxPatch((-protein_width/2, protein_y - protein_height/2),
                                  protein_width, protein_height,
                                  boxstyle="round,pad=0.05",
                                  facecolor='#FFD700', edgecolor=line_color,
                                  linewidth=line_width, alpha=0.9, zorder=15)
        ax.add_patch(protein)
        
        # Channel opening
        ax.plot([0, 0], [protein_y - protein_height/4, protein_y + protein_height/4],
               color=bg_color, linewidth=line_width*2, zorder=16)
        
        if show_labels:
            ax.text(0, protein_y + protein_height/2 + 0.2, 'Protein', 
                   fontsize=font_size*0.7, ha='center', va='bottom', color=line_color)
    
    # Draw particles in left region
    n_left = preset_data['left_particles']
    np.random.seed(42)  # Consistent positions
    for i in range(n_left):
        px = -box_width/2 - gap/2 + np.random.uniform(-box_width/2 + 0.2, box_width/2 - 0.2)
        py = np.random.uniform(-box_height/2 + 0.2, box_height/2 - 0.2)
        circle = Circle((px, py), 0.1, facecolor=particle_color,
                        edgecolor=line_color, linewidth=1, zorder=8)
        ax.add_patch(circle)
    
    # Draw particles in right region
    n_right = preset_data['right_particles']
    np.random.seed(43)
    for i in range(n_right):
        px = box_width/2 + gap/2 + np.random.uniform(-box_width/2 + 0.2, box_width/2 - 0.2)
        py = np.random.uniform(-box_height/2 + 0.2, box_height/2 - 0.2)
        circle = Circle((px, py), 0.1, facecolor=particle_color,
                        edgecolor=line_color, linewidth=1, zorder=8)
        ax.add_patch(circle)
    
    # Draw water molecules for osmosis
    if preset_data.get('show_water'):
        water_color = '#82DCF2'
        np.random.seed(44)
        # More water on the dilute side
        if preset_data['water_direction'] == 'right':
            left_water, right_water = 8, 3
        else:
            left_water, right_water = 3, 8
        
        for i in range(left_water):
            px = -box_width/2 - gap/2 + np.random.uniform(-box_width/2 + 0.2, box_width/2 - 0.2)
            py = np.random.uniform(-box_height/2 + 0.2, box_height/2 - 0.2)
            ax.text(px, py, '~', fontsize=font_size*0.8, ha='center', va='center',
                   color=water_color, fontweight='bold', zorder=7)
        
        for i in range(right_water):
            px = box_width/2 + gap/2 + np.random.uniform(-box_width/2 + 0.2, box_width/2 - 0.2)
            py = np.random.uniform(-box_height/2 + 0.2, box_height/2 - 0.2)
            ax.text(px, py, '~', fontsize=font_size*0.8, ha='center', va='center',
                   color=water_color, fontweight='bold', zorder=7)
    
    # Draw arrows showing movement
    if show_arrows:
        arrow_y = 0
        arrow_color = MY_COLORS['red']
        
        direction = preset_data.get('arrow_direction', 'right')
        if preset_data.get('show_water'):
            direction = preset_data.get('water_direction', 'right')
        
        if direction == 'right' or direction == 'both':
            ax.annotate('', xy=(0.5, arrow_y), xytext=(-0.5, arrow_y),
                       arrowprops=dict(arrowstyle='->', color=arrow_color,
                                      lw=line_width*1.5, mutation_scale=20),
                       zorder=20)
        
        if direction == 'left' or direction == 'both':
            ax.annotate('', xy=(-0.5, arrow_y + 0.3 if direction == 'both' else arrow_y), 
                       xytext=(0.5, arrow_y + 0.3 if direction == 'both' else arrow_y),
                       arrowprops=dict(arrowstyle='->', color=arrow_color,
                                      lw=line_width*1.5, mutation_scale=20),
                       zorder=20)
    
    # Draw ATP label for active transport
    if preset_data.get('show_atp'):
        ax.text(0, -0.7, 'ATP →', fontsize=font_size*0.9, ha='center', va='center',
               color=MY_COLORS['red'], fontweight='bold', zorder=20,
               bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                        edgecolor=MY_COLORS['red'], alpha=0.9))
    
    # Concentration labels
    if show_concentrations:
        ax.text(-box_width/2 - gap/2, box_height/2 + 0.3, preset_data['left_label'],
               fontsize=font_size*0.9, ha='center', va='bottom', color=line_color,
               linespacing=0.9)
        ax.text(box_width/2 + gap/2, box_height/2 + 0.3, preset_data['right_label'],
               fontsize=font_size*0.9, ha='center', va='bottom', color=line_color,
               linespacing=0.9)


# --- Sidebar ---
with st.sidebar:
    st.header("Appearance")
    
    line_weight = st.slider(
        "Line weight",
        min_value=1.0, max_value=4.0, step=0.5,
        key="tr_line_weight"
    )
    
    label_size = st.slider(
        "Label size",
        min_value=10, max_value=20, step=1,
        key="tr_label_size"
    )
    
    st.write("")
    white_background = st.toggle("White background", key="tr_white_bg")


fig_height = 5
fig_width = 8


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
    tab_transport, tab_style, tab_info = st.tabs(["Transport", "Style", "Info"])
    
    # === TRANSPORT TAB ===
    with tab_transport:
        st.caption("Select transport type")
        
        # Diffusion
        st.write("**Diffusion**")
        cols = st.columns(2)
        diffusion_presets = ['Diffusion (high to low)', 'Diffusion (equilibrium)']
        for i, name in enumerate(diffusion_presets):
            with cols[i]:
                short_name = name.replace('Diffusion ', '')
                if st.button(short_name, key=f"tr_btn_{name}", use_container_width=True):
                    st.session_state["tr_preset"] = name
        
        # Osmosis
        st.write("**Osmosis**")
        cols = st.columns(2)
        osmosis_presets = ['Osmosis (into cell)', 'Osmosis (out of cell)']
        for i, name in enumerate(osmosis_presets):
            with cols[i]:
                short_name = name.replace('Osmosis ', '')
                if st.button(short_name, key=f"tr_btn_{name}", use_container_width=True):
                    st.session_state["tr_preset"] = name
        
        # Active/Facilitated
        st.write("**Active/Facilitated**")
        cols = st.columns(2)
        active_presets = ['Active transport', 'Facilitated diffusion']
        for i, name in enumerate(active_presets):
            with cols[i]:
                if st.button(name.replace(' transport', '').replace(' diffusion', ''), 
                            key=f"tr_btn_{name}", use_container_width=True):
                    st.session_state["tr_preset"] = name
        
        st.markdown("---")
        
        current = st.session_state.get("tr_preset", "Diffusion (high to low)")
        if current in TRANSPORT_PRESETS:
            st.markdown(f"**{current}**")
            st.caption(TRANSPORT_PRESETS[current]['description'])
    
    # === STYLE TAB ===
    with tab_style:
        st.caption("Colors")
        
        st.selectbox("Lines/text", options=COLOR_OPTIONS,
                    index=get_index(COLOR_OPTIONS, "tr_line_color"),
                    key="tr_line_color")
        
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Particles", options=COLOR_OPTIONS,
                        index=get_index(COLOR_OPTIONS, "tr_particle_color"),
                        key="tr_particle_color")
        with col2:
            st.selectbox("Membrane", options=COLOR_OPTIONS,
                        index=get_index(COLOR_OPTIONS, "tr_membrane_color"),
                        key="tr_membrane_color")
    
    # === INFO TAB ===
    with tab_info:
        st.caption("Display options")
        st.checkbox("Show labels", key="tr_show_labels")
        st.checkbox("Show arrows", key="tr_show_arrows")
        st.checkbox("Show concentrations", key="tr_show_concentrations")
        
        st.markdown("---")
        st.caption("Key concepts")
        st.markdown("""
        - **Diffusion**: High → Low (passive)
        - **Osmosis**: Water moves (passive)
        - **Active**: Low → High (uses ATP)
        - **Facilitated**: Via proteins (passive)
        """)


# --- Render ---
def render_transport():
    preset_name = st.session_state.get("tr_preset", "Diffusion (high to low)")
    preset = TRANSPORT_PRESETS.get(preset_name, TRANSPORT_PRESETS["Diffusion (high to low)"])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_aspect('equal')
    ax.axis('off')
    
    white_bg = st.session_state.get("tr_white_bg", True)
    apply_figure_style(fig, ax, white_bg)
    bg_color = 'white' if white_bg else 'none'
    
    # Get style settings
    lc = MY_COLORS[st.session_state.get("tr_line_color", "grey")]
    lw = st.session_state.get("tr_line_weight", 2.0)
    fs = st.session_state.get("tr_label_size", 14)
    pc = MY_COLORS[st.session_state.get("tr_particle_color", "blue")]
    mc = MY_COLORS[st.session_state.get("tr_membrane_color", "green")]
    show_labels = st.session_state.get("tr_show_labels", True)
    show_arrows = st.session_state.get("tr_show_arrows", True)
    show_conc = st.session_state.get("tr_show_concentrations", True)
    
    draw_transport_diagram(
        ax, preset,
        line_color=lc, particle_color=pc, membrane_color=mc,
        line_width=lw, font_size=fs,
        show_labels=show_labels, show_arrows=show_arrows,
        show_concentrations=show_conc, bg_color=bg_color
    )
    
    ax.set_xlim(-4, 4)
    ax.set_ylim(-2.5, 2.5)
    
    fig.tight_layout()
    return fig


# --- Main ---
try:
    fig = render_transport()
    
    if fig is not None:
        plot_placeholder.pyplot(fig)
        
        preset = st.session_state.get("tr_preset", "diffusion")
        filename = f"transport_{preset.lower().replace(' ', '_').replace('(', '').replace(')', '')}"
        
        create_download_buttons(fig, svg_placeholder, png_placeholder, filename)
        plt.close(fig)
except Exception as e:
    st.error(f"Error rendering: {e}")
    import traceback
    st.code(traceback.format_exc())

