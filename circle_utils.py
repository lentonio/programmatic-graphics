"""
Circle diagram utilities for educational math graphics.
Provides functions to draw circles with radii, diameters, chords, tangents,
arcs, sectors, segments, and angle markers.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Wedge, Circle, Polygon, FancyArrowPatch
from matplotlib.path import Path
import matplotlib.patches as mpatches


def point_on_circle(center, radius, angle_degrees):
    """
    Get the (x, y) coordinates of a point on a circle.
    
    Args:
        center: (x, y) tuple for circle center
        radius: Circle radius
        angle_degrees: Angle in degrees (0° = right, 90° = top)
    
    Returns:
        numpy array [x, y]
    """
    angle_rad = np.radians(angle_degrees)
    x = center[0] + radius * np.cos(angle_rad)
    y = center[1] + radius * np.sin(angle_rad)
    return np.array([x, y])


def draw_circle(ax, center, radius, color, line_width, line_style='-', 
                fill=False, fill_color=None, fill_alpha=0.3, zorder=10):
    """
    Draw a circle.
    
    Args:
        ax: Matplotlib axes
        center: (x, y) tuple for circle center
        radius: Circle radius
        color: Line color (hex string)
        line_width: Line width
        line_style: Line style ('-', '--', ':')
        fill: Whether to fill the circle
        fill_color: Fill color (defaults to line color)
        fill_alpha: Fill transparency
        zorder: Drawing order
    """
    # Draw the circle outline
    theta = np.linspace(0, 2 * np.pi, 200)
    x = center[0] + radius * np.cos(theta)
    y = center[1] + radius * np.sin(theta)
    
    ax.plot(x, y, color=color, linewidth=line_width, linestyle=line_style, 
            zorder=zorder, solid_capstyle='round')
    
    # Fill if requested
    if fill:
        fc = fill_color if fill_color else color
        circle_patch = plt.Circle(center, radius, facecolor=fc, alpha=fill_alpha,
                                   edgecolor='none', zorder=zorder-1)
        ax.add_patch(circle_patch)


def draw_center_point(ax, center, color, marker_size, zorder=20):
    """
    Draw a point at the circle center.
    
    Args:
        ax: Matplotlib axes
        center: (x, y) tuple
        color: Point color
        marker_size: Size of the marker
        zorder: Drawing order
    """
    ax.plot(center[0], center[1], 'o', color=color, markersize=marker_size, 
            zorder=zorder)


def draw_radius(ax, center, radius, angle_degrees, color, line_width, 
                line_style='-', zorder=15):
    """
    Draw a radius line from center to edge.
    
    Args:
        ax: Matplotlib axes
        center: (x, y) tuple
        radius: Circle radius
        angle_degrees: Angle of the radius (0° = right, 90° = top)
        color: Line color
        line_width: Line width
        line_style: Line style
        zorder: Drawing order
    """
    end_point = point_on_circle(center, radius, angle_degrees)
    ax.plot([center[0], end_point[0]], [center[1], end_point[1]], 
            color=color, linewidth=line_width, linestyle=line_style, 
            zorder=zorder, solid_capstyle='round')


def draw_diameter(ax, center, radius, angle_degrees, color, line_width,
                  line_style='-', zorder=15):
    """
    Draw a diameter line through the center.
    
    Args:
        ax: Matplotlib axes
        center: (x, y) tuple
        radius: Circle radius
        angle_degrees: Angle of the diameter (0° = horizontal)
        color: Line color
        line_width: Line width
        line_style: Line style
        zorder: Drawing order
    """
    point1 = point_on_circle(center, radius, angle_degrees)
    point2 = point_on_circle(center, radius, angle_degrees + 180)
    ax.plot([point1[0], point2[0]], [point1[1], point2[1]], 
            color=color, linewidth=line_width, linestyle=line_style, 
            zorder=zorder, solid_capstyle='round')


def draw_chord(ax, center, radius, angle1_degrees, angle2_degrees, color, 
               line_width, line_style='-', zorder=15):
    """
    Draw a chord between two points on the circle.
    
    Args:
        ax: Matplotlib axes
        center: (x, y) tuple
        radius: Circle radius
        angle1_degrees: Angle of first endpoint
        angle2_degrees: Angle of second endpoint
        color: Line color
        line_width: Line width
        line_style: Line style
        zorder: Drawing order
    """
    point1 = point_on_circle(center, radius, angle1_degrees)
    point2 = point_on_circle(center, radius, angle2_degrees)
    ax.plot([point1[0], point2[0]], [point1[1], point2[1]], 
            color=color, linewidth=line_width, linestyle=line_style, 
            zorder=zorder, solid_capstyle='round')


def draw_tangent(ax, center, radius, angle_degrees, length, color, line_width,
                 line_style='-', zorder=15):
    """
    Draw a tangent line at a point on the circle.
    
    Args:
        ax: Matplotlib axes
        center: (x, y) tuple
        radius: Circle radius
        angle_degrees: Angle where tangent touches the circle
        length: Total length of the tangent line (extends equally both directions)
        color: Line color
        line_width: Line width
        line_style: Line style
        zorder: Drawing order
    """
    touch_point = point_on_circle(center, radius, angle_degrees)
    
    # Tangent is perpendicular to radius, so add 90° to get tangent direction
    tangent_angle = np.radians(angle_degrees + 90)
    tangent_dir = np.array([np.cos(tangent_angle), np.sin(tangent_angle)])
    
    point1 = touch_point - (length / 2) * tangent_dir
    point2 = touch_point + (length / 2) * tangent_dir
    
    ax.plot([point1[0], point2[0]], [point1[1], point2[1]], 
            color=color, linewidth=line_width, linestyle=line_style, 
            zorder=zorder, solid_capstyle='round')


def draw_arc(ax, center, radius, start_angle, end_angle, color, line_width,
             line_style='-', zorder=15):
    """
    Draw an arc (portion of the circle circumference).
    
    Args:
        ax: Matplotlib axes
        center: (x, y) tuple
        radius: Circle radius
        start_angle: Starting angle in degrees
        end_angle: Ending angle in degrees
        color: Line color
        line_width: Line width
        line_style: Line style (note: matplotlib Arc doesn't support all styles)
        zorder: Drawing order
    """
    # Ensure we draw the shorter arc if needed
    # For now, draw from start to end going counterclockwise
    
    # Use parametric plotting for better line style support
    if end_angle < start_angle:
        end_angle += 360
    
    theta = np.linspace(np.radians(start_angle), np.radians(end_angle), 100)
    x = center[0] + radius * np.cos(theta)
    y = center[1] + radius * np.sin(theta)
    
    ax.plot(x, y, color=color, linewidth=line_width, linestyle=line_style,
            zorder=zorder, solid_capstyle='round')


def draw_sector(ax, center, radius, start_angle, end_angle, color, 
                fill_alpha=0.3, edge_color=None, line_width=0, zorder=5):
    """
    Draw a sector (pie slice) of the circle.
    
    Args:
        ax: Matplotlib axes
        center: (x, y) tuple
        radius: Circle radius
        start_angle: Starting angle in degrees
        end_angle: Ending angle in degrees
        color: Fill color
        fill_alpha: Fill transparency
        edge_color: Edge color (None for no edge)
        line_width: Edge line width
        zorder: Drawing order
    """
    wedge = Wedge(center, radius, start_angle, end_angle,
                  facecolor=color, alpha=fill_alpha,
                  edgecolor=edge_color, linewidth=line_width,
                  zorder=zorder)
    ax.add_patch(wedge)


def draw_segment(ax, center, radius, start_angle, end_angle, color,
                 fill_alpha=0.3, zorder=5):
    """
    Draw a segment (area between a chord and its arc).
    
    Args:
        ax: Matplotlib axes
        center: (x, y) tuple
        radius: Circle radius
        start_angle: Starting angle in degrees
        end_angle: Ending angle in degrees
        color: Fill color
        fill_alpha: Fill transparency
        zorder: Drawing order
    """
    # Create the segment as a polygon
    # Arc points
    if end_angle < start_angle:
        end_angle += 360
    
    theta = np.linspace(np.radians(start_angle), np.radians(end_angle), 50)
    arc_x = center[0] + radius * np.cos(theta)
    arc_y = center[1] + radius * np.sin(theta)
    
    # Combine into polygon (arc points form the curved edge, endpoints connect as chord)
    vertices = np.column_stack([arc_x, arc_y])
    
    segment = Polygon(vertices, closed=True, facecolor=color, alpha=fill_alpha,
                      edgecolor='none', zorder=zorder)
    ax.add_patch(segment)


def draw_central_angle_arc(ax, center, angle1, angle2, radius_fraction, 
                           color, line_width, zorder=15):
    """
    Draw an arc marking a central angle.
    
    Args:
        ax: Matplotlib axes
        center: (x, y) tuple
        angle1: First angle in degrees
        angle2: Second angle in degrees
        radius_fraction: Size of arc as fraction of circle radius (e.g., 0.2)
        color: Arc color
        line_width: Line width
        zorder: Drawing order
    """
    arc_radius = radius_fraction  # This will be multiplied by actual radius in caller
    
    # Ensure correct arc direction (smaller arc)
    diff = (angle2 - angle1) % 360
    if diff > 180:
        angle1, angle2 = angle2, angle1
    
    theta = np.linspace(np.radians(angle1), np.radians(angle2), 50)
    x = center[0] + arc_radius * np.cos(theta)
    y = center[1] + arc_radius * np.sin(theta)
    
    ax.plot(x, y, color=color, linewidth=line_width, zorder=zorder,
            solid_capstyle='round')


def draw_right_angle_marker(ax, vertex, arm1_dir, arm2_dir, size, color, 
                            line_width, zorder=15):
    """
    Draw a small square to mark a right angle.
    
    Args:
        ax: Matplotlib axes
        vertex: (x, y) tuple - the vertex of the angle
        arm1_dir: Unit vector direction of first arm
        arm2_dir: Unit vector direction of second arm
        size: Size of the square
        color: Marker color
        line_width: Line width
        zorder: Drawing order
    """
    # Normalize directions
    arm1_dir = np.array(arm1_dir) / np.linalg.norm(arm1_dir)
    arm2_dir = np.array(arm2_dir) / np.linalg.norm(arm2_dir)
    
    vertex = np.array(vertex)
    
    p1 = vertex + size * arm1_dir
    p2 = vertex + size * arm1_dir + size * arm2_dir
    p3 = vertex + size * arm2_dir
    
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=line_width, 
            zorder=zorder)
    ax.plot([p2[0], p3[0]], [p2[1], p3[1]], color=color, linewidth=line_width, 
            zorder=zorder)


def draw_point_on_circle(ax, center, radius, angle_degrees, color, marker_size,
                         marker_style='o', zorder=20):
    """
    Draw a point on the circle circumference.
    
    Args:
        ax: Matplotlib axes
        center: (x, y) tuple
        radius: Circle radius
        angle_degrees: Angle of the point
        color: Point color
        marker_size: Size of the marker
        marker_style: Marker style ('o', 'x', etc.)
        zorder: Drawing order
    
    Returns:
        numpy array [x, y] of the point location
    """
    point = point_on_circle(center, radius, angle_degrees)
    ax.plot(point[0], point[1], marker_style, color=color, markersize=marker_size,
            zorder=zorder)
    return point


def draw_label(ax, position, text, color, font_size, direction='auto',
               distance=0.3, reference_point=None, white_background=True, zorder=100):
    """
    Draw a label at or near a position.
    
    Args:
        ax: Matplotlib axes
        position: (x, y) base position
        text: Label text (can include LaTeX)
        color: Text color
        font_size: Font size
        direction: 'auto', 'above', 'below', 'left', 'right', or angle in degrees
        distance: Distance from position
        reference_point: Point to move away from for 'auto' direction
        white_background: Whether to add white background
        zorder: Drawing order
    """
    position = np.array(position)
    
    # Determine offset direction
    if direction == 'auto' and reference_point is not None:
        # Move away from reference point
        ref = np.array(reference_point)
        offset_dir = position - ref
        if np.linalg.norm(offset_dir) > 1e-10:
            offset_dir = offset_dir / np.linalg.norm(offset_dir)
        else:
            offset_dir = np.array([0, 1])
    elif direction == 'above':
        offset_dir = np.array([0, 1])
    elif direction == 'below':
        offset_dir = np.array([0, -1])
    elif direction == 'left':
        offset_dir = np.array([-1, 0])
    elif direction == 'right':
        offset_dir = np.array([1, 0])
    elif isinstance(direction, (int, float)):
        # Direction is an angle in degrees
        angle_rad = np.radians(direction)
        offset_dir = np.array([np.cos(angle_rad), np.sin(angle_rad)])
    else:
        offset_dir = np.array([0, 1])  # Default to above
    
    label_pos = position + distance * offset_dir
    
    bbox_props = None
    if white_background:
        bbox_props = dict(boxstyle='round,pad=0.15', facecolor='white',
                         edgecolor='none', alpha=0.9)
    
    ax.text(label_pos[0], label_pos[1], text, fontsize=font_size, color=color,
            ha='center', va='center', zorder=zorder, bbox=bbox_props)


def draw_line_label(ax, point1, point2, text, color, font_size, position=0.5,
                    direction='auto', distance=0.3, white_background=True, zorder=100):
    """
    Draw a label along a line (like for radius, diameter, chord).
    
    Args:
        ax: Matplotlib axes
        point1, point2: Endpoints of the line
        text: Label text
        color: Text color
        font_size: Font size
        position: Position along line (0=point1, 0.5=middle, 1=point2)
        direction: 'auto' (perpendicular outward), 'above', 'below', etc.
        distance: Distance from line
        white_background: Whether to add white background
        zorder: Drawing order
    """
    point1 = np.array(point1)
    point2 = np.array(point2)
    
    # Position along the line
    label_base = point1 + position * (point2 - point1)
    
    # Get perpendicular direction
    line_vec = point2 - point1
    perp = np.array([-line_vec[1], line_vec[0]])
    if np.linalg.norm(perp) > 1e-10:
        perp = perp / np.linalg.norm(perp)
    
    if direction == 'auto':
        # Default to one side (positive perpendicular)
        offset_dir = perp
    elif direction == 'above':
        offset_dir = np.array([0, 1])
    elif direction == 'below':
        offset_dir = np.array([0, -1])
    elif direction == 'left':
        offset_dir = np.array([-1, 0])
    elif direction == 'right':
        offset_dir = np.array([1, 0])
    else:
        offset_dir = perp
    
    label_pos = label_base + distance * offset_dir
    
    bbox_props = None
    if white_background:
        bbox_props = dict(boxstyle='round,pad=0.15', facecolor='white',
                         edgecolor='none', alpha=0.9)
    
    ax.text(label_pos[0], label_pos[1], text, fontsize=font_size, color=color,
            ha='center', va='center', zorder=zorder, bbox=bbox_props)


def draw_arc_label(ax, center, radius, start_angle, end_angle, text, color,
                   font_size, distance=0.3, white_background=True, zorder=100):
    """
    Draw a label for an arc, positioned at the arc's midpoint.
    
    Args:
        ax: Matplotlib axes
        center: Circle center
        radius: Circle radius
        start_angle, end_angle: Arc angles in degrees
        text: Label text
        color: Text color
        font_size: Font size
        distance: Distance outward from arc
        white_background: Whether to add white background
        zorder: Drawing order
    """
    # Find midpoint angle
    if end_angle < start_angle:
        end_angle += 360
    mid_angle = (start_angle + end_angle) / 2
    
    # Position on arc
    arc_point = point_on_circle(center, radius, mid_angle)
    
    # Move outward from center
    outward_dir = arc_point - np.array(center)
    if np.linalg.norm(outward_dir) > 1e-10:
        outward_dir = outward_dir / np.linalg.norm(outward_dir)
    
    label_pos = arc_point + distance * outward_dir
    
    bbox_props = None
    if white_background:
        bbox_props = dict(boxstyle='round,pad=0.15', facecolor='white',
                         edgecolor='none', alpha=0.9)
    
    ax.text(label_pos[0], label_pos[1], text, fontsize=font_size, color=color,
            ha='center', va='center', zorder=zorder, bbox=bbox_props)


def auto_set_limits(ax, center, radius, padding=0.5):
    """
    Automatically set axis limits based on circle.
    
    Args:
        ax: Matplotlib axes
        center: (x, y) tuple
        radius: Circle radius
        padding: Padding around the circle
    """
    x_min = center[0] - radius - padding
    x_max = center[0] + radius + padding
    y_min = center[1] - radius - padding
    y_max = center[1] + radius + padding
    
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)


def get_chord_length(radius, angle1_degrees, angle2_degrees):
    """
    Calculate the length of a chord.
    
    Args:
        radius: Circle radius
        angle1_degrees, angle2_degrees: Angles of chord endpoints
    
    Returns:
        Chord length
    """
    angle_diff = abs(angle2_degrees - angle1_degrees)
    if angle_diff > 180:
        angle_diff = 360 - angle_diff
    return 2 * radius * np.sin(np.radians(angle_diff / 2))


def get_arc_length(radius, angle1_degrees, angle2_degrees):
    """
    Calculate the length of an arc.
    
    Args:
        radius: Circle radius
        angle1_degrees, angle2_degrees: Angles of arc endpoints
    
    Returns:
        Arc length
    """
    angle_diff = abs(angle2_degrees - angle1_degrees)
    if angle_diff > 180:
        angle_diff = 360 - angle_diff
    return radius * np.radians(angle_diff)


def get_sector_area(radius, angle1_degrees, angle2_degrees):
    """
    Calculate the area of a sector.
    
    Args:
        radius: Circle radius
        angle1_degrees, angle2_degrees: Angles of sector
    
    Returns:
        Sector area
    """
    angle_diff = abs(angle2_degrees - angle1_degrees)
    if angle_diff > 180:
        angle_diff = 360 - angle_diff
    return 0.5 * radius**2 * np.radians(angle_diff)


def get_segment_area(radius, angle1_degrees, angle2_degrees):
    """
    Calculate the area of a segment.
    
    Args:
        radius: Circle radius
        angle1_degrees, angle2_degrees: Angles of segment
    
    Returns:
        Segment area
    """
    angle_diff = abs(angle2_degrees - angle1_degrees)
    if angle_diff > 180:
        angle_diff = 360 - angle_diff
    theta = np.radians(angle_diff)
    return 0.5 * radius**2 * (theta - np.sin(theta))

