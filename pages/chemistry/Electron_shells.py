"""
Electron Shell Diagrams Page
Shows electrons arranged in shells around a nucleus.
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
from electron_shell_utils import (
    ELECTRON_CONFIG,
    draw_electron_shell_diagram,
    draw_ion_shell_diagram,
    get_element_list,
    get_element_info,
    auto_set_limits_shell
)


# --- Session State Version Check ---
ES_VERSION = 1
if st.session_state.get("es_version", 0) < ES_VERSION:
    for key in list(st.session_state.keys()):
        if key.startswith("es_"):
            del st.session_state[key]
    st.session_state["es_version"] = ES_VERSION

# --- Initialize Session State Defaults ---
ES_DEFAULTS = {
    # Sidebar
    "es_line_weight": 2.0,
    "es_label_size": 16,
    "es_white_bg": DEFAULT_WHITE_BG,
    # Element
    "es_element": "Na",
    "es_is_ion": False,
    "es_charge": 0,
    # Style
    "es_line_color": "grey",
    "es_nucleus_radius": 0.4,
    "es_shell_spacing": 0.5,
    "es_electron_size": 60,
    # Options
    "es_show_config": True,
}

init_session_state(ES_DEFAULTS)


def get_index(options, key):
    val = st.session_state.get(key, options[0])
    try:
        return options.index(val)
    except ValueError:
        return 0


COLOR_OPTIONS = get_color_options()
ELEMENTS = get_element_list()


# --- Sidebar ---
with st.sidebar:
    st.header("Appearance")
    
    line_weight = st.slider(
        "Line weight",
        min_value=1.0, max_value=4.0, step=0.5,
        key="es_line_weight"
    )
    
    label_size = st.slider(
        "Label size",
        min_value=12, max_value=24, step=1,
        key="es_label_size"
    )
    
    st.write("")
    white_background = st.toggle("White background", key="es_white_bg")


fig_height = 6
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
    tab_elem, tab_style, tab_options = st.tabs(["Element", "Style", "Options"])
    
    # === ELEMENT TAB ===
    with tab_elem:
        st.caption("Select element")
        
        # Group elements by period
        st.write("**Period 1**")
        cols = st.columns(4)
        period1 = ['H', 'He']
        for i, elem in enumerate(period1):
            with cols[i]:
                if st.button(elem, key=f"es_btn_{elem}", use_container_width=True):
                    st.session_state["es_element"] = elem
        
        st.write("**Period 2**")
        cols = st.columns(4)
        period2 = ['Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne']
        for i, elem in enumerate(period2):
            with cols[i % 4]:
                if st.button(elem, key=f"es_btn_{elem}", use_container_width=True):
                    st.session_state["es_element"] = elem
        
        st.write("**Period 3**")
        cols = st.columns(4)
        period3 = ['Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar']
        for i, elem in enumerate(period3):
            with cols[i % 4]:
                if st.button(elem, key=f"es_btn_{elem}", use_container_width=True):
                    st.session_state["es_element"] = elem
        
        st.write("**Period 4** (partial)")
        cols = st.columns(4)
        period4 = ['K', 'Ca']
        for i, elem in enumerate(period4):
            with cols[i]:
                if st.button(elem, key=f"es_btn_{elem}", use_container_width=True):
                    st.session_state["es_element"] = elem
        
        st.markdown("---")
        
        current_elem = st.session_state.get("es_element", "Na")
        elem_info = get_element_info(current_elem)
        if elem_info:
            st.markdown(f"**Selected:** {elem_info['name']} ({current_elem})")
            config_str = '.'.join(str(n) for n in elem_info['shells'])
            st.caption(f"Electron configuration: {config_str}")
        
        st.markdown("---")
        
        # Ion options
        is_ion = st.checkbox("Show as ion", key="es_is_ion")
        
        if is_ion:
            charge = st.slider(
                "Charge",
                min_value=-3, max_value=3, step=1,
                key="es_charge"
            )
            
            if charge != 0:
                charge_str = f"{'+' if charge > 0 else ''}{charge}"
                st.caption(f"Ion: {current_elem}{charge_str}")
    
    # === STYLE TAB ===
    with tab_style:
        st.caption("Colors")
        line_color = st.selectbox(
            "Lines/electrons", options=COLOR_OPTIONS,
            index=get_index(COLOR_OPTIONS, "es_line_color"),
            key="es_line_color"
        )
        
        st.write("")
        st.caption("Sizes")
        
        nucleus_radius = st.slider(
            "Nucleus size",
            min_value=0.2, max_value=0.8, step=0.1,
            key="es_nucleus_radius"
        )
        
        shell_spacing = st.slider(
            "Shell spacing",
            min_value=0.3, max_value=0.8, step=0.1,
            key="es_shell_spacing"
        )
        
        electron_size = st.slider(
            "Electron size",
            min_value=30, max_value=100, step=10,
            key="es_electron_size"
        )
    
    # === OPTIONS TAB ===
    with tab_options:
        st.caption("Display options")
        
        show_config = st.checkbox(
            "Show electron configuration",
            key="es_show_config",
            help="Show 2.8.1 etc. below the diagram"
        )
        
        st.markdown("---")
        st.caption("About electron shells")
        st.markdown("""
        - **Shell 1**: max 2 electrons
        - **Shell 2**: max 8 electrons
        - **Shell 3**: max 8 electrons (GCSE)
        - Electrons fill inner shells first
        """)


# --- Render ---
def render_electron_shells():
    element = st.session_state.get("es_element", "Na")
    is_ion = st.session_state.get("es_is_ion", False)
    charge = st.session_state.get("es_charge", 0) if is_ion else 0
    
    if element not in ELECTRON_CONFIG:
        st.error(f"Unknown element: {element}")
        return None
    
    # Create figure
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_aspect('equal')
    ax.axis('off')
    
    white_bg = st.session_state.get("es_white_bg", True)
    apply_figure_style(fig, ax, white_bg)
    bg_color = 'white' if white_bg else 'none'
    
    # Get style settings
    lc = MY_COLORS[st.session_state.get("es_line_color", "grey")]
    lw = st.session_state.get("es_line_weight", 2.0)
    fs = st.session_state.get("es_label_size", 16)
    nr = st.session_state.get("es_nucleus_radius", 0.4)
    ss = st.session_state.get("es_shell_spacing", 0.5)
    es = st.session_state.get("es_electron_size", 60)
    show_config = st.session_state.get("es_show_config", True)
    
    if is_ion and charge != 0:
        draw_ion_shell_diagram(
            ax, element, charge,
            center=(0, 0),
            nucleus_radius=nr,
            shell_spacing=ss,
            line_color=lc,
            line_width=lw,
            electron_size=es,
            font_size=fs,
            show_nucleus_label=True,
            show_config=show_config,
            bg_color=bg_color
        )
    else:
        draw_electron_shell_diagram(
            ax, element,
            center=(0, 0),
            nucleus_radius=nr,
            shell_spacing=ss,
            line_color=lc,
            line_width=lw,
            electron_size=es,
            font_size=fs,
            show_nucleus_label=True,
            show_config=show_config,
            bg_color=bg_color
        )
    
    auto_set_limits_shell(ax, element, nr, ss)
    fig.tight_layout()
    return fig


# --- Main ---
try:
    fig = render_electron_shells()
    
    if fig is not None:
        plot_placeholder.pyplot(fig)
        
        element = st.session_state.get("es_element", "Na")
        is_ion = st.session_state.get("es_is_ion", False)
        charge = st.session_state.get("es_charge", 0)
        
        if is_ion and charge != 0:
            charge_str = f"{'plus' if charge > 0 else 'minus'}{abs(charge)}"
            filename = f"electron_shell_{element}_{charge_str}"
        else:
            filename = f"electron_shell_{element}"
        
        create_download_buttons(fig, svg_placeholder, png_placeholder, filename)
        plt.close(fig)
except Exception as e:
    st.error(f"Error rendering: {e}")
    import traceback
    st.code(traceback.format_exc())

