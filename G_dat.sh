#!/usr/bin/bash

### Key Variables
# `equil`: number of steps to discard as equilibration (default: 4000).  
# `rep.$i.1`: concatenated file of all `report_*` entries in window `$i`.  
# `x1`: constrained coordinate value from ICONST.  
# `g1`: averaged free-energy gradient for window `$i`.  


equil=4000 # equilibration steps to skip
mkdir -p Forces-all # Folder to store raw data for block averaging


for i in 00 01 02 03 04 05 06 07 08 09 10

do
  # 1. Accumulate all report files for this directory
  rm -f rep.$i.1
  grep -h b_m $i/report_* >> rep.$i.1

  # 2. Get the coordinate (x1)
  x1=$(grep cc $i/report_1 | head -3 | tail -1 | awk '{print $3}')

  # 3. Extract the production time-series (excluding equilibration)
  nlines=$(wc -l < rep.$i.1)
  prod=$((nlines - equil))

  if [ $prod -gt 0 ]; then
    # We save only the 5th column (the force/gradient term)
    # We divide by |z|^-1/2 (column 3)
    zet=$(tail -n $prod rep.$i.1 | awk 'BEGIN {a=0.} {a+=$3} END {print a/NR}')
    
    # Export the production forces to a file for Python
    tail -n $prod rep.$i.1 | awk -v zet="$zet" '{print $5/zet}' > Forces-all/forces_$i.dat
    
    # Save a metadata file for the main script to read
    echo "$i $x1 forces_$i.dat" >> Forces-all/metadata.dat
    echo "Saved production data for dir $i ($prod frames)"
  else
    echo "Not enough lines in $i"
  fi
done
