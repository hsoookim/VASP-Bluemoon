 #!/bin/bash

# ensure that this sequence of MD runs is reproducible
rseed="RANDOM_SEED =         311137787                0                0"
echo $rseed >> INCAR_AIMD

# Loop through each directory
for dir in 00 01 02 03 04 05 06 07 08 09 10; do
    # Check if the directory exists
    if [ -d "$dir" ]; then
        #echo "Processing directory $dir"
        
        # Copy files to the directory
        cp INCAR_AIMD "$dir/INCAR"
        cp KPOINTS "$dir/KPOINTS"
        cp POTCAR "$dir/POTCAR"
        cp ICONST "$dir/ICONST"
        cp AIMD.sbatch "$dir/AIMD.sbatch"
        
        cd "$dir" || exit # Change to the directory
        cp POSCAR.vasp POSCAR
        sbatch AIMD.sbatch # Submit the job
        
        cd .. # Change back to the parent directory

    else
        echo "Directory $dir does not exist"
    fi
done

