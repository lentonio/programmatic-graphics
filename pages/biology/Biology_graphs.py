"""
Biology Graphs Page
Enzyme activity curves, population growth, rate graphs.
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


# --- Session State Version Check ---
BG_VERSION = 1
if st.session_state.get("bg_version", 0) < BG_VERSION:
    for key in list(st.session_state.keys()):
        if key.startswith("bg_"):
            del st.session_state[key]
    st.session_state["bg_version"] = BG_VERSION

# --- Initialize Session State Defaults ---
BG_DEFAULTS = {
    # Sidebar
    "bg_line_weight": 2.5,
    "bg_label_size": 14,
    "bg_white_bg": DEFAULT_WHITE_BG,
    # Graph
    "bg_category": "Enzyme activity",
    "bg_preset": "Temperature effect",
    # Style
    "bg_line_color": "blue",
    "bg_show_grid": True,
    "bg_show_optimum": True,
}

init_session_state(BG_DEFAULTS)


def get_index(options, key):
    val = st.session_state.get(key, options[0])
    try:
        return options.index(val)
    except ValueError:
        return 0


COLOR_OPTIONS = get_color_options()


# Biology graph presets
BIOLOGY_PRESETS = {
    'Enzyme activity': {
        'Temperature effect': {
            'x_label': 'Temperature (°C)',
            'y_label': 'Rate of reaction',
            'x_range': (0, 70),
            'func': lambda x: np.exp(-0.01 * (x - 37)**2) * (x > 0) * (x < 65),
            'description': 'Enzyme activity peaks at optimum temperature (~37°C)',
            'optimum': 37,
            'annotations': [('Optimum', 37), ('Denatured', 55)],
        },
        'pH effect': {
            'x_label': 'pH',
            'y_label': 'Rate of reaction',
            'x_range': (0, 14),
            'func': lambda x: np.exp(-0.5 * (x - 7)**2),
            'description': 'Most enzymes work best at neutral pH',
            'optimum': 7,
            'annotations': [('Optimum', 7)],
        },
        'pH effect (pepsin)': {
            'x_label': 'pH',
            'y_label': 'Rate of reaction',
            'x_range': (0, 14),
            'func': lambda x: np.exp(-0.5 * (x - 2)**2),
            'description': 'Pepsin (stomach enzyme) works best at pH 2',
            'optimum': 2,
            'annotations': [('Optimum', 2)],
        },
        'Substrate concentration': {
            'x_label': 'Substrate concentration',
            'y_label': 'Rate of reaction',
            'x_range': (0, 10),
            'func': lambda x: x / (x + 1),
            'description': 'Rate increases then plateaus (Vmax)',
            'optimum': None,
            'annotations': [],
            'show_vmax': True,
        },
    },
    'Population growth': {
        'Exponential (J-curve)': {
            'x_label': 'Time',
            'y_label': 'Population size',
            'x_range': (0, 10),
            'func': lambda x: 10 * np.exp(0.3 * x),
            'description': 'Unlimited resources, no predators',
            'optimum': None,
            'annotations': [],
        },
        'Logistic (S-curve)': {
            'x_label': 'Time',
            'y_label': 'Population size',
            'x_range': (0, 20),
            'func': lambda x: 100 / (1 + 9 * np.exp(-0.5 * x)),
            'description': 'Growth limited by carrying capacity',
            'optimum': None,
            'annotations': [],
            'show_carrying': True,
        },
        'Boom and bust': {
            'x_label': 'Time',
            'y_label': 'Population size',
            'x_range': (0, 20),
            'func': lambda x: 50 * np.exp(-0.05 * x) * (1 + 0.8 * np.sin(x)),
            'description': 'Population fluctuates then stabilises',
            'optimum': None,
            'annotations': [],
        },
        'Predator-prey': {
            'x_label': 'Time',
            'y_label': 'Population size',
            'x_range': (0, 20),
            'func': lambda x: 50 + 30 * np.sin(0.5 * x),
            'func2': lambda x: 30 + 20 * np.sin(0.5 * x - 1),
            'description': 'Prey and predator populations cycle',
            'optimum': None,
            'annotations': [],
            'two_lines': True,
            'labels': ['Prey', 'Predator'],
        },
    },
    'Rates': {
        'Photosynthesis vs light': {
            'x_label': 'Light intensity',
            'y_label': 'Rate of photosynthesis',
            'x_range': (0, 100),
            'func': lambda x: 100 * (1 - np.exp(-0.05 * x)),
            'description': 'Rate increases then plateaus (limiting factor)',
            'optimum': None,
            'annotations': [],
        },
        'Photosynthesis vs CO₂': {
            'x_label': 'CO₂ concentration',
            'y_label': 'Rate of photosynthesis',
            'x_range': (0, 100),
            'func': lambda x: x / (x + 10),
            'description': 'Rate limited by CO₂ availability',
            'optimum': None,
            'annotations': [],
        },
        'Respiration vs temperature': {
            'x_label': 'Temperature (°C)',
            'y_label': 'Rate of respiration',
            'x_range': (0, 50),
            'func': lambda x: np.exp(0.05 * x) * (x < 40) + np.exp(0.05 * 40) * np.exp(-0.2 * (x - 40)) * (x >= 40),
            'description': 'Rate increases with temperature, then drops',
            'optimum': 40,
            'annotations': [],
        },
        'Diffusion rate': {
            'x_label': 'Concentration gradient',
            'y_label': 'Rate of diffusion',
            'x_range': (0, 10),
            'func': lambda x: 0.8 * x,
            'description': 'Rate proportional to concentration gradient',
            'optimum': None,
            'annotations': [],
        },
    },
}


# --- Sidebar ---
with st.sidebar:
    st.header("Appearance")
    
    line_weight = st.slider(
        "Line weight",
        min_value=1.5, max_value=4.0, step=0.5,
        key="bg_line_weight"
    )
    
    label_size = st.slider(
        "Label size",
        min_value=10, max_value=20, step=1,
        key="bg_label_size"
    )
    
    st.write("")
    white_background = st.toggle("White background", key="bg_white_bg")


fig_height = 5
fig_width = 8


# --- Main Layout ---
col_plot, col_controls = st.columns([1.5, 1])

with col_plot:
    plot_placeholder = st.empty()
    st.write("")
    download_cols = st.columns([1.2, 1, 1, 1])
    with download_cols[1]:
        svg_placeholder = st.empty()
    with download_cols[2]:
        png_placeholder = st.empty()

with col_controls:
    tab_graph, tab_style, tab_info = st.tabs(["Graph", "Style", "Info"])
    
    # === GRAPH TAB ===
    with tab_graph:
        category = st.radio(
            "Category:",
            list(BIOLOGY_PRESETS.keys()),
            horizontal=True,
            key="bg_category"
        )
        
        st.write("")
        st.caption("Select graph")
        
        presets = BIOLOGY_PRESETS.get(category, {})
        for name in presets.keys():
            if st.button(name, key=f"bg_btn_{category}_{name}", use_container_width=True):
                st.session_state["bg_preset"] = name
        
        st.markdown("---")
        
        current = st.session_state.get("bg_preset", list(presets.keys())[0] if presets else "")
        if current in presets:
            st.markdown(f"**{current}**")
            st.caption(presets[current]['description'])
    
    # === STYLE TAB ===
    with tab_style:
        st.caption("Colors")
        st.selectbox("Line color", options=COLOR_OPTIONS,
                    index=get_index(COLOR_OPTIONS, "bg_line_color"),
                    key="bg_line_color")
        
        st.write("")
        st.caption("Display")
        st.checkbox("Show grid", key="bg_show_grid")
        st.checkbox("Show optimum/key points", key="bg_show_optimum")
    
    # === INFO TAB ===
    with tab_info:
        category = st.session_state.get("bg_category", "Enzyme activity")
        
        if category == "Enzyme activity":
            st.markdown("""
            **Enzyme graphs:**
            - Enzymes have an optimum temperature/pH
            - Too hot → denaturation (shape changes)
            - Wrong pH → denaturation
            - Rate increases with substrate until saturated
            """)
        elif category == "Population growth":
            st.markdown("""
            **Population graphs:**
            - J-curve: unlimited growth
            - S-curve: limited by carrying capacity
            - Predator-prey: populations cycle
            - Birth rate, death rate, migration
            """)
        else:
            st.markdown("""
            **Rate graphs:**
            - Limiting factors cause plateaus
            - Photosynthesis: light, CO₂, temperature
            - Diffusion: concentration gradient
            - Respiration: temperature affects enzymes
            """)


# --- Render ---
def render_biology_graph():
    category = st.session_state.get("bg_category", "Enzyme activity")
    presets = BIOLOGY_PRESETS.get(category, {})
    preset_name = st.session_state.get("bg_preset", list(presets.keys())[0] if presets else "")
    
    if preset_name not in presets:
        preset_name = list(presets.keys())[0] if presets else None
    
    if not preset_name:
        return None
    
    preset = presets[preset_name]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    white_bg = st.session_state.get("bg_white_bg", True)
    apply_figure_style(fig, ax, white_bg)
    
    # Get style settings
    lw = st.session_state.get("bg_line_weight", 2.5)
    fs = st.session_state.get("bg_label_size", 14)
    line_color = MY_COLORS[st.session_state.get("bg_line_color", "blue")]
    show_grid = st.session_state.get("bg_show_grid", True)
    show_optimum = st.session_state.get("bg_show_optimum", True)
    
    axis_color = AXIS_COLOR  # Consistent dark grey like function graphs
    
    # Generate data
    x_range = preset['x_range']
    x = np.linspace(x_range[0], x_range[1], 200)
    y = preset['func'](x)
    
    # Plot main line
    ax.plot(x, y, color=line_color, linewidth=lw, label=preset.get('labels', [''])[0] if preset.get('two_lines') else '')
    
    # Plot second line if predator-prey
    if preset.get('two_lines') and 'func2' in preset:
        y2 = preset['func2'](x)
        ax.plot(x, y2, color=MY_COLORS['red'], linewidth=lw, 
               linestyle='--', label=preset['labels'][1])
        ax.legend(fontsize=fs*0.8, loc='upper right')
    
    # Show optimum point
    if show_optimum and preset.get('optimum') is not None:
        opt_x = preset['optimum']
        opt_y = preset['func'](opt_x)
        ax.axvline(x=opt_x, color=axis_color, linestyle='--', linewidth=1, alpha=0.5)
        ax.scatter([opt_x], [opt_y], color=line_color, s=80, zorder=10)
        ax.annotate(f'Optimum\n({opt_x})', xy=(opt_x, opt_y), 
                   xytext=(opt_x + (x_range[1]-x_range[0])*0.1, opt_y),
                   fontsize=fs*0.8, color=axis_color,
                   arrowprops=dict(arrowstyle='->', color=axis_color, lw=1))
    
    # Show Vmax line for substrate concentration
    if show_optimum and preset.get('show_vmax'):
        vmax = preset['func'](x_range[1])
        ax.axhline(y=vmax, color=axis_color, linestyle='--', linewidth=1, alpha=0.5)
        ax.text(x_range[1]*0.95, vmax*1.05, 'Vmax', fontsize=fs*0.8, 
               color=axis_color, ha='right')
    
    # Show carrying capacity
    if show_optimum and preset.get('show_carrying'):
        carrying = preset['func'](x_range[1])
        ax.axhline(y=carrying, color=axis_color, linestyle='--', linewidth=1, alpha=0.5)
        ax.text(x_range[1]*0.95, carrying*1.05, 'Carrying capacity', 
               fontsize=fs*0.8, color=axis_color, ha='right')
    
    # Axis labels
    ax.set_xlabel(preset['x_label'], fontsize=fs, color=axis_color)
    ax.set_ylabel(preset['y_label'], fontsize=fs, color=axis_color)
    
    # Grid
    if show_grid:
        ax.grid(True, alpha=0.3, color=axis_color)
    
    # Axis styling
    ax.tick_params(colors=axis_color, labelsize=fs*0.8)
    for spine in ax.spines.values():
        spine.set_color(axis_color)
    
    ax.set_xlim(x_range)
    ax.set_ylim(0, max(y) * 1.2)
    
    fig.tight_layout()
    return fig


# --- Main ---
try:
    fig = render_biology_graph()
    
    if fig is not None:
        plot_placeholder.pyplot(fig)
        
        category = st.session_state.get("bg_category", "enzyme")
        preset = st.session_state.get("bg_preset", "graph")
        filename = f"biology_{category.lower().replace(' ', '_')}_{preset.lower().replace(' ', '_')}"
        
        create_download_buttons(fig, svg_placeholder, png_placeholder, filename)
        plt.close(fig)
except Exception as e:
    st.error(f"Error rendering: {e}")
    import traceback
    st.code(traceback.format_exc())

