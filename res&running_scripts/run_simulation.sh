#!/bin/bash
if [ "$#" -lt 4 ]; then
    echo "Usage: ./run_simulation.sh no_repetitions valueof_k no_configurations current_dir"
    exit 1
fi

echo $4
cd $4
pwd
times=$1
echo $times

counter=1
while [ $counter -le $1 ]
do
    ../run_results.sh $counter $2 $3 $4
    ((counter++))
done
