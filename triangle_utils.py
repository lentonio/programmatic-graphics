"""
Triangle diagram utilities for educational math graphics.
Provides functions to draw triangles with labeled sides, angles, and special markers.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, FancyBboxPatch, Rectangle, Polygon
from matplotlib.transforms import Affine2D
import matplotlib.patches as mpatches


# Direction vectors for label positioning (TikZ-style)
DIRECTIONS = {
    'above': np.array([0, 1]),
    'below': np.array([0, -1]),
    'left': np.array([-1, 0]),
    'right': np.array([1, 0]),
    'above left': np.array([-0.707, 0.707]),
    'above right': np.array([0.707, 0.707]),
    'below left': np.array([-0.707, -0.707]),
    'below right': np.array([0.707, -0.707]),
    'center': np.array([0, 0]),
    'auto': None  # Will be computed based on context
}


def get_triangle_vertices_from_sss(a, b, c, base_center=(0, 0), base_angle=0):
    """
    Compute triangle vertices from three side lengths (SSS).
    
    Args:
        a, b, c: Side lengths (a opposite to A, b opposite to B, c opposite to C)
                 Convention: c is the base, a and b are the other two sides
        base_center: Center point of the base (side c)
        base_angle: Rotation angle of the base in degrees
    
    Returns:
        numpy array of shape (3, 2) with vertices [A, B, C]
        where C is at the apex, and A-B is the base
    """
    # Check triangle inequality
    if not (a + b > c and b + c > a and a + c > b):
        raise ValueError("Invalid triangle: side lengths violate triangle inequality")
    
    # Place base along x-axis centered at origin first
    half_c = c / 2
    A = np.array([-half_c, 0])
    B = np.array([half_c, 0])
    
    # Find C using law of cosines: cos(A) = (b² + c² - a²) / (2bc)
    cos_A = (b**2 + c**2 - a**2) / (2 * b * c)
    cos_A = np.clip(cos_A, -1, 1)  # Handle numerical errors
    angle_A = np.arccos(cos_A)
    
    # C is at distance b from A, at angle angle_A from the base
    C = A + b * np.array([np.cos(angle_A), np.sin(angle_A)])
    
    # Apply rotation
    if base_angle != 0:
        theta = np.radians(base_angle)
        rotation_matrix = np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta), np.cos(theta)]
        ])
        A = rotation_matrix @ A
        B = rotation_matrix @ B
        C = rotation_matrix @ C
    
    # Translate to base_center
    center_offset = np.array(base_center)
    A = A + center_offset
    B = B + center_offset
    C = C + center_offset
    
    return np.array([A, B, C])


def get_triangle_vertices_from_coordinates(coords):
    """
    Convert coordinate input to vertices array.
    
    Args:
        coords: List of 3 tuples [(x1, y1), (x2, y2), (x3, y3)]
    
    Returns:
        numpy array of shape (3, 2)
    """
    return np.array(coords)


def draw_triangle(ax, vertices, color, line_width, line_style='-', fill=False, 
                  fill_color=None, fill_alpha=0.3, zorder=10):
    """
    Draw the triangle edges.
    
    Args:
        ax: Matplotlib axes
        vertices: numpy array of shape (3, 2) with vertices [A, B, C]
        color: Edge color (hex string)
        line_width: Line width
        line_style: Line style ('-', '--', ':')
        fill: Whether to fill the triangle
        fill_color: Fill color (defaults to edge color if None)
        fill_alpha: Fill transparency
        zorder: Drawing order
    """
    # Close the triangle by appending the first vertex
    closed_vertices = np.vstack([vertices, vertices[0]])
    
    # Draw edges
    ax.plot(closed_vertices[:, 0], closed_vertices[:, 1],
            color=color, linewidth=line_width, linestyle=line_style, 
            zorder=zorder, solid_capstyle='round', solid_joinstyle='round')
    
    # Fill if requested
    if fill:
        fc = fill_color if fill_color else color
        triangle_patch = Polygon(vertices, closed=True, 
                                  facecolor=fc, alpha=fill_alpha,
                                  edgecolor='none', zorder=zorder-1)
        ax.add_patch(triangle_patch)


def get_side_midpoint(vertices, side_index):
    """
    Get the midpoint of a triangle side.
    
    Args:
        vertices: numpy array of shape (3, 2)
        side_index: 0 for A-B, 1 for B-C, 2 for C-A
    
    Returns:
        numpy array of shape (2,) with midpoint coordinates
    """
    i = side_index
    j = (side_index + 1) % 3
    return (vertices[i] + vertices[j]) / 2


def get_side_length(vertices, side_index):
    """
    Get the length of a triangle side.
    
    Args:
        vertices: numpy array of shape (3, 2)
        side_index: 0 for A-B, 1 for B-C, 2 for C-A
    
    Returns:
        float: length of the side
    """
    i = side_index
    j = (side_index + 1) % 3
    return np.linalg.norm(vertices[j] - vertices[i])


def get_side_angle(vertices, side_index):
    """
    Get the angle of a side relative to horizontal (in degrees).
    
    Args:
        vertices: numpy array of shape (3, 2)
        side_index: 0 for A-B, 1 for B-C, 2 for C-A
    
    Returns:
        float: angle in degrees
    """
    i = side_index
    j = (side_index + 1) % 3
    direction = vertices[j] - vertices[i]
    return np.degrees(np.arctan2(direction[1], direction[0]))


def get_outward_direction(vertices, side_index):
    """
    Get the outward-pointing normal direction for a side.
    
    Args:
        vertices: numpy array of shape (3, 2)
        side_index: 0 for A-B, 1 for B-C, 2 for C-A
    
    Returns:
        numpy array of shape (2,) - unit vector pointing outward
    """
    i = side_index
    j = (side_index + 1) % 3
    k = (side_index + 2) % 3  # The opposite vertex
    
    # Get the side direction and its perpendicular
    side_vec = vertices[j] - vertices[i]
    # Perpendicular (rotate 90° counterclockwise)
    perp = np.array([-side_vec[1], side_vec[0]])
    perp = perp / np.linalg.norm(perp)
    
    # Check which direction is outward (away from opposite vertex)
    midpoint = (vertices[i] + vertices[j]) / 2
    to_opposite = vertices[k] - midpoint
    
    if np.dot(perp, to_opposite) > 0:
        perp = -perp  # Flip to point outward
    
    return perp


def draw_side_label(ax, vertices, side_index, label_text, color, font_size,
                    position=0.5, direction='auto', distance=0.3, 
                    rotate_with_side=False, zorder=100,
                    bbox_style=None, white_background=True):
    """
    Draw a label on a triangle side.
    
    Args:
        ax: Matplotlib axes
        vertices: numpy array of shape (3, 2)
        side_index: 0 for A-B, 1 for B-C, 2 for C-A
        label_text: Text to display (can include LaTeX)
        color: Text color
        font_size: Font size
        position: Position along side (0=start, 0.5=middle, 1=end)
        direction: 'auto', 'above', 'below', etc. or custom direction
        distance: Distance from the side (in data units)
        rotate_with_side: If True, rotate label to align with side
        zorder: Drawing order
        bbox_style: Dict of bbox parameters or None
        white_background: Whether to add white background to label
    """
    i = side_index
    j = (side_index + 1) % 3
    
    # Calculate position along the side
    point = vertices[i] + position * (vertices[j] - vertices[i])
    
    # Determine offset direction
    if direction == 'auto':
        offset_dir = get_outward_direction(vertices, side_index)
    elif direction in DIRECTIONS:
        offset_dir = DIRECTIONS[direction]
        if offset_dir is None:
            offset_dir = get_outward_direction(vertices, side_index)
    else:
        offset_dir = np.array([0, 0])
    
    # Apply offset
    label_pos = point + distance * offset_dir
    
    # Calculate rotation if needed
    rotation = 0
    if rotate_with_side:
        rotation = get_side_angle(vertices, side_index)
        # Keep text readable (not upside down)
        if rotation > 90:
            rotation -= 180
        elif rotation < -90:
            rotation += 180
    
    # Set up bbox
    bbox_props = None
    if white_background:
        bbox_props = dict(boxstyle='round,pad=0.15', facecolor='white', 
                         edgecolor='none', alpha=0.9)
    if bbox_style:
        bbox_props = bbox_style
    
    # Draw the label
    ax.text(label_pos[0], label_pos[1], label_text,
            fontsize=font_size, color=color,
            ha='center', va='center',
            rotation=rotation,
            zorder=zorder,
            bbox=bbox_props)


def get_vertex_angle(vertices, vertex_index):
    """
    Get the interior angle at a vertex (in degrees).
    
    Args:
        vertices: numpy array of shape (3, 2)
        vertex_index: 0, 1, or 2
    
    Returns:
        float: interior angle in degrees
    """
    i = vertex_index
    prev_i = (i - 1) % 3
    next_i = (i + 1) % 3
    
    # Vectors from vertex to adjacent vertices
    v1 = vertices[prev_i] - vertices[i]
    v2 = vertices[next_i] - vertices[i]
    
    # Angle between vectors
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    cos_angle = np.clip(cos_angle, -1, 1)
    
    return np.degrees(np.arccos(cos_angle))


def get_angle_bisector_direction(vertices, vertex_index):
    """
    Get the direction of the angle bisector at a vertex (pointing inward).
    
    Args:
        vertices: numpy array of shape (3, 2)
        vertex_index: 0, 1, or 2
    
    Returns:
        numpy array of shape (2,) - unit vector along bisector (pointing into triangle)
    """
    i = vertex_index
    prev_i = (i - 1) % 3
    next_i = (i + 1) % 3
    
    # Unit vectors from vertex to adjacent vertices
    v1 = vertices[prev_i] - vertices[i]
    v1 = v1 / np.linalg.norm(v1)
    v2 = vertices[next_i] - vertices[i]
    v2 = v2 / np.linalg.norm(v2)
    
    # Bisector is the sum of unit vectors
    bisector = v1 + v2
    if np.linalg.norm(bisector) < 1e-10:
        # Degenerate case (180° angle)
        bisector = np.array([-v1[1], v1[0]])
    else:
        bisector = bisector / np.linalg.norm(bisector)
    
    return bisector


def draw_angle_arc(ax, vertices, vertex_index, color, line_width,
                   radius=0.4, zorder=10):
    """
    Draw an arc marking the angle at a vertex.
    
    Args:
        ax: Matplotlib axes
        vertices: numpy array of shape (3, 2)
        vertex_index: 0, 1, or 2
        color: Arc color
        line_width: Line width
        radius: Arc radius (in data units)
        zorder: Drawing order
    """
    i = vertex_index
    prev_i = (i - 1) % 3
    next_i = (i + 1) % 3
    
    vertex = vertices[i]
    
    # Vectors to adjacent vertices
    v1 = vertices[prev_i] - vertex
    v2 = vertices[next_i] - vertex
    
    # Angles of these vectors
    angle1 = np.degrees(np.arctan2(v1[1], v1[0]))
    angle2 = np.degrees(np.arctan2(v2[1], v2[0]))
    
    # Ensure we draw the interior angle (shorter arc)
    # Normalize angles to [0, 360)
    angle1 = angle1 % 360
    angle2 = angle2 % 360
    
    # Determine which direction to draw the arc
    diff = (angle2 - angle1) % 360
    if diff > 180:
        angle1, angle2 = angle2, angle1
    
    # Create arc
    arc = Arc(vertex, 2*radius, 2*radius, 
              angle=0, theta1=angle1, theta2=angle2,
              color=color, linewidth=line_width, zorder=zorder)
    ax.add_patch(arc)


def draw_right_angle_marker(ax, vertices, vertex_index, color, line_width,
                            size=0.3, zorder=10):
    """
    Draw a small square to mark a right angle.
    
    Args:
        ax: Matplotlib axes
        vertices: numpy array of shape (3, 2)
        vertex_index: 0, 1, or 2
        color: Marker color
        line_width: Line width
        size: Size of the square (in data units)
        zorder: Drawing order
    """
    i = vertex_index
    prev_i = (i - 1) % 3
    next_i = (i + 1) % 3
    
    vertex = vertices[i]
    
    # Unit vectors along the two sides
    v1 = vertices[prev_i] - vertex
    v1 = v1 / np.linalg.norm(v1)
    v2 = vertices[next_i] - vertex
    v2 = v2 / np.linalg.norm(v2)
    
    # Four corners of the right angle marker
    p1 = vertex + size * v1
    p2 = vertex + size * v1 + size * v2
    p3 = vertex + size * v2
    
    # Draw the two lines of the square
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 
            color=color, linewidth=line_width, zorder=zorder)
    ax.plot([p2[0], p3[0]], [p2[1], p3[1]], 
            color=color, linewidth=line_width, zorder=zorder)


def draw_angle_label(ax, vertices, vertex_index, label_text, color, font_size,
                     distance=0.6, direction='auto', zorder=100,
                     white_background=True):
    """
    Draw a label for an angle at a vertex.
    
    Args:
        ax: Matplotlib axes
        vertices: numpy array of shape (3, 2)
        vertex_index: 0, 1, or 2
        label_text: Text to display
        color: Text color
        font_size: Font size
        distance: Distance from vertex along bisector
        direction: 'auto' (along bisector) or a direction string
        zorder: Drawing order
        white_background: Whether to add white background
    """
    vertex = vertices[vertex_index]
    
    # Determine offset direction
    if direction == 'auto':
        offset_dir = get_angle_bisector_direction(vertices, vertex_index)
    elif direction in DIRECTIONS:
        offset_dir = DIRECTIONS[direction]
        if offset_dir is None:
            offset_dir = get_angle_bisector_direction(vertices, vertex_index)
    else:
        offset_dir = get_angle_bisector_direction(vertices, vertex_index)
    
    # Calculate label position
    label_pos = vertex + distance * offset_dir
    
    # Set up bbox
    bbox_props = None
    if white_background:
        bbox_props = dict(boxstyle='round,pad=0.15', facecolor='white', 
                         edgecolor='none', alpha=0.9)
    
    # Draw the label
    ax.text(label_pos[0], label_pos[1], label_text,
            fontsize=font_size, color=color,
            ha='center', va='center',
            zorder=zorder,
            bbox=bbox_props)


def draw_vertex_label(ax, vertices, vertex_index, label_text, color, font_size,
                      distance=0.4, direction='auto', zorder=100,
                      white_background=True):
    """
    Draw a label for a vertex (e.g., "A", "B", "C").
    
    Args:
        ax: Matplotlib axes
        vertices: numpy array of shape (3, 2)
        vertex_index: 0, 1, or 2
        label_text: Text to display
        color: Text color
        font_size: Font size
        distance: Distance from vertex
        direction: 'auto' (away from centroid) or a direction string
        zorder: Drawing order
        white_background: Whether to add white background
    """
    vertex = vertices[vertex_index]
    
    # Determine offset direction
    if direction == 'auto':
        # Point away from triangle centroid
        centroid = np.mean(vertices, axis=0)
        offset_dir = vertex - centroid
        offset_dir = offset_dir / np.linalg.norm(offset_dir)
    elif direction in DIRECTIONS:
        offset_dir = DIRECTIONS[direction]
        if offset_dir is None:
            centroid = np.mean(vertices, axis=0)
            offset_dir = vertex - centroid
            offset_dir = offset_dir / np.linalg.norm(offset_dir)
    else:
        offset_dir = np.array([0, 1])
    
    # Calculate label position
    label_pos = vertex + distance * offset_dir
    
    # Set up bbox
    bbox_props = None
    if white_background:
        bbox_props = dict(boxstyle='round,pad=0.15', facecolor='white', 
                         edgecolor='none', alpha=0.9)
    
    # Draw the label
    ax.text(label_pos[0], label_pos[1], label_text,
            fontsize=font_size, color=color,
            ha='center', va='center',
            zorder=zorder,
            bbox=bbox_props)


def draw_tick_marks(ax, vertices, side_index, num_ticks, color, line_width,
                    tick_length=0.15, zorder=10):
    """
    Draw tick marks on a side to indicate equal lengths.
    
    Args:
        ax: Matplotlib axes
        vertices: numpy array of shape (3, 2)
        side_index: 0 for A-B, 1 for B-C, 2 for C-A
        num_ticks: Number of tick marks (1, 2, or 3 typically)
        color: Tick color
        line_width: Line width
        tick_length: Length of each tick mark
        zorder: Drawing order
    """
    midpoint = get_side_midpoint(vertices, side_index)
    outward = get_outward_direction(vertices, side_index)
    
    # Get side direction for spacing ticks
    i = side_index
    j = (side_index + 1) % 3
    side_dir = vertices[j] - vertices[i]
    side_dir = side_dir / np.linalg.norm(side_dir)
    
    # Spacing between ticks
    tick_spacing = tick_length * 0.8
    
    # Calculate tick positions
    start_offset = -((num_ticks - 1) / 2) * tick_spacing
    
    for t in range(num_ticks):
        offset = start_offset + t * tick_spacing
        tick_center = midpoint + offset * side_dir
        
        # Draw tick perpendicular to side
        p1 = tick_center - (tick_length / 2) * outward
        p2 = tick_center + (tick_length / 2) * outward
        
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]],
                color=color, linewidth=line_width, zorder=zorder)


def create_triangle_figure(figsize=(8, 8), equal_aspect=True):
    """
    Create a figure and axes suitable for triangle diagrams.
    
    Args:
        figsize: Figure size tuple
        equal_aspect: Whether to enforce equal aspect ratio
    
    Returns:
        fig, ax tuple
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    if equal_aspect:
        ax.set_aspect('equal')
    
    # Remove axes by default for clean diagrams
    ax.axis('off')
    
    return fig, ax


def auto_set_limits(ax, vertices, padding=0.5):
    """
    Automatically set axis limits based on triangle vertices.
    
    Args:
        ax: Matplotlib axes
        vertices: numpy array of shape (3, 2)
        padding: Padding around the triangle (in data units)
    """
    x_min, y_min = vertices.min(axis=0) - padding
    x_max, y_max = vertices.max(axis=0) + padding
    
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)


# Preset triangles for convenience
def get_equilateral_triangle(side_length=2, center=(0, 0)):
    """Get vertices for an equilateral triangle."""
    return get_triangle_vertices_from_sss(side_length, side_length, side_length, 
                                          base_center=center)


def get_isoceles_triangle(base=2, leg=2.5, center=(0, 0)):
    """Get vertices for an isoceles triangle (two equal legs)."""
    return get_triangle_vertices_from_sss(leg, leg, base, base_center=center)


def get_right_triangle(base=3, height=4, center=(0, 0)):
    """Get vertices for a right triangle (right angle at origin-side)."""
    hypotenuse = np.sqrt(base**2 + height**2)
    return get_triangle_vertices_from_sss(height, hypotenuse, base, base_center=center)


def get_30_60_90_triangle(short_leg=1, center=(0, 0)):
    """Get vertices for a 30-60-90 triangle."""
    long_leg = short_leg * np.sqrt(3)
    hypotenuse = 2 * short_leg
    return get_triangle_vertices_from_sss(long_leg, hypotenuse, short_leg, base_center=center)


def get_45_45_90_triangle(leg=1, center=(0, 0)):
    """Get vertices for a 45-45-90 triangle."""
    hypotenuse = leg * np.sqrt(2)
    return get_triangle_vertices_from_sss(leg, hypotenuse, leg, base_center=center)

