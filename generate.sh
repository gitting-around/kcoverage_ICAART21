#!/bin/bash
if [ "$#" -lt 3 ]; then
    echo "Usage: ./generate.sh noag notg_interval kinterval"
    exit 1
fi

cnt_k=2

while [ $cnt_k -le $3 ]
do
    cnt_tg=1
    while [ $cnt_tg -le $2 ]
    do
        #./generate_launch_files no_agents no_targets rw_method wu_method coverage sim_duration frequency tg_update tgreq tgresp tgbehav
        # tgreq --> 0 - normal broadcast to all, 1 - kclosest, 2 - kfurthest, 3 - krandom
        # tgresp --> 0 - willingness, 1 - newestNearest, 2 - available, 3 - graph, 4 - received call
        # tgbehav --> 0 - normal interactions, 1 - random &follow (in this case previous toggles are irrelevant)
        #usual willingness stuff
        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 0 0 0 0
        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 1 0 0 0

        #random &follow
        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 0 0 0 1
        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 1 0 0 1

        #bc to all
        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 0 0 1 0
        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 1 0 1 0

        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 0 0 2 0
        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 1 0 2 0

        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 0 0 3 0
        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 1 0 3 0

        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 0 0 4 0
        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 1 0 4 0

        #krandom
        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 0 3 1 0
        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 1 3 1 0

        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 0 3 2 0
        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 1 3 2 0

        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 0 3 3 0
        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 1 3 3 0

        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 0 3 4 0
        ./generate_launch_files.py $1 $cnt_tg RW_Pignatta WU_Pignatta $cnt_k 300 0 1 3 4 0

         cnt_tg=$((cnt_tg + 3))
    done

    #./generate_launch_files.py $1 100 RW_Pignatta WU_Pignatta $cnt_k 300 0 0
    #./generate_launch_files.py $1 100 RW_Pignatta WU_Pignatta $cnt_k 300 0 1
    #./generate_launch_files.py $1 200 RW_Pignatta WU_Pignatta $cnt_k 300 0 0
    #./generate_launch_files.py $1 200 RW_Pignatta WU_Pignatta $cnt_k 300 0 1

    ((cnt_k++)) 
done

