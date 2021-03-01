#!/bin/bash
if [ "$#" -lt 4 ]; then
    echo "Usage: ./run_results.sh no_repetitions valueof_k no_configurations current_dir"
    exit 1
fi
echo "The script will run for preset combinations of request and response models"
##STATIC#################################
counter=1
notg=1
while [ $counter -le $3 ]
do
    cd 10_${notg}_300_$2_static/10_${notg}_300_$2_static_000/case_$1
    pwd
    ../../../../handle_results.py 10 $notg 300 $2 1 000
    cd ../../..
    pwd

    cd 10_${notg}_300_$2_static/10_${notg}_300_$2_static_001/case_$1
    pwd
    ../../../../handle_results.py 10 $notg 300 $2 1 001
    cd ../../..
    nor=1
    while [ $nor -le 4 ]
        do
            cd 10_${notg}_300_$2_static/10_${notg}_300_$2_static_0${nor}0/case_$1
            ../../../../handle_results.py 10 $notg 300 $2 1 0${nor}0
            cd ../../..

            ((nor++))
    done

    #Loop over resp models for bc to krandom
    nor=1
    while [ $nor -le 4 ]
        do
            cd 10_${notg}_300_$2_static/10_${notg}_300_$2_static_3${nor}0/case_$1
            ../../../../handle_results.py 10 $notg 300 $2 1 3${nor}0
            cd ../../..

            ((nor++))
    done

    notg=$((notg + 3))
    ((counter++))
done

##DYNAMIC################################
counter=1
notg=1
while [ $counter -le $3 ]
do
    cd 10_${notg}_300_$2_dynamic/10_${notg}_300_$2_dynamic_000/case_$1
    ../../../../handle_results.py 10 $notg 300 $2 0 000
    cd ../../..

    cd 10_${notg}_300_$2_dynamic/10_${notg}_300_$2_dynamic_001/case_$1
    ../../../../handle_results.py 10 $notg 300 $2 0 001
    cd ../../..

    nor=1
    while [ $nor -le 4 ]
        do
            cd 10_${notg}_300_$2_dynamic/10_${notg}_300_$2_dynamic_0${nor}0/case_$1
            ../../../../handle_results.py 10 $notg 300 $2 0 0${nor}0
            cd ../../..

            ((nor++))
    done

    #Loop over resp models for bc to krandom
    nor=1
    while [ $nor -le 4 ]
        do
            cd 10_${notg}_300_$2_dynamic/10_${notg}_300_$2_dynamic_3${nor}0/case_$1
            ../../../../handle_results.py 10 $notg 300 $2 0 3${nor}0
            cd ../../..

            ((nor++))
    done

    notg=$((notg + 3))
    ((counter++))
done
