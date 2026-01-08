import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import sympy as sp
from sympy import nsimplify, pi, E, latex
import streamlit as st
import io
from numpy import log, log10 
from scipy.stats import binom 

from graph_utils import create_graph, eval_function, latex_to_python, get_y_values_for_curve

sp.arcsin = sp.asin
sp.arccos = sp.acos
sp.arctan = sp.atan

MY_COLORS = {
    'blue': '#82DCF2',
    'red': '#EF665F',
    'green': '#8FE384',
    'yellow': '#FFC753',
    'orange': '#FF8A56',
    'pink': '#F688C9',
    'grey': '#4C5B64'
}

PI = 3.1415927


#-------SIDEBAR--------------------

with st.sidebar:
    """# Axes and gridlines"""
    xlowercol, xuppercol, xunitcol = st.columns(3)
    with xlowercol:
        xuserlowerinput = st.number_input("Lower $x$", value=-2.0, key="sidebar_xlower")
    with xuppercol:
        xuserupperinput = st.number_input("Upper $x$", value=8.0, key="sidebar_xupper")
    with xunitcol:
        x_is_pi = st.segmented_control("x unit:", options = ["1", "π"], default = '1', key="unit_control_1")
    xuserlower = xuserlowerinput * (PI if x_is_pi == "π" else 1)
    xuserupper = xuserupperinput * (PI if x_is_pi == "π" else 1)
    
    ylowercol, yuppercol, yunitcol = st.columns(3)
    with ylowercol:
        yuserlowerinput = st.number_input("Lower $y$", value=-2.0, key="sidebar_ylower")
    with yuppercol:
        yuserupperinput = st.number_input("Upper $y$", value=8.0, key="sidebar_yupper")
    with yunitcol:
        y_is_pi = st.segmented_control("$y$ unit:", options = ["1", "π"], default = '1', key="unit_control_2")
    yuserlower = yuserlowerinput * (PI if y_is_pi == "π" else 1)
    yuserupper = yuserupperinput * (PI if y_is_pi == "π" else 1)
    
    xdifference = xuserupper - xuserlower
    ydifference = yuserupper - yuserlower
    xlower = xuserlower - 0.025 * xdifference
    xupper = xuserupper + 0.025 * xdifference
    ylower = yuserlower - 0.025 * ydifference
    yupper = yuserupper + 0.025 * ydifference
    
    showvalues = st.checkbox("Show values on axes", value=True)
    
    if showvalues:
        xstepcol, ystepcol = st.columns(2)
        with xstepcol:
            x_base_step = st.number_input("$x$-axis step:", value=2.0, step=0.01)
            xstep = x_base_step * (PI if x_is_pi == "π" else 1)
        with ystepcol:
            y_base_step = st.number_input("$y$-axis step:", value=2.0, step=0.01)
            ystep = y_base_step * (PI if y_is_pi == "π" else 1)
        
        label_format_is_decimal = st.toggle("Use decimal labels", value=False) 
        
        label_size = st.slider("Label size", min_value=12, max_value=26, value=20, step=1)
    else:
        xstep = 1
        ystep = 1
        label_size = 20
        label_format_is_decimal = False

    gridstyle = st.segmented_control("Gridlines", options = ["None", "Major", "Minor"], default = 'None')

    if gridstyle == 'Minor':
        xdivcol, ydivcol = st.columns(2)
        with xdivcol:
            xminordivisor = st.number_input("Minor divisor for $x$:", value=4)
        with ydivcol:
            yminordivisor = st.number_input("Minor divisor for $y$:", value=4)
    else:
        xminordivisor = 1
        yminordivisor = 1

    if not gridstyle:
        gridstyle = "None"

    """# Appearance"""
    axis_weight = st.slider("Axis weight", min_value=1.5, max_value=4.0, value=3.0, step=0.5)

    heightcol, widthcol = st.columns(2)
    with heightcol:
        imageheight = st.number_input("Height", value=8)
    with widthcol:
        imagewidth = st.number_input("Width", value=10)

    st.write("")  # Adds vertical space
    white_background = st.toggle("White background", value=False)


#-------INITIAL PLOT-------------------------

x_init = np.linspace(xlower, xupper, 100000)
y_init = np.zeros_like(x_init)  # Create corresponding y values

fig, ax = create_graph(
    xlower=xlower,
    xupper=xupper,
    ylower=ylower,
    yupper=yupper,
    xstep=xstep,
    ystep=ystep,
    gridstyle=gridstyle,
    xminordivisor=xminordivisor,
    yminordivisor=yminordivisor,
    imagewidth=imagewidth,
    imageheight=imageheight,
    xuserlower=xuserlower,
    xuserupper=xuserupper,
    yuserlower=yuserlower,
    yuserupper=yuserupper,
    showvalues=showvalues,
    axis_weight=axis_weight,
    label_size=label_size,
    white_background=white_background,
    label_format_is_decimal=label_format_is_decimal,
    skip_static_plots=False  # or True if you want to skip plotting static data
)

ax.plot(x_init, y_init, alpha=0)  # Plot invisible points
ax.margins(x=0, y=0)  # Remove margins
fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)  # Remove all padding
ax.set_xlim(xlower, xupper)  # Force exact limits
ax.set_ylim(ylower, yupper)  # Force exact limits


#-------ADD FUNCTIONS-------------------------

if "plotted_functions" not in st.session_state:
    st.session_state.plotted_functions = []  # List to store function data

if "plotted_points" not in st.session_state:
    st.session_state.plotted_points = []

if "plot_data" not in st.session_state:
    st.session_state.plot_data = {"x": None, "y": None, "function": None}

if "selected_color" not in st.session_state:
    st.session_state.selected_color = "blue"  # Default color

if "selected_line_style" not in st.session_state:
    st.session_state.selected_line_style = "-"  # Default line style

if "plotted_implicit_functions" not in st.session_state:
    st.session_state.plotted_implicit_functions = []

if "plotted_parametric_functions" not in st.session_state:
    st.session_state.plotted_parametric_functions = []

# --- Add state for multiple areas ---
if "plotted_areas" not in st.session_state:
    st.session_state.plotted_areas = [None] * 3 # Initialize list for 3 areas

# --- Add state for binomial distributions ---
if "plotted_binomials" not in st.session_state:
    st.session_state.plotted_binomials = [None] * 3 # Initialize list for 3 binomial plots
# --- End addition ---

if "plot_counter" not in st.session_state:
    st.session_state.plot_counter = 0

for i in range(8):  # Changed from range(5)
    if f"point_color_{i}" not in st.session_state:
        st.session_state[f"point_color_{i}"] = "blue"
    if f"point_style_{i}" not in st.session_state:
        st.session_state[f"point_style_{i}"] = "×"  # Default to cross marker


master_col1, master_col2 = st.columns([1.5, 1])

with master_col1:
    plot_placeholder = st.empty()
    st.write("")
    download_columns = st.columns([1.2, 1, 1, 1])
    with download_columns[1]:
        svg_placeholder = st.empty()
    with download_columns[2]:
        png_placeholder = st.empty()

with master_col2:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Explicit functions", 
        "Implicit functions", 
        "Parametric functions", 
        "Points", 
        "Areas",
        "Binomial"
    ])
    
    with tab1:
        st.subheader("Plot explicit functions", divider="gray")
        
        # Initialize conversion variables
        python_str = None
        preview_expr = None
        
        # Input row
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1], vertical_alignment="bottom")
        
        with col1:
            latex_input = st.text_input(f"Function 1", 
                                      value=r"\frac{x}{2}-\sin(x)",
                                      key=f"latex_function_1")
        
        with col2:
            color_choice = st.selectbox("Color", 
                                      options=list(MY_COLORS.keys()), 
                                      key=f"latex_color_1",
                                      index=0,
                                      label_visibility="collapsed")
        
        with col3:
            line_styles = ("solid", "dashed", "dotted")
            line_style_choice = st.selectbox("Line style", 
                                           line_styles,
                                           key=f"latex_style_1",
                                           index=0,
                                           label_visibility="collapsed")
            
            line_style = {
                "solid": "-",
                "dashed": "--",
                "dotted": ":"
            }[line_style_choice]
        
        # Do LaTeX conversion here so python_str is available for plot button
        if latex_input.strip():
            python_str, preview_expr = latex_to_python(latex_input)
        
        with col4:
            if st.button("Plot", key=f"latex_plot_1"):
                if latex_input.strip() and python_str:
                    x = np.linspace(xlower, xupper, 100000)
                    y = eval_function(python_str, x, np, ylower, yupper)
                    
                    st.session_state.plot_counter += 1
                    func_data = {
                        "x": x,
                        "y": y,
                        "function": python_str,
                        "color": color_choice,
                        "line_style": line_style,
                        "zorder": 10 + st.session_state.plot_counter  # Base zorder of 10 for all functions
                    }
                    
                    if 0 < len(st.session_state.plotted_functions):
                        st.session_state.plotted_functions[0] = func_data
                    else:
                        st.session_state.plotted_functions.append(func_data)

        # Add remaining 4 function inputs
        for i in range(2, 6):  # Functions 2-5
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1], vertical_alignment="bottom")
            
            with col1:
                latex_input_i = st.text_input(f"Function {i}", 
                                            value="",
                                            key=f"latex_function_{i}")
            
            with col2:
                color_choice_i = st.selectbox("Color", 
                                            options=list(MY_COLORS.keys()), 
                                            key=f"latex_color_{i}",
                                            index=0,
                                            label_visibility="collapsed")
            
            with col3:
                line_style_choice_i = st.selectbox("Line style", 
                                                 line_styles,
                                                 key=f"latex_style_{i}",
                                                 index=0,
                                                 label_visibility="collapsed")
                
                line_style_i = {
                    "solid": "-",
                    "dashed": "--",
                    "dotted": ":"
                }[line_style_choice_i]
            
            # Do LaTeX conversion
            python_str_i = None
            if latex_input_i.strip():
                python_str_i, _ = latex_to_python(latex_input_i)
            
            with col4:
                if st.button("Plot", key=f"latex_plot_{i}"):
                    if latex_input_i.strip() and python_str_i:
                        x = np.linspace(xlower, xupper, 100000)
                        y = eval_function(python_str_i, x, np, ylower, yupper)
                        
                        st.session_state.plot_counter += 1
                        func_data = {
                            "x": x,
                            "y": y,
                            "function": python_str_i,
                            "color": color_choice_i,
                            "line_style": line_style_i,
                            "zorder": 10 + st.session_state.plot_counter  # Base zorder of 10 for all functions
                        }
                        
                        if i-1 < len(st.session_state.plotted_functions):
                            st.session_state.plotted_functions[i-1] = func_data
                        else:
                            st.session_state.plotted_functions.append(func_data)
                            
        st.caption("Enter functions of $x$ in latex.")

    with tab2:
        st.subheader("Plot implicit functions", divider="gray")
        
        # Create up to 5 implicit function input rows
        for i in range(5):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1], vertical_alignment="bottom")
            
            with col1:
                default_value = r"x^2 + y^2 - 1" if i == 0 else ""
                latex_input = st.text_input(f"Function {i+1}", 
                                     value=default_value,
                                     key=f"implicit_latex_{i}")
            
            with col2:
                color_choice = st.selectbox("Color", 
                                      options=list(MY_COLORS.keys()), 
                                      key=f"implicit_color_{i}",
                                      index=0,
                                      label_visibility="collapsed")
            
            with col3:
                line_styles = ("solid", "dashed", "dotted")
                line_style_choice = st.selectbox("Line style", 
                                               line_styles,
                                               key=f"implicit_style_{i}",
                                               index=0,
                                               label_visibility="collapsed")
                
                line_style = {
                    "solid": "-",
                    "dashed": "--",
                    "dotted": ":"
                }[line_style_choice]
            
            # Do LaTeX conversion here so python_str is available for plot button
            python_str = None
            if latex_input.strip():
                python_str, _ = latex_to_python(latex_input)
            
            with col4:
                if st.button("Plot", key=f"plot_implicit_{i}"):
                    if latex_input.strip() and python_str:
                        st.session_state.plot_counter += 1
                        implicit_data = {
                            "function": python_str,
                            "color": color_choice,
                            "line_style": line_style,
                            "zorder": 10 + st.session_state.plot_counter  # Base zorder of 10 for all functions
                        }
                        
                        if i < len(st.session_state.plotted_implicit_functions):
                            st.session_state.plotted_implicit_functions[i] = implicit_data
                        else:
                            st.session_state.plotted_implicit_functions.append(implicit_data)

        st.caption("Entering $f(x,y)$ will plot the curve $f(x,y) = 0$.\n\nFor example, $x^2 + y^2 - 1$ plots the unit circle.")

    with tab3:
        st.subheader("Plot parametric functions", divider="gray")
        
        # Create up to 5 parametric function input rows
        for i in range(5):
            # All controls in one row with minimum widths
            col1, col2, col3, col4, col5, col6 = st.columns([3.5, 3.5, 2, 2, 2, 1.5], vertical_alignment="bottom")
            with col1:
                default_x = r"\cos(t)" if i == 0 else ""
                x_latex = st.text_input(f"Function {i+1}",
                                      value=default_x,
                                      key=f"param_x_latex_{i}")
            with col2:
                default_y = r"\sin(t)" if i == 0 else ""
                y_latex = st.text_input(" ",  # Invisible label
                                      value=default_y,
                                      key=f"param_y_latex_{i}")
            with col3:
                t_range = st.text_input(" ",  # Invisible label
                                      value=r"-\pi:\pi" if i == 0 else "",
                                      key=f"param_range_{i}")
            with col4:
                color_choice = st.selectbox(" ",  # Invisible label
                                          options=list(MY_COLORS.keys()), 
                                          key=f"param_color_{i}",
                                          index=0,
                                          label_visibility="collapsed")
            
            with col5:
                line_styles = ("solid", "dashed", "dotted")
                line_style_choice = st.selectbox(" ",  # Invisible label
                                               line_styles,
                                               key=f"param_style_{i}",
                                               index=0,
                                               label_visibility="collapsed")
                line_style = {
                    "solid": "-",
                    "dashed": "--",
                    "dotted": ":"
                }[line_style_choice]
            
            # Convert LaTeX before plot button
            x_python = None
            y_python = None
            if x_latex.strip() and y_latex.strip():
                x_python, _ = latex_to_python(x_latex, param_var='t')
                y_python, _ = latex_to_python(y_latex, param_var='t')
            
            with col6:
                if st.button("Plot", key=f"plot_param_{i}"):
                    if x_python and y_python and t_range:
                        try:
                            # Parse t range with better LaTeX handling
                            t_start, t_end = t_range.split(":")
                            
                            # Convert start and end values from LaTeX if needed
                            t_start_python, _ = latex_to_python(t_start)
                            t_end_python, _ = latex_to_python(t_end)
                            
                            # Replace π with PI constant and evaluate
                            t_start = float(eval(t_start_python.replace("π", str(PI))))
                            t_end = float(eval(t_end_python.replace("π", str(PI))))
                            
                            # Create t values
                            t = np.linspace(t_start, t_end, 1000)
                            
                            # Evaluate x(t) and y(t)
                            x = eval_function(x_python, t, np, xlower, xupper, xlower, xupper, param_var='t')
                            y = eval_function(y_python, t, np, ylower, yupper, xlower, xupper, param_var='t')
                            
                            st.session_state.plot_counter += 1
                            param_data = {
                                "x": x,
                                "y": y,
                                "function": (x_python, y_python),
                                "color": color_choice,
                                "line_style": line_style,
                                "zorder": 10 + st.session_state.plot_counter
                            }
                            
                            if i < len(st.session_state.plotted_parametric_functions):
                                st.session_state.plotted_parametric_functions[i] = param_data
                            else:
                                st.session_state.plotted_parametric_functions.append(param_data)
                        except Exception as e:
                            st.error(f"Error plotting parametric function: {str(e)}")
            
            # Add some space between functions
            st.write("")

        st.caption("Enter latex functions $x(t)$ and $y(t)$ along with a latex domain in the format start:end.")

    with tab4:
        st.subheader("Plot points", divider="gray")
        
        # Create up to 8 point input rows (changed from 5)
        for i in range(8):  # Changed from range(5)
            col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 1, 1, 1], vertical_alignment="bottom")
            
            with col1:
                x_coord = st.number_input(f"$x_{i+1}$", key=f"point_x_{i}")
            
            with col2:
                y_coord = st.number_input(f"$y_{i+1}$", key=f"point_y_{i}")
                
            with col3:
                point_color = st.selectbox("Color", 
                                         options=list(MY_COLORS.keys()), 
                                         key=f"point_color_{i}",
                                         label_visibility="collapsed")
            
            with col4:
                marker_style = st.selectbox("Style", 
                                          ("×", "○"), 
                                          key=f"point_style_{i}",
                                          label_visibility="collapsed")
                marker = "x" if marker_style == "×" else "o"
            
            with col5:
                if st.button("Plot", key=f"plot_point_{i}"):
                    point_data = {
                        "x": x_coord,
                        "y": y_coord,
                        "marker": marker,
                        "color": point_color
                    }
                    
                    if i < len(st.session_state.plotted_points):
                        st.session_state.plotted_points[i] = point_data
                    else:
                        st.session_state.plotted_points.append(point_data)

    with tab5:
        st.subheader("Plot areas", divider="gray")

        # Get list of all plotted functions for selection (remains the same)
        explicit_functions = [f"Explicit {i+1}"
                             for i, func in enumerate(st.session_state.plotted_functions)
                             if func is not None] # Check func is not None
        
        implicit_functions = [f"Implicit {i+1}"
                             for i, func in enumerate(st.session_state.plotted_implicit_functions)
                             if func is not None] # Check func is not None
        
        parametric_functions = [f"Parametric {i+1}"
                               for i, func in enumerate(st.session_state.plotted_parametric_functions)
                               if func is not None] # Check func is not None
        
        # Add placeholder options if no functions are plotted yet
        if not explicit_functions and not implicit_functions and not parametric_functions:
             all_functions = ["(Plot a function first)"]
             # Disable inputs if no functions exist? Or allow Top/Bottom/x-axis?
             # For now, let's allow Top/Bottom/x-axis selection always.
             all_functions_selectable = [] 
        else:
             all_functions_selectable = explicit_functions + implicit_functions + parametric_functions
             
        # --- Create UI for 3 areas ---
        for i in range(3):
            st.markdown(f"--- \n**Area {i+1}**") # Separator and title for each area
            
            # Retrieve current settings for this area index if they exist
            current_area = st.session_state.plotted_areas[i]
            default_outer = current_area["outer_func_id"] if current_area else "Top"
            default_inner = current_area["inner_func_id"] if current_area else "Bottom"
            default_x_start = current_area["x_start"] if current_area else xuserlower
            default_x_end = current_area["x_end"] if current_area else xuserupper
            default_color = current_area["color"] if current_area else "blue"
            default_opacity = current_area["opacity"] if current_area else 0.3
            
            # Define widget keys unique to this area index
            outer_key = f"area_outer_{i}"
            inner_key = f"area_inner_{i}"
            x_start_key = f"area_x_start_{i}"
            x_end_key = f"area_x_end_{i}"
            color_key = f"area_color_{i}"
            opacity_key = f"area_opacity_{i}"
            fill_key = f"area_fill_{i}"
            clear_key = f"area_clear_{i}"

            col1, col2, col3 = st.columns([2, 2, 3]) # Layout columns for function selection
            with col1:
                 # Get index for default selection
                outer_options = ["Top"] + all_functions_selectable
                try:
                    outer_idx = outer_options.index(default_outer)
                except ValueError:
                    outer_idx = 0 # Default to "Top" if previous selection not found
                    
                first_func_id = st.selectbox("Outer",
                                            options=outer_options,
                                            index=outer_idx, # Use calculated index
                                            key=outer_key)
            with col2:
                 # Get index for default selection
                inner_options = ["Bottom", "x-axis"] + all_functions_selectable
                try:
                    inner_idx = inner_options.index(default_inner)
                except ValueError:
                    inner_idx = 0 # Default to "Bottom" if previous selection not found
                    
                second_func_id = st.selectbox("Inner",
                                            options=inner_options,
                                            index=inner_idx, # Use calculated index
                                            key=inner_key)

            # --- Adjust columns for the second row of controls ---
            col4, col5, col6, col7, set_button_col, clear_button_col = st.columns(
                [1.5, 1.5, 1, 1, 0.75, 0.75], # Adjusted ratios
                vertical_alignment="bottom"
            ) 
            # --- End of column adjustment ---

            with col4:
                x_start = st.number_input("Lower $x$", value=default_x_start, key=x_start_key)
            with col5:
                x_end = st.number_input("Upper $x$", value=default_x_end, key=x_end_key)
            with col6:
                 # Get index for default color
                color_options = list(MY_COLORS.keys())
                try:
                     color_idx = color_options.index(default_color)
                except ValueError:
                     color_idx = 0 # Default to first color
                     
                fill_color = st.selectbox("Color",
                                          options=color_options,
                                          key=color_key,
                                          index=color_idx, 
                                          label_visibility="collapsed")
            with col7:
                opacity = st.number_input("Opacity",
                                          min_value=0.0,
                                          max_value=1.0,
                                          value=default_opacity,
                                          step=0.1,
                                          key=opacity_key,
                                          label_visibility="collapsed")
            
            # --- Place buttons directly in their own columns ---
            with set_button_col:
                 if st.button("Set", key=fill_key):
                     if first_func_id and second_func_id:
                         # REMOVE zorder calculation/storage here
                         area_data = {
                             "outer_func_id": first_func_id,
                             "inner_func_id": second_func_id,
                             "x_start": x_start,
                             "x_end": x_end,
                             "color": fill_color,
                             "opacity": opacity,
                             # "zorder": 5 + st.session_state.plot_counter # REMOVED THIS LINE
                         }
                         st.session_state.plotted_areas[i] = area_data
                         # Need to trigger a re-run to plot the newly set area
                         st.rerun() # Add rerun to see change immediately
                     else:
                         st.warning(f"Please select functions for Area {i+1}.")
            with clear_button_col:
                  if st.button("Clear", key=clear_key):
                       st.session_state.plotted_areas[i] = None
                       st.rerun() # Add rerun to see change immediately

        st.caption("""
        If a curve has multiple y-values at an x-coordinate:\n
        • Outer function uses the **maximum** y-value\n
        • Inner function uses the **minimum** y-value
        """)

    with tab6:
        st.subheader("Plot Binomial Distributions", divider="gray")
        
        # Create UI for 3 binomial plots
        for i in range(3):
            st.markdown(f"--- \n**Distribution {i+1}**") 
            
            # Retrieve current settings if they exist
            current_binom = st.session_state.plotted_binomials[i]
            default_n = current_binom["n"] if current_binom else 10
            default_p = current_binom["p"] if current_binom else 0.5
            default_color = current_binom["color"] if current_binom else "blue"
            
            # Define unique keys
            n_key = f"binom_n_{i}"
            p_key = f"binom_p_{i}"
            color_key = f"binom_color_{i}"
            set_key = f"binom_set_{i}"
            clear_key = f"binom_clear_{i}"

            bcol1, bcol2, bcol3 = st.columns([1, 1, 2]) # Layout columns
            with bcol1:
                n_trials = st.number_input(f"$n$ (trials)", 
                                           min_value=1, 
                                           value=default_n, 
                                           step=1, 
                                           key=n_key)
            with bcol2:
                prob_success = st.number_input(f"$p$ (probability)", 
                                               min_value=0.0, 
                                               max_value=1.0, 
                                               value=default_p, 
                                               step=0.01, 
                                               format="%.2f", # Format p display
                                               key=p_key)
            
            bcol4, bcol5, bcol6 = st.columns([1, 1, 1], vertical_alignment="bottom") # Layout columns
            with bcol4:
                 # Get index for default color
                color_options = list(MY_COLORS.keys())
                try:
                     color_idx = color_options.index(default_color)
                except ValueError:
                     color_idx = 0 # Default to first color
                     
                binom_color = st.selectbox("Color",
                                          options=color_options,
                                          key=color_key,
                                          index=color_idx, # Use calculated index
                                          label_visibility="collapsed")
            with bcol5:
                 if st.button("Set", key=set_key):
                     st.session_state.plot_counter += 1 # Increment for zorder
                     binom_data = {
                         "n": n_trials,
                         "p": prob_success,
                         "color": binom_color,
                         "zorder": 10 + st.session_state.plot_counter # Start zorder similar to functions
                     }
                     st.session_state.plotted_binomials[i] = binom_data
                     st.rerun()
            with bcol6:
                  if st.button("Clear", key=clear_key):
                       st.session_state.plotted_binomials[i] = None
                       st.rerun()

        st.caption("Plots the probability mass function $P(X=k)$ for $k=0, 1, ..., n$.")


for func_data in st.session_state.plotted_functions:
    if "zorder" not in func_data:
        st.session_state.plot_counter += 1
        func_data["zorder"] = st.session_state.plot_counter
    
    ax.plot(
        func_data["x"],
        func_data["y"],
        color=MY_COLORS[func_data["color"]],
        linestyle=func_data["line_style"],
        linewidth=axis_weight * 1.3,
        zorder=func_data["zorder"])

for point_data in st.session_state.plotted_points:
    if "zorder" not in point_data:
        st.session_state.plot_counter += 1
        point_data["zorder"] = 1000 + st.session_state.plot_counter  # Much higher base zorder for points
        
    if point_data["marker"] == "x":
        markersize = axis_weight * 6
        markeredgewidth = axis_weight
    else:  # circle
        markersize = axis_weight * 3
        markeredgewidth = axis_weight
    
    ax.plot(point_data["x"], 
           point_data["y"], 
           marker=point_data["marker"],
           color=MY_COLORS[point_data["color"]], 
           markersize=markersize,
           markeredgewidth=markeredgewidth,
           linestyle='none',
           zorder=point_data["zorder"])

# Plot all stored implicit functions
for implicit_data in st.session_state.plotted_implicit_functions:
    if implicit_data and implicit_data["function"].strip():
        if "zorder" not in implicit_data:
            st.session_state.plot_counter += 1
            implicit_data["zorder"] = st.session_state.plot_counter
            
        x = np.linspace(xlower, xupper, 1000)
        y = np.linspace(ylower, yupper, 1000)
        X, Y = np.meshgrid(x, y)
        
        # Evaluate the expression
        x_sym, y_sym = sp.symbols('x y')
        expr = eval(implicit_data["function"], {
            "x": x_sym, 
            "y": y_sym, 
            "lib": sp  # This is what users expect to use
        })
        
        # Convert to numpy function and plot
        f = sp.lambdify((x_sym, y_sym), expr)
        Z = f(X, Y)
        
        ax.contour(X, Y, Z, levels=[0], 
                  colors=[MY_COLORS[implicit_data["color"]]],
                  linestyles=[implicit_data["line_style"]],
                  linewidths=axis_weight * 1.3,
                  zorder=implicit_data["zorder"])

for param_data in st.session_state.plotted_parametric_functions:
    if param_data:
        # Filter out NaN values before plotting
        valid_mask = ~(np.isnan(param_data["x"]) | np.isnan(param_data["y"]))
        ax.plot(
            param_data["x"][valid_mask],
            param_data["y"][valid_mask],
            color=MY_COLORS[param_data["color"]],
            linestyle=param_data["line_style"],
            linewidth=axis_weight * 1.3,
            zorder=param_data["zorder"])

# --- Add loop for plotting AREAS ---
for i, area_data in enumerate(st.session_state.plotted_areas):
    if area_data is not None:
        # Extract parameters for this area
        first_func_idx = area_data["outer_func_id"]
        second_func_idx = area_data["inner_func_id"]
        x_start = area_data["x_start"]
        x_end = area_data["x_end"]
        fill_color = area_data["color"]
        opacity = area_data["opacity"]
        # REMOVE zorder extraction: zorder = area_data["zorder"]
        
        # --- Assign low zorder for areas ---
        zorder_value = 1.0 + i * 0.01 # e.g., 1.0, 1.01, 1.02
        # --- End assignment ---

        try:
            # Get x values for the fill
            # Ensure start is less than end
            if x_start > x_end:
                st.warning(f"Area {i+1}: Lower x ({x_start}) is greater than Upper x ({x_end}). Swapping them.")
                x_start, x_end = x_end, x_start 
                
            # Prevent zero-width area    
            if np.isclose(x_start, x_end):
                 st.warning(f"Area {i+1}: Lower x and Upper x are the same. Skipping fill.")
                 continue # Skip to next area
                 
            x_fill = np.linspace(x_start, x_end, 500) # Reduced points for performance

            # Initialize y arrays
            upper_y = None
            lower_y = None

            # --- Get upper function data --- (Copied and adapted from original 'Fill' button logic)
            if first_func_idx == "Top":
                upper_y = np.full_like(x_fill, yupper + 0.025 * ydifference)
            elif first_func_idx.startswith("Explicit"):
                idx = int(first_func_idx.split()[1]) - 1
                if idx < len(st.session_state.plotted_functions) and st.session_state.plotted_functions[idx]:
                     upper_y = eval_function(st.session_state.plotted_functions[idx]["function"], x_fill, np, ylower, yupper)
                else: upper_y = np.full_like(x_fill, np.nan) # Function doesn't exist
            elif first_func_idx.startswith("Implicit"):
                idx = int(first_func_idx.split()[1]) - 1
                if idx < len(st.session_state.plotted_implicit_functions) and st.session_state.plotted_implicit_functions[idx]:
                    implicit_data = st.session_state.plotted_implicit_functions[idx]
                    try:
                        x = np.linspace(xlower, xupper, 200) # Reduced points
                        y = np.linspace(ylower, yupper, 200) # Reduced points
                        X, Y = np.meshgrid(x, y)
                        x_sym, y_sym = sp.symbols('x y')
                        # Ensure 'lib' is available if needed in implicit func string
                        expr = eval(implicit_data["function"], {"x": x_sym, "y": y_sym, "lib": sp, "np": np, "sp": sp}) 
                        f = sp.lambdify((x_sym, y_sym), expr, modules=['numpy', {'ImmutableDenseMatrix': np.array}]) # Use numpy for lambdify
                        Z = f(X, Y)
                        temp_fig, temp_ax = plt.subplots()
                        cs = temp_ax.contour(X, Y, Z, levels=[0])
                        plt.close(temp_fig)
                        if len(cs.allsegs[0]) > 0:
                            x_points = np.concatenate([seg[:, 0] for seg in cs.allsegs[0]])
                            y_points = np.concatenate([seg[:, 1] for seg in cs.allsegs[0]])
                            upper_y = get_y_values_for_curve(x_fill, x_points, y_points, take_max=True)
                        else: upper_y = np.full_like(x_fill, np.nan)
                    except Exception as e_impl: upper_y = np.full_like(x_fill, np.nan); st.error(f"Area {i+1} Implicit Upper Error: {e_impl}")
                else: upper_y = np.full_like(x_fill, np.nan) # Function doesn't exist
            elif first_func_idx.startswith("Parametric"):
                idx = int(first_func_idx.split()[1]) - 1
                if idx < len(st.session_state.plotted_parametric_functions) and st.session_state.plotted_parametric_functions[idx]:
                    param_data = st.session_state.plotted_parametric_functions[idx]
                    try:
                         upper_y = get_y_values_for_curve(x_fill, param_data["x"], param_data["y"], take_max=True)
                    except Exception as e_param: upper_y = np.full_like(x_fill, np.nan); st.error(f"Area {i+1} Parametric Upper Error: {e_param}")
                else: upper_y = np.full_like(x_fill, np.nan) # Function doesn't exist

            # --- Get lower function data --- (Copied and adapted similarly)
            if second_func_idx == "Bottom":
                lower_y = np.full_like(x_fill, ylower - 0.025 * ydifference)
            elif second_func_idx == "x-axis":
                lower_y = np.zeros_like(x_fill)
            elif second_func_idx.startswith("Explicit"):
                idx = int(second_func_idx.split()[1]) - 1
                if idx < len(st.session_state.plotted_functions) and st.session_state.plotted_functions[idx]:
                    lower_y = eval_function(st.session_state.plotted_functions[idx]["function"], x_fill, np, ylower, yupper)
                else: lower_y = np.full_like(x_fill, np.nan)
            elif second_func_idx.startswith("Implicit"):
                idx = int(second_func_idx.split()[1]) - 1
                if idx < len(st.session_state.plotted_implicit_functions) and st.session_state.plotted_implicit_functions[idx]:
                    implicit_data = st.session_state.plotted_implicit_functions[idx]
                    try:
                        x = np.linspace(xlower, xupper, 200) # Reduced points
                        y = np.linspace(ylower, yupper, 200) # Reduced points
                        X, Y = np.meshgrid(x, y)
                        x_sym, y_sym = sp.symbols('x y')
                        # Ensure 'lib' is available if needed in implicit func string
                        expr = eval(implicit_data["function"], {"x": x_sym, "y": y_sym, "lib": sp, "np": np, "sp": sp}) 
                        f = sp.lambdify((x_sym, y_sym), expr, modules=['numpy', {'ImmutableDenseMatrix': np.array}])
                        Z = f(X, Y)
                        temp_fig, temp_ax = plt.subplots()
                        cs = temp_ax.contour(X, Y, Z, levels=[0])
                        plt.close(temp_fig)
                        if len(cs.allsegs[0]) > 0:
                            x_points = np.concatenate([seg[:, 0] for seg in cs.allsegs[0]])
                            y_points = np.concatenate([seg[:, 1] for seg in cs.allsegs[0]])
                            lower_y = get_y_values_for_curve(x_fill, x_points, y_points, take_max=False) # take_max=False for lower
                        else: lower_y = np.full_like(x_fill, np.nan)
                    except Exception as e_impl: lower_y = np.full_like(x_fill, np.nan); st.error(f"Area {i+1} Implicit Lower Error: {e_impl}")
                else: lower_y = np.full_like(x_fill, np.nan)
            elif second_func_idx.startswith("Parametric"):
                 idx = int(second_func_idx.split()[1]) - 1
                 if idx < len(st.session_state.plotted_parametric_functions) and st.session_state.plotted_parametric_functions[idx]:
                     param_data = st.session_state.plotted_parametric_functions[idx]
                     try:
                          lower_y = get_y_values_for_curve(x_fill, param_data["x"], param_data["y"], take_max=False) # take_max=False for lower
                     except Exception as e_param: lower_y = np.full_like(x_fill, np.nan); st.error(f"Area {i+1} Parametric Lower Error: {e_param}")
                 else: lower_y = np.full_like(x_fill, np.nan) # Function doesn't exist


            # --- Check if we have valid data and fill ---
            if upper_y is not None and lower_y is not None:
                # Ensure y values are within plot limits (approx) - helps prevent weird fill artifacts
                # Clip values slightly outside the user range to avoid issues near boundaries
                upper_y = np.clip(upper_y, ylower - abs(0.1*ydifference), yupper + abs(0.1*ydifference))
                lower_y = np.clip(lower_y, ylower - abs(0.1*ydifference), yupper + abs(0.1*ydifference))

                # Define where lower_y <= upper_y, considering NaNs
                valid_fill_mask = (lower_y <= upper_y) & ~np.isnan(upper_y) & ~np.isnan(lower_y)

                if np.any(valid_fill_mask):
                    ax.fill_between(x_fill[valid_fill_mask],
                                  lower_y[valid_fill_mask],
                                  upper_y[valid_fill_mask],
                                  color=MY_COLORS[fill_color],
                                  alpha=opacity,
                                  zorder=zorder_value, # Use the new low zorder
                                  linewidth=0.0) # No edge line for fill
                elif np.any(~np.isnan(upper_y)) and np.any(~np.isnan(lower_y)): # Check if functions existed but didn't overlap correctly
                     st.warning(f"Area {i+1}: Inner function is above outer function in the specified range.")

            else: # Handles cases where one or both functions couldn't be evaluated
                st.warning(f"Area {i+1}: Could not compute valid boundaries for filling.")

        except Exception as e:
            st.error(f"Error processing Area {i+1}: {str(e)}")
# --- End of Area plotting loop ---

# --- Add loop for plotting BINOMIAL distributions ---
for i, binom_data in enumerate(st.session_state.plotted_binomials):
    if binom_data is not None:
        # Extract parameters
        n = binom_data["n"]
        p = binom_data["p"]
        color = binom_data["color"]
        
        # Assign low zorder for bars
        zorder_value = 1.5 + i * 0.01 # e.g., 1.50, 1.51, 1.52

        try:
            # Define range of outcomes k
            k_values = np.arange(0, n + 1)

            # Calculate PMF using scipy.stats.binom
            pmf_values = binom.pmf(k_values, n, p)

            # Plot as a bar chart - alpha parameter is now removed
            ax.bar(k_values,
                   pmf_values,
                   color=MY_COLORS[color],
                   width=0.5, 
                   zorder=zorder_value # Use the low zorder
                   # alpha parameter removed here
                   )

        except Exception as e:
            st.error(f"Error plotting Binomial {i+1} (n={n}, p={p}): {str(e)}")
# --- End of Binomial plotting loop ---


if not white_background:
    ax.set_facecolor('none')  # Transparent background
    fig.patch.set_facecolor('none')  # Transparent figure background

plot_placeholder.pyplot(fig)


#-------SAVE IMAGES-------------------------

svg_buffer = io.StringIO()
fig.savefig(svg_buffer, format="svg")
svg_data = svg_buffer.getvalue()
svg_buffer.close()

svg_placeholder.download_button(
    label="Download SVG",
    data=svg_data,
    file_name="figure1.svg",
    mime="image/svg+xml",
)

png_buffer = io.BytesIO()
fig.savefig(png_buffer, format="png", dpi=300, bbox_inches="tight", pad_inches=0)
png_buffer.seek(0)
png_data = png_buffer.getvalue()
png_buffer.close()

png_placeholder.download_button(
    label = "Download PNG", 
    data=png_data, 
    file_name="figure1.png", 
    mime="image/png")


#-------unused-------

# latex_preview = sp.latex(y1_sym)  # Convert to LaTeX
# st.latex(f"y = {latex_preview}")  # Display LaTeX preview
