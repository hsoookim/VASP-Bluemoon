import os
import shutil
import numpy as np
import copy
'''
Usage summary:
1. Inputs (interactive prompts):
- Initial POSCAR filename ex) POSCAR_00.vasp
- Final POSCAR filename ex) POSCAR_09.vasp
- atom index ex) O35, H1, H2
- number of intermediate images
2. Linearly interpolates user-specified atoms over a given number of intermediate images
3. Writes each interpolated POSCAR into numbered folders staring 00, 01, ..., final 

Important assumptions and notes:
- Interpolation is performed in fractional coordinates; coordinates >1 are wrapped by subtracting 1.
- The script chooses the “base” atoms (non-interpolated atoms) from initial structure to the midpoint intermediate images, and later images from the final structure.

Example run:
python Linear_interpolation.py
(when prompted) initial.vasp
final.vasp
O35,H21,H22
9
This produces 11 directories (00..10) with POSCAR files for a 9-image interpolation between initial and final
'''

def read_POSCAR(file_path):
    with open(file_path, 'r') as f:
        poscar_data = f.readlines()
    
    # Extract lattice vectors, elements, number of atoms
    lattice_vectors = [list(map(float, line.split())) for line in poscar_data[2:5]]
    elements = poscar_data[5].split()
    num_atoms = list(map(int, poscar_data[6].split()))

    # Element list
    element_list = []
    for spec, count in zip(elements, num_atoms):
        for i in range(1, count + 1):
            element_list.append(f"{spec}{i}")   

    # Check if Selective Dynamics is used
    selective_dynamics = False
    if poscar_data[7][0] in ['S', 's']:
        selective_dynamics = True
        start_index = 9
    else:
        start_index = 8
    
    # Extract atomic positions
    atomic_positions = []
    for line in poscar_data[start_index:]:
        atomic_positions.append(line.split()[:6])
    
    return lattice_vectors, elements, num_atoms, selective_dynamics, atomic_positions, element_list

def write_POSCAR(file_path, original_lines, selective_dynamics, atomic_positions):
    with open(file_path, 'w') as f:
        for line in original_lines[:7]:
            f.write(line)
        if selective_dynamics:
            f.write("Selective dynamics\n")
        f.write("Direct\n")
        for position in atomic_positions:
            f.write(" ".join(position) + '\n')

def linear_interpolation(atomic_positions_i, atomic_positions_f, atom_indices, t, base="initial"):
    # Pick the base structure (entire structure copied first)
    inter_positions = copy.deepcopy(atomic_positions_i if base == "initial" else atomic_positions_f)
    
    for atom_index in atom_indices:
        for i in range(3):
            inter_positions[atom_index][i] = str(float(atomic_positions_i[atom_index][i]) + (t * (float(atomic_positions_f[atom_index][i]) - float(atomic_positions_i[atom_index][i]))))

            if float(inter_positions[atom_index][i]) >= 1.0:
                inter_positions[atom_index][i] = str(float(inter_positions[atom_index][i]) - 1.0)
    
    return inter_positions

#initial_filename = "contcar_a_85.vasp"
#final_filename = "contcar_a_50.vasp"
#input_species_list = ['O35', 'H21', 'H22']
#num_images = 9

initial_filename = input("Enter the initial POSCAR filename: ")
final_filename = input("Enter the final POSCAR filename: ")
input_species_list = input("Enter the input species list (ex> O35,H21,H22): ").split(',')
num_images = int(input("Enter the number of intermidiate images: "))

# Remove leading/trailing whitespace from species
input_species_list = [species.strip() for species in input_species_list]

with open(os.path.join(initial_filename), 'r') as f:
    original_lines = f.readlines()
            
lattice_vectors_i, elements_i, num_atoms_i, selective_dynamics_i, atomic_positions_i, element_list_i = read_POSCAR(initial_filename)
lattice_vectors_f, elements_f, num_atoms_f, selective_dynamics_f, atomic_positions_f, element_list_f = read_POSCAR(final_filename)

t_values = np.linspace(0, 1, num_images+2)[1:-1]
midpoint = len(t_values) // 2 
atom_indices = [element_list_i.index(species) for species in input_species_list]

for i, t in enumerate(t_values, start=1):

    base = "initial" if i <= midpoint else "final"
    inter_positions = linear_interpolation(atomic_positions_i, atomic_positions_f, atom_indices, t, base=base)
    
    output_directory = f"{i:02d}"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    output_file_path = os.path.join(output_directory, f"POSCAR")
    write_POSCAR(output_file_path, original_lines, selective_dynamics_i, inter_positions)
    
# Create directory and copy initial POSCAR
initial_dir = "00"
if not os.path.exists(initial_dir):
    os.makedirs(initial_dir)
shutil.copy(initial_filename, os.path.join(initial_dir, "POSCAR"))

# Create directory for the final POSCAR
final_dir = f"{num_images+1:02d}"
if not os.path.exists(final_dir):
    os.makedirs(final_dir)
shutil.copy(final_filename, os.path.join(final_dir, "POSCAR"))
