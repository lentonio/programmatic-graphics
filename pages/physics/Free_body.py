"""
Free-Body Diagrams Page
Draw objects with force vectors showing weight, normal, friction, applied forces.
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
from freebody_utils import (
    draw_force_arrow,
    draw_block,
    draw_particle,
    draw_inclined_plane,
    draw_ground,
    auto_set_limits_freebody,
    FREEBODY_PRESETS,
    FORCE_COLORS
)


# --- Session State Version Check ---
FB_VERSION = 1
if st.session_state.get("fb_version", 0) < FB_VERSION:
    for key in list(st.session_state.keys()):
        if key.startswith("fb_"):
            del st.session_state[key]
    st.session_state["fb_version"] = FB_VERSION

# --- Initialize Session State Defaults ---
FB_DEFAULTS = {
    # Sidebar
    "fb_line_weight": 2.5,
    "fb_label_size": 14,
    "fb_white_bg": DEFAULT_WHITE_BG,
    # Scenario
    "fb_preset": "Block on flat surface",
    # Style
    "fb_object_color": "grey",
    "fb_weight_color": "blue",
    "fb_normal_color": "green",
    "fb_friction_color": "orange",
    "fb_applied_color": "red",
    "fb_tension_color": "purple",
    # Options
    "fb_show_object": True,
    "fb_show_ground": True,
    "fb_arrow_scale": 1.0,
}

init_session_state(FB_DEFAULTS)


def get_index(options, key):
    val = st.session_state.get(key, options[0])
    try:
        return options.index(val)
    except ValueError:
        return 0


COLOR_OPTIONS = get_color_options()
PRESET_NAMES = list(FREEBODY_PRESETS.keys())


# --- Sidebar ---
with st.sidebar:
    st.header("Appearance")
    
    line_weight = st.slider(
        "Line weight",
        min_value=1.5, max_value=4.0, step=0.5,
        key="fb_line_weight"
    )
    
    label_size = st.slider(
        "Label size",
        min_value=10, max_value=20, step=1,
        key="fb_label_size"
    )
    
    st.write("")
    white_background = st.toggle("White background", key="fb_white_bg")


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
    tab_scenario, tab_style, tab_options = st.tabs(["Scenario", "Style", "Options"])
    
    # === SCENARIO TAB ===
    with tab_scenario:
        st.caption("Select scenario")
        
        # Flat surface scenarios
        st.write("**Flat surface**")
        cols = st.columns(2)
        flat_presets = ['Block on flat surface', 'Block being pushed']
        for i, name in enumerate(flat_presets):
            with cols[i]:
                if st.button(name.replace('Block ', ''), key=f"fb_btn_{name}", 
                            use_container_width=True):
                    st.session_state["fb_preset"] = name
        
        # Inclined plane scenarios
        st.write("**Inclined plane**")
        cols = st.columns(2)
        incline_presets = ['Block on inclined plane', 'Block sliding down']
        for i, name in enumerate(incline_presets):
            with cols[i]:
                if st.button(name.replace('Block ', ''), key=f"fb_btn_{name}",
                            use_container_width=True):
                    st.session_state["fb_preset"] = name
        
        # Other scenarios
        st.write("**Other**")
        cols = st.columns(2)
        other_presets = ['Hanging object', 'Object on two strings', 'Particle (simple)']
        for i, name in enumerate(other_presets):
            with cols[i % 2]:
                if st.button(name, key=f"fb_btn_{name}", use_container_width=True):
                    st.session_state["fb_preset"] = name
        
        st.markdown("---")
        
        current = st.session_state.get("fb_preset", "Block on flat surface")
        preset = FREEBODY_PRESETS.get(current, FREEBODY_PRESETS["Block on flat surface"])
        st.markdown(f"**Selected:** {current}")
        st.caption(preset['description'])
        
        # Show forces
        force_names = [f['name'] for f in preset['forces']]
        st.info(f"Forces: {', '.join(force_names)}")
    
    # === STYLE TAB ===
    with tab_style:
        st.caption("Object color")
        st.selectbox("Object", options=COLOR_OPTIONS,
                    index=get_index(COLOR_OPTIONS, "fb_object_color"),
                    key="fb_object_color")
        
        st.write("")
        st.caption("Force colors")
        
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Weight (W)", options=COLOR_OPTIONS,
                        index=get_index(COLOR_OPTIONS, "fb_weight_color"),
                        key="fb_weight_color")
            st.selectbox("Friction (f)", options=COLOR_OPTIONS,
                        index=get_index(COLOR_OPTIONS, "fb_friction_color"),
                        key="fb_friction_color")
            st.selectbox("Tension (T)", options=COLOR_OPTIONS,
                        index=get_index(COLOR_OPTIONS, "fb_tension_color"),
                        key="fb_tension_color")
        with col2:
            st.selectbox("Normal (N)", options=COLOR_OPTIONS,
                        index=get_index(COLOR_OPTIONS, "fb_normal_color"),
                        key="fb_normal_color")
            st.selectbox("Applied (F)", options=COLOR_OPTIONS,
                        index=get_index(COLOR_OPTIONS, "fb_applied_color"),
                        key="fb_applied_color")
    
    # === OPTIONS TAB ===
    with tab_options:
        st.caption("Display options")
        
        st.checkbox("Show object", key="fb_show_object")
        st.checkbox("Show ground/surface", key="fb_show_ground")
        
        st.slider("Arrow scale", min_value=0.5, max_value=2.0, step=0.1,
                 key="fb_arrow_scale")
        
        st.markdown("---")
        st.caption("Force key")
        st.markdown("""
        - **W** = Weight (mg)
        - **N** = Normal reaction
        - **f** = Friction
        - **F** = Applied force
        - **T** = Tension
        """)


# --- Render ---
def render_freebody():
    preset_name = st.session_state.get("fb_preset", "Block on flat surface")
    preset = FREEBODY_PRESETS.get(preset_name, FREEBODY_PRESETS["Block on flat surface"])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_aspect('equal')
    ax.axis('off')
    
    white_bg = st.session_state.get("fb_white_bg", True)
    apply_figure_style(fig, ax, white_bg)
    bg_color = 'white' if white_bg else 'none'
    
    # Get style settings
    lw = st.session_state.get("fb_line_weight", 2.5)
    fs = st.session_state.get("fb_label_size", 14)
    obj_color = MY_COLORS[st.session_state.get("fb_object_color", "grey")]
    arrow_scale = st.session_state.get("fb_arrow_scale", 1.0)
    show_object = st.session_state.get("fb_show_object", True)
    show_ground = st.session_state.get("fb_show_ground", True)
    
    # Force colors
    force_colors = {
        'weight': MY_COLORS[st.session_state.get("fb_weight_color", "blue")],
        'normal': MY_COLORS[st.session_state.get("fb_normal_color", "green")],
        'friction': MY_COLORS[st.session_state.get("fb_friction_color", "orange")],
        'applied': MY_COLORS[st.session_state.get("fb_applied_color", "red")],
        'tension': MY_COLORS[st.session_state.get("fb_tension_color", "purple")],
    }
    
    diagram_type = preset['type']
    forces = preset['forces']
    
    # Object center position
    center = (0, 0)
    incline_angle = 0
    
    if diagram_type == 'flat':
        if show_ground:
            draw_ground(ax, (-2, 2), y=-0.4, color=obj_color, line_width=lw)
        if show_object:
            draw_block(ax, center, width=1.0, height=0.8, color=obj_color,
                      fill_color=bg_color, line_width=lw)
    
    elif diagram_type == 'incline':
        incline_angle = preset.get('angle', 30)
        
        if show_ground:
            surface = draw_inclined_plane(ax, (-1.5, -1.5), length=3, 
                                         angle_deg=incline_angle, color=obj_color,
                                         line_width=lw, font_size=fs*0.8)
            # Position block on slope
            center = (0, -0.3 + 0.5 * np.tan(np.radians(incline_angle)))
        
        if show_object:
            draw_block(ax, center, width=0.8, height=0.6, angle_deg=incline_angle,
                      color=obj_color, fill_color=bg_color, line_width=lw)
    
    elif diagram_type == 'hanging':
        if show_object:
            draw_block(ax, center, width=0.8, height=0.6, color=obj_color,
                      fill_color=bg_color, line_width=lw)
        # Draw string
        if show_ground:
            ax.plot([0, 0], [0.3, 1.5], color=obj_color, linewidth=lw, zorder=5)
            ax.plot([-0.3, 0.3], [1.5, 1.5], color=obj_color, linewidth=lw*1.5, zorder=5)
    
    elif diagram_type == 'two_strings':
        if show_object:
            draw_particle(ax, center, radius=0.15, color=obj_color)
        # Draw strings
        if show_ground:
            ax.plot([0, -1.2], [0, 1.2], color=obj_color, linewidth=lw, zorder=5)
            ax.plot([0, 1.2], [0, 1.2], color=obj_color, linewidth=lw, zorder=5)
    
    elif diagram_type == 'particle':
        if show_object:
            draw_particle(ax, center, radius=0.15, color=obj_color)
        if show_ground:
            draw_ground(ax, (-1.5, 1.5), y=-0.15, color=obj_color, line_width=lw)
    
    # Draw forces
    for force in forces:
        name = force['name']
        color = force_colors.get(force['color_key'], obj_color)
        mag = force['mag'] * arrow_scale
        
        # Handle special angle keywords
        angle = force['angle']
        if angle == 'normal':
            angle = 90 + incline_angle
        elif angle == 'up_slope':
            angle = 180 + incline_angle
        elif angle == 'down_slope':
            angle = incline_angle
        
        draw_force_arrow(ax, center, mag, angle, color=color,
                        line_width=lw, label=name, font_size=fs)
    
    auto_set_limits_freebody(ax)
    fig.tight_layout()
    return fig


# --- Main ---
try:
    fig = render_freebody()
    
    if fig is not None:
        plot_placeholder.pyplot(fig)
        
        preset = st.session_state.get("fb_preset", "block")
        filename = f"freebody_{preset.lower().replace(' ', '_')}"
        
        create_download_buttons(fig, svg_placeholder, png_placeholder, filename)
        plt.close(fig)
except Exception as e:
    st.error(f"Error rendering: {e}")
    import traceback
    st.code(traceback.format_exc())

