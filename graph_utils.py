import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import sympy as sp
from sympy import nsimplify, pi, E, latex
from sympy.parsing.latex import parse_latex
import streamlit as st
import io
import warnings

# Add this constant at the top with the other imports
E = 2.7182818284590452  # Euler's number

def latex_to_python(latex_str, param_var='x'):
    """Converts LaTeX math expression to Python code.
    Returns (python_str, preview_expr) on success or (None, error_msg) on failure.
    param_var: the variable to use in the expression (default 'x' for regular functions, 't' for parametric)"""
    try:
        # Handle \log(x) before parsing - replace with \log_{10}(x)
        if r'\log(' in latex_str and not r'\log_' in latex_str:
            latex_str = latex_str.replace(r'\log(', r'\log_{10}(')
            
        # Parse LaTeX to SymPy expression
        expr = parse_latex(latex_str)
        
        # Convert to string and replace function names with lib. prefix
        python_str = str(expr)
        
        # Handle the special case of ln(x) first
        if 'log' in python_str and ', E)' in python_str:
            python_str = python_str.replace(f'log({param_var}, E)', f'lib.log({param_var})')
        elif 'log' in python_str and ', 10)' in python_str:
            python_str = python_str.replace(f'log({param_var}, 10)', f'lib.log10({param_var})')
        elif 'log' in python_str and ',' in python_str:
            # Handle arbitrary base: log(x, base) -> log(x)/log(base)
            base = python_str.split(',')[1].strip().rstrip(')')
            python_str = f'lib.log({param_var})/lib.log({base})'
        else:
            # Direct replacements (where latex command = python function name)
            for func in ['sin', 'cos', 'tan', 'exp', 'sqrt']:
                python_str = python_str.replace(func, f'lib.{func}')
            
            # Special cases where latex command ≠ python function name
            replacements = {
                'ln': 'lib.log',  # natural logarithm
                'log(': 'lib.log10(',  # base-10 logarithm (this is the standard in LaTeX)
                'Abs': 'lib.abs',  # Absolute value (modulus)
                'arcsin': 'lib.asin',  # inverse sine
                'arccos': 'lib.acos',  # inverse cosine
                'arctan': 'lib.atan',  # inverse tangent
                'csc': 'reciprocal(sin)',  # cosecant
                'sec': 'reciprocal(cos)',  # secant
                'cot': 'reciprocal(tan)',  # cotangent
                'e': 'lib.e',  # Euler's number
            }
            
            for latex_func, py_func in replacements.items():
                # Use word boundaries for Abs to avoid replacing AbsoluteGamma etc. if ever added
                if latex_func == 'Abs':
                     python_str = python_str.replace(latex_func + '(', py_func + '(') # Replace Abs(...)
                else:
                     python_str = python_str.replace(latex_func, py_func)
        
        return python_str, expr
    except Exception as e:
        return None, f"Invalid LaTeX: {str(e)}"

def eval_function(user_func, x, lib, ylower=None, yupper=None, xlower=None, xupper=None, param_var='x'):
    """Evaluates the user-defined function with the given library (np or sp).
    For implicit functions, x should be a tuple of (x_sym, y_sym).
    For parametric functions, param_var should be 't'."""
    if isinstance(x, tuple):  # Handle implicit function case
        x_vals, y_vals = x[0], x[1]
        result = eval(user_func, {"x": x_vals, "y": y_vals, "lib": lib})
        # Filter points outside plot boundaries for implicit functions
        if ylower is not None and yupper is not None and xlower is not None and xupper is not None:
            result[(y_vals < ylower) | (y_vals > yupper) | (x_vals < xlower) | (x_vals > xupper)] = np.nan
        return result
    else:  # Handle explicit and parametric function cases
        eval_dict = {
            param_var: x, 
            "lib": lib,
            "log": lib.log,
            "log10": lib.log10,
            "E": E
        }
        y = eval(user_func, eval_dict)
        
        if isinstance(x, np.ndarray):
            if param_var == 'x':  # For explicit functions
                # Detect rapid changes
                threshold_change = 10000
                dy = lib.abs(lib.diff(y))
                y[1:][dy > threshold_change] = lib.nan    # Handles asymptotes
                y[:-1][dy > threshold_change] = lib.nan
                
                # Apply y-range filtering
                if ylower is not None and yupper is not None:
                    y[(y < ylower) | (y > yupper)] = np.nan
            else:  # For parametric functions
                # Detect rapid changes in both x and y for parametric curves
                threshold_change = 10000
                if isinstance(y, np.ndarray):  # y coordinate
                    dy = lib.abs(lib.diff(y))
                    y[1:][dy > threshold_change] = lib.nan
                    y[:-1][dy > threshold_change] = lib.nan
                    
                # Filter points outside plot boundaries
                if ylower is not None and yupper is not None and xlower is not None and xupper is not None:
                    y[(y < ylower) | (y > yupper) | (x < xlower) | (x > xupper)] = lib.nan
            
        return y

def create_graph(xlower, xupper, ylower, yupper, xstep, ystep, gridstyle,
    xminordivisor, yminordivisor, imagewidth, imageheight,
    xuserlower, xuserupper, yuserlower, yuserupper,
    showvalues, axis_weight, label_size, white_background, 
    label_format_is_decimal,
    x=None, skip_static_plots=False):
    """Create and save a mathematical graph with the specified parameters."""

    #------define some nested functions---------
                    
    def plot_function(y, color, style, x_coords=None):
        """Plot a function with specified parameters."""
        if x_coords is None:
            x_coords = x  # Use the default x values for explicit functions (y = f(x))
        ax.plot(x_coords, y,
            color=color,
            linestyle=style,
            linewidth=axis_weight*1.3) # Vary line width

    def set_grid_style(style):
        """Set the grid style."""
        # Always set major locators
        ax.set_xticks(np.arange(xuserlower, xuserupper + xstep, xstep))
        ax.set_yticks(np.arange(yuserlower, yupper + ystep, ystep)) # Use yupper here to include potential endpoint

        # --- Define low zorder for gridlines ---
        grid_zorder = 0.5 
        # --- End definition ---

        if style == 'None':
            ax.grid(False)
        elif style == 'Major':
            ax.grid(True, which='major', color='#666666', linestyle='-', alpha=0.5, linewidth=axis_weight*0.7, zorder=grid_zorder)
        elif style == 'Minor':
            ax.xaxis.set_minor_locator(plt.MultipleLocator(xstep/xminordivisor))
            ax.yaxis.set_minor_locator(plt.MultipleLocator(ystep/yminordivisor))
            ax.grid(True, which='major', color='#666666', linestyle='-', alpha=0.5, linewidth=axis_weight*0.7, zorder=grid_zorder)
            ax.grid(True, which='minor', color='#999999', linestyle='-', alpha=0.2, linewidth=axis_weight*0.7, zorder=grid_zorder)
            ax.tick_params(which='minor', length=0)

    def sympy_formatter(x, pos):
        """Format a number as a LaTeX expression, preferring simple integers/fractions."""
        try:
            # Handle zero explicitly
            if abs(x) < 1e-10:
                return '$0$'

            # Check if the number is very close to an integer
            if np.isclose(x, round(x), atol=1e-8): # Check if close to integer
                 latex_str = f'{int(round(x))}' # Format as integer
                 return f'${latex_str}$'

            # --- Revised Logic (from previous pi issue fix) ---
            tolerance = 0.001 
            expr_rational = nsimplify(x, tolerance=tolerance)
            is_rational_accurate = abs(expr_rational.evalf() - x) < tolerance
            expr_pi = nsimplify(x, [pi], tolerance=tolerance)
            is_pi_accurate = abs(expr_pi.evalf() - x) < tolerance

            if is_rational_accurate and isinstance(expr_rational, (sp.Integer, sp.Rational)):
                final_expr = expr_rational
            elif is_pi_accurate:
                 final_expr = expr_pi
            elif is_rational_accurate: 
                 final_expr = expr_rational
            else:
                 # Fallback: Check for integer again, otherwise use general format
                 if np.isclose(x, round(x), atol=1e-8):
                      latex_str = f'{int(round(x))}'
                 else:
                      latex_str = f'{x:.4g}' # Use more significant digits for fallback
                 return f'${latex_str}$' 

            latex_str = latex(final_expr)
            latex_str = latex_str.replace(r'\frac', r'\dfrac')
            
        except (TypeError, AttributeError, ValueError):
             # Fallback: Check for integer again, otherwise use general format
             if np.isclose(x, round(x), atol=1e-8):
                  latex_str = f'{int(round(x))}'
             else:
                  latex_str = f'{x:.4g}' # Use more significant digits for fallback
             return f'${latex_str}$'
             
        return f'${latex_str}$'
        
    def decimal_formatter(x, pos):
        """Format a number as a standard decimal, avoiding early scientific notation."""
        # Handle zero explicitly
        if abs(x) < 1e-10: return '0' 
        
        # Check if the number is very close to an integer
        if np.isclose(x, round(x), atol=1e-8):
            return f'{int(round(x))}' # Format as integer
        
        # Use fixed point for reasonably small/large numbers, general otherwise
        if 0.01 <= abs(x) < 10000: # Adjust range as needed
            # Attempt to format with a few decimal places, removing trailing zeros/point
            formatted = f'{x:.4f}'.rstrip('0').rstrip('.')
            return formatted
        else:
            return f'{x:.4g}' # Use general format (allows scientific) for very large/small
    # --- End of Decimal Formatter ---

    #------create the graph---------
                    
    fig, ax = plt.subplots(figsize=(imagewidth, imageheight))

    if not skip_static_plots:
        i = 1
        while True:
            try:
                y = eval(f'y{i}')
                color = eval(f'y{i}color')
                style = eval(f'y{i}style')
                try:
                    x_coords = eval(f'x{i}')
                    plot_function(y, color, style, x_coords)
                except NameError:
                    plot_function(y, color, style)
                i += 1
            except NameError:
                break

    # Axis spines
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_position('zero')
        ax.spines[spine].set_linewidth(axis_weight)
        ax.spines[spine].set_color('#435159')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
                    
    ax.yaxis.set_ticks_position('none')
    ax.xaxis.set_ticks_position('none')

    # --- Explicitly draw gridlines and ticks BELOW data elements ---
    ax.set_axisbelow(True)
    # --- End Addition ---

    set_grid_style(gridstyle) # Apply grid (now respecting axisbelow)

    if showvalues:
        # --- Conditional Formatter Application ---
        if label_format_is_decimal:
            ax.xaxis.set_major_formatter(FuncFormatter(decimal_formatter))
            ax.yaxis.set_major_formatter(FuncFormatter(decimal_formatter))
        else:
            ax.xaxis.set_major_formatter(FuncFormatter(sympy_formatter))
            ax.yaxis.set_major_formatter(FuncFormatter(sympy_formatter))
        # --- End of Conditional Formatter ---

        ax.tick_params(axis='both', 
                       labelsize=label_size, 
                       labelfontfamily='sans-serif', 
                       colors = '#435159')
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            # --- Restore background logic to depend only on white_background toggle ---
            if white_background: # Check only the main toggle
                label.set_bbox(dict(facecolor='white',
                                  edgecolor='none',
                                  pad=1))            
            else:
                label.set_bbox(None) 
            # --- End of background logic change ---
            
        yticks = ax.get_yticks()
        xticks = ax.get_xticks()
        # Filter out the zero tick if it exists before removing it
        ax.set_yticks([tick for tick in yticks if abs(tick) > 1e-10])
        ax.set_xticks([tick for tick in xticks if abs(tick) > 1e-10])
    else:
        ax.set_xticklabels([])
        ax.set_yticklabels([])

    ax.set_xlim(xlower, xupper)
    ax.set_ylim(ylower, yupper)

    return fig, ax 

def get_y_values_for_curve(x_fill, curve_points_x, curve_points_y, take_max=True):
    """
    Get y values for a curve that might have multiple y values per x.
    Handles unsorted input points and potential NaNs.
    Args:
        x_fill: x values to interpolate/find matches at
        curve_points_x: x coordinates of the curve points
        curve_points_y: y coordinates of the curve points
        take_max: if True, take maximum y value for each x, otherwise take minimum
    Returns:
        Array of y values corresponding to x_fill points, with NaNs where no match found.
    """
    # Filter out NaN pairs immediately
    valid_mask = ~np.isnan(curve_points_x) & ~np.isnan(curve_points_y)
    if not np.any(valid_mask):
        return np.full_like(x_fill, np.nan) # Return all NaNs if no valid points

    x_valid = curve_points_x[valid_mask]
    y_valid = curve_points_y[valid_mask]
    
    # Sort points by x-coordinate for efficient processing
    sort_idx = np.argsort(x_valid)
    x_sorted = x_valid[sort_idx]
    y_sorted = y_valid[sort_idx]

    # Find y values for each x in x_fill
    y_result = np.full_like(x_fill, np.nan) # Initialize with NaNs

    # Use searchsorted for potentially faster lookups
    # Find indices where x_fill values would be inserted into x_sorted
    left_indices = np.searchsorted(x_sorted, x_fill, side='left')
    right_indices = np.searchsorted(x_sorted, x_fill, side='right')

    for i, x in enumerate(x_fill):
        # Get the slice of y_sorted corresponding to this x value
        relevant_y_slice = y_sorted[left_indices[i]:right_indices[i]]
        
        if relevant_y_slice.size > 0:
            with warnings.catch_warnings(): # Suppress warning on empty slice max/min
                 warnings.simplefilter("ignore", category=RuntimeWarning)
                 if take_max:
                     y_result[i] = np.nanmax(relevant_y_slice)
                 else:
                     y_result[i] = np.nanmin(relevant_y_slice)
        # else: y_result[i] remains NaN

    # Simple interpolation for NaNs between valid points (optional, can be slow)
    # This helps fill small gaps but might not be perfect for complex curves
    # Consider commenting out if performance is critical or behavior is undesirable
    is_nan = np.isnan(y_result)
    if np.any(is_nan) and np.any(~is_nan): # Check if there are both NaNs and non-NaNs
         try:
              # Use non-NaN points for interpolation
              x_non_nan = x_fill[~is_nan]
              y_non_nan = y_result[~is_nan]
              if len(x_non_nan) > 1: # Need at least 2 points to interpolate
                   y_result[is_nan] = np.interp(x_fill[is_nan], x_non_nan, y_non_nan)
         except Exception:
              pass # Ignore interpolation errors

    return y_result
