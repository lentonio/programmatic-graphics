"""
Quadrilateral Diagrams Page
Creates educational quadrilateral diagrams with labeled vertices, sides, angles, and markers.
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
from quadrilateral_utils import (
    get_quadrilateral_vertices_from_coordinates,
    get_centroid,
    get_square,
    get_rectangle,
    get_parallelogram,
    get_rhombus,
    get_trapezium,
    get_kite,
    get_isosceles_trapezium,
    draw_quadrilateral,
    draw_vertex_label,
    draw_side_label,
    draw_angle_arc,
    draw_right_angle_marker,
    draw_angle_label,
    draw_tick_marks,
    draw_parallel_marks,
    draw_diagonal,
    get_vertex_angle,
    get_side_length,
    auto_set_limits
)


# --- Initialize Session State Defaults ---
QUAD_DEFAULTS = {
    # Sidebar
    "quad_axis_weight": 3.0,
    "quad_label_size": 20,
    "quad_padding": 1.0,
    "quad_white_bg": DEFAULT_WHITE_BG,
    # Definition
    "quad_input_method": "Preset shapes",
    "quad_preset_type": "Square",
    "quad_preset_rotation": 0.0,
    # Square
    "quad_square_side": 4.0,
    # Rectangle
    "quad_rect_width": 5.0,
    "quad_rect_height": 3.0,
    # Parallelogram
    "quad_para_base": 5.0,
    "quad_para_side": 3.0,
    "quad_para_angle": 60.0,
    # Rhombus
    "quad_rhombus_side": 4.0,
    "quad_rhombus_angle": 60.0,
    # Trapezium
    "quad_trap_top": 3.0,
    "quad_trap_bottom": 5.0,
    "quad_trap_height": 3.0,
    "quad_trap_offset": 0.0,
    # Kite
    "quad_kite_d1": 4.0,
    "quad_kite_d2": 6.0,
    "quad_kite_split": 0.3,
    # Coordinates
    "quad_ax": -2.0, "quad_ay": 0.0,
    "quad_bx": 2.0, "quad_by": 0.0,
    "quad_cx": 3.0, "quad_cy": 3.0,
    "quad_dx": -1.0, "quad_dy": 3.0,
    # Style
    "quad_color": "grey",
    "quad_line_style": "solid",
    "quad_fill": False,
    "quad_fill_color": "blue",
    "quad_fill_alpha": 0.2,
    # Vertices
    "quad_show_vlabels": True,
    "quad_vlabel_a": "$A$", "quad_vlabel_b": "$B$", 
    "quad_vlabel_c": "$C$", "quad_vlabel_d": "$D$",
    "quad_vlabel_dist": 0.5,
    # Sides
    "quad_show_slabels": False,
    # Angles
    "quad_show_angles": False,
    "quad_angle_a": True, "quad_angle_b": True, 
    "quad_angle_c": True, "quad_angle_d": True,
    "quad_angle_radius": 0.5,
    "quad_right_a": False, "quad_right_b": False,
    "quad_right_c": False, "quad_right_d": False,
    "quad_right_size": 0.4,
    "quad_alabel_a": "", "quad_alabel_b": "",
    "quad_alabel_c": "", "quad_alabel_d": "",
    "quad_alabel_dist": 0.3,
    # Ticks & Parallels
    "quad_show_ticks": False,
    "quad_ticks_ab": 0, "quad_ticks_bc": 0,
    "quad_ticks_cd": 0, "quad_ticks_da": 0,
    "quad_tick_length": 0.25,
    "quad_show_parallel": False,
    "quad_parallel_ab": 0, "quad_parallel_bc": 0,
    "quad_parallel_cd": 0, "quad_parallel_da": 0,
    # Diagonals
    "quad_show_diag_ac": False,
    "quad_show_diag_bd": False,
    "quad_diag_label_ac": "",
    "quad_diag_label_bd": "",
}
# Side labels
for i in range(4):
    QUAD_DEFAULTS[f"quad_slabel_{i}"] = ""
    QUAD_DEFAULTS[f"quad_slabel_pos_{i}"] = 0.5
    QUAD_DEFAULTS[f"quad_slabel_dir_{i}"] = "auto"
    QUAD_DEFAULTS[f"quad_slabel_dist_{i}"] = 0.4

init_session_state(QUAD_DEFAULTS)


# Helper to get selectbox index
def get_index(options, key):
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
        key="quad_axis_weight"
    )
    
    label_size = st.slider(
        "Label size",
        min_value=12, max_value=30, step=1,
        key="quad_label_size"
    )
    
    padding = st.slider(
        "Padding",
        min_value=0.5, max_value=3.0, step=0.25,
        key="quad_padding"
    )
    
    st.write("")
    white_background = st.toggle("White background", key="quad_white_bg")


# Fixed figure size
fig_height = 8
fig_width = 8


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
    tab_def, tab_style, tab_vertices, tab_sides, tab_angles, tab_marks, tab_diag = st.tabs([
        "Definition",
        "Style",
        "Vertices",
        "Sides",
        "Angles",
        "Marks",
        "Diagonals"
    ])
    
    # === DEFINITION TAB ===
    with tab_def:
        input_method = st.radio(
            "Define quadrilateral by:",
            ["Preset shapes", "Coordinates"],
            horizontal=True,
            key="quad_input_method"
        )
        
        st.write("")
        
        if input_method == "Preset shapes":
            preset_opts = ["Square", "Rectangle", "Parallelogram", "Rhombus", 
                          "Trapezium", "Isosceles trapezium", "Kite"]
            preset_cols = st.columns([2, 1])
            with preset_cols[0]:
                preset_type = st.selectbox(
                    "Shape type", preset_opts,
                    index=get_index(preset_opts, "quad_preset_type"),
                    key="quad_preset_type"
                )
            with preset_cols[1]:
                preset_rotation = st.number_input("Rotation (°)", step=15.0, key="quad_preset_rotation")
            
            st.write("")
            
            if preset_type == "Square":
                square_side = st.number_input("Side length", min_value=0.1, step=0.5, key="quad_square_side")
            
            elif preset_type == "Rectangle":
                rect_cols = st.columns(2)
                with rect_cols[0]:
                    rect_width = st.number_input("Width", min_value=0.1, step=0.5, key="quad_rect_width")
                with rect_cols[1]:
                    rect_height = st.number_input("Height", min_value=0.1, step=0.5, key="quad_rect_height")
            
            elif preset_type == "Parallelogram":
                para_cols = st.columns(3)
                with para_cols[0]:
                    para_base = st.number_input("Base", min_value=0.1, step=0.5, key="quad_para_base")
                with para_cols[1]:
                    para_side = st.number_input("Side", min_value=0.1, step=0.5, key="quad_para_side")
                with para_cols[2]:
                    para_angle = st.number_input("Angle (°)", min_value=1.0, max_value=179.0, step=5.0, key="quad_para_angle")
            
            elif preset_type == "Rhombus":
                rhombus_cols = st.columns(2)
                with rhombus_cols[0]:
                    rhombus_side = st.number_input("Side", min_value=0.1, step=0.5, key="quad_rhombus_side")
                with rhombus_cols[1]:
                    rhombus_angle = st.number_input("Angle (°)", min_value=1.0, max_value=179.0, step=5.0, key="quad_rhombus_angle")
            
            elif preset_type == "Trapezium":
                trap_cols = st.columns(2)
                with trap_cols[0]:
                    trap_top = st.number_input("Top (parallel)", min_value=0.1, step=0.5, key="quad_trap_top")
                    trap_height = st.number_input("Height", min_value=0.1, step=0.5, key="quad_trap_height")
                with trap_cols[1]:
                    trap_bottom = st.number_input("Bottom (parallel)", min_value=0.1, step=0.5, key="quad_trap_bottom")
                    trap_offset = st.number_input("Top offset", step=0.5, key="quad_trap_offset", 
                                                  help="Horizontal shift of top side")
            
            elif preset_type == "Isosceles trapezium":
                iso_trap_cols = st.columns(3)
                with iso_trap_cols[0]:
                    trap_top = st.number_input("Top", min_value=0.1, step=0.5, key="quad_trap_top")
                with iso_trap_cols[1]:
                    trap_bottom = st.number_input("Bottom", min_value=0.1, step=0.5, key="quad_trap_bottom")
                with iso_trap_cols[2]:
                    trap_height = st.number_input("Height", min_value=0.1, step=0.5, key="quad_trap_height")
            
            elif preset_type == "Kite":
                kite_cols = st.columns(3)
                with kite_cols[0]:
                    kite_d1 = st.number_input("Width", min_value=0.1, step=0.5, key="quad_kite_d1",
                                             help="Horizontal diagonal")
                with kite_cols[1]:
                    kite_d2 = st.number_input("Height", min_value=0.1, step=0.5, key="quad_kite_d2",
                                             help="Vertical diagonal")
                with kite_cols[2]:
                    kite_split = st.slider("Split", min_value=0.1, max_value=0.9, step=0.1, key="quad_kite_split",
                                          help="Where diagonals cross")
        
        else:  # Coordinates
            coord_cols = st.columns(2)
            with coord_cols[0]:
                st.caption("Vertex A")
                ax_coord = st.number_input("$x_A$", step=0.5, key="quad_ax")
                ay_coord = st.number_input("$y_A$", step=0.5, key="quad_ay")
                st.caption("Vertex C")
                cx_coord = st.number_input("$x_C$", step=0.5, key="quad_cx")
                cy_coord = st.number_input("$y_C$", step=0.5, key="quad_cy")
            with coord_cols[1]:
                st.caption("Vertex B")
                bx_coord = st.number_input("$x_B$", step=0.5, key="quad_bx")
                by_coord = st.number_input("$y_B$", step=0.5, key="quad_by")
                st.caption("Vertex D")
                dx_coord = st.number_input("$x_D$", step=0.5, key="quad_dx")
                dy_coord = st.number_input("$y_D$", step=0.5, key="quad_dy")
    
    # === STYLE TAB ===
    with tab_style:
        style_cols = st.columns(3)
        line_style_opts = ["solid", "dashed", "dotted"]
        with style_cols[0]:
            quad_color = st.selectbox("Color", options=COLOR_OPTIONS,
                                      index=get_index(COLOR_OPTIONS, "quad_color"), key="quad_color")
        with style_cols[1]:
            quad_line_style = st.selectbox("Line style", line_style_opts,
                                           index=get_index(line_style_opts, "quad_line_style"), key="quad_line_style")
        with style_cols[2]:
            quad_fill = st.checkbox("Fill shape", key="quad_fill")
        
        if quad_fill:
            fill_cols = st.columns(2)
            with fill_cols[0]:
                quad_fill_color = st.selectbox("Fill color", options=COLOR_OPTIONS,
                                               index=get_index(COLOR_OPTIONS, "quad_fill_color"), key="quad_fill_color")
            with fill_cols[1]:
                quad_fill_alpha = st.slider("Fill opacity", 0.0, 1.0, key="quad_fill_alpha")
        else:
            quad_fill_color = quad_color
            quad_fill_alpha = 0.2
    
    # === VERTICES TAB ===
    with tab_vertices:
        show_vertex_labels = st.checkbox("Show vertex labels", key="quad_show_vlabels")
        
        if show_vertex_labels:
            st.write("")
            vlabel_cols = st.columns(4)
            with vlabel_cols[0]:
                vertex_a_label = st.text_input("A", key="quad_vlabel_a")
            with vlabel_cols[1]:
                vertex_b_label = st.text_input("B", key="quad_vlabel_b")
            with vlabel_cols[2]:
                vertex_c_label = st.text_input("C", key="quad_vlabel_c")
            with vlabel_cols[3]:
                vertex_d_label = st.text_input("D", key="quad_vlabel_d")
            
            vertex_label_dist = st.number_input("Distance from vertex", min_value=0.1, step=0.1, key="quad_vlabel_dist")
    
    # === SIDES TAB ===
    with tab_sides:
        show_side_labels = st.checkbox("Show side labels", key="quad_show_slabels")
        
        if show_side_labels:
            side_names = ["Side AB", "Side BC", "Side CD", "Side DA"]
            dir_opts = ["auto", "above", "below", "left", "right"]
            for side_idx, side_name in enumerate(side_names):
                with st.expander(f"{side_name}", expanded=(side_idx == 0)):
                    sl_cols = st.columns([2, 1, 1, 1])
                    with sl_cols[0]:
                        st.text_input("Label", key=f"quad_slabel_{side_idx}", placeholder="e.g. $5$")
                    with sl_cols[1]:
                        st.slider("Position", 0.0, 1.0, key=f"quad_slabel_pos_{side_idx}")
                    with sl_cols[2]:
                        st.selectbox("Direction", dir_opts,
                                    index=get_index(dir_opts, f"quad_slabel_dir_{side_idx}"),
                                    key=f"quad_slabel_dir_{side_idx}")
                    with sl_cols[3]:
                        st.number_input("Dist", min_value=0.0, step=0.1, key=f"quad_slabel_dist_{side_idx}")
    
    # === ANGLES TAB ===
    with tab_angles:
        show_angles = st.checkbox("Show angle markers", key="quad_show_angles")
        
        if show_angles:
            st.caption("Show arcs at:")
            angle_cols = st.columns(5)
            with angle_cols[0]:
                show_angle_a = st.checkbox("A", key="quad_angle_a")
            with angle_cols[1]:
                show_angle_b = st.checkbox("B", key="quad_angle_b")
            with angle_cols[2]:
                show_angle_c = st.checkbox("C", key="quad_angle_c")
            with angle_cols[3]:
                show_angle_d = st.checkbox("D", key="quad_angle_d")
            with angle_cols[4]:
                angle_radius = st.number_input("Radius", min_value=0.1, step=0.1, key="quad_angle_radius")
            
            st.caption("Use square (right angle) marker:")
            right_cols = st.columns(5)
            with right_cols[0]:
                right_a = st.checkbox("A □", key="quad_right_a")
            with right_cols[1]:
                right_b = st.checkbox("B □", key="quad_right_b")
            with right_cols[2]:
                right_c = st.checkbox("C □", key="quad_right_c")
            with right_cols[3]:
                right_d = st.checkbox("D □", key="quad_right_d")
            with right_cols[4]:
                right_size = st.number_input("Size", min_value=0.1, step=0.1, key="quad_right_size")
            
            st.caption("Angle labels:")
            alabel_cols = st.columns(5)
            with alabel_cols[0]:
                st.text_input("A", key="quad_alabel_a", placeholder="$\\alpha$")
            with alabel_cols[1]:
                st.text_input("B", key="quad_alabel_b", placeholder="$\\beta$")
            with alabel_cols[2]:
                st.text_input("C", key="quad_alabel_c", placeholder="$\\gamma$")
            with alabel_cols[3]:
                st.text_input("D", key="quad_alabel_d", placeholder="$\\delta$")
            with alabel_cols[4]:
                angle_label_dist = st.number_input("Dist", min_value=0.1, step=0.1, key="quad_alabel_dist")
    
    # === MARKS TAB (Ticks & Parallel markers) ===
    with tab_marks:
        st.caption("Tick marks (equal sides)")
        show_ticks = st.checkbox("Show tick marks", key="quad_show_ticks")
        
        if show_ticks:
            tick_cols = st.columns(5)
            with tick_cols[0]:
                ticks_ab = st.number_input("AB", min_value=0, max_value=3, key="quad_ticks_ab")
            with tick_cols[1]:
                ticks_bc = st.number_input("BC", min_value=0, max_value=3, key="quad_ticks_bc")
            with tick_cols[2]:
                ticks_cd = st.number_input("CD", min_value=0, max_value=3, key="quad_ticks_cd")
            with tick_cols[3]:
                ticks_da = st.number_input("DA", min_value=0, max_value=3, key="quad_ticks_da")
            with tick_cols[4]:
                tick_length = st.number_input("Length", min_value=0.05, step=0.05, key="quad_tick_length")
        
        st.markdown("---")
        
        st.caption("Parallel arrows")
        show_parallel = st.checkbox("Show parallel markers", key="quad_show_parallel")
        
        if show_parallel:
            para_cols = st.columns(4)
            with para_cols[0]:
                parallel_ab = st.number_input("AB →", min_value=0, max_value=3, key="quad_parallel_ab")
            with para_cols[1]:
                parallel_bc = st.number_input("BC →", min_value=0, max_value=3, key="quad_parallel_bc")
            with para_cols[2]:
                parallel_cd = st.number_input("CD →", min_value=0, max_value=3, key="quad_parallel_cd")
            with para_cols[3]:
                parallel_da = st.number_input("DA →", min_value=0, max_value=3, key="quad_parallel_da")
            
            st.caption("Use same number of arrows on parallel sides")
    
    # === DIAGONALS TAB ===
    with tab_diag:
        st.caption("Diagonals")
        diag_cols = st.columns(2)
        with diag_cols[0]:
            show_diag_ac = st.checkbox("Show diagonal AC", key="quad_show_diag_ac")
            if show_diag_ac:
                diag_label_ac = st.text_input("Label AC", key="quad_diag_label_ac")
        with diag_cols[1]:
            show_diag_bd = st.checkbox("Show diagonal BD", key="quad_show_diag_bd")
            if show_diag_bd:
                diag_label_bd = st.text_input("Label BD", key="quad_diag_label_bd")


# --- Build Quadrilateral ---
def build_quadrilateral():
    """Build quadrilateral vertices from current input settings."""
    try:
        if input_method == "Preset shapes":
            rotation = st.session_state.get("quad_preset_rotation", 0)
            
            if preset_type == "Square":
                side = st.session_state.get("quad_square_side", 4.0)
                vertices = get_square(side, rotation=rotation)
            
            elif preset_type == "Rectangle":
                w = st.session_state.get("quad_rect_width", 5.0)
                h = st.session_state.get("quad_rect_height", 3.0)
                vertices = get_rectangle(w, h, rotation=rotation)
            
            elif preset_type == "Parallelogram":
                base = st.session_state.get("quad_para_base", 5.0)
                side = st.session_state.get("quad_para_side", 3.0)
                angle = st.session_state.get("quad_para_angle", 60.0)
                vertices = get_parallelogram(base, side, angle, rotation=rotation)
            
            elif preset_type == "Rhombus":
                side = st.session_state.get("quad_rhombus_side", 4.0)
                angle = st.session_state.get("quad_rhombus_angle", 60.0)
                vertices = get_rhombus(side, angle, rotation=rotation)
            
            elif preset_type == "Trapezium":
                top = st.session_state.get("quad_trap_top", 3.0)
                bottom = st.session_state.get("quad_trap_bottom", 5.0)
                height = st.session_state.get("quad_trap_height", 3.0)
                offset = st.session_state.get("quad_trap_offset", 0.0)
                vertices = get_trapezium(top, bottom, height, offset, rotation=rotation)
            
            elif preset_type == "Isosceles trapezium":
                top = st.session_state.get("quad_trap_top", 3.0)
                bottom = st.session_state.get("quad_trap_bottom", 5.0)
                height = st.session_state.get("quad_trap_height", 3.0)
                vertices = get_isosceles_trapezium(top, bottom, height, rotation=rotation)
            
            elif preset_type == "Kite":
                d1 = st.session_state.get("quad_kite_d1", 4.0)
                d2 = st.session_state.get("quad_kite_d2", 6.0)
                split = st.session_state.get("quad_kite_split", 0.3)
                vertices = get_kite(d1, d2, split, rotation=rotation)
            
            else:
                vertices = get_square(4.0)
        
        else:  # Coordinates
            coords = [
                (st.session_state.get("quad_ax", -2), st.session_state.get("quad_ay", 0)),
                (st.session_state.get("quad_bx", 2), st.session_state.get("quad_by", 0)),
                (st.session_state.get("quad_cx", 3), st.session_state.get("quad_cy", 3)),
                (st.session_state.get("quad_dx", -1), st.session_state.get("quad_dy", 3)),
            ]
            vertices = get_quadrilateral_vertices_from_coordinates(coords)
        
        return vertices
    except Exception as e:
        st.error(f"Error building quadrilateral: {e}")
        return get_square(4.0)


# --- Render Quadrilateral ---
def render_quadrilateral():
    """Render the quadrilateral with all configured options."""
    
    vertices = build_quadrilateral()
    centroid = get_centroid(vertices)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Set limits
    auto_set_limits(ax, vertices, padding)
    
    # Apply background
    apply_figure_style(fig, ax, white_background)
    
    line_width = axis_weight * 1.3
    line_style_map = {"solid": "-", "dashed": "--", "dotted": ":"}
    
    # --- Draw diagonals first (behind the main shape) ---
    show_diag_ac = st.session_state.get("quad_show_diag_ac", False)
    show_diag_bd = st.session_state.get("quad_show_diag_bd", False)
    
    if show_diag_ac:
        draw_diagonal(ax, vertices, 'AC', color=MY_COLORS[quad_color], 
                     line_width=line_width * 0.7, line_style='--',
                     label=st.session_state.get("quad_diag_label_ac", ""),
                     font_size=label_size, white_background=white_background)
    
    if show_diag_bd:
        draw_diagonal(ax, vertices, 'BD', color=MY_COLORS[quad_color],
                     line_width=line_width * 0.7, line_style='--',
                     label=st.session_state.get("quad_diag_label_bd", ""),
                     font_size=label_size, white_background=white_background)
    
    # --- Draw main quadrilateral ---
    draw_quadrilateral(
        ax, vertices,
        color=MY_COLORS[quad_color],
        line_width=line_width,
        line_style=line_style_map.get(quad_line_style, '-'),
        fill=quad_fill,
        fill_color=MY_COLORS[quad_fill_color] if quad_fill else None,
        fill_alpha=quad_fill_alpha,
        zorder=10
    )
    
    # --- Draw angle markers ---
    show_angles = st.session_state.get("quad_show_angles", False)
    if show_angles:
        angle_radius = st.session_state.get("quad_angle_radius", 0.5)
        right_size = st.session_state.get("quad_right_size", 0.4)
        angle_label_dist = st.session_state.get("quad_alabel_dist", 0.3)
        
        vertex_keys = ['a', 'b', 'c', 'd']
        for i, vk in enumerate(vertex_keys):
            show_this = st.session_state.get(f"quad_angle_{vk}", True)
            use_right = st.session_state.get(f"quad_right_{vk}", False)
            angle_label = st.session_state.get(f"quad_alabel_{vk}", "")
            
            if show_this:
                if use_right:
                    draw_right_angle_marker(ax, vertices, i, size=right_size,
                                           color=MY_COLORS[quad_color], line_width=line_width * 0.8)
                else:
                    draw_angle_arc(ax, vertices, i, radius=angle_radius,
                                  color=MY_COLORS[quad_color], line_width=line_width * 0.8)
                
                if angle_label:
                    draw_angle_label(ax, vertices, i, angle_label, radius=angle_radius,
                                    distance=angle_label_dist, color=MY_COLORS[quad_color],
                                    font_size=label_size * 0.8, white_background=white_background)
    
    # --- Draw tick marks ---
    show_ticks = st.session_state.get("quad_show_ticks", False)
    if show_ticks:
        tick_length = st.session_state.get("quad_tick_length", 0.25)
        tick_counts = [
            st.session_state.get("quad_ticks_ab", 0),
            st.session_state.get("quad_ticks_bc", 0),
            st.session_state.get("quad_ticks_cd", 0),
            st.session_state.get("quad_ticks_da", 0),
        ]
        for i, count in enumerate(tick_counts):
            if count > 0:
                p1, p2 = vertices[i], vertices[(i + 1) % 4]
                draw_tick_marks(ax, p1, p2, count, tick_length=tick_length,
                               color=MY_COLORS[quad_color], line_width=line_width * 0.8)
    
    # --- Draw parallel markers ---
    show_parallel = st.session_state.get("quad_show_parallel", False)
    if show_parallel:
        parallel_counts = [
            st.session_state.get("quad_parallel_ab", 0),
            st.session_state.get("quad_parallel_bc", 0),
            st.session_state.get("quad_parallel_cd", 0),
            st.session_state.get("quad_parallel_da", 0),
        ]
        for i, count in enumerate(parallel_counts):
            if count > 0:
                p1, p2 = vertices[i], vertices[(i + 1) % 4]
                draw_parallel_marks(ax, p1, p2, count, arrow_size=0.25,
                                   color=MY_COLORS[quad_color], line_width=line_width * 0.8)
    
    # --- Draw side labels ---
    show_slabels = st.session_state.get("quad_show_slabels", False)
    if show_slabels:
        for i in range(4):
            label = st.session_state.get(f"quad_slabel_{i}", "")
            if label:
                pos = st.session_state.get(f"quad_slabel_pos_{i}", 0.5)
                direction = st.session_state.get(f"quad_slabel_dir_{i}", "auto")
                dist = st.session_state.get(f"quad_slabel_dist_{i}", 0.4)
                p1, p2 = vertices[i], vertices[(i + 1) % 4]
                draw_side_label(ax, p1, p2, label, position=pos, direction=direction,
                               distance=dist, color=MY_COLORS[quad_color],
                               font_size=label_size * 0.85, centroid=centroid,
                               white_background=white_background)
    
    # --- Draw vertex labels ---
    show_vlabels = st.session_state.get("quad_show_vlabels", True)
    if show_vlabels:
        vlabel_dist = st.session_state.get("quad_vlabel_dist", 0.5)
        labels = [
            st.session_state.get("quad_vlabel_a", "$A$"),
            st.session_state.get("quad_vlabel_b", "$B$"),
            st.session_state.get("quad_vlabel_c", "$C$"),
            st.session_state.get("quad_vlabel_d", "$D$"),
        ]
        for i, label in enumerate(labels):
            if label:
                draw_vertex_label(ax, vertices[i], label, direction='auto',
                                 distance=vlabel_dist, color=MY_COLORS[quad_color],
                                 font_size=label_size, centroid=centroid,
                                 white_background=white_background)
    
    fig.tight_layout()
    return fig


# --- Main Rendering Logic ---
try:
    fig = render_quadrilateral()
    plot_placeholder.pyplot(fig)
    create_download_buttons(fig, svg_placeholder, png_placeholder, "quadrilateral")
    plt.close(fig)
except Exception as e:
    st.error(f"Error rendering: {e}")
    import traceback
    st.code(traceback.format_exc())

