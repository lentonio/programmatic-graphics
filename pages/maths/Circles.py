"""
Circle Diagrams Page
Creates educational circle diagrams with radii, diameters, chords, tangents,
arcs, sectors, segments, and angle markers.
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
from circle_utils import (
    draw_circle,
    draw_center_point,
    draw_radius,
    draw_diameter,
    draw_chord,
    draw_tangent,
    draw_arc,
    draw_sector,
    draw_segment,
    draw_central_angle_arc,
    draw_point_on_circle,
    draw_label,
    draw_line_label,
    draw_arc_label,
    point_on_circle,
    auto_set_limits,
    get_chord_length,
    get_arc_length,
    get_sector_area,
    get_segment_area
)


# --- Initialize Session State Defaults ---
CIRC_DEFAULTS = {
    # Sidebar
    "circ_axis_weight": 3.0,
    "circ_label_size": 20,
    "circ_padding": 1.0,
    "circ_white_bg": DEFAULT_WHITE_BG,
    # Definition
    "circ_cx": 0.0, "circ_cy": 0.0, "circ_radius": 3.0,
    "circ_show_center": True, "circ_center_label": "$O$",
    # Style
    "circ_color": "grey", "circ_line_style": "solid",
    "circ_fill": False, "circ_fill_color": "blue", "circ_fill_alpha": 0.2,
    # Diameter
    "circ_show_diameter": False, "circ_diameter_angle": 0.0, "circ_diameter_label": "",
    # Arcs
    "circ_show_arc": False, "circ_arc_start": 0.0, "circ_arc_end": 90.0,
    "circ_arc_color": "blue", "circ_arc_label": "", "circ_arc_style": "solid",
    # Sector
    "circ_show_sector": False, "circ_sector_start": 0.0, "circ_sector_end": 60.0,
    "circ_sector_color": "blue", "circ_sector_alpha": 0.3,
    # Segment
    "circ_show_segment": False, "circ_segment_start": 30.0, "circ_segment_end": 150.0,
    "circ_segment_color": "blue", "circ_segment_alpha": 0.3,
}
# Radii
for i in range(3):
    CIRC_DEFAULTS[f"circ_show_radius_{i}"] = (i == 0)
    CIRC_DEFAULTS[f"circ_radius_angle_{i}"] = 45.0 + i * 90
    CIRC_DEFAULTS[f"circ_radius_label_{i}"] = "$r$" if i == 0 else ""
# Chords
for i in range(2):
    CIRC_DEFAULTS[f"circ_show_chord_{i}"] = False
    CIRC_DEFAULTS[f"circ_chord_a1_{i}"] = 30.0 + i * 60
    CIRC_DEFAULTS[f"circ_chord_a2_{i}"] = 150.0 + i * 60
    CIRC_DEFAULTS[f"circ_chord_label_{i}"] = ""
# Tangents
for i in range(2):
    CIRC_DEFAULTS[f"circ_show_tangent_{i}"] = False
    CIRC_DEFAULTS[f"circ_tangent_angle_{i}"] = 90.0 + i * 90
    CIRC_DEFAULTS[f"circ_tangent_len_{i}"] = 4.0
    CIRC_DEFAULTS[f"circ_tangent_label_{i}"] = ""
# Central angles
for i in range(3):
    CIRC_DEFAULTS[f"circ_show_ca_{i}"] = False
    CIRC_DEFAULTS[f"circ_ca_start_{i}"] = float(i * 60)
    CIRC_DEFAULTS[f"circ_ca_end_{i}"] = float(60 + i * 60)
    CIRC_DEFAULTS[f"circ_ca_radius_{i}"] = 0.6
    CIRC_DEFAULTS[f"circ_ca_label_{i}"] = ""
    CIRC_DEFAULTS[f"circ_ca_label_dist_{i}"] = 0.3
# Points on circle
for i in range(4):
    CIRC_DEFAULTS[f"circ_show_point_{i}"] = False
    CIRC_DEFAULTS[f"circ_point_angle_{i}"] = float(i * 90)
    CIRC_DEFAULTS[f"circ_point_label_{i}"] = ""

init_session_state(CIRC_DEFAULTS)


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
        key="circ_axis_weight"
    )
    
    label_size = st.slider(
        "Label size",
        min_value=12, max_value=30, step=1,
        key="circ_label_size"
    )
    
    padding = st.slider(
        "Padding around circle",
        min_value=0.5, max_value=3.0, step=0.25,
        key="circ_padding"
    )
    
    st.write("")
    white_background = st.toggle("White background", key="circ_white_bg")


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
    tab_def, tab_style, tab_radii, tab_chords, tab_arcs, tab_angles, tab_points = st.tabs([
        "Definition",
        "Style",
        "Radii & Diameter",
        "Chords & Tangents",
        "Arcs & Sectors",
        "Angles",
        "Points & Labels"
    ])
    
    # === DEFINITION TAB ===
    with tab_def:
        st.caption("Circle definition")
        def_cols = st.columns(3)
        with def_cols[0]:
            center_x = st.number_input("Center $x$", step=0.5, key="circ_cx")
        with def_cols[1]:
            center_y = st.number_input("Center $y$", step=0.5, key="circ_cy")
        with def_cols[2]:
            radius = st.number_input("Radius", min_value=0.1, step=0.5, key="circ_radius")
        
        center = (center_x, center_y)
        
        st.write("")
        show_center = st.checkbox("Show center point", key="circ_show_center")
        
        if show_center:
            center_label = st.text_input("Center label", key="circ_center_label")
    
    # === STYLE TAB ===
    with tab_style:
        style_cols = st.columns(3)
        line_style_opts = ["solid", "dashed", "dotted"]
        with style_cols[0]:
            circ_color = st.selectbox("Color", options=COLOR_OPTIONS,
                                      index=get_index(COLOR_OPTIONS, "circ_color"), key="circ_color")
        with style_cols[1]:
            circ_line_style = st.selectbox("Line style", line_style_opts,
                                           index=get_index(line_style_opts, "circ_line_style"), key="circ_line_style")
        with style_cols[2]:
            circ_fill = st.checkbox("Fill circle", key="circ_fill")
        
        if circ_fill:
            fill_cols = st.columns(2)
            with fill_cols[0]:
                circ_fill_color = st.selectbox("Fill color", options=COLOR_OPTIONS,
                                               index=get_index(COLOR_OPTIONS, "circ_fill_color"), key="circ_fill_color")
            with fill_cols[1]:
                circ_fill_alpha = st.slider("Fill opacity", 0.0, 1.0, key="circ_fill_alpha")
        else:
            circ_fill_color = circ_color
            circ_fill_alpha = 0.2
    
    # === RADII & DIAMETER TAB ===
    with tab_radii:
        # Radii
        st.caption("Radii (up to 3)")
        for i in range(3):
            with st.expander(f"Radius {i+1}", expanded=(i == 0)):
                r_cols = st.columns([1, 2, 1])
                with r_cols[0]:
                    show_radius = st.checkbox("Show", key=f"circ_show_radius_{i}")
                with r_cols[1]:
                    radius_angle = st.number_input("Angle (°)", step=15.0, key=f"circ_radius_angle_{i}")
                with r_cols[2]:
                    radius_label = st.text_input("Label", key=f"circ_radius_label_{i}")
        
        st.markdown("---")
        
        # Diameter
        st.caption("Diameter")
        diam_cols = st.columns([1, 2, 1])
        with diam_cols[0]:
            show_diameter = st.checkbox("Show", key="circ_show_diameter")
        with diam_cols[1]:
            diameter_angle = st.number_input("Angle (°)", step=15.0, key="circ_diameter_angle")
        with diam_cols[2]:
            diameter_label = st.text_input("Label", key="circ_diameter_label", placeholder="$d$")
    
    # === CHORDS & TANGENTS TAB ===
    with tab_chords:
        # Chords
        st.caption("Chords (up to 2)")
        for i in range(2):
            with st.expander(f"Chord {i+1}", expanded=(i == 0)):
                c_cols = st.columns([1, 1, 1, 1])
                with c_cols[0]:
                    show_chord = st.checkbox("Show", key=f"circ_show_chord_{i}")
                with c_cols[1]:
                    chord_angle1 = st.number_input("Start °", step=15.0, key=f"circ_chord_a1_{i}")
                with c_cols[2]:
                    chord_angle2 = st.number_input("End °", step=15.0, key=f"circ_chord_a2_{i}")
                with c_cols[3]:
                    chord_label = st.text_input("Label", key=f"circ_chord_label_{i}")
        
        st.markdown("---")
        
        # Tangents
        st.caption("Tangents (up to 2)")
        for i in range(2):
            with st.expander(f"Tangent {i+1}", expanded=False):
                t_cols = st.columns([1, 1, 1, 1])
                with t_cols[0]:
                    show_tangent = st.checkbox("Show", key=f"circ_show_tangent_{i}")
                with t_cols[1]:
                    tangent_angle = st.number_input("Touch °", step=15.0, key=f"circ_tangent_angle_{i}")
                with t_cols[2]:
                    tangent_length = st.number_input("Length", min_value=0.5, step=0.5, key=f"circ_tangent_len_{i}")
                with t_cols[3]:
                    tangent_label = st.text_input("Label", key=f"circ_tangent_label_{i}")
    
    # === ARCS & SECTORS TAB ===
    with tab_arcs:
        arc_style_opts = ["solid", "dashed"]
        # Arc highlighting
        st.caption("Highlighted arc")
        arc_cols = st.columns([1, 1, 1, 1])
        with arc_cols[0]:
            show_arc = st.checkbox("Show", key="circ_show_arc")
        with arc_cols[1]:
            arc_start = st.number_input("Start °", step=15.0, key="circ_arc_start")
        with arc_cols[2]:
            arc_end = st.number_input("End °", step=15.0, key="circ_arc_end")
        with arc_cols[3]:
            arc_color = st.selectbox("Color", options=COLOR_OPTIONS,
                                     index=get_index(COLOR_OPTIONS, "circ_arc_color"), key="circ_arc_color")
        
        if show_arc:
            arc_cols2 = st.columns(2)
            with arc_cols2[0]:
                arc_label = st.text_input("Arc label", key="circ_arc_label")
            with arc_cols2[1]:
                arc_style = st.selectbox("Style", arc_style_opts,
                                         index=get_index(arc_style_opts, "circ_arc_style"), key="circ_arc_style")
        
        st.markdown("---")
        
        # Sector
        st.caption("Sector (filled)")
        sec_cols = st.columns([1, 1, 1, 1])
        with sec_cols[0]:
            show_sector = st.checkbox("Show", key="circ_show_sector")
        with sec_cols[1]:
            sector_start = st.number_input("Start °", step=15.0, key="circ_sector_start")
        with sec_cols[2]:
            sector_end = st.number_input("End °", step=15.0, key="circ_sector_end")
        with sec_cols[3]:
            sector_color = st.selectbox("Color", options=COLOR_OPTIONS,
                                        index=get_index(COLOR_OPTIONS, "circ_sector_color"), key="circ_sector_color")
        
        if show_sector:
            sector_alpha = st.slider("Sector opacity", 0.0, 1.0, key="circ_sector_alpha")
        
        st.markdown("---")
        
        # Segment
        st.caption("Segment (between chord and arc)")
        seg_cols = st.columns([1, 1, 1, 1])
        with seg_cols[0]:
            show_segment = st.checkbox("Show", key="circ_show_segment")
        with seg_cols[1]:
            segment_start = st.number_input("Start °", step=15.0, key="circ_segment_start")
        with seg_cols[2]:
            segment_end = st.number_input("End °", step=15.0, key="circ_segment_end")
        with seg_cols[3]:
            segment_color = st.selectbox("Color", options=COLOR_OPTIONS,
                                         index=get_index(COLOR_OPTIONS, "circ_segment_color"), key="circ_segment_color")
        
        if show_segment:
            segment_alpha = st.slider("Segment opacity", 0.0, 1.0, key="circ_segment_alpha")
    
    # === ANGLES TAB ===
    with tab_angles:
        st.caption("Central angle markers (up to 3)")
        for i in range(3):
            with st.expander(f"Angle {i+1}", expanded=(i == 0)):
                ca_cols = st.columns([1, 1, 1])
                with ca_cols[0]:
                    show_ca = st.checkbox("Show", key=f"circ_show_ca_{i}")
                with ca_cols[1]:
                    ca_start = st.number_input("From °", step=15.0, key=f"circ_ca_start_{i}")
                with ca_cols[2]:
                    ca_end = st.number_input("To °", step=15.0, key=f"circ_ca_end_{i}")
                
                ca_cols2 = st.columns([1, 1, 1])
                with ca_cols2[0]:
                    ca_radius = st.number_input("Arc size", min_value=0.2, step=0.1, key=f"circ_ca_radius_{i}")
                with ca_cols2[1]:
                    ca_label = st.text_input("Label", key=f"circ_ca_label_{i}", placeholder="$\\theta$")
                with ca_cols2[2]:
                    ca_label_dist = st.number_input("Label dist", min_value=0.1, step=0.1, key=f"circ_ca_label_dist_{i}")
    
    # === POINTS & LABELS TAB ===
    with tab_points:
        st.caption("Points on circle (up to 4)")
        for i in range(4):
            with st.expander(f"Point {i+1}", expanded=(i == 0)):
                p_cols = st.columns([1, 1, 2])
                with p_cols[0]:
                    show_point = st.checkbox("Show", key=f"circ_show_point_{i}")
                with p_cols[1]:
                    point_angle = st.number_input("Angle °", step=15.0, key=f"circ_point_angle_{i}")
                with p_cols[2]:
                    point_label = st.text_input("Label", key=f"circ_point_label_{i}", 
                                                placeholder=f"$P_{i+1}$")


# --- Render Circle ---
def render_circle():
    """Render the circle with all configured options."""
    
    # Create figure
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Set limits with padding
    auto_set_limits(ax, center, radius, padding=padding)
    
    # Apply background
    apply_figure_style(fig, ax, white_background)
    
    line_width = axis_weight * 1.3
    line_style_map = {"solid": "-", "dashed": "--", "dotted": ":"}
    
    # --- Draw sector (behind everything) ---
    if show_sector:
        draw_sector(ax, center, radius, sector_start, sector_end,
                   color=MY_COLORS[sector_color], fill_alpha=sector_alpha, zorder=2)
    
    # --- Draw segment ---
    if show_segment:
        draw_segment(ax, center, radius, segment_start, segment_end,
                    color=MY_COLORS[segment_color], fill_alpha=segment_alpha, zorder=2)
    
    # --- Draw main circle ---
    draw_circle(
        ax, center, radius,
        color=MY_COLORS[circ_color],
        line_width=line_width,
        line_style=line_style_map[circ_line_style],
        fill=circ_fill,
        fill_color=MY_COLORS[circ_fill_color] if circ_fill else None,
        fill_alpha=circ_fill_alpha,
        zorder=10
    )
    
    # --- Draw highlighted arc (on top of circle) ---
    if show_arc:
        draw_arc(ax, center, radius, arc_start, arc_end,
                color=MY_COLORS[arc_color], line_width=line_width * 1.5,
                line_style=line_style_map[arc_style], zorder=12)
        if arc_label:
            draw_arc_label(ax, center, radius, arc_start, arc_end, arc_label,
                          color=MY_COLORS[arc_color], font_size=label_size,
                          distance=0.5, white_background=white_background, zorder=100)
    
    # --- Draw diameter ---
    if show_diameter:
        draw_diameter(ax, center, radius, diameter_angle,
                     color=MY_COLORS[circ_color], line_width=line_width, zorder=15)
        if diameter_label:
            p1 = point_on_circle(center, radius, diameter_angle)
            p2 = point_on_circle(center, radius, diameter_angle + 180)
            draw_line_label(ax, p1, p2, diameter_label,
                           color=MY_COLORS[circ_color], font_size=label_size,
                           position=0.5, distance=0.4, white_background=white_background)
    
    # --- Draw radii ---
    for i in range(3):
        if st.session_state.get(f"circ_show_radius_{i}", False):
            r_angle = st.session_state.get(f"circ_radius_angle_{i}", 45)
            r_label = st.session_state.get(f"circ_radius_label_{i}", "")
            
            draw_radius(ax, center, radius, r_angle,
                       color=MY_COLORS[circ_color], line_width=line_width, zorder=15)
            
            if r_label:
                end_pt = point_on_circle(center, radius, r_angle)
                draw_line_label(ax, center, end_pt, r_label,
                               color=MY_COLORS[circ_color], font_size=label_size,
                               position=0.5, distance=0.4, white_background=white_background)
    
    # --- Draw chords ---
    for i in range(2):
        if st.session_state.get(f"circ_show_chord_{i}", False):
            a1 = st.session_state.get(f"circ_chord_a1_{i}", 30)
            a2 = st.session_state.get(f"circ_chord_a2_{i}", 150)
            c_label = st.session_state.get(f"circ_chord_label_{i}", "")
            
            draw_chord(ax, center, radius, a1, a2,
                      color=MY_COLORS[circ_color], line_width=line_width, zorder=15)
            
            if c_label:
                p1 = point_on_circle(center, radius, a1)
                p2 = point_on_circle(center, radius, a2)
                draw_line_label(ax, p1, p2, c_label,
                               color=MY_COLORS[circ_color], font_size=label_size,
                               position=0.5, distance=0.4, white_background=white_background)
    
    # --- Draw tangents ---
    for i in range(2):
        if st.session_state.get(f"circ_show_tangent_{i}", False):
            t_angle = st.session_state.get(f"circ_tangent_angle_{i}", 90)
            t_len = st.session_state.get(f"circ_tangent_len_{i}", 4)
            t_label = st.session_state.get(f"circ_tangent_label_{i}", "")
            
            draw_tangent(ax, center, radius, t_angle, t_len,
                        color=MY_COLORS[circ_color], line_width=line_width, zorder=15)
            
            if t_label:
                touch_pt = point_on_circle(center, radius, t_angle)
                tangent_dir = np.array([np.cos(np.radians(t_angle + 90)), 
                                        np.sin(np.radians(t_angle + 90))])
                end_pt = touch_pt + (t_len / 2) * tangent_dir
                draw_line_label(ax, touch_pt, end_pt, t_label,
                               color=MY_COLORS[circ_color], font_size=label_size,
                               position=0.5, distance=0.4, white_background=white_background)
    
    # --- Draw central angle markers ---
    for i in range(3):
        if st.session_state.get(f"circ_show_ca_{i}", False):
            ca_s = st.session_state.get(f"circ_ca_start_{i}", 0)
            ca_e = st.session_state.get(f"circ_ca_end_{i}", 60)
            ca_r = st.session_state.get(f"circ_ca_radius_{i}", 0.6)
            ca_lbl = st.session_state.get(f"circ_ca_label_{i}", "")
            ca_lbl_dist = st.session_state.get(f"circ_ca_label_dist_{i}", 0.3)
            
            draw_central_angle_arc(ax, center, ca_s, ca_e, ca_r,
                                  color=MY_COLORS[circ_color], line_width=line_width * 0.7, zorder=15)
            
            if ca_lbl:
                mid_angle = (ca_s + ca_e) / 2
                label_pos = point_on_circle(center, ca_r * 0.6, mid_angle)
                draw_label(ax, label_pos, ca_lbl, color=MY_COLORS[circ_color],
                          font_size=label_size, direction='auto', distance=ca_lbl_dist,
                          reference_point=center, white_background=white_background)
    
    # --- Draw center point and label ---
    if show_center:
        draw_center_point(ax, center, color=MY_COLORS[circ_color], 
                         marker_size=axis_weight * 3, zorder=20)
        if center_label:
            draw_label(ax, center, center_label, color=MY_COLORS[circ_color],
                      font_size=label_size, direction='below', distance=0.4,
                      white_background=white_background)
    
    # --- Draw points on circle ---
    for i in range(4):
        if st.session_state.get(f"circ_show_point_{i}", False):
            p_angle = st.session_state.get(f"circ_point_angle_{i}", 0)
            p_label = st.session_state.get(f"circ_point_label_{i}", "")
            
            pt = draw_point_on_circle(ax, center, radius, p_angle,
                                      color=MY_COLORS[circ_color],
                                      marker_size=axis_weight * 3, zorder=25)
            
            if p_label:
                draw_label(ax, pt, p_label, color=MY_COLORS[circ_color],
                          font_size=label_size, direction='auto', distance=0.4,
                          reference_point=center, white_background=white_background)
    
    fig.tight_layout()
    return fig


# --- Main Rendering Logic ---
fig = render_circle()

# Display
plot_placeholder.pyplot(fig)

# Download buttons
create_download_buttons(fig, svg_placeholder, png_placeholder, "circle")

# Show computed info at bottom of controls
with col_controls:
    info_parts = [f"**Radius:** {radius:.2f}", f"**Diameter:** {2*radius:.2f}", 
                  f"**Circumference:** {2*np.pi*radius:.2f}", f"**Area:** {np.pi*radius**2:.2f}"]
    st.caption(" · ".join(info_parts))

plt.close(fig)
