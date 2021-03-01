#!/bin/bash
timestamp=$(date '+%d-%m_%H-%M');
echo $timestamp
mkdir raw_logs_pignatta_$timestamp
#rosparam set /use_sim_time True
##STATIC#################################
counter=1
notg=1
while [ $counter -le $3 ]
do
    echo "static_${notg}_$2_case$1_000" >> keeping_track_pignatta.txt
    t=$(date '+%d-%m_%H-%M');
    echo "$t" >> keeping_track_pignatta.txt
    mkdir -p 10_${notg}_300_$2_static/10_${notg}_300_$2_static_000/case_$1
    roslaunch gitagent_2 agent_10_${notg}_RW_Pignatta_WU_Pignatta_$2_300_0_0_000.launch seedval:=$1
    mv output_* 10_${notg}_300_$2_static/10_${notg}_300_$2_static_000/case_$1/
    mv gitlogger_* 10_${notg}_300_$2_static/10_${notg}_300_$2_static_000/case_$1/
    cp ~/.ros/log/latest -LR raw_logs_pignatta_$timestamp/log_static_${notg}_$2_case$1_000


    #echo "static_${notg}_$2_case$1_001" >> keeping_track_pignatta.txt
    #t=$(date '+%d-%m_%H-%M');
    #echo "$t" >> keeping_track_pignatta.txt
    #mkdir -p 10_${notg}_300_$2_static/10_${notg}_300_$2_static_001/case_$1
    #roslaunch gitagent_2 agent_10_${notg}_RW_Pignatta_WU_Pignatta_$2_300_0_0_001.launch seedval:=$1
    #mv output_* 10_${notg}_300_$2_static/10_${notg}_300_$2_static_001/case_$1/
    #mv gitlogger_* 10_${notg}_300_$2_static/10_${notg}_300_$2_static_001/case_$1/
    #cp ~/.ros/log/latest -LR raw_logs_pignatta_$timestamp/log_static_${notg}_$2_case$1_001


    #Loop over resp models for bc to all
    nor=1
    while [ $nor -le 4 ]
    do
        echo "static_${notg}_$2_case$1_0${nor}0" >> keeping_track_pignatta.txt
        t=$(date '+%d-%m_%H-%M');
        echo "$t" >> keeping_track_pignatta.txt
	mkdir -p 10_${notg}_300_$2_static/10_${notg}_300_$2_static_0${nor}0/case_$1
	roslaunch gitagent_2 agent_10_${notg}_RW_Pignatta_WU_Pignatta_$2_300_0_0_0${nor}0.launch seedval:=$1
	mv output_* 10_${notg}_300_$2_static/10_${notg}_300_$2_static_0${nor}0/case_$1/
	mv gitlogger_* 10_${notg}_300_$2_static/10_${notg}_300_$2_static_0${nor}0/case_$1/
        cp ~/.ros/log/latest -LR raw_logs_pignatta_$timestamp/log_static_${notg}_$2_case$1_0${nor}0
	((nor++))
        if [ $nor -eq 3 ]
        then
            ((nor++))
        fi
    done

    #Loop over resp models for bc to krandom
    nor=1
    while [ $nor -le 4 ]
    do
        echo "static_${notg}_$2_case$1_3${nor}0" >> keeping_track_pignatta.txt
        t=$(date '+%d-%m_%H-%M');
        echo "$t" >> keeping_track_pignatta.txt
	mkdir -p 10_${notg}_300_$2_static/10_${notg}_300_$2_static_3${nor}0/case_$1
	roslaunch gitagent_2 agent_10_${notg}_RW_Pignatta_WU_Pignatta_$2_300_0_0_3${nor}0.launch seedval:=$1
	mv output_* 10_${notg}_300_$2_static/10_${notg}_300_$2_static_3${nor}0/case_$1/
	mv gitlogger_* 10_${notg}_300_$2_static/10_${notg}_300_$2_static_3${nor}0/case_$1/
        cp ~/.ros/log/latest -LR raw_logs_pignatta_$timestamp/log_static_${notg}_$2_case$1_3${nor}0
	((nor++))
        if [ $nor -eq 3 ]
        then
            ((nor++))
        fi
    done

    notg=$((notg + 3))
    ((counter++))
done
#########################################
##DYNAMIC################################
counter=1
notg=1
while [ $counter -le $3 ]
do
    echo "dynamic_${notg}_$2_case$1_000" >> keeping_track_pignatta.txt
    t=$(date '+%d-%m_%H-%M');
    echo "$t" >> keeping_track_pignatta.txt
    mkdir -p 10_${notg}_300_$2_dynamic/10_${notg}_300_$2_dynamic_000/case_$1
    roslaunch gitagent_2 agent_10_${notg}_RW_Pignatta_WU_Pignatta_$2_300_0_1_000.launch seedval:=$1
    mv output_* 10_${notg}_300_$2_dynamic/10_${notg}_300_$2_dynamic_000/case_$1/
    mv gitlogger_* 10_${notg}_300_$2_dynamic/10_${notg}_300_$2_dynamic_000/case_$1/
    cp ~/.ros/log/latest -LR raw_logs_pignatta_$timestamp/log_dynamic_${notg}_$2_case$1_000

    #echo "dynamic_${notg}_$2_case$1_001" >> keeping_track_pignatta.txt
    #t=$(date '+%d-%m_%H-%M');
    #echo "$t" >> keeping_track_pignatta.txt
    #mkdir -p 10_${notg}_300_$2_dynamic/10_${notg}_300_$2_dynamic_001/case_$1
    #roslaunch gitagent_2 agent_10_${notg}_RW_Pignatta_WU_Pignatta_$2_300_0_1_001.launch seedval:=$1
    #mv output_* 10_${notg}_300_$2_dynamic/10_${notg}_300_$2_dynamic_001/case_$1/
    #mv gitlogger_* 10_${notg}_300_$2_dynamic/10_${notg}_300_$2_dynamic_001/case_$1/
    #cp ~/.ros/log/latest -LR raw_logs_pignatta_$timestamp/log_dynamic_${notg}_$2_case$1_001

    #Loop over resp models for bc to all
    nor=1
    while [ $nor -le 4 ]
    do
        echo "dynamic_${notg}_$2_case$1_0${nor}0" >> keeping_track_pignatta.txt
        t=$(date '+%d-%m_%H-%M');
        echo "$t" >> keeping_track_pignatta.txt
	mkdir -p 10_${notg}_300_$2_dynamic/10_${notg}_300_$2_dynamic_0${nor}0/case_$1
	roslaunch gitagent_2 agent_10_${notg}_RW_Pignatta_WU_Pignatta_$2_300_0_1_0${nor}0.launch seedval:=$1
	mv output_* 10_${notg}_300_$2_dynamic/10_${notg}_300_$2_dynamic_0${nor}0/case_$1/
	mv gitlogger_* 10_${notg}_300_$2_dynamic/10_${notg}_300_$2_dynamic_0${nor}0/case_$1/
        cp ~/.ros/log/latest -LR raw_logs_pignatta_$timestamp/log_dynamic_${notg}_$2_case$1_0${nor}0
        ((nor++))
        if [ $nor -eq 3 ]
        then
            ((nor++))
        fi
    done

    #Loop over resp models for bc to krandom
    nor=1
    while [ $nor -le 4 ]
    do
        echo "dynamic_${notg}_$2_case$1_3${nor}0" >> keeping_track_pignatta.txt
        t=$(date '+%d-%m_%H-%M');
        echo "$t" >> keeping_track_pignatta.txt
	mkdir -p 10_${notg}_300_$2_dynamic/10_${notg}_300_$2_dynamic_3${nor}0/case_$1
	roslaunch gitagent_2 agent_10_${notg}_RW_Pignatta_WU_Pignatta_$2_300_0_1_3${nor}0.launch seedval:=$1
	mv output_* 10_${notg}_300_$2_dynamic/10_${notg}_300_$2_dynamic_3${nor}0/case_$1/
	mv gitlogger_* 10_${notg}_300_$2_dynamic/10_${notg}_300_$2_dynamic_3${nor}0/case_$1/
        cp ~/.ros/log/latest -LR raw_logs_pignatta_$timestamp/log_dynamic_${notg}_$2_case$1_3${nor}0
        ((nor++))
        if [ $nor -eq 3 ]
        then
            ((nor++))
        fi
    done

    notg=$((notg + 3))
    ((counter++))
done
