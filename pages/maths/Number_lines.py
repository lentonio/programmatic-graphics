"""
Number Line Diagrams Page
Creates educational number line diagrams with points, intervals, and labels.
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
from number_line_utils import (
    draw_number_line,
    draw_tick_marks,
    draw_minor_ticks,
    draw_tick_labels,
    draw_point,
    draw_point_label,
    draw_interval,
    draw_interval_fill,
    auto_set_limits
)


# --- Initialize Session State Defaults ---
NL_DEFAULTS = {
    # Sidebar
    "nl_axis_weight": 3.0,
    "nl_label_size": 18,
    "nl_white_bg": DEFAULT_WHITE_BG,
    # Definition
    "nl_min": -5.0,
    "nl_max": 5.0,
    "nl_arrows": True,
    # Style
    "nl_color": "grey",
    "nl_line_style": "solid",
    # Ticks
    "nl_show_ticks": True,
    "nl_major_step": 1.0,
    "nl_tick_len": 0.3,
    "nl_show_labels": True,
    "nl_label_format": "auto",
    "nl_show_minor": False,
    "nl_minor_div": 2,
}
# Add point defaults
for i in range(5):
    NL_DEFAULTS[f"nl_show_pt_{i}"] = False
    NL_DEFAULTS[f"nl_pt_val_{i}"] = float(i)
    NL_DEFAULTS[f"nl_pt_style_{i}"] = "filled"
    NL_DEFAULTS[f"nl_pt_color_{i}"] = "blue"
    NL_DEFAULTS[f"nl_pt_label_{i}"] = ""
    NL_DEFAULTS[f"nl_pt_label_pos_{i}"] = "above"
# Add interval defaults
for i in range(3):
    NL_DEFAULTS[f"nl_show_int_{i}"] = False
    NL_DEFAULTS[f"nl_int_start_{i}"] = -2.0 + i
    NL_DEFAULTS[f"nl_int_end_{i}"] = 2.0 + i
    NL_DEFAULTS[f"nl_int_color_{i}"] = "blue"
    NL_DEFAULTS[f"nl_int_start_style_{i}"] = "closed"
    NL_DEFAULTS[f"nl_int_end_style_{i}"] = "closed"
    NL_DEFAULTS[f"nl_int_fill_{i}"] = True

init_session_state(NL_DEFAULTS)


# Helper to get selectbox index from session state value
def get_index(options, key):
    """Get the index of the current session state value in options list."""
    val = st.session_state.get(key, options[0])
    try:
        return options.index(val)
    except ValueError:
        return 0


COLOR_OPTIONS = get_color_options()


# --- Sidebar: Appearance Settings ---
with st.sidebar:
    st.header("Appearance")
    
    axis_weight = st.slider(
        "Line weight",
        min_value=1.5, max_value=4.0, step=0.5,
        key="nl_axis_weight"
    )
    
    label_size = st.slider(
        "Label size",
        min_value=12, max_value=30, step=1,
        key="nl_label_size"
    )
    
    st.write("")
    white_background = st.toggle("White background", key="nl_white_bg")


# Fixed figure size
fig_width = 12
fig_height = 3


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
    tab_def, tab_style, tab_ticks, tab_points, tab_intervals = st.tabs([
        "Definition",
        "Style",
        "Ticks & Labels",
        "Points",
        "Intervals"
    ])
    
    # === DEFINITION TAB ===
    with tab_def:
        st.caption("Number line range")
        range_cols = st.columns(2)
        with range_cols[0]:
            min_val = st.number_input("Minimum", step=1.0, key="nl_min")
        with range_cols[1]:
            max_val = st.number_input("Maximum", step=1.0, key="nl_max")
        
        # Validate range
        if min_val >= max_val:
            st.error("Minimum must be less than maximum")
            max_val = min_val + 1
        
        st.write("")
        show_arrows = st.checkbox("Show arrows at endpoints", key="nl_arrows")
    
    # === STYLE TAB ===
    with tab_style:
        style_cols = st.columns(2)
        with style_cols[0]:
            nl_color = st.selectbox("Line color", options=COLOR_OPTIONS, 
                                    index=get_index(COLOR_OPTIONS, "nl_color"), key="nl_color")
        with style_cols[1]:
            style_options = ["solid", "dashed"]
            nl_line_style = st.selectbox("Line style", style_options,
                                         index=get_index(style_options, "nl_line_style"), key="nl_line_style")
    
    # === TICKS & LABELS TAB ===
    with tab_ticks:
        st.caption("Major ticks")
        tick_cols = st.columns(2)
        with tick_cols[0]:
            show_ticks = st.checkbox("Show major ticks", key="nl_show_ticks")
        with tick_cols[1]:
            if show_ticks:
                major_step = st.number_input("Step", min_value=0.1, step=0.5, key="nl_major_step")
        
        if show_ticks:
            tick_cols2 = st.columns(2)
            with tick_cols2[0]:
                tick_length = st.number_input("Tick length", min_value=0.1, step=0.1, key="nl_tick_len")
            with tick_cols2[1]:
                show_labels = st.checkbox("Show labels", key="nl_show_labels")
            
            if show_labels:
                format_options = ["auto", "integer", "decimal", "fraction"]
                label_format = st.selectbox("Label format", format_options,
                                           index=get_index(format_options, "nl_label_format"), key="nl_label_format")
        
        st.markdown("---")
        
        st.caption("Minor ticks")
        minor_cols = st.columns(2)
        with minor_cols[0]:
            show_minor = st.checkbox("Show minor ticks", key="nl_show_minor")
        with minor_cols[1]:
            if show_minor:
                minor_divisions = st.number_input("Divisions", min_value=2, max_value=10, key="nl_minor_div")
    
    # === POINTS TAB ===
    with tab_points:
        st.caption("Points on number line (up to 5)")
        for i in range(5):
            with st.expander(f"Point {i+1}", expanded=(i == 0)):
                p_cols = st.columns([1, 2, 1, 1])
                with p_cols[0]:
                    show_pt = st.checkbox("Show", key=f"nl_show_pt_{i}")
                with p_cols[1]:
                    pt_value = st.number_input("Value", step=0.5, key=f"nl_pt_val_{i}")
                with p_cols[2]:
                    pt_style_opts = ["filled", "open"]
                    pt_style = st.selectbox("Style", pt_style_opts,
                                           index=get_index(pt_style_opts, f"nl_pt_style_{i}"), 
                                           key=f"nl_pt_style_{i}")
                with p_cols[3]:
                    pt_color = st.selectbox("Color", options=COLOR_OPTIONS,
                                           index=get_index(COLOR_OPTIONS, f"nl_pt_color_{i}"),
                                           key=f"nl_pt_color_{i}")
                
                if show_pt:
                    pt_label_cols = st.columns([2, 1])
                    with pt_label_cols[0]:
                        pt_label = st.text_input("Label", key=f"nl_pt_label_{i}", placeholder="e.g. $a$")
                    with pt_label_cols[1]:
                        label_pos_opts = ["above", "below"]
                        pt_label_pos = st.selectbox("Position", label_pos_opts,
                                                   index=get_index(label_pos_opts, f"nl_pt_label_pos_{i}"),
                                                   key=f"nl_pt_label_pos_{i}")
    
    # === INTERVALS TAB ===
    with tab_intervals:
        st.caption("Intervals (up to 3)")
        for i in range(3):
            with st.expander(f"Interval {i+1}", expanded=(i == 0)):
                int_cols = st.columns([1, 1, 1, 1])
                with int_cols[0]:
                    show_int = st.checkbox("Show", key=f"nl_show_int_{i}")
                with int_cols[1]:
                    int_start = st.number_input("Start", step=0.5, key=f"nl_int_start_{i}")
                with int_cols[2]:
                    int_end = st.number_input("End", step=0.5, key=f"nl_int_end_{i}")
                with int_cols[3]:
                    int_color = st.selectbox("Color", options=COLOR_OPTIONS,
                                            index=get_index(COLOR_OPTIONS, f"nl_int_color_{i}"),
                                            key=f"nl_int_color_{i}")
                
                if show_int:
                    int_cols2 = st.columns([1, 1, 1])
                    endpoint_opts = ["closed", "open", "arrow"]
                    with int_cols2[0]:
                        int_start_style = st.selectbox(
                            "Start", endpoint_opts,
                            index=get_index(endpoint_opts, f"nl_int_start_style_{i}"),
                            key=f"nl_int_start_style_{i}",
                            help="closed = [, open = (, arrow = extends to -∞"
                        )
                    with int_cols2[1]:
                        int_end_style = st.selectbox(
                            "End", endpoint_opts,
                            index=get_index(endpoint_opts, f"nl_int_end_style_{i}"),
                            key=f"nl_int_end_style_{i}",
                            help="closed = ], open = ), arrow = extends to +∞"
                        )
                    with int_cols2[2]:
                        int_fill = st.checkbox("Fill", key=f"nl_int_fill_{i}")
        
        st.caption("Use 'closed' for [ or ], 'open' for ( or ), 'arrow' for infinite extent.")


# --- Render Number Line ---
def render_number_line():
    """Render the number line with all configured options."""
    
    # Create figure
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_aspect('auto')
    ax.axis('off')
    
    # Set limits
    auto_set_limits(ax, min_val, max_val)
    
    # Apply background
    apply_figure_style(fig, ax, white_background)
    
    line_width = axis_weight * 1.3
    line_style_map = {"solid": "-", "dashed": "--"}
    
    # --- Draw interval fills first (behind everything) ---
    for i in range(3):
        if st.session_state.get(f"nl_show_int_{i}", False):
            i_start = st.session_state.get(f"nl_int_start_{i}", -2)
            i_end = st.session_state.get(f"nl_int_end_{i}", 2)
            i_color = st.session_state.get(f"nl_int_color_{i}", "blue")
            i_fill = st.session_state.get(f"nl_int_fill_{i}", True)
            
            if i_fill:
                draw_interval_fill(ax, i_start, i_end, 
                                  color=MY_COLORS[i_color], alpha=0.2, zorder=2)
    
    # --- Draw main number line ---
    draw_number_line(
        ax, min_val, max_val,
        color=MY_COLORS[nl_color],
        line_width=line_width,
        show_arrows=show_arrows,
        zorder=10
    )
    
    # --- Draw ticks ---
    ticks = []
    if show_ticks:
        ticks = draw_tick_marks(
            ax, min_val, max_val, major_step,
            color=MY_COLORS[nl_color],
            line_width=line_width,
            tick_length=tick_length,
            zorder=15
        )
        
        # Minor ticks
        if show_minor:
            draw_minor_ticks(
                ax, min_val, max_val, major_step, minor_divisions,
                color=MY_COLORS[nl_color],
                line_width=line_width * 0.7,
                tick_length=tick_length * 0.5,
                zorder=14
            )
        
        # Labels
        if show_labels:
            draw_tick_labels(
                ax, ticks,
                color=MY_COLORS[nl_color],
                font_size=label_size,
                format_type=label_format,
                offset=tick_length + 0.2,
                white_background=white_background,
                zorder=100
            )
    
    # --- Draw intervals ---
    for i in range(3):
        if st.session_state.get(f"nl_show_int_{i}", False):
            i_start = st.session_state.get(f"nl_int_start_{i}", -2)
            i_end = st.session_state.get(f"nl_int_end_{i}", 2)
            i_color = st.session_state.get(f"nl_int_color_{i}", "blue")
            i_start_style = st.session_state.get(f"nl_int_start_style_{i}", "closed")
            i_end_style = st.session_state.get(f"nl_int_end_style_{i}", "closed")
            
            draw_interval(
                ax, i_start, i_end,
                color=MY_COLORS[i_color],
                line_width=line_width,
                start_style=i_start_style,
                end_style=i_end_style,
                interval_offset=0.2,
                zorder=20
            )
    
    # --- Draw points ---
    for i in range(5):
        if st.session_state.get(f"nl_show_pt_{i}", False):
            p_val = st.session_state.get(f"nl_pt_val_{i}", 0)
            p_style = st.session_state.get(f"nl_pt_style_{i}", "filled")
            p_color = st.session_state.get(f"nl_pt_color_{i}", "blue")
            p_label = st.session_state.get(f"nl_pt_label_{i}", "")
            p_label_pos = st.session_state.get(f"nl_pt_label_pos_{i}", "above")
            
            draw_point(
                ax, p_val,
                color=MY_COLORS[p_color],
                marker_size=axis_weight * 4,
                marker_style=p_style,
                zorder=25
            )
            
            if p_label:
                draw_point_label(
                    ax, p_val, p_label,
                    color=MY_COLORS[p_color],
                    font_size=label_size,
                    offset=0.4,
                    direction=p_label_pos,
                    white_background=white_background,
                    zorder=100
                )
    
    fig.tight_layout()
    return fig


# --- Main Rendering Logic ---
fig = render_number_line()

# Display
plot_placeholder.pyplot(fig)

# Download buttons
create_download_buttons(fig, svg_placeholder, png_placeholder, "number_line")

# Show info at bottom of controls
with col_controls:
    range_size = max_val - min_val
    st.caption(f"**Range:** {min_val} to {max_val} · **Size:** {range_size}")

plt.close(fig)
