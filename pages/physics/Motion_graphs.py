"""
Motion Graphs Page
Distance-time, velocity-time, and acceleration-time graphs for kinematics.
"""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from shared_utils import (
    MY_COLORS,
    AXIS_COLOR,
    get_color_options,
    create_download_buttons,
    apply_figure_style,
    init_session_state,
    DEFAULT_WHITE_BG
)


# --- Session State Version Check ---
MG_VERSION = 1
if st.session_state.get("mg_version", 0) < MG_VERSION:
    for key in list(st.session_state.keys()):
        if key.startswith("mg_"):
            del st.session_state[key]
    st.session_state["mg_version"] = MG_VERSION

# --- Initialize Session State Defaults ---
MG_DEFAULTS = {
    # Sidebar
    "mg_line_weight": 2.5,
    "mg_label_size": 14,
    "mg_white_bg": DEFAULT_WHITE_BG,
    # Graph type
    "mg_graph_type": "Distance-time",
    "mg_preset": "Constant speed",
    # Style
    "mg_line_color": "blue",
    "mg_show_grid": True,
    "mg_show_values": True,
}

init_session_state(MG_DEFAULTS)


def get_index(options, key):
    val = st.session_state.get(key, options[0])
    try:
        return options.index(val)
    except ValueError:
        return 0


COLOR_OPTIONS = get_color_options()


# Motion presets for each graph type
MOTION_PRESETS = {
    'Distance-time': {
        'Constant speed': {
            'segments': [(0, 0, 5, 10)],  # (t1, d1, t2, d2)
            'description': 'Object moving at constant speed',
            'y_label': 'Distance (m)',
        },
        'Stationary then moving': {
            'segments': [(0, 0, 2, 0), (2, 0, 5, 9)],
            'description': 'Object at rest, then moves at constant speed',
            'y_label': 'Distance (m)',
        },
        'Moving then stationary': {
            'segments': [(0, 0, 3, 6), (3, 6, 5, 6)],
            'description': 'Object moves, then stops',
            'y_label': 'Distance (m)',
        },
        'Changing speed': {
            'segments': [(0, 0, 2, 2), (2, 2, 4, 8), (4, 8, 5, 9)],
            'description': 'Object changes speed (slow, fast, slow)',
            'y_label': 'Distance (m)',
        },
        'Accelerating': {
            'type': 'curve',
            'func': lambda t: 0.4 * t**2,
            't_range': (0, 5),
            'description': 'Object accelerating uniformly',
            'y_label': 'Distance (m)',
        },
    },
    'Velocity-time': {
        'Constant velocity': {
            'segments': [(0, 4, 5, 4)],
            'description': 'Object moving at constant velocity',
            'y_label': 'Velocity (m/s)',
        },
        'Uniform acceleration': {
            'segments': [(0, 0, 5, 10)],
            'description': 'Object accelerating uniformly from rest',
            'y_label': 'Velocity (m/s)',
        },
        'Accelerate then constant': {
            'segments': [(0, 0, 2, 6), (2, 6, 5, 6)],
            'description': 'Object accelerates then maintains speed',
            'y_label': 'Velocity (m/s)',
        },
        'Accelerate then decelerate': {
            'segments': [(0, 0, 2.5, 8), (2.5, 8, 5, 0)],
            'description': 'Object speeds up then slows down',
            'y_label': 'Velocity (m/s)',
        },
        'Deceleration to rest': {
            'segments': [(0, 10, 4, 0), (4, 0, 5, 0)],
            'description': 'Object decelerating to rest',
            'y_label': 'Velocity (m/s)',
        },
        'Freefall (dropped)': {
            'segments': [(0, 0, 3, 30)],
            'description': 'Object in freefall (g ≈ 10 m/s²)',
            'y_label': 'Velocity (m/s)',
        },
    },
    'Acceleration-time': {
        'Constant acceleration': {
            'segments': [(0, 2, 5, 2)],
            'description': 'Object with constant acceleration',
            'y_label': 'Acceleration (m/s²)',
        },
        'No acceleration': {
            'segments': [(0, 0, 5, 0)],
            'description': 'Object moving at constant velocity (a=0)',
            'y_label': 'Acceleration (m/s²)',
        },
        'Freefall': {
            'segments': [(0, 10, 5, 10)],
            'description': 'Object in freefall (g ≈ 10 m/s²)',
            'y_label': 'Acceleration (m/s²)',
        },
        'Changing acceleration': {
            'segments': [(0, 4, 2, 4), (2, 0, 4, 0), (4, -2, 5, -2)],
            'description': 'Accelerate, coast, decelerate',
            'y_label': 'Acceleration (m/s²)',
        },
    },
}


# --- Sidebar ---
with st.sidebar:
    st.header("Appearance")
    
    line_weight = st.slider(
        "Line weight",
        min_value=1.5, max_value=4.0, step=0.5,
        key="mg_line_weight"
    )
    
    label_size = st.slider(
        "Label size",
        min_value=10, max_value=20, step=1,
        key="mg_label_size"
    )
    
    st.write("")
    white_background = st.toggle("White background", key="mg_white_bg")


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
    tab_motion, tab_style, tab_info = st.tabs(["Motion", "Style", "Info"])
    
    # === MOTION TAB ===
    with tab_motion:
        graph_type = st.radio(
            "Graph type:",
            ["Distance-time", "Velocity-time", "Acceleration-time"],
            horizontal=True,
            key="mg_graph_type"
        )
        
        st.write("")
        st.caption("Select motion pattern")
        
        presets = MOTION_PRESETS.get(graph_type, {})
        preset_names = list(presets.keys())
        
        cols = st.columns(2)
        for i, name in enumerate(preset_names):
            with cols[i % 2]:
                if st.button(name, key=f"mg_btn_{graph_type}_{name}", 
                            use_container_width=True):
                    st.session_state["mg_preset"] = name
        
        st.markdown("---")
        
        current_preset = st.session_state.get("mg_preset", preset_names[0] if preset_names else "")
        if current_preset in presets:
            st.markdown(f"**Selected:** {current_preset}")
            st.caption(presets[current_preset]['description'])
    
    # === STYLE TAB ===
    with tab_style:
        st.caption("Colors")
        st.selectbox("Line color", options=COLOR_OPTIONS,
                    index=get_index(COLOR_OPTIONS, "mg_line_color"),
                    key="mg_line_color")
        
        st.write("")
        st.caption("Display")
        st.checkbox("Show grid", key="mg_show_grid")
        st.checkbox("Show axis values", key="mg_show_values")
    
    # === INFO TAB ===
    with tab_info:
        st.caption("Interpreting motion graphs")
        
        graph_type = st.session_state.get("mg_graph_type", "Distance-time")
        
        if graph_type == "Distance-time":
            st.markdown("""
            **Distance-time graphs:**
            - Gradient = speed
            - Steeper = faster
            - Horizontal = stationary
            - Curved = accelerating
            """)
        elif graph_type == "Velocity-time":
            st.markdown("""
            **Velocity-time graphs:**
            - Gradient = acceleration
            - Area under graph = distance
            - Horizontal = constant velocity
            - Positive slope = accelerating
            - Negative slope = decelerating
            """)
        else:
            st.markdown("""
            **Acceleration-time graphs:**
            - Positive = speeding up
            - Negative = slowing down
            - Zero = constant velocity
            - Area = change in velocity
            """)


# --- Render ---
def render_motion_graph():
    graph_type = st.session_state.get("mg_graph_type", "Distance-time")
    preset_name = st.session_state.get("mg_preset", "Constant speed")
    
    presets = MOTION_PRESETS.get(graph_type, {})
    if preset_name not in presets:
        preset_name = list(presets.keys())[0] if presets else None
    
    if not preset_name:
        return None
    
    preset = presets[preset_name]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    white_bg = st.session_state.get("mg_white_bg", True)
    apply_figure_style(fig, ax, white_bg)
    
    # Get style settings
    lw = st.session_state.get("mg_line_weight", 2.5)
    fs = st.session_state.get("mg_label_size", 14)
    line_color = MY_COLORS[st.session_state.get("mg_line_color", "blue")]
    show_grid = st.session_state.get("mg_show_grid", True)
    show_values = st.session_state.get("mg_show_values", True)
    
    axis_color = AXIS_COLOR  # Consistent dark grey like function graphs
    
    # Plot data
    if preset.get('type') == 'curve':
        # Curved line (e.g., accelerating distance-time)
        t_range = preset['t_range']
        t = np.linspace(t_range[0], t_range[1], 100)
        y = preset['func'](t)
        ax.plot(t, y, color=line_color, linewidth=lw)
        t_max, y_max = t_range[1], max(y)
    else:
        # Piecewise linear segments
        segments = preset['segments']
        for seg in segments:
            t1, y1, t2, y2 = seg
            ax.plot([t1, t2], [y1, y2], color=line_color, linewidth=lw)
        
        # Calculate axis limits
        all_t = [s[0] for s in segments] + [s[2] for s in segments]
        all_y = [s[1] for s in segments] + [s[3] for s in segments]
        t_max = max(all_t)
        y_max = max(all_y)
        y_min = min(all_y)
    
    # Configure axes
    ax.set_xlabel("Time (s)", fontsize=fs, color=axis_color)
    ax.set_ylabel(preset.get('y_label', 'Value'), fontsize=fs, color=axis_color)
    
    # Set limits with padding
    ax.set_xlim(0, t_max * 1.1)
    
    if preset.get('type') != 'curve':
        if y_min < 0:
            ax.set_ylim(y_min * 1.2, y_max * 1.2)
        else:
            ax.set_ylim(0, y_max * 1.2 if y_max > 0 else 1)
    else:
        ax.set_ylim(0, y_max * 1.2)
    
    # Grid
    if show_grid:
        ax.grid(True, alpha=0.3, color=axis_color)
    
    # Axis styling
    ax.tick_params(colors=axis_color, labelsize=fs*0.8)
    for spine in ax.spines.values():
        spine.set_color(axis_color)
    
    if not show_values:
        ax.set_xticklabels([])
        ax.set_yticklabels([])
    
    # Add origin marker
    ax.axhline(y=0, color=axis_color, linewidth=0.5, alpha=0.5)
    ax.axvline(x=0, color=axis_color, linewidth=0.5, alpha=0.5)
    
    fig.tight_layout()
    return fig


# --- Main ---
try:
    fig = render_motion_graph()
    
    if fig is not None:
        plot_placeholder.pyplot(fig)
        
        graph_type = st.session_state.get("mg_graph_type", "distance")
        preset = st.session_state.get("mg_preset", "motion")
        filename = f"motion_{graph_type.lower().replace('-', '_')}_{preset.lower().replace(' ', '_')}"
        
        create_download_buttons(fig, svg_placeholder, png_placeholder, filename)
        plt.close(fig)
except Exception as e:
    st.error(f"Error rendering: {e}")
    import traceback
    st.code(traceback.format_exc())

