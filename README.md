System PREREQUISITES:

Ubuntu 16.04

ROS kinetic

--Could work with other versions of ubuntu and ROS, but is not tested.

-----------------------
RUNNING THE SIMULATIONS
-----------------------

In order to run the simulations:

ubuntu-terminal$ cd ~/catkin_ws

ubuntu-terminal$ ./run_simulation.sh no_repetitions value_of_k_interval no_configurations

where no_repetitions: how many runs with different seeds do we want for one configuration

value_of_k_interval: the script will start with k=3, both for the static and dynamic case, will increment by 2, until k=value_of_k_interval

no_configurations: nr of scenarios with different number of targets. E.g., if equal to 7, the simulations will start with 1 target, for all the methods (willingness, etc.). The number of targets will increment with 3. The simulation stops after the final configuration with the max nr of targets has finished.

-------------------
GETTING THE RESULTS
-------------------

Assume the folders with the raw data are located in folder ubuntu/catkin_ws/test/

ubuntu-terminal$ cd ..

Make sure the files run_results.sh, run_simulation_results.sh and handle_results.py are in the current location after "cd .."

ubuntu-terminal$ ./run_simulation_results.sh no_repetitions valueof_k no_configurations current_dir scriptname

where no_repetitions: how many runs with different seeds do we want for one configuration

valueof_k: if I want the results for k=3, this is set to 3

no_configurations: nr of scenarios with different number of targets.

current_dir that holds the raw data: test/

scriptname: handle_results.py

This script generates csv files for all configurations. Check in handle_results.py and change the paths there to where you want the files to be generated.

Once this is done, make sure you have the csv file and the get_boxplot.py in the same folder, or simply call the script from where it is located as:

ubuntu-terminal$ python3 ./get_boxplot.py coverage distinct_scenarios repetitions what2run (0 all, 1 static, 2 dynamic) amIequal(0,1)

coverage: valueof_k

distinct_scenarios: no_configurations

repetitions: no_repetitions

what2run: 0 for all static and dynamic

amIequal: 0 if we're looking for k>=coverage

Boxplots will be generated as well as the standard deviations for each case.

---------------------------
For ICAART2020 runs: use commit:	5a10e5a	fixed readme	2019‑12‑09

