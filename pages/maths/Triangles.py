"""
Triangle Diagrams Page
Creates educational triangle diagrams with labeled sides, angles, and markers.
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
from triangle_utils import (
    get_triangle_vertices_from_sss,
    get_triangle_vertices_from_coordinates,
    draw_triangle,
    draw_side_label,
    draw_angle_arc,
    draw_right_angle_marker,
    draw_angle_label,
    draw_vertex_label,
    draw_tick_marks,
    get_vertex_angle,
    get_side_length,
    get_equilateral_triangle,
    get_isoceles_triangle,
    get_right_triangle,
    get_30_60_90_triangle,
    get_45_45_90_triangle,
    auto_set_limits
)


# --- Initialize Session State Defaults ---
TRI_DEFAULTS = {
    # Sidebar
    "tri_axis_weight": 3.0,
    "tri_label_size": 20,
    "tri_padding": 1.0,
    "tri_white_bg": DEFAULT_WHITE_BG,
    # Definition
    "tri_input_method": "Side lengths (SSS)",
    "tri_side_a": 3.0, "tri_side_b": 4.0, "tri_side_c": 5.0,
    "tri_base_x": 0.0, "tri_base_y": 0.0, "tri_rotation": 0.0,
    "tri_ax": -2.5, "tri_ay": 0.0, "tri_bx": 2.5, "tri_by": 0.0, "tri_cx": 0.0, "tri_cy": 4.0,
    "tri_preset_type": "Equilateral", "tri_preset_rotation": 0.0,
    "tri_preset_side": 5.0, "tri_preset_base": 4.0, "tri_preset_leg": 5.0,
    "tri_preset_base_rt": 4.0, "tri_preset_height": 3.0, "tri_preset_short": 2.0, "tri_preset_leg_45": 4.0,
    # Style
    "tri_color": "grey", "tri_line_style": "solid", "tri_fill": False,
    "tri_fill_color": "blue", "tri_fill_alpha": 0.2,
    # Vertices
    "tri_show_vlabels": True, "tri_vlabel_a": "$A$", "tri_vlabel_b": "$B$", "tri_vlabel_c": "$C$",
    "tri_vlabel_dist": 0.6,
    # Sides
    "tri_show_slabels": False,
    # Angles
    "tri_show_angles": False, "tri_angle_a": True, "tri_angle_b": True, "tri_angle_c": True,
    "tri_angle_radius": 0.5, "tri_right_a": False, "tri_right_b": False, "tri_right_c": False,
    "tri_right_size": 0.4, "tri_alabel_a": "", "tri_alabel_b": "", "tri_alabel_c": "",
    "tri_alabel_dist": 0.8,
    # Ticks
    "tri_show_ticks": False, "tri_ticks_ab": 0, "tri_ticks_bc": 0, "tri_ticks_ca": 0, "tri_tick_length": 0.25,
}
# Side labels
for i in range(3):
    TRI_DEFAULTS[f"tri_slabel_{i}"] = ""
    TRI_DEFAULTS[f"tri_slabel_pos_{i}"] = 0.5
    TRI_DEFAULTS[f"tri_slabel_dir_{i}"] = "auto"
    TRI_DEFAULTS[f"tri_slabel_dist_{i}"] = 0.4

init_session_state(TRI_DEFAULTS)


# Helper to get selectbox index from session state value
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
        key="tri_axis_weight"
    )
    
    label_size = st.slider(
        "Label size",
        min_value=12, max_value=30, step=1,
        key="tri_label_size"
    )
    
    padding = st.slider(
        "Padding around triangle",
        min_value=0.5, max_value=3.0, step=0.25,
        key="tri_padding"
    )
    
    st.write("")
    white_background = st.toggle("White background", key="tri_white_bg")


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
    tab_def, tab_style, tab_vertices, tab_sides, tab_angles, tab_ticks = st.tabs([
        "Definition",
        "Style", 
        "Vertices",
        "Sides",
        "Angles",
        "Ticks"
    ])
    
    # === DEFINITION TAB ===
    with tab_def:
        input_method = st.radio(
            "Define triangle by:",
            ["Side lengths (SSS)", "Coordinates", "Preset shapes"],
            horizontal=True,
            key="tri_input_method"
        )
        
        st.write("")
        
        # --- Side lengths input ---
        if input_method == "Side lengths (SSS)":
            side_cols = st.columns(3)
            with side_cols[0]:
                side_a = st.number_input("Side $a$", min_value=0.01, step=0.1, key="tri_side_a",
                                         help="Opposite to vertex A")
            with side_cols[1]:
                side_b = st.number_input("Side $b$", min_value=0.01, step=0.1, key="tri_side_b",
                                         help="Opposite to vertex B")
            with side_cols[2]:
                side_c = st.number_input("Side $c$ (base)", min_value=0.01, step=0.1, key="tri_side_c",
                                         help="The base of the triangle")
            
            st.caption("Position")
            pos_cols = st.columns(3)
            with pos_cols[0]:
                base_x = st.number_input("Center $x$", step=0.5, key="tri_base_x")
            with pos_cols[1]:
                base_y = st.number_input("Center $y$", step=0.5, key="tri_base_y")
            with pos_cols[2]:
                rotation = st.number_input("Rotation (°)", step=15.0, key="tri_rotation")
        
        # --- Coordinates input ---
        elif input_method == "Coordinates":
            coord_cols = st.columns(3)
            with coord_cols[0]:
                st.caption("Vertex A")
                ax_coord = st.number_input("$x_A$", step=0.5, key="tri_ax")
                ay_coord = st.number_input("$y_A$", step=0.5, key="tri_ay")
            with coord_cols[1]:
                st.caption("Vertex B")
                bx_coord = st.number_input("$x_B$", step=0.5, key="tri_bx")
                by_coord = st.number_input("$y_B$", step=0.5, key="tri_by")
            with coord_cols[2]:
                st.caption("Vertex C")
                cx_coord = st.number_input("$x_C$", step=0.5, key="tri_cx")
                cy_coord = st.number_input("$y_C$", step=0.5, key="tri_cy")
        
        # --- Preset shapes ---
        else:
            preset_opts = ["Equilateral", "Isoceles", "Right triangle", "30-60-90", "45-45-90"]
            preset_cols = st.columns([2, 1])
            with preset_cols[0]:
                preset_type = st.selectbox(
                    "Preset type", preset_opts,
                    index=get_index(preset_opts, "tri_preset_type"),
                    key="tri_preset_type"
                )
            with preset_cols[1]:
                preset_rotation = st.number_input("Rotation (°)", step=15.0, key="tri_preset_rotation")
            
            if preset_type == "Equilateral":
                preset_side = st.number_input("Side length", min_value=0.01, step=0.5, key="tri_preset_side")
            elif preset_type == "Isoceles":
                iso_cols = st.columns(2)
                with iso_cols[0]:
                    preset_base = st.number_input("Base", min_value=0.01, step=0.5, key="tri_preset_base")
                with iso_cols[1]:
                    preset_leg = st.number_input("Legs", min_value=0.01, step=0.5, key="tri_preset_leg")
            elif preset_type == "Right triangle":
                rt_cols = st.columns(2)
                with rt_cols[0]:
                    preset_base = st.number_input("Base", min_value=0.01, step=0.5, key="tri_preset_base_rt")
                with rt_cols[1]:
                    preset_height = st.number_input("Height", min_value=0.01, step=0.5, key="tri_preset_height")
            elif preset_type == "30-60-90":
                preset_short = st.number_input("Short leg", min_value=0.01, step=0.5, key="tri_preset_short")
            else:  # 45-45-90
                preset_leg_45 = st.number_input("Leg length", min_value=0.01, step=0.5, key="tri_preset_leg_45")
    
    # === STYLE TAB ===
    with tab_style:
        style_cols = st.columns(3)
        line_style_opts = ["solid", "dashed", "dotted"]
        with style_cols[0]:
            tri_color = st.selectbox("Color", options=COLOR_OPTIONS, 
                                     index=get_index(COLOR_OPTIONS, "tri_color"), key="tri_color")
        with style_cols[1]:
            tri_line_style = st.selectbox("Line style", line_style_opts,
                                          index=get_index(line_style_opts, "tri_line_style"), key="tri_line_style")
        with style_cols[2]:
            tri_fill = st.checkbox("Fill triangle", key="tri_fill")
        
        if tri_fill:
            fill_cols = st.columns(2)
            with fill_cols[0]:
                tri_fill_color = st.selectbox("Fill color", options=COLOR_OPTIONS,
                                              index=get_index(COLOR_OPTIONS, "tri_fill_color"), key="tri_fill_color")
            with fill_cols[1]:
                tri_fill_alpha = st.slider("Fill opacity", 0.0, 1.0, key="tri_fill_alpha")
        else:
            tri_fill_color = tri_color
            tri_fill_alpha = 0.2
    
    # === VERTICES TAB ===
    with tab_vertices:
        show_vertex_labels = st.checkbox("Show vertex labels", key="tri_show_vlabels")
        
        if show_vertex_labels:
            st.write("")
            vlabel_cols = st.columns(3)
            with vlabel_cols[0]:
                vertex_a_label = st.text_input("Label A", key="tri_vlabel_a")
            with vlabel_cols[1]:
                vertex_b_label = st.text_input("Label B", key="tri_vlabel_b")
            with vlabel_cols[2]:
                vertex_c_label = st.text_input("Label C", key="tri_vlabel_c")
            
            vertex_label_dist = st.number_input("Distance from vertex", min_value=0.1, step=0.1, key="tri_vlabel_dist")
    
    # === SIDES TAB ===
    with tab_sides:
        show_side_labels = st.checkbox("Show side labels", key="tri_show_slabels")
        
        if show_side_labels:
            side_names = ["Side AB (opposite C)", "Side BC (opposite A)", "Side CA (opposite B)"]
            dir_opts = ["auto", "above", "below", "left", "right"]
            for side_idx, side_name in enumerate(side_names):
                with st.expander(f"{side_name}", expanded=(side_idx == 0)):
                    sl_cols = st.columns([2, 1, 1, 1])
                    with sl_cols[0]:
                        st.text_input("Label", key=f"tri_slabel_{side_idx}", placeholder="e.g. $5$")
                    with sl_cols[1]:
                        st.slider("Position", 0.0, 1.0, key=f"tri_slabel_pos_{side_idx}", help="Along side")
                    with sl_cols[2]:
                        st.selectbox(
                            "Direction", dir_opts,
                            index=get_index(dir_opts, f"tri_slabel_dir_{side_idx}"),
                            key=f"tri_slabel_dir_{side_idx}"
                        )
                    with sl_cols[3]:
                        st.number_input("Distance", min_value=0.0, step=0.1, key=f"tri_slabel_dist_{side_idx}")
    
    # === ANGLES TAB ===
    with tab_angles:
        show_angles = st.checkbox("Show angle markers", key="tri_show_angles")
        
        if show_angles:
            st.caption("Show arcs at:")
            angle_cols = st.columns(4)
            with angle_cols[0]:
                show_angle_a = st.checkbox("Angle A", key="tri_angle_a")
            with angle_cols[1]:
                show_angle_b = st.checkbox("Angle B", key="tri_angle_b")
            with angle_cols[2]:
                show_angle_c = st.checkbox("Angle C", key="tri_angle_c")
            with angle_cols[3]:
                angle_radius = st.number_input("Arc radius", min_value=0.1, step=0.1, key="tri_angle_radius")
            
            st.caption("Use square (right angle) marker instead:")
            right_cols = st.columns(4)
            with right_cols[0]:
                right_a = st.checkbox("A □", key="tri_right_a")
            with right_cols[1]:
                right_b = st.checkbox("B □", key="tri_right_b")
            with right_cols[2]:
                right_c = st.checkbox("C □", key="tri_right_c")
            with right_cols[3]:
                right_size = st.number_input("Square size", min_value=0.1, step=0.1, key="tri_right_size")
            
            st.caption("Angle labels:")
            alabel_cols = st.columns(4)
            with alabel_cols[0]:
                angle_a_label = st.text_input("A label", key="tri_alabel_a", placeholder="$\\alpha$")
            with alabel_cols[1]:
                angle_b_label = st.text_input("B label", key="tri_alabel_b", placeholder="$\\beta$")
            with alabel_cols[2]:
                angle_c_label = st.text_input("C label", key="tri_alabel_c", placeholder="$\\gamma$")
            with alabel_cols[3]:
                angle_label_dist = st.number_input("Label dist", min_value=0.2, step=0.1, key="tri_alabel_dist")
    
    # === TICKS TAB ===
    with tab_ticks:
        show_ticks = st.checkbox("Show tick marks (for equal sides)", key="tri_show_ticks")
        
        if show_ticks:
            st.write("")
            tick_cols = st.columns(4)
            with tick_cols[0]:
                ticks_ab = st.number_input("Ticks on AB", min_value=0, max_value=3, key="tri_ticks_ab")
            with tick_cols[1]:
                ticks_bc = st.number_input("Ticks on BC", min_value=0, max_value=3, key="tri_ticks_bc")
            with tick_cols[2]:
                ticks_ca = st.number_input("Ticks on CA", min_value=0, max_value=3, key="tri_ticks_ca")
            with tick_cols[3]:
                tick_length = st.number_input("Tick length", min_value=0.05, step=0.05, key="tri_tick_length")
            
            st.caption("Use the same number of ticks on sides of equal length.")


# --- Build Triangle ---
def build_triangle():
    """Build triangle vertices from current input settings."""
    try:
        if input_method == "Side lengths (SSS)":
            vertices = get_triangle_vertices_from_sss(
                side_a, side_b, side_c,
                base_center=(base_x, base_y),
                base_angle=rotation
            )
        elif input_method == "Coordinates":
            vertices = get_triangle_vertices_from_coordinates([
                (ax_coord, ay_coord),
                (bx_coord, by_coord),
                (cx_coord, cy_coord)
            ])
        else:  # Presets
            if preset_type == "Equilateral":
                vertices = get_equilateral_triangle(preset_side)
            elif preset_type == "Isoceles":
                vertices = get_isoceles_triangle(preset_base, preset_leg)
            elif preset_type == "Right triangle":
                vertices = get_right_triangle(preset_base, preset_height)
            elif preset_type == "30-60-90":
                vertices = get_30_60_90_triangle(preset_short)
            else:  # 45-45-90
                vertices = get_45_45_90_triangle(preset_leg_45)
            
            # Apply rotation if needed
            if preset_rotation != 0:
                theta = np.radians(preset_rotation)
                rot_matrix = np.array([
                    [np.cos(theta), -np.sin(theta)],
                    [np.sin(theta), np.cos(theta)]
                ])
                centroid = np.mean(vertices, axis=0)
                vertices = np.array([rot_matrix @ (v - centroid) + centroid for v in vertices])
        
        return vertices
    except ValueError as e:
        st.error(f"Invalid triangle: {str(e)}")
        return None


def render_triangle(vertices):
    """Render the triangle with all configured options."""
    
    # Create figure
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Set limits with padding
    auto_set_limits(ax, vertices, padding=padding)
    
    # Apply background
    apply_figure_style(fig, ax, white_background)
    
    line_width = axis_weight * 1.3
    line_style_map = {"solid": "-", "dashed": "--", "dotted": ":"}
    
    # Draw triangle
    draw_triangle(
        ax, vertices,
        color=MY_COLORS[tri_color],
        line_width=line_width,
        line_style=line_style_map[tri_line_style],
        fill=tri_fill,
        fill_color=MY_COLORS[tri_fill_color] if tri_fill else None,
        fill_alpha=tri_fill_alpha,
        zorder=10
    )
    
    # Draw vertex labels
    if show_vertex_labels:
        labels = [vertex_a_label, vertex_b_label, vertex_c_label]
        for i, label_text in enumerate(labels):
            if label_text:
                draw_vertex_label(
                    ax, vertices, i, label_text,
                    color=MY_COLORS[tri_color],
                    font_size=label_size,
                    distance=vertex_label_dist,
                    direction='auto',
                    zorder=50,
                    white_background=white_background
                )
    
    # Draw side labels
    if show_side_labels:
        for side_idx in range(3):
            label_text = st.session_state.get(f"tri_slabel_{side_idx}", "")
            if label_text:
                draw_side_label(
                    ax, vertices, side_idx, label_text,
                    color=MY_COLORS[tri_color],
                    font_size=label_size,
                    position=st.session_state.get(f"tri_slabel_pos_{side_idx}", 0.5),
                    direction=st.session_state.get(f"tri_slabel_dir_{side_idx}", "auto"),
                    distance=st.session_state.get(f"tri_slabel_dist_{side_idx}", 0.4),
                    rotate_with_side=False,
                    zorder=50,
                    white_background=white_background
                )
    
    # Draw angle markers
    if show_angles:
        angle_shows = [show_angle_a, show_angle_b, show_angle_c]
        right_angles = [right_a, right_b, right_c]
        angle_labels = [angle_a_label, angle_b_label, angle_c_label]
        
        for i in range(3):
            if angle_shows[i]:
                if right_angles[i]:
                    draw_right_angle_marker(
                        ax, vertices, i,
                        color=MY_COLORS[tri_color],
                        line_width=line_width * 0.7,
                        size=right_size,
                        zorder=15
                    )
                else:
                    draw_angle_arc(
                        ax, vertices, i,
                        color=MY_COLORS[tri_color],
                        line_width=line_width * 0.7,
                        radius=angle_radius,
                        zorder=15
                    )
                
                if angle_labels[i]:
                    draw_angle_label(
                        ax, vertices, i, angle_labels[i],
                        color=MY_COLORS[tri_color],
                        font_size=label_size,
                        distance=angle_label_dist,
                        direction='auto',
                        zorder=50,
                        white_background=white_background
                    )
    
    # Draw tick marks
    if show_ticks:
        ticks = [ticks_ab, ticks_bc, ticks_ca]
        for side_idx, num_ticks in enumerate(ticks):
            if num_ticks > 0:
                draw_tick_marks(
                    ax, vertices, side_idx, num_ticks,
                    color=MY_COLORS[tri_color],
                    line_width=line_width * 0.7,
                    tick_length=tick_length,
                    zorder=20
                )
    
    fig.tight_layout()
    return fig


# --- Main Rendering Logic ---
vertices = build_triangle()

if vertices is not None:
    # Render the triangle
    fig = render_triangle(vertices)
    
    # Display
    plot_placeholder.pyplot(fig)
    
    # Download buttons
    create_download_buttons(fig, svg_placeholder, png_placeholder, "triangle")
    
    # Show computed info at bottom of controls
    with col_controls:
        angles = [get_vertex_angle(vertices, i) for i in range(3)]
        sides = [get_side_length(vertices, i) for i in range(3)]
        
        st.caption(f"**Angles:** A={angles[0]:.1f}°, B={angles[1]:.1f}°, C={angles[2]:.1f}° · **Sides:** AB={sides[0]:.2f}, BC={sides[1]:.2f}, CA={sides[2]:.2f}")
    
    plt.close(fig)
