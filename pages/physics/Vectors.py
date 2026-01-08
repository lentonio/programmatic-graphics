"""
Vector Diagrams Page
Draw vectors, show addition (tip-to-tail), resultants, and component resolution.
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
from vector_utils import (
    draw_vector,
    draw_vector_addition,
    draw_component_resolution,
    draw_angle_arc,
    draw_axes,
    auto_set_limits_vectors,
    VECTOR_PRESETS
)


# --- Session State Version Check ---
VEC_VERSION = 1
if st.session_state.get("vec_version", 0) < VEC_VERSION:
    for key in list(st.session_state.keys()):
        if key.startswith("vec_"):
            del st.session_state[key]
    st.session_state["vec_version"] = VEC_VERSION

# --- Initialize Session State Defaults ---
VEC_DEFAULTS = {
    # Sidebar
    "vec_line_weight": 2.5,
    "vec_label_size": 14,
    "vec_white_bg": DEFAULT_WHITE_BG,
    # Mode
    "vec_mode": "Vector addition",
    "vec_preset": "Two vectors (acute)",
    # Custom vectors
    "vec_num_vectors": 2,
    "vec_v1_mag": 2.0,
    "vec_v1_angle": 30,
    "vec_v2_mag": 1.5,
    "vec_v2_angle": 80,
    "vec_v3_mag": 1.0,
    "vec_v3_angle": 150,
    # Resolution
    "vec_res_mag": 2.5,
    "vec_res_angle": 40,
    # Style
    "vec_color1": "grey",
    "vec_color2": "blue",
    "vec_resultant_color": "red",
    # Options
    "vec_show_resultant": True,
    "vec_show_axes": True,
    "vec_show_angle": True,
}

init_session_state(VEC_DEFAULTS)


def get_index(options, key):
    val = st.session_state.get(key, options[0])
    try:
        return options.index(val)
    except ValueError:
        return 0


COLOR_OPTIONS = get_color_options()
PRESET_NAMES = list(VECTOR_PRESETS.keys())


# --- Sidebar ---
with st.sidebar:
    st.header("Appearance")
    
    line_weight = st.slider(
        "Line weight",
        min_value=1.5, max_value=4.0, step=0.5,
        key="vec_line_weight"
    )
    
    label_size = st.slider(
        "Label size",
        min_value=10, max_value=20, step=1,
        key="vec_label_size"
    )
    
    st.write("")
    white_background = st.toggle("White background", key="vec_white_bg")


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
    tab_vectors, tab_style, tab_options = st.tabs(["Vectors", "Style", "Options"])
    
    # === VECTORS TAB ===
    with tab_vectors:
        mode = st.radio(
            "Mode:",
            ["Vector addition", "Component resolution", "Custom vectors"],
            horizontal=True,
            key="vec_mode"
        )
        
        st.write("")
        
        if mode == "Vector addition":
            st.caption("Select preset")
            cols = st.columns(2)
            for i, name in enumerate(PRESET_NAMES):
                with cols[i % 2]:
                    if st.button(name, key=f"vec_btn_{name}", use_container_width=True):
                        st.session_state["vec_preset"] = name
            
            st.markdown("---")
            current = st.session_state.get("vec_preset", "Two vectors (acute)")
            preset = VECTOR_PRESETS.get(current, VECTOR_PRESETS["Two vectors (acute)"])
            st.markdown(f"**Selected:** {current}")
            st.caption(preset['description'])
            
            # Show resultant info
            vectors = preset['vectors']
            rx = sum(m * np.cos(np.radians(a)) for m, a in vectors)
            ry = sum(m * np.sin(np.radians(a)) for m, a in vectors)
            r_mag = np.sqrt(rx**2 + ry**2)
            r_angle = np.degrees(np.arctan2(ry, rx))
            st.info(f"Resultant: magnitude ≈ {r_mag:.2f}, angle ≈ {r_angle:.1f}°")
        
        elif mode == "Component resolution":
            st.caption("Vector to resolve")
            
            res_mag = st.slider(
                "Magnitude",
                min_value=0.5, max_value=4.0, step=0.1,
                key="vec_res_mag"
            )
            
            res_angle = st.slider(
                "Angle (°)",
                min_value=0, max_value=90, step=5,
                key="vec_res_angle"
            )
            
            # Show components
            fx = res_mag * np.cos(np.radians(res_angle))
            fy = res_mag * np.sin(np.radians(res_angle))
            st.info(f"Components: Fx = {fx:.2f}, Fy = {fy:.2f}")
        
        else:  # Custom vectors
            st.caption("Define vectors")
            
            num_vectors = st.slider(
                "Number of vectors",
                min_value=1, max_value=3, step=1,
                key="vec_num_vectors"
            )
            
            st.write("")
            
            # Vector 1
            st.write("**Vector 1**")
            col1, col2 = st.columns(2)
            with col1:
                st.number_input("Magnitude", min_value=0.1, max_value=5.0, 
                               step=0.1, key="vec_v1_mag")
            with col2:
                st.number_input("Angle (°)", min_value=-180, max_value=180,
                               step=5, key="vec_v1_angle")
            
            if num_vectors >= 2:
                st.write("**Vector 2**")
                col1, col2 = st.columns(2)
                with col1:
                    st.number_input("Magnitude", min_value=0.1, max_value=5.0,
                                   step=0.1, key="vec_v2_mag")
                with col2:
                    st.number_input("Angle (°)", min_value=-180, max_value=180,
                                   step=5, key="vec_v2_angle")
            
            if num_vectors >= 3:
                st.write("**Vector 3**")
                col1, col2 = st.columns(2)
                with col1:
                    st.number_input("Magnitude", min_value=0.1, max_value=5.0,
                                   step=0.1, key="vec_v3_mag")
                with col2:
                    st.number_input("Angle (°)", min_value=-180, max_value=180,
                                   step=5, key="vec_v3_angle")
    
    # === STYLE TAB ===
    with tab_style:
        st.caption("Colors")
        
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Vector color", options=COLOR_OPTIONS,
                        index=get_index(COLOR_OPTIONS, "vec_color1"),
                        key="vec_color1")
        with col2:
            st.selectbox("Resultant", options=COLOR_OPTIONS,
                        index=get_index(COLOR_OPTIONS, "vec_resultant_color"),
                        key="vec_resultant_color")
    
    # === OPTIONS TAB ===
    with tab_options:
        st.caption("Display options")
        
        st.checkbox("Show resultant vector", key="vec_show_resultant")
        st.checkbox("Show axes", key="vec_show_axes")
        st.checkbox("Show angle arcs", key="vec_show_angle")


# --- Render ---
def render_vectors():
    mode = st.session_state.get("vec_mode", "Vector addition")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_aspect('equal')
    ax.axis('off')
    
    white_bg = st.session_state.get("vec_white_bg", True)
    apply_figure_style(fig, ax, white_bg)
    
    # Get style settings
    lw = st.session_state.get("vec_line_weight", 2.5)
    fs = st.session_state.get("vec_label_size", 14)
    vec_color = MY_COLORS[st.session_state.get("vec_color1", "grey")]
    res_color = MY_COLORS[st.session_state.get("vec_resultant_color", "red")]
    show_resultant = st.session_state.get("vec_show_resultant", True)
    show_axes = st.session_state.get("vec_show_axes", True)
    show_angle = st.session_state.get("vec_show_angle", True)
    
    all_points = [(0, 0)]
    
    if mode == "Vector addition":
        preset_name = st.session_state.get("vec_preset", "Two vectors (acute)")
        preset = VECTOR_PRESETS.get(preset_name, VECTOR_PRESETS["Two vectors (acute)"])
        vectors = preset['vectors']
        labels = preset.get('labels', None)
        
        result = draw_vector_addition(
            ax, vectors, start=(0, 0),
            colors=[vec_color] * len(vectors),
            resultant_color=res_color,
            line_width=lw, font_size=fs,
            show_resultant=show_resultant,
            labels=labels
        )
        all_points = result['end_points']
        
        # Show angle arc for first vector
        if show_angle and len(vectors) > 0:
            draw_angle_arc(ax, (0, 0), 0.4, 0, vectors[0][1],
                          color=vec_color, label=f"{vectors[0][1]}°", font_size=fs*0.8)
    
    elif mode == "Component resolution":
        mag = st.session_state.get("vec_res_mag", 2.5)
        angle = st.session_state.get("vec_res_angle", 40)
        
        end = draw_component_resolution(
            ax, (0, 0), mag, angle,
            main_color=vec_color, comp_color=res_color,
            line_width=lw, font_size=fs,
            labels=('F', 'Fₓ', 'Fᵧ')
        )
        all_points = [(0, 0), end, (end[0], 0), (0, end[1])]
        
        # Show angle
        if show_angle:
            draw_angle_arc(ax, (0, 0), 0.5, 0, angle,
                          color=vec_color, label=f"θ={angle}°", font_size=fs*0.8)
    
    else:  # Custom vectors
        num = st.session_state.get("vec_num_vectors", 2)
        vectors = []
        labels = []
        
        if num >= 1:
            vectors.append((st.session_state.get("vec_v1_mag", 2.0),
                           st.session_state.get("vec_v1_angle", 30)))
            labels.append('A')
        if num >= 2:
            vectors.append((st.session_state.get("vec_v2_mag", 1.5),
                           st.session_state.get("vec_v2_angle", 80)))
            labels.append('B')
        if num >= 3:
            vectors.append((st.session_state.get("vec_v3_mag", 1.0),
                           st.session_state.get("vec_v3_angle", 150)))
            labels.append('C')
        
        result = draw_vector_addition(
            ax, vectors, start=(0, 0),
            colors=[vec_color] * len(vectors),
            resultant_color=res_color,
            line_width=lw, font_size=fs,
            show_resultant=show_resultant,
            labels=labels
        )
        all_points = result['end_points']
    
    # Draw axes if enabled
    if show_axes:
        max_extent = max(max(abs(p[0]) for p in all_points),
                        max(abs(p[1]) for p in all_points), 1)
        draw_axes(ax, (0, 0), max_extent * 0.3, color='#888888',
                 line_width=1, font_size=fs*0.8)
    
    auto_set_limits_vectors(ax, all_points)
    fig.tight_layout()
    return fig


# --- Main ---
try:
    fig = render_vectors()
    
    if fig is not None:
        plot_placeholder.pyplot(fig)
        
        mode = st.session_state.get("vec_mode", "addition")
        filename = f"vectors_{mode.lower().replace(' ', '_')}"
        
        create_download_buttons(fig, svg_placeholder, png_placeholder, filename)
        plt.close(fig)
except Exception as e:
    st.error(f"Error rendering: {e}")
    import traceback
    st.code(traceback.format_exc())

