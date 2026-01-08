"""
Utility functions for drawing vector diagrams.
Supports vector addition, resultants, and component resolution.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Arc


def draw_vector(ax, start, magnitude, angle_deg, color='#4C5B64', 
                line_width=2.5, head_width=0.15, head_length=0.1,
                label=None, label_offset=0.2, font_size=14, zorder=10):
    """
    Draw a vector arrow.
    
    Args:
        ax: matplotlib axes
        start: (x, y) starting point
        magnitude: length of vector
        angle_deg: angle in degrees (0=right, 90=up)
        color: arrow color
        line_width: width of arrow shaft
        head_width: width of arrow head
        head_length: length of arrow head
        label: optional label text
        label_offset: distance of label from arrow midpoint
        font_size: size of label text
        zorder: drawing order
    
    Returns:
        end point (x, y) of the vector
    """
    angle_rad = np.radians(angle_deg)
    dx = magnitude * np.cos(angle_rad)
    dy = magnitude * np.sin(angle_rad)
    
    end = (start[0] + dx, start[1] + dy)
    
    # Draw arrow
    ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(arrowstyle='->', color=color,
                               lw=line_width, mutation_scale=15),
                zorder=zorder)
    
    # Draw label if provided
    if label:
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        
        # Offset perpendicular to vector direction
        perp_angle = angle_rad + np.pi / 2
        label_x = mid_x + label_offset * np.cos(perp_angle)
        label_y = mid_y + label_offset * np.sin(perp_angle)
        
        ax.text(label_x, label_y, label, fontsize=font_size,
                ha='center', va='center', color=color, fontweight='bold')
    
    return end


def draw_vector_from_components(ax, start, vx, vy, color='#4C5B64',
                                 line_width=2.5, label=None, 
                                 label_offset=0.2, font_size=14, zorder=10):
    """
    Draw a vector from x and y components.
    
    Returns:
        end point (x, y) of the vector
    """
    magnitude = np.sqrt(vx**2 + vy**2)
    angle_deg = np.degrees(np.arctan2(vy, vx))
    
    return draw_vector(ax, start, magnitude, angle_deg, color=color,
                      line_width=line_width, label=label,
                      label_offset=label_offset, font_size=font_size,
                      zorder=zorder)


def draw_component_resolution(ax, start, magnitude, angle_deg,
                               main_color='#4C5B64', comp_color='#EF665F',
                               line_width=2.5, font_size=14,
                               show_dashed=True, labels=('F', 'Fx', 'Fy')):
    """
    Draw a vector with its x and y components.
    
    Args:
        start: starting point
        magnitude: vector magnitude
        angle_deg: vector angle
        main_color: color of main vector
        comp_color: color of components
        show_dashed: show dashed lines to complete rectangle
        labels: tuple of (main_label, x_label, y_label)
    """
    angle_rad = np.radians(angle_deg)
    
    # Components
    fx = magnitude * np.cos(angle_rad)
    fy = magnitude * np.sin(angle_rad)
    
    end_x = start[0] + fx
    end_y = start[1] + fy
    
    # Draw component vectors
    draw_vector(ax, start, abs(fx), 0 if fx >= 0 else 180, color=comp_color,
               line_width=line_width * 0.8, label=labels[1] if labels else None,
               label_offset=-0.25, font_size=font_size * 0.9, zorder=8)
    
    draw_vector(ax, (end_x, start[1]), abs(fy), 90 if fy >= 0 else 270, 
               color=comp_color, line_width=line_width * 0.8,
               label=labels[2] if labels else None, label_offset=0.25,
               font_size=font_size * 0.9, zorder=8)
    
    # Draw dashed lines to show rectangle
    if show_dashed:
        ax.plot([start[0], start[0]], [start[1], end_y], 
               color=comp_color, linestyle='--', linewidth=1, alpha=0.5, zorder=5)
        ax.plot([start[0], end_x], [end_y, end_y], 
               color=comp_color, linestyle='--', linewidth=1, alpha=0.5, zorder=5)
    
    # Draw main vector on top
    draw_vector(ax, start, magnitude, angle_deg, color=main_color,
               line_width=line_width, label=labels[0] if labels else None,
               label_offset=0.3, font_size=font_size, zorder=10)
    
    return (end_x, end_y)


def draw_vector_addition(ax, vectors, start=(0, 0), colors=None,
                         resultant_color='#EF665F', line_width=2.5,
                         font_size=14, show_resultant=True,
                         labels=None):
    """
    Draw vectors tip-to-tail and show resultant.
    
    Args:
        vectors: list of (magnitude, angle_deg) tuples
        start: starting point
        colors: list of colors for each vector (or None for default)
        resultant_color: color of resultant vector
        show_resultant: whether to draw the resultant
        labels: list of labels for each vector
    
    Returns:
        dict with 'end_points' and 'resultant' info
    """
    default_colors = ['#4C5B64', '#5B9BD5', '#70AD47', '#FFC000', '#7030A0']
    
    if colors is None:
        colors = default_colors
    
    current_pos = start
    end_points = [start]
    
    # Draw each vector tip-to-tail
    for i, (mag, angle) in enumerate(vectors):
        color = colors[i % len(colors)]
        label = labels[i] if labels and i < len(labels) else None
        
        current_pos = draw_vector(ax, current_pos, mag, angle, color=color,
                                  line_width=line_width, label=label,
                                  font_size=font_size, zorder=10 + i)
        end_points.append(current_pos)
    
    # Calculate and draw resultant
    resultant_info = None
    if show_resultant and len(vectors) > 0:
        rx = current_pos[0] - start[0]
        ry = current_pos[1] - start[1]
        resultant_mag = np.sqrt(rx**2 + ry**2)
        resultant_angle = np.degrees(np.arctan2(ry, rx))
        
        if resultant_mag > 0.01:  # Only draw if significant
            draw_vector(ax, start, resultant_mag, resultant_angle,
                       color=resultant_color, line_width=line_width * 1.2,
                       label='R', font_size=font_size, zorder=20)
        
        resultant_info = {
            'magnitude': resultant_mag,
            'angle': resultant_angle,
            'components': (rx, ry)
        }
    
    return {
        'end_points': end_points,
        'resultant': resultant_info
    }


def draw_angle_arc(ax, center, radius, start_angle, end_angle,
                   color='#4C5B64', line_width=1.5, label=None,
                   font_size=12):
    """Draw an arc to indicate an angle."""
    arc = Arc(center, 2*radius, 2*radius, angle=0,
              theta1=start_angle, theta2=end_angle,
              color=color, linewidth=line_width, zorder=5)
    ax.add_patch(arc)
    
    if label:
        mid_angle = np.radians((start_angle + end_angle) / 2)
        label_r = radius * 1.5
        label_x = center[0] + label_r * np.cos(mid_angle)
        label_y = center[1] + label_r * np.sin(mid_angle)
        ax.text(label_x, label_y, label, fontsize=font_size,
                ha='center', va='center', color=color)


def draw_axes(ax, origin=(0, 0), length=2, color='#4C5B64', 
              line_width=1.5, show_labels=True, font_size=12):
    """Draw x and y axes."""
    # X axis
    ax.annotate('', xy=(origin[0] + length, origin[1]), xytext=origin,
                arrowprops=dict(arrowstyle='->', color=color, lw=line_width))
    # Y axis
    ax.annotate('', xy=(origin[0], origin[1] + length), xytext=origin,
                arrowprops=dict(arrowstyle='->', color=color, lw=line_width))
    
    if show_labels:
        ax.text(origin[0] + length + 0.1, origin[1], 'x', fontsize=font_size,
                ha='left', va='center', color=color)
        ax.text(origin[0], origin[1] + length + 0.1, 'y', fontsize=font_size,
                ha='center', va='bottom', color=color)


# Preset scenarios
VECTOR_PRESETS = {
    'Two vectors (acute)': {
        'vectors': [(2, 30), (1.5, 80)],
        'labels': ['A', 'B'],
        'description': 'Two vectors at acute angle'
    },
    'Two vectors (obtuse)': {
        'vectors': [(2, 20), (1.5, 140)],
        'labels': ['A', 'B'],
        'description': 'Two vectors at obtuse angle'
    },
    'Three vectors': {
        'vectors': [(1.5, 0), (1.2, 60), (1, 150)],
        'labels': ['A', 'B', 'C'],
        'description': 'Three vectors added together'
    },
    'Perpendicular vectors': {
        'vectors': [(2, 0), (1.5, 90)],
        'labels': ['A', 'B'],
        'description': 'Two perpendicular vectors'
    },
    'Opposite vectors': {
        'vectors': [(2, 0), (1.5, 180)],
        'labels': ['A', 'B'],
        'description': 'Vectors in opposite directions'
    },
    'Equilibrium (3 vectors)': {
        'vectors': [(2, 0), (2, 120), (2, 240)],
        'labels': ['A', 'B', 'C'],
        'description': 'Three vectors in equilibrium (resultant ≈ 0)'
    },
}


def auto_set_limits_vectors(ax, points, padding=0.8):
    """Set axis limits based on vector endpoints."""
    if not points:
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.set_aspect('equal')
        return
    
    points_array = np.array(points)
    x_min, y_min = points_array.min(axis=0)
    x_max, y_max = points_array.max(axis=0)
    
    # Ensure origin is included
    x_min = min(x_min, 0)
    y_min = min(y_min, 0)
    x_max = max(x_max, 0)
    y_max = max(y_max, 0)
    
    x_range = max(x_max - x_min, 2)
    y_range = max(y_max - y_min, 2)
    max_range = max(x_range, y_range)
    
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2
    
    half_range = max_range / 2 + padding
    
    ax.set_xlim(x_center - half_range, x_center + half_range)
    ax.set_ylim(y_center - half_range, y_center + half_range)
    ax.set_aspect('equal')

