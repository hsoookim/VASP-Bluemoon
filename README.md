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

