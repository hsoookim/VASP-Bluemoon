# VASP-Bluemoon
Thermodynamic Integration – Blue Moon Method (VASP)
This repository contains scripts and input examples for performing thermodynamic integration (TI) with the Blue Moon ensemble method using VASP. 
The workflow targets to run contrained AIMD to obtain free-energy profiles G(ξ) along a reaction coordinate ξ.

## What this repo provides: 
- **INCAR templates** for constrained AIMD.
- **Linear interpolation** of reaction-coordinate (“images” along ξ).
- **Parsers** for mean forces (⟨∂G/∂ξ⟩) from REPORTs per image.
- **Integration utilities** to compute G(ξ) profile optionally fitting.

## VASP cAIMD Setup
### a. INCAR
- `LBLUEOUT = .TRUE.`  
  Required to obtain the **free-energy gradient**. This prints to the `REPORT` file after the `>Blue_moon` keyword for each MD step.  

### b. ICONST
Defines the **geometric constraint(s)** for the simulation.  
- Documentation: [VASP ICONST manual](https://cms.mpi.univie.ac.at/vasp/vasp/ICONST.html)  
- Example:  
  Suppose you define one contraint, `X-coordinate of O atom`, and vary it systematically, for example by linear interpolation.  
  If you create 9 incremental variations of 'X-coordinate of O atom', this corresponds to **11 separate constrained MD (cMD) runs**, including the starting and ending configurations.

### c. POSCAR, KPOINTS, POTCAR
No modifications are required compared to standard AIMD runs.  

### d. REPORT File Management

When running cAIMD in multiple stages (e.g., restarting jobs or splitting into shorter time blocks),  
**always make a copy of the `REPORT` file at the end of each segment.**  
- Rename each copy systematically (e.g. `report_x`).  
- Later, the extraction script (`G_dat.sh`) can be pointed to these files (`report_*`) and will process them together.  

## Post-processing
### G_dat.sh
This script processes `report_*` files computes the mean force ⟨∂G/∂ξ⟩, with error bars.
- Run the “g_dat.sh” shell in directory where all folders are located to extract averaged values of reaction coordinate values and free-energy gradients.
- In this script, you have to give how many steps will be ignored as equilibration step.
- Concatenates all `report_*` files in each directory into a single file `rep.$i.1`.
- Reads the constrained coordinate (`x1`) from the `report_1` file (based on the `ICONST` definition).
- Averages the fifth column (scaled force term) over the production portion of the trajectory.  
- Normalizes by the factor `zet` from column 3.
- Computes the standard error of the mean (SEM).
- Store the output in a file named as ‘delG.dat’. with four columns "image   r   g   sem"

### Integral
- Run the “integrate_fit.py” on ‘delG.dat’ to do the path integral.

This script performs **numerical integration of free-energy gradients** (⟨∂G/∂ξ⟩) to obtain the free-energy profile \( G(ξ) \).  
It reads in processed data, such as `delG.dat`, fits the force data, integrates it, and produces both **numerical results** and **plots**.

- **Input parsing**: Reads "image   r(reaction coordinate)   g(mean force)   sem(error)" from data file.
- **Flexible fitting options**:
  - **Polynomial fit** (user-defined degree).
  - **Cubic spline fit** (smooth interpolation).
  - **Raw integration** (direct trapezoid rule, no fitting).
- **Integration methods**:
  - `quad` (adaptive quadrature from SciPy).
  - `trapezoid` (trapezoidal rule).
- **r vs g plot**:
  - Plots mean force('r' vs.'g') with SEM error bars.

- **r vs Free-energy profile**:
  - Integrates 'g' to yield \( G(ξ) \).
  - Automatically shifts the profile so the minimum energy is set to **zero reference**.
  - Annotates the maximum barrier height on the plot.
Uses a custom ACS-style plotting function (`acs_plot_style.py`) for journal-ready graphics.
- **Usage** python integrate_poly.py <data_file>

