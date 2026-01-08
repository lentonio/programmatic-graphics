"""
Skeletal Formulae Page
Shows carbon backbone with implied hydrogens, heteroatoms labeled.
"""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from shared_utils import (
    MY_COLORS,
    get_color_options,
    create_download_buttons,
    apply_figure_style,
    init_session_state,
    DEFAULT_WHITE_BG
)
from formula_utils import (
    parse_smiles_for_formula,
    draw_skeletal_formula,
    auto_set_limits_formula,
    FORMULA_PRESETS
)


# --- Session State Version Check ---
SF_VERSION = 1
if st.session_state.get("sf_version", 0) < SF_VERSION:
    for key in list(st.session_state.keys()):
        if key.startswith("sf_"):
            del st.session_state[key]
    st.session_state["sf_version"] = SF_VERSION

# --- Initialize Session State Defaults ---
SF_DEFAULTS = {
    # Sidebar
    "sf_line_weight": 2.5,
    "sf_label_size": 14,
    "sf_white_bg": DEFAULT_WHITE_BG,
    # Molecule
    "sf_input_method": "Preset molecules",
    "sf_preset": "Ethanol",
    "sf_smiles": "CCO",
    # Style
    "sf_line_color": "grey",
}

init_session_state(SF_DEFAULTS)


def get_index(options, key):
    val = st.session_state.get(key, options[0])
    try:
        return options.index(val)
    except ValueError:
        return 0


COLOR_OPTIONS = get_color_options()
PRESET_NAMES = list(FORMULA_PRESETS.keys())


# --- Sidebar ---
with st.sidebar:
    st.header("Appearance")
    
    line_weight = st.slider(
        "Line weight",
        min_value=1.5, max_value=4.0, step=0.5,
        key="sf_line_weight"
    )
    
    label_size = st.slider(
        "Label size",
        min_value=10, max_value=24, step=1,
        key="sf_label_size"
    )
    
    st.write("")
    white_background = st.toggle("White background", key="sf_white_bg")


fig_height = 6
fig_width = 10


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
    tab_mol, tab_style, tab_info = st.tabs(["Molecule", "Style", "Info"])
    
    # === MOLECULE TAB ===
    with tab_mol:
        input_method = st.radio(
            "Select molecule:",
            ["Preset molecules", "SMILES input"],
            horizontal=True,
            key="sf_input_method"
        )
        
        st.write("")
        
        if input_method == "Preset molecules":
            st.caption("Alkanes")
            cols = st.columns(4)
            alkanes = ['Methane', 'Ethane', 'Propane', 'Butane']
            for i, name in enumerate(alkanes):
                with cols[i % 4]:
                    if st.button(name, key=f"sf_btn_{name}", use_container_width=True):
                        st.session_state["sf_preset"] = name
            
            st.caption("Alkenes & Alkynes")
            cols = st.columns(4)
            unsaturated = ['Ethene', 'Propene', 'Ethyne']
            for i, name in enumerate(unsaturated):
                with cols[i % 4]:
                    if st.button(name, key=f"sf_btn_{name}", use_container_width=True):
                        st.session_state["sf_preset"] = name
            
            st.caption("Alcohols")
            cols = st.columns(4)
            alcohols = ['Methanol', 'Ethanol', 'Propan-1-ol', 'Propan-2-ol']
            for i, name in enumerate(alcohols):
                with cols[i % 4]:
                    if st.button(name, key=f"sf_btn_{name}", use_container_width=True):
                        st.session_state["sf_preset"] = name
            
            st.caption("Carboxylic acids & Carbonyls")
            cols = st.columns(4)
            carbonyls = ['Methanoic acid', 'Ethanoic acid', 'Methanal', 'Ethanal', 'Propanone']
            for i, name in enumerate(carbonyls):
                with cols[i % 4]:
                    if st.button(name, key=f"sf_btn_{name}", use_container_width=True):
                        st.session_state["sf_preset"] = name
            
            st.caption("Other")
            cols = st.columns(4)
            other = ['Water', 'Ammonia', 'Carbon dioxide', 'Benzene']
            for i, name in enumerate(other):
                with cols[i % 4]:
                    if st.button(name, key=f"sf_btn_{name}", use_container_width=True):
                        st.session_state["sf_preset"] = name
            
            st.markdown("---")
            current_preset = st.session_state.get("sf_preset", "Ethanol")
            st.markdown(f"**Selected:** {current_preset}")
            st.caption(f"SMILES: `{FORMULA_PRESETS.get(current_preset, 'CCO')}`")
        
        else:  # SMILES input
            st.caption("Enter a SMILES string")
            smiles_input = st.text_input(
                "SMILES",
                key="sf_smiles",
                placeholder="e.g., CCO, CC(=O)O, c1ccccc1"
            )
    
    # === STYLE TAB ===
    with tab_style:
        st.caption("Colors")
        line_color = st.selectbox(
            "Lines/text", options=COLOR_OPTIONS,
            index=get_index(COLOR_OPTIONS, "sf_line_color"),
            key="sf_line_color"
        )
    
    # === INFO TAB ===
    with tab_info:
        st.caption("About skeletal formulae")
        st.markdown("""
        **Skeletal formulae** show:
        - Carbon atoms as line vertices/ends
        - C-C bonds as lines
        - Heteroatoms (O, N, etc.) labeled
        - Hydrogen atoms implied (not shown)
        
        **Conventions:**
        - Each vertex = carbon atom
        - Each line end = carbon atom
        - Double/triple bonds shown
        - Only non-C, non-H atoms labeled
        """)


# --- Render ---
def render_skeletal_formula():
    input_method = st.session_state.get("sf_input_method", "Preset molecules")
    
    if input_method == "SMILES input":
        smiles = st.session_state.get("sf_smiles", "CCO")
    else:
        preset = st.session_state.get("sf_preset", "Ethanol")
        smiles = FORMULA_PRESETS.get(preset, "CCO")
    
    if not smiles:
        st.warning("Enter a SMILES string")
        return None
    
    # Don't add hydrogens for skeletal formula
    mol_data, error = parse_smiles_for_formula(smiles, add_hydrogens=False)
    
    if error:
        st.error(error)
        return None
    
    # Create figure
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_aspect('equal')
    ax.axis('off')
    
    white_bg = st.session_state.get("sf_white_bg", True)
    apply_figure_style(fig, ax, white_bg)
    bg_color = 'white' if white_bg else 'none'
    
    # Get style settings
    lc = MY_COLORS[st.session_state.get("sf_line_color", "grey")]
    lw = st.session_state.get("sf_line_weight", 2.5)
    fs = st.session_state.get("sf_label_size", 14)
    
    draw_skeletal_formula(
        ax, mol_data,
        line_color=lc,
        line_width=lw,
        font_size=fs,
        bg_color=bg_color
    )
    
    auto_set_limits_formula(ax, mol_data)
    fig.tight_layout()
    return fig


# --- Main ---
try:
    fig = render_skeletal_formula()
    
    if fig is not None:
        plot_placeholder.pyplot(fig)
        
        input_method = st.session_state.get("sf_input_method", "Preset molecules")
        if input_method == "SMILES input":
            smiles = st.session_state.get("sf_smiles", "molecule")
            filename = f"skeletal_{smiles.replace('=', '').replace('(', '').replace(')', '')[:20]}"
        else:
            preset = st.session_state.get("sf_preset", "ethanol")
            filename = f"skeletal_{preset.lower().replace(' ', '_').replace('-', '_')}"
        
        create_download_buttons(fig, svg_placeholder, png_placeholder, filename)
        plt.close(fig)
except Exception as e:
    st.error(f"Error rendering: {e}")
    import traceback
    st.code(traceback.format_exc())

