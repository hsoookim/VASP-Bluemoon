# VASP-Bluemoon
Thermodynamic Integration – Blue Moon Method (VASP)
This repository contains scripts and input examples for performing thermodynamic integration (TI) with the Blue Moon ensemble method using VASP. 
The workflow targets to run contrained AIMD to obtain free-energy profiles G(ξ) along a reaction coordinate ξ.

## What this repo provides: 
- **INCAR templates** for constrained AIMD.
- **Linear interpolation** of reaction-coordinate (“images” along ξ).
- **Parsers** for mean forces (⟨∂G/∂ξ⟩) from REPORTs per image.
- **Integration utilities** to compute G(ξ) profile optionally fitting.

- 
