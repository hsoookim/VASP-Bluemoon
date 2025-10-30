# VASP-Bluemoon
Thermodynamic Integration – Blue Moon Method (VASP) 

This repository contains scripts and input examples for performing thermodynamic integration (TI) with the Blue Moon ensemble method using VASP. 
The workflow targets to run contrained AIMD to obtain free-energy profiles G(ξ) along a reaction coordinate ξ.  
  
Relevant VASPwiki documentations
- Bluemoon ensemble : https://vasp.at/wiki/Blue_moon_ensemble
- LBLUEOUT = .TRUE. : https://vasp.at/wiki/Blue_moon_ensemble_calculations

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
- Documentation: https://vasp.at/wiki/ICONST  
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
### 1. Extract Mean Forces (`G_dat.sh`)
This shell script processes VASP `report_*` files in each constraint window and outputs averaged free-energy gradients.

**What it does**
- Skips an initial equilibration period (user-defined).
- Concatenates all `report_*` files into `rep.$i.1` per window.
- Reads the constrained coordinate (`x1`) from `report_1`.
- Computes the mean force ⟨∂G/∂ξ⟩:
  - Averages column 5 (scaled force term).
  - Normalizes by column 3 (`|z|^(-1/2)`).
- Calculates the **standard error of the mean (SEM)**.
- Saves results to `delG.dat` with four columns
  - `image`: window index/label  
  - `r`: reaction coordinate (Å, rad, etc.)  
  - `delG`: mean force ⟨∂G/∂ξ⟩ (eV/Å)  
  - `sem`: standard error of the mean (eV/Å)  

### 2. Integrate Free-Energy Profile (`integrate_poly.py`)

This Python script performs **numerical integration of mean force data** (⟨∂G/∂ξ⟩) to construct the free-energy profile \( G(ξ) \).  
It reads processed data (e.g., `delG.dat`), applies fitting methods, integrates the force, and produces both **numerical output** and **plots**.

**Features**
- **Flexible fitting**:
  - Polynomial fit (degree chosen interactively).
  - Cubic spline fit (smooth interpolation).
  - Raw integration (direct trapezoid rule without fitting).
- **Integration methods**:
  - `quad` (adaptive quadrature via SciPy).
  - `trapezoid` (trapezoidal rule).
- **Plotting**:
  - **r vs. delG**: mean force with SEM error bars and fitted curve.
  - **r vs. G(ξ)**: integrated free-energy profile.
    - Profile is shifted so that the minimum is at **0 eV**.
    - Maximum barrier height is automatically annotated.
- **Style**: uses `acs_plot_style.py` for publication-quality (ACS-style) plots.

#### Usage
```bash
python integrate_poly.py delG.dat
```
The script will interactively prompt for:
Invert x-axis (yes/no)  
Fit type (poly, spline, or raw)  
Polynomial degree (if poly)  
Integration method (quad or trapezoid)  
Dense sampling option (yes/no)  

