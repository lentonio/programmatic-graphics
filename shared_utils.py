"""
Shared utilities for the Graph App.
Contains common styling, colors, and export functions used across all pages.
"""

import io
import streamlit as st
import matplotlib.pyplot as plt


# =============================================================================
# GLOBAL DEFAULTS - Change these to affect all pages
# =============================================================================

# Default background: False = transparent, True = white
DEFAULT_WHITE_BG = False

# Default line/label sizes
DEFAULT_LINE_WEIGHT = 2.5
DEFAULT_LABEL_SIZE = 16

# =============================================================================
# COLOR PALETTE - Add/modify colors here
# =============================================================================

MY_COLORS = {
    'blue': '#82DCF2',
    'red': '#EF665F',
    'green': '#8FE384',
    'yellow': '#FFC753',
    'orange': '#FF8A56',
    'pink': '#F688C9',
    'purple': '#B57EDC',
    'grey': '#4C5B64'
}

# Axis/line color for graphs
AXIS_COLOR = '#435159'

# Dark background color (when not transparent)
DARK_BG_COLOR = '#0E1117'


def get_color_options():
    """Return list of color names for selectboxes."""
    return list(MY_COLORS.keys())


def create_download_buttons(fig, svg_placeholder, png_placeholder, filename_base="figure"):
    """
    Create SVG and PNG download buttons for a matplotlib figure.
    
    Args:
        fig: Matplotlib figure
        svg_placeholder: Streamlit placeholder for SVG button
        png_placeholder: Streamlit placeholder for PNG button
        filename_base: Base name for downloaded files
    """
    # SVG export
    svg_buffer = io.StringIO()
    fig.savefig(svg_buffer, format="svg")
    svg_data = svg_buffer.getvalue()
    svg_buffer.close()
    
    svg_placeholder.download_button(
        label="Download SVG",
        data=svg_data,
        file_name=f"{filename_base}.svg",
        mime="image/svg+xml",
    )
    
    # PNG export
    png_buffer = io.BytesIO()
    fig.savefig(png_buffer, format="png", dpi=300, bbox_inches="tight", pad_inches=0.1)
    png_buffer.seek(0)
    png_data = png_buffer.getvalue()
    png_buffer.close()
    
    png_placeholder.download_button(
        label="Download PNG",
        data=png_data,
        file_name=f"{filename_base}.png",
        mime="image/png"
    )


def setup_figure_appearance_controls(sidebar=True, key_prefix=""):
    """
    Common appearance controls for figure dimensions and background.
    
    Args:
        sidebar: If True, place controls in sidebar. If False, return values for inline use.
        key_prefix: Prefix for widget keys to avoid conflicts between pages
    
    Returns:
        dict with 'width', 'height', 'white_background', 'axis_weight', 'label_size'
    """
    container = st.sidebar if sidebar else st
    
    with container:
        st.markdown("### Appearance")
        
        axis_weight = st.slider(
            "Line weight", 
            min_value=1.5, max_value=4.0, value=3.0, step=0.5,
            key=f"{key_prefix}axis_weight"
        )
        
        height_col, width_col = st.columns(2)
        with height_col:
            height = st.number_input("Height", value=8, key=f"{key_prefix}height")
        with width_col:
            width = st.number_input("Width", value=8, key=f"{key_prefix}width")
        
        label_size = st.slider(
            "Label size", 
            min_value=12, max_value=30, value=20, step=1,
            key=f"{key_prefix}label_size"
        )
        
        st.write("")
        white_background = st.toggle("White background", value=True, key=f"{key_prefix}white_bg")
    
    return {
        'width': width,
        'height': height,
        'white_background': white_background,
        'axis_weight': axis_weight,
        'label_size': label_size
    }


def apply_figure_style(fig, ax, white_background=True):
    """
    Apply common styling to a figure.
    
    Args:
        fig: Matplotlib figure
        ax: Matplotlib axes
        white_background: Whether to use white background
    """
    if not white_background:
        ax.set_facecolor('none')
        fig.patch.set_facecolor('none')
    else:
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')


def init_session_state(defaults):
    """
    Initialize session state with default values if not already set.
    Call this at the start of each page to ensure state persistence.
    
    Args:
        defaults: Dictionary of {key: default_value}
    """
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

