"""
Number line utilities for educational math graphics.
Provides functions to draw number lines with tick marks, labels, points, and intervals.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, FancyBboxPatch
from fractions import Fraction


def draw_number_line(ax, min_val, max_val, color, line_width, 
                     show_arrows=True, y_position=0, zorder=10):
    """
    Draw the main number line.
    
    Args:
        ax: Matplotlib axes
        min_val: Minimum value on the line
        max_val: Maximum value on the line
        color: Line color
        line_width: Line width
        show_arrows: Whether to show arrows at endpoints
        y_position: Vertical position of the line
        zorder: Drawing order
    """
    # Calculate some padding for arrows
    padding = (max_val - min_val) * 0.05
    
    if show_arrows:
        # Draw line with arrows using FancyArrowPatch
        arrow = FancyArrowPatch(
            (min_val - padding, y_position), 
            (max_val + padding, y_position),
            arrowstyle='<->', 
            mutation_scale=line_width * 5,
            color=color, 
            linewidth=line_width,
            zorder=zorder
        )
        ax.add_patch(arrow)
    else:
        # Simple line without arrows
        ax.plot([min_val, max_val], [y_position, y_position],
                color=color, linewidth=line_width, zorder=zorder,
                solid_capstyle='round')


def draw_tick_marks(ax, min_val, max_val, step, color, line_width,
                    tick_length=0.3, y_position=0, zorder=15):
    """
    Draw tick marks on the number line.
    
    Args:
        ax: Matplotlib axes
        min_val: Minimum value
        max_val: Maximum value
        step: Step between ticks
        color: Tick color
        line_width: Line width
        tick_length: Length of tick marks (in y units)
        y_position: Vertical position of the line
        zorder: Drawing order
    
    Returns:
        List of tick positions
    """
    # Generate tick positions
    ticks = np.arange(min_val, max_val + step/2, step)
    
    for tick in ticks:
        ax.plot([tick, tick], 
                [y_position - tick_length/2, y_position + tick_length/2],
                color=color, linewidth=line_width, zorder=zorder,
                solid_capstyle='round')
    
    return ticks


def draw_minor_ticks(ax, min_val, max_val, major_step, divisions, color, 
                     line_width, tick_length=0.15, y_position=0, zorder=14):
    """
    Draw minor tick marks between major ticks.
    
    Args:
        ax: Matplotlib axes
        min_val: Minimum value
        max_val: Maximum value
        major_step: Step between major ticks
        divisions: Number of minor divisions per major step
        color: Tick color
        line_width: Line width
        tick_length: Length of minor tick marks
        y_position: Vertical position of the line
        zorder: Drawing order
    """
    minor_step = major_step / divisions
    ticks = np.arange(min_val, max_val + minor_step/2, minor_step)
    major_ticks = set(np.round(np.arange(min_val, max_val + major_step/2, major_step), 10))
    
    for tick in ticks:
        # Skip major tick positions
        if round(tick, 10) in major_ticks:
            continue
        ax.plot([tick, tick], 
                [y_position - tick_length/2, y_position + tick_length/2],
                color=color, linewidth=line_width * 0.7, zorder=zorder,
                solid_capstyle='round')


def format_tick_label(value, format_type='auto', max_denominator=100):
    """
    Format a tick value as a string.
    
    Args:
        value: Numeric value
        format_type: 'auto', 'integer', 'decimal', 'fraction'
        max_denominator: Maximum denominator for fraction conversion
    
    Returns:
        Formatted string
    """
    if format_type == 'integer':
        return f"${int(round(value))}$"
    elif format_type == 'decimal':
        if value == int(value):
            return f"${int(value)}$"
        return f"${value:.2g}$"
    elif format_type == 'fraction':
        if value == int(value):
            return f"${int(value)}$"
        frac = Fraction(value).limit_denominator(max_denominator)
        if frac.denominator == 1:
            return f"${frac.numerator}$"
        return f"$\\frac{{{frac.numerator}}}{{{frac.denominator}}}$"
    else:  # auto
        if value == int(value):
            return f"${int(value)}$"
        # Try fraction first
        frac = Fraction(value).limit_denominator(max_denominator)
        if abs(float(frac) - value) < 1e-9:
            if frac.denominator == 1:
                return f"${frac.numerator}$"
            return f"$\\frac{{{frac.numerator}}}{{{frac.denominator}}}$"
        return f"${value:.2g}$"


def draw_tick_labels(ax, ticks, color, font_size, format_type='auto',
                     y_position=0, offset=0.5, white_background=True, zorder=100):
    """
    Draw labels at tick positions.
    
    Args:
        ax: Matplotlib axes
        ticks: List/array of tick positions
        color: Text color
        font_size: Font size
        format_type: 'auto', 'integer', 'decimal', 'fraction'
        y_position: Vertical position of the line
        offset: Distance below the line for labels
        white_background: Whether to add white background
        zorder: Drawing order
    """
    bbox_props = None
    if white_background:
        bbox_props = dict(boxstyle='round,pad=0.1', facecolor='white',
                         edgecolor='none', alpha=0.9)
    
    for tick in ticks:
        label = format_tick_label(tick, format_type)
        ax.text(tick, y_position - offset, label,
                fontsize=font_size, color=color,
                ha='center', va='top', zorder=zorder,
                bbox=bbox_props)


def draw_point(ax, position, color, marker_size, marker_style='filled',
               y_position=0, zorder=25):
    """
    Draw a point on the number line.
    
    Args:
        ax: Matplotlib axes
        position: X position on the line
        color: Point color
        marker_size: Size of the marker
        marker_style: 'filled' (solid dot) or 'open' (hollow circle)
        y_position: Vertical position of the line
        zorder: Drawing order
    """
    if marker_style == 'filled':
        ax.plot(position, y_position, 'o', color=color, markersize=marker_size,
                zorder=zorder)
    else:  # open
        ax.plot(position, y_position, 'o', color=color, markersize=marker_size,
                markerfacecolor='white', markeredgewidth=marker_size/4,
                zorder=zorder)


def draw_point_label(ax, position, label_text, color, font_size,
                     y_position=0, offset=0.5, direction='above',
                     white_background=True, zorder=100):
    """
    Draw a label for a point.
    
    Args:
        ax: Matplotlib axes
        position: X position of the point
        label_text: Label text
        color: Text color
        font_size: Font size
        y_position: Vertical position of the line
        offset: Distance from the line
        direction: 'above' or 'below'
        white_background: Whether to add white background
        zorder: Drawing order
    """
    bbox_props = None
    if white_background:
        bbox_props = dict(boxstyle='round,pad=0.15', facecolor='white',
                         edgecolor='none', alpha=0.9)
    
    if direction == 'above':
        y = y_position + offset
        va = 'bottom'
    else:
        y = y_position - offset
        va = 'top'
    
    ax.text(position, y, label_text, fontsize=font_size, color=color,
            ha='center', va=va, zorder=zorder, bbox=bbox_props)


def draw_interval(ax, start, end, color, line_width, y_position=0,
                  start_style='closed', end_style='closed',
                  interval_offset=0.15, zorder=20):
    """
    Draw an interval/range on the number line.
    
    Args:
        ax: Matplotlib axes
        start: Start value
        end: End value
        color: Interval color
        line_width: Line width
        y_position: Vertical position of the line
        start_style: 'closed' (filled dot), 'open' (hollow), or 'arrow'
        end_style: 'closed', 'open', or 'arrow'
        interval_offset: Vertical offset for the interval line
        zorder: Drawing order
    """
    y = y_position + interval_offset
    
    # Draw the interval line
    ax.plot([start, end], [y, y], color=color, linewidth=line_width * 1.5,
            zorder=zorder, solid_capstyle='butt')
    
    # Draw endpoint markers
    marker_size = line_width * 4
    
    # Start endpoint
    if start_style == 'closed':
        ax.plot(start, y, 'o', color=color, markersize=marker_size, zorder=zorder+1)
    elif start_style == 'open':
        ax.plot(start, y, 'o', color=color, markersize=marker_size,
                markerfacecolor='white', markeredgewidth=marker_size/4, zorder=zorder+1)
    elif start_style == 'arrow':
        # Arrow pointing left (to negative infinity)
        ax.annotate('', xy=(start - 0.3, y), xytext=(start, y),
                   arrowprops=dict(arrowstyle='->', color=color, lw=line_width * 1.5),
                   zorder=zorder+1)
    
    # End endpoint
    if end_style == 'closed':
        ax.plot(end, y, 'o', color=color, markersize=marker_size, zorder=zorder+1)
    elif end_style == 'open':
        ax.plot(end, y, 'o', color=color, markersize=marker_size,
                markerfacecolor='white', markeredgewidth=marker_size/4, zorder=zorder+1)
    elif end_style == 'arrow':
        # Arrow pointing right (to positive infinity)
        ax.annotate('', xy=(end + 0.3, y), xytext=(end, y),
                   arrowprops=dict(arrowstyle='->', color=color, lw=line_width * 1.5),
                   zorder=zorder+1)


def draw_interval_fill(ax, start, end, color, alpha=0.3, y_position=0,
                       height=0.4, zorder=5):
    """
    Draw a filled region for an interval.
    
    Args:
        ax: Matplotlib axes
        start: Start value
        end: End value
        color: Fill color
        alpha: Fill transparency
        y_position: Vertical position of the line
        height: Height of the filled region
        zorder: Drawing order
    """
    rect = FancyBboxPatch(
        (start, y_position - height/2), end - start, height,
        boxstyle="round,pad=0.02,rounding_size=0.1",
        facecolor=color, alpha=alpha, edgecolor='none',
        zorder=zorder
    )
    ax.add_patch(rect)


def draw_brace(ax, start, end, color, line_width, y_position=0,
               brace_offset=0.4, label="", font_size=12, zorder=30):
    """
    Draw a brace under an interval with optional label.
    
    Args:
        ax: Matplotlib axes
        start: Start value
        end: End value
        color: Brace color
        line_width: Line width
        y_position: Vertical position of the line
        brace_offset: Vertical offset for the brace
        label: Label text for the brace
        font_size: Font size for label
        zorder: Drawing order
    """
    y = y_position - brace_offset
    mid = (start + end) / 2
    
    # Draw brace as three segments
    ax.plot([start, start], [y, y - 0.1], color=color, linewidth=line_width, zorder=zorder)
    ax.plot([start, mid], [y - 0.1, y - 0.2], color=color, linewidth=line_width, zorder=zorder)
    ax.plot([mid, end], [y - 0.2, y - 0.1], color=color, linewidth=line_width, zorder=zorder)
    ax.plot([end, end], [y - 0.1, y], color=color, linewidth=line_width, zorder=zorder)
    
    if label:
        ax.text(mid, y - 0.35, label, fontsize=font_size, color=color,
                ha='center', va='top', zorder=zorder)


def auto_set_limits(ax, min_val, max_val, padding_factor=0.15):
    """
    Automatically set axis limits.
    
    Args:
        ax: Matplotlib axes
        min_val: Minimum value on number line
        max_val: Maximum value on number line
        padding_factor: Padding as fraction of range
    """
    range_val = max_val - min_val
    padding = range_val * padding_factor
    
    ax.set_xlim(min_val - padding, max_val + padding)
    ax.set_ylim(-1.5, 1.5)


def create_number_line_figure(figsize=(12, 3)):
    """
    Create a figure and axes suitable for number line diagrams.
    
    Args:
        figsize: Figure size tuple
    
    Returns:
        fig, ax tuple
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_aspect('auto')
    ax.axis('off')
    return fig, ax

