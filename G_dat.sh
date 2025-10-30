#!/usr/bin/bash

equil=4000 # front part

for i in 00 01 02 03 04 05 06 07 08 09 10 

do
  # Remove any existing rep.* files
  rm -f rep.$i.1

  #grep b_m $i/report_* | awk '{$1=""; print $0}' >> rep.$i.1  # .1 accumulates all report_* files
  grep -h b_m $i/report_* >> rep.$i.1  # .1 accumulates all report_* files
      # .1 does not mean anything. all cumulated report_* files
      # b_m> lambda    |z|^(-1/2)    GkT    |z|^(-1/2)*(lambda+GkT)

  # Collect coordinate and energy data from rep.*.1
    x1=$(grep cc $i/report_1 | head -3 | tail -1 | awk '{print $3}') # get coordinate(constrained in ICONST)

    nlines=$(wc -l < rep.$i.1)
    prod=$((nlines - equil)) # Exclude first $equil amount of time of total simulation 
    echo "Production lines after equilibration: $prod"

    if [ $prod -gt 0 ]; then
      zet=$(tail -n $prod rep.$i.1 | awk 'BEGIN {a=0.} {a+=$3} END {print a/NR}')
      g1=$(tail -n $prod rep.$i.1 | awk -v zet="$zet" 'BEGIN {a=0.} {a+=$5} END {print a/NR/zet}')

      # Calculate the standard deviation for the fifth column (g1)
      std_dev=$(tail -n $prod rep.$i.1 | awk -v g1="$g1" -v zet="$zet" 'BEGIN {sum_sq=0; n=0} {sum_sq+=($5/(zet)-g1)^2; n+=1} END {print sqrt(sum_sq/(n-1))}')

      # Calculate the standard error of the mean (SEM)
      sem=$(echo "$std_dev $prod" | awk '{print $1/sqrt($2)}')

      echo "dir: $i, x1: $x1, g1: $g1, SEM: $sem"
      echo "$i $x1 $g1 $sem" >> delG.dat
    else
      echo "Not enough production lines for rep.$i.1 in $report_file"
    fi
    
done
