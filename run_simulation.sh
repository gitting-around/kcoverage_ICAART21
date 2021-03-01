#!/bin/bash
if [ "$#" -lt 3 ]; then
    echo "Usage: ./run_simulation.sh no_repetitions value_of_k_interval no_configurations"
    exit 1
fi

k=3
while [ $k -le $2 ]
do
    counter=1
    notg=1
    while [ $counter -le $3 ]
    do
        mkdir 10_${notg}_300_${k}_static
        mkdir 10_${notg}_300_${k}_dynamic
        ((counter++))  
        notg=$((notg + 3))
    done
    k=$((k + 2))
done

k=3
while [ $k -le $2 ]
do
    counter=1
    while [ $counter -le $1 ]
    do    
        ./run_simulation_short.sh $counter $k $3
        
        ((counter++))
    done
    k=$((k + 2))
done
finish=$(date '+%d-%m_%H');
echo "Simulation complete at ${finish}" >> keeping_track_pignatta.txt
