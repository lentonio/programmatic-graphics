"""
Dot-and-Cross Diagrams Page
Creates educational diagrams showing ionic and covalent bonding with electron dots and crosses.
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
from dotcross_utils import (
    ELEMENT_DATA,
    PRESET_MOLECULES,
    draw_atom_circle,
    draw_covalent_molecule,
    draw_ionic_compound,
    auto_set_limits,
    get_preset_names,
    get_preset_molecule,
    get_element_list,
    parse_smiles
)


# --- Initialize Session State Defaults ---
# Version bump to reset stale session state values
DC_VERSION = 2
if st.session_state.get("dc_version", 0) < DC_VERSION:
    # Clear old SMILES-related keys that may have bad values
    for key in ["dc_smiles_overlap", "dc_smiles_manual_scale", "dc_smiles_auto_scale", "dc_smiles_scale"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state["dc_version"] = DC_VERSION

DC_DEFAULTS = {
    # Sidebar
    "dc_line_weight": 2.5,
    "dc_label_size": 18,
    "dc_white_bg": DEFAULT_WHITE_BG,
    # Definition
    "dc_input_method": "Preset molecules",
    "dc_preset": "H₂O",
    "dc_smiles": "CCO",  # Ethanol as example
    # Style
    "dc_line_color": "grey",
    "dc_dot_color": "grey",
    "dc_cross_color": "red",
    "dc_atom_radius": 0.6,
    "dc_electron_size": 80,
    # Options
    "dc_show_all_electrons": True,
    "dc_show_brackets": True,
}

init_session_state(DC_DEFAULTS)


# Helper to get selectbox index
def get_index(options, key):
    val = st.session_state.get(key, options[0])
    try:
        return options.index(val)
    except ValueError:
        return 0


COLOR_OPTIONS = get_color_options()
PRESET_NAMES = get_preset_names()


# --- Sidebar: Appearance Settings ---
with st.sidebar:
    st.header("Appearance")
    
    line_weight = st.slider(
        "Line weight",
        min_value=1.5, max_value=4.0, step=0.5,
        key="dc_line_weight"
    )
    
    label_size = st.slider(
        "Label size",
        min_value=12, max_value=30, step=1,
        key="dc_label_size"
    )
    
    st.write("")
    white_background = st.toggle("White background", key="dc_white_bg")


# Fixed figure size
fig_height = 6
fig_width = 10


# --- Main Layout ---
col_plot, col_controls = st.columns([1.5, 1])


# --- Plot Column ---
with col_plot:
    plot_placeholder = st.empty()
    st.write("")
    download_cols = st.columns([1.2, 1, 1, 1])
    with download_cols[1]:
        svg_placeholder = st.empty()
    with download_cols[2]:
        png_placeholder = st.empty()


# --- Controls Column with Tabs ---
with col_controls:
    tab_def, tab_style, tab_options = st.tabs([
        "Molecule",
        "Style",
        "Options"
    ])
    
    # === MOLECULE TAB ===
    with tab_def:
        input_method = st.radio(
            "Select molecule:",
            ["Preset molecules", "SMILES input"],
            horizontal=True,
            key="dc_input_method"
        )
        
        st.write("")
        
        if input_method == "Preset molecules":
            # Group presets by type
            covalent_presets = [k for k, v in PRESET_MOLECULES.items() if v['type'] == 'covalent']
            ionic_presets = [k for k, v in PRESET_MOLECULES.items() if v['type'] == 'ionic']
            
            st.caption("Covalent molecules")
            cov_cols = st.columns(4)
            for i, preset in enumerate(covalent_presets):
                with cov_cols[i % 4]:
                    if st.button(preset, key=f"btn_cov_{preset}", use_container_width=True):
                        st.session_state["dc_preset"] = preset
            
            st.write("")
            st.caption("Ionic compounds")
            ion_cols = st.columns(4)
            for i, preset in enumerate(ionic_presets):
                with ion_cols[i % 4]:
                    if st.button(preset, key=f"btn_ion_{preset}", use_container_width=True):
                        st.session_state["dc_preset"] = preset
            
            st.markdown("---")
            
            # Show current selection and description
            current_preset = st.session_state.get("dc_preset", "H₂O")
            molecule_data = get_preset_molecule(current_preset)
            
            st.markdown(f"**Selected:** {current_preset}")
            st.caption(molecule_data.get('description', ''))
            
            bonding_type = molecule_data.get('type', 'covalent')
            st.info(f"Bonding type: **{bonding_type.capitalize()}**")
        
        else:  # SMILES input
            st.caption("Enter a SMILES string")
            st.warning("⚠️ Dot-and-cross diagrams work best for simple molecules. "
                      "Complex molecules will have unavoidable overlap issues.")
            smiles_input = st.text_input(
                "SMILES",
                key="dc_smiles",
                placeholder="e.g., O, C, N, O=C=O"
            )
            
            
            # Show what molecule was parsed
            if smiles_input:
                ar = st.session_state.get("dc_atom_radius", 0.6)
                    
                mol_data, err = parse_smiles(smiles_input, scale='auto', 
                                             atom_radius=ar, target_overlap=0.45)
                if mol_data and not err:
                    atom_list = [a['element'] for a in mol_data['atoms']]
                    # Truncate for large molecules
                    if len(atom_list) > 10:
                        st.caption(f"Atoms: {len(atom_list)} total ({atom_list[:5]}...)")
                    else:
                        st.caption(f"Atoms: {' - '.join(atom_list)}")
                    
                    # Debug: show which atoms have lone pairs
                    lp = mol_data.get('lone_pairs', {})
                    if lp:
                        lp_atoms = [atom_list[i] for i in lp.keys() if i < len(atom_list)]
                        unique_lp = list(set(lp_atoms))
                        st.caption(f"Lone pairs on: {', '.join(unique_lp)}")
            
            st.markdown("---")
            
            st.caption("Example SMILES:")
            examples = {
                "Water": "O",
                "Methane": "C",
                "Ethanol": "CCO",
                "Acetic acid": "CC(=O)O",
                "Carbon dioxide": "O=C=O",
                "Ammonia": "N",
                "Hydrogen peroxide": "OO",
                "Formaldehyde": "C=O",
            }
            
            def set_smiles(smi):
                st.session_state["dc_smiles"] = smi
            
            ex_cols = st.columns(2)
            for i, (name, smi) in enumerate(examples.items()):
                with ex_cols[i % 2]:
                    st.button(
                        f"{name}", 
                        key=f"ex_{smi}", 
                        use_container_width=True,
                        on_click=set_smiles,
                        args=(smi,)
                    )
    
    # === STYLE TAB ===
    with tab_style:
        st.caption("Colors")
        color_cols = st.columns(3)
        with color_cols[0]:
            line_color = st.selectbox(
                "Lines/text", options=COLOR_OPTIONS,
                index=get_index(COLOR_OPTIONS, "dc_line_color"),
                key="dc_line_color"
            )
        with color_cols[1]:
            dot_color = st.selectbox(
                "Dots (●)", options=COLOR_OPTIONS,
                index=get_index(COLOR_OPTIONS, "dc_dot_color"),
                key="dc_dot_color"
            )
        with color_cols[2]:
            cross_color = st.selectbox(
                "Crosses (×)", options=COLOR_OPTIONS,
                index=get_index(COLOR_OPTIONS, "dc_cross_color"),
                key="dc_cross_color"
            )
        
        st.write("")
        st.caption("Sizes")
        size_cols = st.columns(2)
        with size_cols[0]:
            atom_radius = st.slider(
                "Atom radius", min_value=0.3, max_value=1.0, step=0.1,
                key="dc_atom_radius"
            )
        with size_cols[1]:
            electron_size = st.slider(
                "Electron size", min_value=40, max_value=150, step=10,
                key="dc_electron_size"
            )
    
    # === OPTIONS TAB ===
    with tab_options:
        st.caption("Display options")
        
        show_all_electrons = st.checkbox(
            "Show all outer shell electrons",
            key="dc_show_all_electrons",
            help="Show lone pairs as well as bonding electrons"
        )
        
        show_brackets = st.checkbox(
            "Show ionic brackets and charges",
            key="dc_show_brackets",
            help="Show square brackets around ions with charge notation"
        )
        
        st.markdown("---")
        
        st.caption("Key")
        st.markdown("""
        - **●** (dots) = electrons from first element
        - **×** (crosses) = electrons from second element
        - Shared electrons appear in the overlap region between atoms
        - Lone pairs are electrons not involved in bonding
        """)


# --- Render Diagram ---
def render_dotcross():
    """Render the dot-and-cross diagram."""
    
    # Get current molecule based on input method
    input_method = st.session_state.get("dc_input_method", "Preset molecules")
    
    if input_method == "SMILES input":
        smiles = st.session_state.get("dc_smiles", "O")
        ar = st.session_state.get("dc_atom_radius", 0.6)
            
        molecule_data, error = parse_smiles(smiles, scale='auto', 
                                            atom_radius=ar, target_overlap=0.45)
        
        if error:
            st.error(error)
            return None
        if molecule_data is None:
            st.warning("Enter a valid SMILES string")
            return None
    else:
        current_preset = st.session_state.get("dc_preset", "H₂O")
        molecule_data = get_preset_molecule(current_preset)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Apply background
    apply_figure_style(fig, ax, white_background)
    
    # Get style settings
    lc = MY_COLORS[st.session_state.get("dc_line_color", "grey")]
    dc = MY_COLORS[st.session_state.get("dc_dot_color", "grey")]
    cc = MY_COLORS[st.session_state.get("dc_cross_color", "red")]
    ar = st.session_state.get("dc_atom_radius", 0.6)
    es = st.session_state.get("dc_electron_size", 80)
    show_all = st.session_state.get("dc_show_all_electrons", True)
    show_brackets = st.session_state.get("dc_show_brackets", True)
    
    # Background color for label readability (none = transparent)
    bg = 'white' if white_background else 'none'
    
    # Draw based on bonding type
    if molecule_data['type'] == 'covalent':
        draw_covalent_molecule(
            ax, molecule_data,
            atom_radius=ar,
            dot_color=dc,
            cross_color=cc,
            line_color=lc,
            line_width=line_weight,
            font_size=label_size,
            electron_size=es,
            show_all_electrons=show_all,
            bg_color=bg
        )
    else:  # ionic
        draw_ionic_compound(
            ax, molecule_data,
            atom_radius=ar,
            dot_color=dc,
            cross_color=cc,
            line_color=lc,
            line_width=line_weight,
            font_size=label_size,
            electron_size=es,
            show_brackets=show_brackets,
            bg_color=bg
        )
    
    # Set limits
    auto_set_limits(ax, molecule_data, padding=1.5)
    
    fig.tight_layout()
    return fig


# --- Main Rendering Logic ---
try:
    fig = render_dotcross()
    
    if fig is not None:
        plot_placeholder.pyplot(fig)
        
        # Get filename based on input method
        input_method = st.session_state.get("dc_input_method", "Preset molecules")
        if input_method == "SMILES input":
            smiles = st.session_state.get("dc_smiles", "molecule")
            filename = f"dotcross_{smiles.replace('=', '').replace('(', '').replace(')', '')[:20]}"
        else:
            current_preset = st.session_state.get("dc_preset", "H2O")
            filename = f"dotcross_{current_preset.replace('₂', '2').replace('₃', '3').replace('₄', '4')}"
        
        create_download_buttons(fig, svg_placeholder, png_placeholder, filename)
        plt.close(fig)
except Exception as e:
    st.error(f"Error rendering: {e}")
    import traceback
    st.code(traceback.format_exc())

