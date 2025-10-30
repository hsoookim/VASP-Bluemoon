import os, sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.integrate import quad, simps, trapezoid
from scipy.interpolate import CubicSpline

STYLE_FILE = "/home/hk26346/00-Script/acs_plot_style.py"
STYLE_DIR  = os.path.dirname(STYLE_FILE)

if STYLE_DIR not in sys.path:
    sys.path.append(STYLE_DIR)

from acs_plot_style import apply_style
apply_style(usetex=False)     

def read_data(file_path):
    """Read label, r, g, and sem values from the file."""
    image, r, g, sem = [], [], [], []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                row = line.strip().split()
                if len(row) == 4:
                    try:
                        image.append(row[0])
                        r.append(float(row[1]))
                        g.append(float(row[2]))
                        sem.append(float(row[3]))
                    except ValueError:
                        print(f"Warning: Skipping invalid line: {row}")
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

    if len(r) < 2:
        print("Error: Not enough data for integration.")
        sys.exit(1)

    return image, r, g, sem


def fit_function(r, g, fit_type='poly', degree=3):
    """Fit r vs g using either a polynomial or a cubic spline."""
    if fit_type == 'spline':
        # Sort data by r for spline
        r_np, g_np = np.array(r), np.array(g)
        sort_idx = np.argsort(r_np)
        r_sorted = r_np[sort_idx]
        g_sorted = g_np[sort_idx]
        
        # Ensure r values are strictly increasing
        if np.any(np.diff(r_sorted) <= 0):
            raise ValueError("r values must be strictly increasing and unique for spline fitting.")
        
        spline = CubicSpline(r_sorted, g_sorted)
        print("DEBUG: Spline fit object created.")
        return spline
    else:
        coeffs = np.polyfit(r, g, degree)
        print(f"DEBUG: Polynomial coefficients: {coeffs}")
        return np.poly1d(coeffs)


def integrate_function(func, r_vals, method='quad', dense=True):
    """Integrate any function using the specified method with optional dense or raw spacing."""
    if dense:
        r_points = np.linspace(min(r_vals), max(r_vals), 500)
    else:
        r_points = r_vals

    if method == 'quad':
        tg_vals = [0.0]
        for i in range(1, len(r_points)):
            area, _ = quad(func, r_points[i - 1], r_points[i])
            tg_vals.append(tg_vals[-1] + area)
        return list(r_points), tg_vals

    elif method == 'trapezoid':
        if dense:
            y = func(r_points)
            tg_vals = [0.0]
            for i in range(1, len(r_points)):
                area = trapezoid(y[:i+1], r_points[:i+1])
                tg_vals.append(area)
            return list(r_points), tg_vals
        else:
            y = func(r_vals)
            tg_vals = [0.0]
            for i in range(1, len(r_vals)):
                area = trapezoid(y[:i+1], r_vals[:i+1])
                tg_vals.append(area)
            return r_vals, tg_vals

    else:
        raise ValueError("Unsupported integration method. Choose 'quad' or 'trapezoid'.")


def plot_r_vs_g(r, g, sem, func=None, invert_axis=False, label=None, filename_suffix="plot"):
    fig, ax = plt.subplots(figsize=(3.25, 3.25))

    ax.errorbar(r, g, yerr=sem, fmt='o', fillstyle='none', color='black', label='r vs g (with SEM)')

    if func is not None:
        r_dense = np.linspace(min(r), max(r), 500)
        ax.plot(r_dense, func(r_dense), 'r-', label=label if label else 'Fitted curve')

    ax.axhline(y=0, color='black', linestyle='--', label='g = 0')
    ax.set_xlabel('Coordinate')
    ax.set_ylabel(r"Mean Force (eV/$\AA$)")
    ax.set_title('r vs g')

    if invert_axis:
        ax.invert_xaxis()

    # ax.grid(True)
    ax.legend()
    fig.savefig(f'r_vs_g_{filename_suffix}.png', bbox_inches="tight")
    return fig, ax


def plot_r_vs_tg(r_vals, tg_vals, invert_axis, filename_suffix):
    max_tg = max(tg_vals)
    max_index = tg_vals.index(max_tg)
    max_r = r_vals[max_index]

    #fig, ax = plt.subplots(figsize=(7, 2.5))
    fig, ax = plt.subplots(figsize=(3.25, 3.25))

    ax.plot(r_vals, tg_vals, marker='o', linestyle='-', color='black')
    #ax.axhline(y=0, color='black', linestyle='--', label='G = 0')
    ax.set_xlabel('Reaction Coordinate')
    ax.set_ylabel('G (eV)')
    #ax.set_title('Free Energy Path')
    ax.set_ylim(0, 2.0)

    if invert_axis:
        ax.invert_xaxis()

    # ax.grid(True)
    ax.annotate(f'{max_tg:.3f} eV', (max_r, max_tg),
                textcoords="offset points", xytext=(10, 10),
                ha='center', fontsize=12)

    fig.savefig(f'r_vs_tg_{filename_suffix}.png', bbox_inches="tight")
    return fig, ax


def integrate_and_plot(file_path):
    user_input = input("Invert x-axis for plots? (yes/no): ").strip().lower()
    invert_axis = user_input in ("yes", "y")

    image, r, g, sem = read_data(file_path)

    fit_type = input("Choose fit type (poly/spline/raw): ").strip().lower()
    dense_input = input("Use dense sampling for integration? (yes/no): ").strip().lower()
    dense = dense_input in ("yes", "y")
    interval_type = "dense" if dense else "rval"

    if fit_type == 'spline':
        func = fit_function(r, g, fit_type='spline')
        print(f"DEBUG: Spline evaluation example func({r[0]}): {func(r[0])}")
        method = input("Choose integration method (quad/trapezoid): ").strip().lower()
        r_vals, tg_vals = integrate_function(func, r, method, dense)
        label = 'Spline fit'
        filename_suffix = f'spline_{interval_type}'

    elif fit_type == 'raw':
        method = 'trapezoid' # Use raw data for integration
        tg_vals = [0.0]
        for i in range(1, len(r)):
            area = trapezoid(g[:i+1], r[:i+1])
            tg_vals.append(area)
        r_vals = r
        label = 'Raw data'
        filename_suffix = f'raw_{interval_type}'

    else:
        while True:
            try:
                degree = int(input("Enter polynomial degree: ").strip())
                if degree >= 1:
                    break
                else:
                    print("Degree must be >= 1")
            except ValueError:
                print("Error: Please enter a valid integer.")

        func = fit_function(r, g, fit_type='poly', degree=degree)
        print(f"DEBUG: Poly evaluation example func({r[0]}): {func(r[0])}")
        method = input("Choose integration method (quad/trapezoid): ").strip().lower()
        if method in ["quad", "q"]:
            method = "quad"
        elif method in ["trapezoid", "t"]:
            method = "trapezoid"
        else:
            raise ValueError("Invalid choice. Please enter 'quad' (q) or 'trapezoid' (t).")
        r_vals, tg_vals = integrate_function(func, r, method, dense)
        label = f'{degree}-degree poly'
        filename_suffix = f'poly{degree}_{interval_type}'

    # Use the minimum tg value as reference point
    min_tg = min(tg_vals)
    tg_vals = [v - min_tg for v in tg_vals]


    for xi, tgi in zip(r_vals, tg_vals):
        print(f"r = {xi:.4f}, G = {tgi:.6f} eV")

    plot_r_vs_g(r, g, sem, func if fit_type != 'raw' else None, invert_axis, label, filename_suffix)
    plot_r_vs_tg(r_vals, tg_vals, invert_axis, filename_suffix)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python integrate_poly.py <data_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    integrate_and_plot(file_path)
