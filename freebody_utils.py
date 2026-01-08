"""
Utility functions for drawing free-body diagrams.
Supports blocks, particles, inclined planes with force vectors.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyArrowPatch


def draw_force_arrow(ax, start, magnitude, angle_deg, color='#4C5B64',
                     line_width=2.5, label=None, label_pos='end',
                     font_size=14, zorder=15):
    """
    Draw a force arrow.
    
    Args:
        start: starting point (usually on object surface)
        magnitude: arrow length (visual, not actual force value)
        angle_deg: direction in degrees (0=right, 90=up)
        label: force label (e.g., 'W', 'N', 'F')
        label_pos: 'end', 'mid', or 'start'
    """
    angle_rad = np.radians(angle_deg)
    dx = magnitude * np.cos(angle_rad)
    dy = magnitude * np.sin(angle_rad)
    
    end = (start[0] + dx, start[1] + dy)
    
    ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(arrowstyle='->', color=color,
                               lw=line_width, mutation_scale=18),
                zorder=zorder)
    
    if label:
        if label_pos == 'end':
            lx = end[0] + 0.15 * np.cos(angle_rad)
            ly = end[1] + 0.15 * np.sin(angle_rad)
        elif label_pos == 'mid':
            lx = (start[0] + end[0]) / 2 + 0.2 * np.cos(angle_rad + np.pi/2)
            ly = (start[1] + end[1]) / 2 + 0.2 * np.sin(angle_rad + np.pi/2)
        else:  # start
            lx = start[0] - 0.15 * np.cos(angle_rad)
            ly = start[1] - 0.15 * np.sin(angle_rad)
        
        ax.text(lx, ly, label, fontsize=font_size, ha='center', va='center',
                color=color, fontweight='bold', zorder=zorder+1)
    
    return end


def draw_block(ax, center, width=1.0, height=0.8, angle_deg=0,
               color='#4C5B64', fill_color='white', line_width=2.5,
               label=None, font_size=14, zorder=10):
    """
    Draw a rectangular block.
    
    Args:
        center: center position
        width, height: dimensions
        angle_deg: rotation angle
        label: optional label inside block
    """
    angle_rad = np.radians(angle_deg)
    
    # Calculate corners relative to center
    hw, hh = width/2, height/2
    corners_local = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
    
    # Rotate corners
    cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)
    corners = []
    for x, y in corners_local:
        rx = x * cos_a - y * sin_a + center[0]
        ry = x * sin_a + y * cos_a + center[1]
        corners.append((rx, ry))
    
    block = Polygon(corners, closed=True, facecolor=fill_color,
                   edgecolor=color, linewidth=line_width, zorder=zorder)
    ax.add_patch(block)
    
    if label:
        ax.text(center[0], center[1], label, fontsize=font_size,
                ha='center', va='center', color=color, zorder=zorder+1)
    
    return corners


def draw_particle(ax, center, radius=0.15, color='#4C5B64',
                  fill_color='#4C5B64', line_width=2, zorder=10):
    """Draw a particle (filled circle)."""
    circle = Circle(center, radius, facecolor=fill_color,
                   edgecolor=color, linewidth=line_width, zorder=zorder)
    ax.add_patch(circle)


def draw_inclined_plane(ax, base_left, length=3, angle_deg=30,
                        color='#4C5B64', line_width=2.5,
                        show_angle_arc=True, font_size=12, zorder=5):
    """
    Draw an inclined plane (triangle).
    
    Args:
        base_left: left corner of base
        length: length of base
        angle_deg: angle of incline
    
    Returns:
        dict with 'surface_start', 'surface_end', 'surface_angle' for placing objects
    """
    angle_rad = np.radians(angle_deg)
    
    # Calculate vertices
    base_right = (base_left[0] + length, base_left[1])
    top = (base_right[0], base_left[1] + length * np.tan(angle_rad))
    
    # Draw triangle
    triangle = Polygon([base_left, base_right, top], closed=True,
                      facecolor='none', edgecolor=color,
                      linewidth=line_width, zorder=zorder)
    ax.add_patch(triangle)
    
    # Draw hatching on base (ground)
    for i in range(int(length * 4)):
        x = base_left[0] + i * 0.25
        ax.plot([x, x - 0.1], [base_left[1], base_left[1] - 0.15],
               color=color, linewidth=1, zorder=zorder-1)
    
    # Draw angle arc
    if show_angle_arc:
        from matplotlib.patches import Arc
        arc = Arc(base_right, 0.6, 0.6, angle=0, theta1=180-angle_deg, theta2=180,
                 color=color, linewidth=1.5, zorder=zorder)
        ax.add_patch(arc)
        
        # Angle label
        label_angle = np.radians(180 - angle_deg/2)
        ax.text(base_right[0] + 0.5 * np.cos(label_angle),
               base_right[1] + 0.5 * np.sin(label_angle),
               f"{angle_deg}°", fontsize=font_size, ha='center', va='center',
               color=color)
    
    return {
        'surface_start': base_left,
        'surface_end': top,
        'surface_angle': angle_deg,
        'surface_length': length / np.cos(angle_rad)
    }


def draw_ground(ax, x_range, y=0, color='#4C5B64', line_width=2, zorder=5):
    """Draw ground with hatching."""
    ax.plot(x_range, [y, y], color=color, linewidth=line_width, zorder=zorder)
    
    # Hatching
    num_hatches = int((x_range[1] - x_range[0]) * 4)
    for i in range(num_hatches):
        x = x_range[0] + i * 0.25
        ax.plot([x, x - 0.1], [y, y - 0.15], color=color, linewidth=1, zorder=zorder-1)


def get_surface_point(surface_info, fraction):
    """Get a point on the inclined surface."""
    start = surface_info['surface_start']
    end = surface_info['surface_end']
    x = start[0] + fraction * (end[0] - start[0])
    y = start[1] + fraction * (end[1] - start[1])
    return (x, y)


# Preset free-body scenarios
FREEBODY_PRESETS = {
    'Block on flat surface': {
        'type': 'flat',
        'description': 'Stationary block with weight and normal force',
        'forces': [
            {'name': 'W', 'angle': 270, 'mag': 1.2, 'color_key': 'weight'},
            {'name': 'N', 'angle': 90, 'mag': 1.2, 'color_key': 'normal'},
        ]
    },
    'Block being pushed': {
        'type': 'flat',
        'description': 'Block with applied force and friction',
        'forces': [
            {'name': 'W', 'angle': 270, 'mag': 1.0, 'color_key': 'weight'},
            {'name': 'N', 'angle': 90, 'mag': 1.0, 'color_key': 'normal'},
            {'name': 'F', 'angle': 0, 'mag': 0.8, 'color_key': 'applied'},
            {'name': 'f', 'angle': 180, 'mag': 0.5, 'color_key': 'friction'},
        ]
    },
    'Block on inclined plane': {
        'type': 'incline',
        'angle': 30,
        'description': 'Block on slope with resolved weight components',
        'forces': [
            {'name': 'W', 'angle': 270, 'mag': 1.2, 'color_key': 'weight'},
            {'name': 'N', 'angle': 'normal', 'mag': 1.0, 'color_key': 'normal'},
            {'name': 'f', 'angle': 'up_slope', 'mag': 0.6, 'color_key': 'friction'},
        ]
    },
    'Block sliding down': {
        'type': 'incline',
        'angle': 40,
        'description': 'Block sliding down with kinetic friction',
        'forces': [
            {'name': 'W', 'angle': 270, 'mag': 1.2, 'color_key': 'weight'},
            {'name': 'N', 'angle': 'normal', 'mag': 0.9, 'color_key': 'normal'},
            {'name': 'f', 'angle': 'up_slope', 'mag': 0.4, 'color_key': 'friction'},
        ]
    },
    'Hanging object': {
        'type': 'hanging',
        'description': 'Object suspended by rope/string',
        'forces': [
            {'name': 'W', 'angle': 270, 'mag': 1.2, 'color_key': 'weight'},
            {'name': 'T', 'angle': 90, 'mag': 1.2, 'color_key': 'tension'},
        ]
    },
    'Object on two strings': {
        'type': 'two_strings',
        'description': 'Object supported by two angled strings',
        'forces': [
            {'name': 'W', 'angle': 270, 'mag': 1.0, 'color_key': 'weight'},
            {'name': 'T₁', 'angle': 120, 'mag': 0.8, 'color_key': 'tension'},
            {'name': 'T₂', 'angle': 60, 'mag': 0.8, 'color_key': 'tension'},
        ]
    },
    'Particle (simple)': {
        'type': 'particle',
        'description': 'Point particle with forces',
        'forces': [
            {'name': 'W', 'angle': 270, 'mag': 1.0, 'color_key': 'weight'},
            {'name': 'N', 'angle': 90, 'mag': 1.0, 'color_key': 'normal'},
        ]
    },
}

# Default force colors
FORCE_COLORS = {
    'weight': 'blue',
    'normal': 'green',
    'friction': 'orange',
    'applied': 'red',
    'tension': 'purple',
}


def auto_set_limits_freebody(ax, padding=0.5):
    """Set reasonable limits for free-body diagram."""
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-2.5, 2.5)
    ax.set_aspect('equal')

