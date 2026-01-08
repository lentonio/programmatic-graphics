"""
Utility functions for drawing quadrilateral diagrams.
Supports various quadrilateral types with labeled vertices, sides, angles, and markers.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Polygon, FancyArrowPatch
from matplotlib.lines import Line2D


# Direction vectors for label positioning
DIRECTIONS = {
    'above': (0, 1),
    'below': (0, -1),
    'left': (-1, 0),
    'right': (1, 0),
    'above left': (-0.707, 0.707),
    'above right': (0.707, 0.707),
    'below left': (-0.707, -0.707),
    'below right': (0.707, -0.707),
}


def get_quadrilateral_vertices_from_coordinates(coords):
    """
    Create vertices array from coordinate list.
    
    Args:
        coords: List of 4 (x, y) tuples for vertices A, B, C, D
    
    Returns:
        numpy array of shape (4, 2)
    """
    return np.array(coords)


def get_centroid(vertices):
    """Get the centroid of a quadrilateral."""
    return np.mean(vertices, axis=0)


def rotate_points(points, angle_deg, center=(0, 0)):
    """Rotate points around a center by given angle in degrees."""
    angle_rad = np.radians(angle_deg)
    cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)
    rotation_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
    
    centered = points - np.array(center)
    rotated = np.dot(centered, rotation_matrix.T)
    return rotated + np.array(center)


# --- Preset Shape Generators ---

def get_square(side_length, center=(0, 0), rotation=0):
    """Generate a square centered at given point."""
    half = side_length / 2
    vertices = np.array([
        [-half, -half],  # A (bottom-left)
        [half, -half],   # B (bottom-right)
        [half, half],    # C (top-right)
        [-half, half],   # D (top-left)
    ])
    if rotation != 0:
        vertices = rotate_points(vertices, rotation)
    return vertices + np.array(center)


def get_rectangle(width, height, center=(0, 0), rotation=0):
    """Generate a rectangle centered at given point."""
    hw, hh = width / 2, height / 2
    vertices = np.array([
        [-hw, -hh],  # A
        [hw, -hh],   # B
        [hw, hh],    # C
        [-hw, hh],   # D
    ])
    if rotation != 0:
        vertices = rotate_points(vertices, rotation)
    return vertices + np.array(center)


def get_parallelogram(base, side, angle_deg, center=(0, 0), rotation=0):
    """
    Generate a parallelogram.
    
    Args:
        base: Length of the base (AB and DC)
        side: Length of the side (AD and BC)
        angle_deg: Interior angle at A (between base and side)
    """
    angle_rad = np.radians(angle_deg)
    offset_x = side * np.cos(angle_rad)
    offset_y = side * np.sin(angle_rad)
    
    vertices = np.array([
        [0, 0],                      # A
        [base, 0],                   # B
        [base + offset_x, offset_y], # C
        [offset_x, offset_y],        # D
    ])
    
    # Center the shape
    centroid = get_centroid(vertices)
    vertices = vertices - centroid + np.array(center)
    
    if rotation != 0:
        vertices = rotate_points(vertices, rotation, center)
    return vertices


def get_rhombus(side, angle_deg, center=(0, 0), rotation=0):
    """
    Generate a rhombus (all sides equal).
    
    Args:
        side: Length of all sides
        angle_deg: Interior angle at A
    """
    return get_parallelogram(side, side, angle_deg, center, rotation)


def get_trapezium(parallel_top, parallel_bottom, height, offset=0, center=(0, 0), rotation=0):
    """
    Generate a trapezium (one pair of parallel sides).
    
    Args:
        parallel_top: Length of top parallel side (DC)
        parallel_bottom: Length of bottom parallel side (AB)
        height: Perpendicular distance between parallel sides
        offset: Horizontal offset of top side from center (positive = right)
    """
    hb = parallel_bottom / 2
    ht = parallel_top / 2
    
    vertices = np.array([
        [-hb, 0],                    # A
        [hb, 0],                     # B
        [offset + ht, height],       # C
        [offset - ht, height],       # D
    ])
    
    # Center the shape
    centroid = get_centroid(vertices)
    vertices = vertices - centroid + np.array(center)
    
    if rotation != 0:
        vertices = rotate_points(vertices, rotation, center)
    return vertices


def get_kite(d1, d2, split_ratio=0.3, center=(0, 0), rotation=0):
    """
    Generate a kite shape.
    
    Args:
        d1: Length of the horizontal diagonal (AC)
        d2: Length of the vertical diagonal (BD)
        split_ratio: Where the diagonals cross (0-1, from bottom)
    """
    h1 = d1 / 2
    v_bottom = d2 * split_ratio
    v_top = d2 * (1 - split_ratio)
    
    vertices = np.array([
        [-h1, 0],       # A (left)
        [0, -v_bottom], # B (bottom)
        [h1, 0],        # C (right)
        [0, v_top],     # D (top)
    ])
    
    vertices = vertices + np.array(center)
    
    if rotation != 0:
        vertices = rotate_points(vertices, rotation, center)
    return vertices


def get_isosceles_trapezium(parallel_top, parallel_bottom, height, center=(0, 0), rotation=0):
    """Generate an isosceles trapezium (legs are equal length)."""
    return get_trapezium(parallel_top, parallel_bottom, height, offset=0, center=center, rotation=rotation)


# --- Drawing Functions ---

def draw_quadrilateral(ax, vertices, color='#4C5B64', line_width=2.5, line_style='-', 
                       fill=False, fill_color=None, fill_alpha=0.2, zorder=10):
    """
    Draw the quadrilateral outline.
    
    Args:
        ax: Matplotlib axes
        vertices: numpy array of shape (4, 2) for vertices A, B, C, D
        color: Line color
        line_width: Line width
        line_style: '-', '--', ':', etc.
        fill: Whether to fill the quadrilateral
        fill_color: Fill color (defaults to line color)
        fill_alpha: Fill transparency
        zorder: Drawing order
    """
    # Close the shape by appending first vertex
    closed_vertices = np.vstack([vertices, vertices[0]])
    
    # Draw outline
    ax.plot(closed_vertices[:, 0], closed_vertices[:, 1], 
            color=color, linewidth=line_width, linestyle=line_style, 
            solid_capstyle='round', solid_joinstyle='round', zorder=zorder)
    
    # Fill if requested
    if fill:
        fc = fill_color if fill_color else color
        polygon = Polygon(vertices, closed=True, facecolor=fc, 
                         edgecolor='none', alpha=fill_alpha, zorder=zorder-1)
        ax.add_patch(polygon)


def draw_vertex_label(ax, vertex, label, direction='auto', distance=0.5, 
                      color='#4C5B64', font_size=16, centroid=None,
                      white_background=True, zorder=100):
    """
    Draw a label at a vertex.
    
    Args:
        vertex: (x, y) position of the vertex
        label: Text to display (can include LaTeX)
        direction: 'auto' or one of DIRECTIONS keys
        distance: Distance from vertex
        centroid: Center of quadrilateral (for auto direction)
    """
    if not label:
        return
    
    if direction == 'auto' and centroid is not None:
        # Point away from centroid
        dir_vec = np.array(vertex) - np.array(centroid)
        dir_vec = dir_vec / (np.linalg.norm(dir_vec) + 1e-10)
    elif direction in DIRECTIONS:
        dir_vec = np.array(DIRECTIONS[direction])
    else:
        dir_vec = np.array([0, 1])  # default to above
    
    label_pos = np.array(vertex) + dir_vec * distance
    
    bbox = dict(boxstyle='round,pad=0.1', facecolor='white', edgecolor='none', alpha=0.8) if white_background else None
    
    ax.text(label_pos[0], label_pos[1], label, fontsize=font_size, 
            ha='center', va='center', color=color, zorder=zorder, bbox=bbox)


def draw_side_label(ax, p1, p2, label, position=0.5, direction='auto', distance=0.4,
                    color='#4C5B64', font_size=14, centroid=None,
                    white_background=True, zorder=100):
    """
    Draw a label along a side.
    
    Args:
        p1, p2: Endpoints of the side
        label: Text to display
        position: 0-1, where along the side to place label
        direction: 'auto', 'above', 'below', 'left', 'right'
        distance: Perpendicular distance from side
        centroid: Center of shape (for auto direction)
    """
    if not label:
        return
    
    # Point along the side
    mid = np.array(p1) * (1 - position) + np.array(p2) * position
    
    # Perpendicular direction
    side_vec = np.array(p2) - np.array(p1)
    perp = np.array([-side_vec[1], side_vec[0]])
    perp = perp / (np.linalg.norm(perp) + 1e-10)
    
    if direction == 'auto' and centroid is not None:
        # Point away from centroid
        to_centroid = np.array(centroid) - mid
        if np.dot(perp, to_centroid) > 0:
            perp = -perp
    elif direction == 'below' or direction == 'left':
        if perp[1] > 0 or (perp[1] == 0 and perp[0] > 0):
            perp = -perp
    elif direction == 'above' or direction == 'right':
        if perp[1] < 0 or (perp[1] == 0 and perp[0] < 0):
            perp = -perp
    
    label_pos = mid + perp * distance
    
    bbox = dict(boxstyle='round,pad=0.1', facecolor='white', edgecolor='none', alpha=0.8) if white_background else None
    
    ax.text(label_pos[0], label_pos[1], label, fontsize=font_size,
            ha='center', va='center', color=color, zorder=zorder, bbox=bbox)


def get_vertex_angle(vertices, vertex_idx):
    """
    Calculate the interior angle at a vertex.
    
    Args:
        vertices: Array of quadrilateral vertices
        vertex_idx: Index of the vertex (0=A, 1=B, 2=C, 3=D)
    
    Returns:
        Angle in degrees
    """
    n = len(vertices)
    prev_idx = (vertex_idx - 1) % n
    next_idx = (vertex_idx + 1) % n
    
    v = vertices[vertex_idx]
    v_prev = vertices[prev_idx]
    v_next = vertices[next_idx]
    
    vec1 = v_prev - v
    vec2 = v_next - v
    
    cos_angle = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-10)
    cos_angle = np.clip(cos_angle, -1, 1)
    
    return np.degrees(np.arccos(cos_angle))


def draw_angle_arc(ax, vertices, vertex_idx, radius=0.5, color='#4C5B64', 
                   line_width=2, zorder=15):
    """
    Draw an arc showing the interior angle at a vertex.
    """
    n = len(vertices)
    prev_idx = (vertex_idx - 1) % n
    next_idx = (vertex_idx + 1) % n
    
    v = vertices[vertex_idx]
    v_prev = vertices[prev_idx]
    v_next = vertices[next_idx]
    
    vec1 = v_prev - v
    vec2 = v_next - v
    
    angle1 = np.degrees(np.arctan2(vec1[1], vec1[0]))
    angle2 = np.degrees(np.arctan2(vec2[1], vec2[0]))
    
    # Ensure we draw the interior angle (smaller arc)
    if angle1 > angle2:
        angle1, angle2 = angle2, angle1
    if angle2 - angle1 > 180:
        angle1, angle2 = angle2, angle1 + 360
    
    arc = Arc(v, 2*radius, 2*radius, angle=0, theta1=angle1, theta2=angle2,
              color=color, linewidth=line_width, zorder=zorder)
    ax.add_patch(arc)


def draw_right_angle_marker(ax, vertices, vertex_idx, size=0.4, color='#4C5B64',
                            line_width=2, zorder=15):
    """
    Draw a square marker indicating a right angle.
    """
    n = len(vertices)
    prev_idx = (vertex_idx - 1) % n
    next_idx = (vertex_idx + 1) % n
    
    v = vertices[vertex_idx]
    v_prev = vertices[prev_idx]
    v_next = vertices[next_idx]
    
    # Unit vectors along each side
    vec1 = v_prev - v
    vec1 = vec1 / (np.linalg.norm(vec1) + 1e-10) * size
    
    vec2 = v_next - v
    vec2 = vec2 / (np.linalg.norm(vec2) + 1e-10) * size
    
    # Draw the square
    p1 = v + vec1
    p2 = v + vec1 + vec2
    p3 = v + vec2
    
    ax.plot([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]], 
            color=color, linewidth=line_width, zorder=zorder)


def draw_angle_label(ax, vertices, vertex_idx, label, radius=0.5, distance=0.3,
                     color='#4C5B64', font_size=14, white_background=True, zorder=100):
    """
    Draw a label for an angle.
    """
    if not label:
        return
    
    n = len(vertices)
    prev_idx = (vertex_idx - 1) % n
    next_idx = (vertex_idx + 1) % n
    
    v = vertices[vertex_idx]
    v_prev = vertices[prev_idx]
    v_next = vertices[next_idx]
    
    # Bisector direction
    vec1 = v_prev - v
    vec1 = vec1 / (np.linalg.norm(vec1) + 1e-10)
    
    vec2 = v_next - v
    vec2 = vec2 / (np.linalg.norm(vec2) + 1e-10)
    
    bisector = vec1 + vec2
    bisector = bisector / (np.linalg.norm(bisector) + 1e-10)
    
    label_pos = v + bisector * (radius + distance)
    
    bbox = dict(boxstyle='round,pad=0.1', facecolor='white', edgecolor='none', alpha=0.8) if white_background else None
    
    ax.text(label_pos[0], label_pos[1], label, fontsize=font_size,
            ha='center', va='center', color=color, zorder=zorder, bbox=bbox)


def draw_tick_marks(ax, p1, p2, num_ticks, tick_length=0.25, color='#4C5B64',
                    line_width=2, zorder=20):
    """
    Draw tick marks on a side to indicate equal lengths.
    """
    if num_ticks <= 0:
        return
    
    mid = (np.array(p1) + np.array(p2)) / 2
    side_vec = np.array(p2) - np.array(p1)
    side_len = np.linalg.norm(side_vec)
    
    # Perpendicular direction
    perp = np.array([-side_vec[1], side_vec[0]])
    perp = perp / (side_len + 1e-10) * tick_length
    
    # Spacing between ticks
    spacing = 0.15
    
    for i in range(num_ticks):
        offset = (i - (num_ticks - 1) / 2) * spacing
        tick_center = mid + (side_vec / side_len) * offset
        
        ax.plot([tick_center[0] - perp[0]/2, tick_center[0] + perp[0]/2],
                [tick_center[1] - perp[1]/2, tick_center[1] + perp[1]/2],
                color=color, linewidth=line_width, zorder=zorder)


def draw_parallel_marks(ax, p1, p2, num_arrows, arrow_size=0.3, color='#4C5B64',
                        line_width=2, zorder=20):
    """
    Draw arrow marks on a side to indicate parallel sides.
    
    Args:
        num_arrows: Number of arrow heads (1, 2, or 3)
    """
    if num_arrows <= 0:
        return
    
    mid = (np.array(p1) + np.array(p2)) / 2
    side_vec = np.array(p2) - np.array(p1)
    side_len = np.linalg.norm(side_vec)
    unit_vec = side_vec / (side_len + 1e-10)
    
    # Perpendicular for arrow wings
    perp = np.array([-unit_vec[1], unit_vec[0]]) * arrow_size * 0.4
    
    # Spacing between arrows
    spacing = 0.2
    
    for i in range(num_arrows):
        offset = (i - (num_arrows - 1) / 2) * spacing
        arrow_tip = mid + unit_vec * offset
        arrow_back = arrow_tip - unit_vec * arrow_size * 0.5
        
        # Draw arrow head (two lines forming a V pointing along the side)
        ax.plot([arrow_back[0] + perp[0], arrow_tip[0], arrow_back[0] - perp[0]],
                [arrow_back[1] + perp[1], arrow_tip[1], arrow_back[1] - perp[1]],
                color=color, linewidth=line_width, zorder=zorder)


def draw_diagonal(ax, vertices, diagonal='AC', color='#4C5B64', line_width=2,
                  line_style='--', label='', label_pos=0.5, label_dist=0.3,
                  font_size=14, white_background=True, zorder=8):
    """
    Draw a diagonal line.
    
    Args:
        diagonal: 'AC' or 'BD'
    """
    if diagonal == 'AC':
        p1, p2 = vertices[0], vertices[2]
    else:  # BD
        p1, p2 = vertices[1], vertices[3]
    
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 
            color=color, linewidth=line_width, linestyle=line_style, zorder=zorder)
    
    if label:
        centroid = get_centroid(vertices)
        draw_side_label(ax, p1, p2, label, position=label_pos, direction='auto',
                       distance=label_dist, color=color, font_size=font_size,
                       centroid=centroid, white_background=white_background, zorder=100)


def get_side_length(vertices, side_idx):
    """
    Get the length of a side.
    
    Args:
        side_idx: 0=AB, 1=BC, 2=CD, 3=DA
    """
    n = len(vertices)
    p1 = vertices[side_idx]
    p2 = vertices[(side_idx + 1) % n]
    return np.linalg.norm(p2 - p1)


def auto_set_limits(ax, vertices, padding=1.0):
    """
    Automatically set axis limits based on vertices.
    """
    x_min, y_min = vertices.min(axis=0)
    x_max, y_max = vertices.max(axis=0)
    
    # Add padding
    x_range = x_max - x_min
    y_range = y_max - y_min
    
    # Make it square-ish
    max_range = max(x_range, y_range)
    
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2
    
    half_range = max_range / 2 + padding
    
    ax.set_xlim(x_center - half_range, x_center + half_range)
    ax.set_ylim(y_center - half_range, y_center + half_range)
    ax.set_aspect('equal')

