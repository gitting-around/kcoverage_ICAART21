#!/usr/bin/env python
import numpy as np
import sys
import pdb
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import matplotlib.cm as cm
import csv
import os

def plot(no_agents, no_targets, sim_duration, coverage, tg_update):

    data = np.zeros((no_targets, sim_duration-1))
    #print data
    if tg_update == 0:
        staticdynamic = "dynamic"
    else:
        staticdynamic = "static"
    case = "_" + str(no_agents) + "_" + str(no_targets) + "_" + str(sim_duration) + "_" + str(coverage) + "_" + staticdynamic

    for x in range(no_agents):
        with open("output_" + str(x+1), "r") as f:
            lines = f.readlines()
            i = 0
            for line in lines:
                item = map(int, line.split())
                if item:
                    for it in item:
                        data[it-1][i] += 1
                        #print data[it-1][i]
                i += 1
    
    print data

    fig, ax = plt.subplots(nrows=no_targets, sharex=True)

    xaxis = np.array(range(data.shape[1]))
    for j in range(data.shape[0]):
        yaxis = data[j,:]
        #yaxis = data[j,:] + j*no_agents
        if no_targets > 1:
            ax[j].step(xaxis, yaxis)
            ax[j].plot(xaxis, np.array([coverage for i in range(len(xaxis))]), 'g--')
            ax[j].set_ylabel("no agents")
        else:
            ax.step(xaxis, yaxis)
            ax.plot(xaxis, np.array([coverage for i in range(len(xaxis))]), 'g--')
            ax.set_ylabel("no agents")

    #plt.yticks(ytick)
    plt.xlabel("t")
    
    plt.grid(True, which="both", ls="-")
    plt.savefig("coverage.png")
    #plt.show()

def plot_w(no_agents, no_targets, sim_duration, coverage, tg_update):
    #colors = cm.rainbow(np.linspace(0, 1, no_agents))
    colors = cm.get_cmap('rainbow', no_agents)
    fig, ax = plt.subplots()
    for x in range(no_agents):
        with open("output_w_"+str(x+1), "r") as f:
            lines = f.readlines()
            for line in lines:
                item = map(float, line.split())
                plt.plot(item[1], item[0] + no_agents*x, '-x', color=colors(x))

    plt.xlabel("t")
    plt.ylabel("willingness")
    plt.grid(True, which="both", ls="-")
    plt.savefig("willingness.png")
    #plt.show()

def static_cov(no_agents, no_targets, sim_duration, coverage, tg_update):
    ################################### ACTIVE COVERAGE ##########################################
    data = np.zeros((no_targets, sim_duration-1))
    data_k = np.zeros((no_targets, sim_duration-1))
    #print data
    #for x in range(no_agents):
    for x in range(no_agents):
        with open("output_"+str(x+1), "r") as f:
            lines = f.readlines()
            #get first 299 lines, 0-298
            lines = lines[:sim_duration-1]
            i = 0
            for line in lines:
                item = map(int, line.split())
                if item:
                    for it in item:
                        data[it-1][i] += 1
                        data_k[it-1][i] += 1
                i += 1

    #print data
    #print data_k
    ##1-COVERAGE######################################
    #print data
    #Compute avg(tt1c_vector) - Average time to get 1 agent covering a target
    ave_time, min_time_all_cov = computeMetrics(data=data, coverage=1)

    print "1-Coverage ave time:\t\t%g" % ave_time
    print "1-Coverage min to cover all:\t%g" % min_time_all_cov

    ##K-COVERAGE######################################
    ave_time_k, min_time_all_cov_k = computeMetrics(data=data_k, coverage=coverage)

    print "k-Coverage ave time:\t\t%g" % ave_time_k
    print "k-Coverage min to cover all:\t%g" % min_time_all_cov_k

    #WRITE TO csv
    if tg_update == 0:
        staticdynamic = "dynamic"
    else:
        staticdynamic = "static"
    case = str(no_agents) + "_" + str(no_targets) + "_" + str(sim_duration) + "_" + str(coverage) + "_" + staticdynamic
    fname = "/home/mfi01/catkin_ws/" + "_" + case + ".csv"

    with open(fname, 'a') as f:
        #case = "Case no_ag: %d, no_tg: %d, sim_duration: %d, coverage: %d" % (no_agents, no_targets, sim_duration, coverage)
        #f.write(case + "\n")
        row = [str(ave_time), str(min_time_all_cov), str(ave_time_k), str(min_time_all_cov_k)]
        writer = csv.writer(f)
        writer.writerow(row)
        #f.write(str(ave_time) + " ")
        #f.write(str(min_time_all_cov) + " ")

    ################################### PASIVE COVERAGE ##########################################
    data = np.zeros((no_targets, sim_duration-1))
    data_k = np.zeros((no_targets, sim_duration-1))
    #print data
    #for x in range(no_agents):
    for x in range(no_agents):
        with open("output_"+str(x+1), "r") as f:
            lines = f.readlines()
            lines = lines[sim_duration:]
            i = 0
            for line in lines:
                item = map(int, line.split())
                if item:
                    for it in item:
                        data[it-1][i] += 1
                        data_k[it-1][i] += 1
                i += 1

    #print data
    #print data_k
    ##1-COVERAGE######################################
    #print data
    #Compute avg(tt1c_vector) - Average time to get 1 agent covering a target
    ave_time, min_time_all_cov = computeMetrics(data=data, coverage=1)

    print "1-Coverage ave time:\t\t%g" % ave_time
    print "1-Coverage min to cover all:\t%g" % min_time_all_cov

    ##K-COVERAGE######################################
    ave_time_k, min_time_all_cov_k = computeMetrics(data=data_k, coverage=coverage)

    print "k-Coverage ave time:\t\t%g" % ave_time_k
    print "k-Coverage min to cover all:\t%g" % min_time_all_cov_k

    #WRITE TO csv
    if tg_update == 0:
        staticdynamic = "passive_dynamic"
    else:
        staticdynamic = "passive_static"
    case = str(no_agents) + "_" + str(no_targets) + "_" + str(sim_duration) + "_" + str(coverage) + "_" + staticdynamic
    fname = "/home/mfi01/catkin_ws/" + "_" + case + ".csv"

    with open(fname, 'a') as f:
        #case = "Case no_ag: %d, no_tg: %d, sim_duration: %d, coverage: %d" % (no_agents, no_targets, sim_duration, coverage)
        #f.write(case + "\n")
        row = [str(ave_time), str(min_time_all_cov), str(ave_time_k), str(min_time_all_cov_k)]
        writer = csv.writer(f)
        writer.writerow(row)
        #f.write(str(ave_time) + " ")
        #f.write(str(min_time_all_cov) + " ")

def computeMetrics(data,coverage):
    #if 0 in all timesteps, place one at the end of row - something VERY UGLY will follow
    allzeros = np.all(data>=coverage, axis=1)
    i = 0
    for x in allzeros:
        if not x:
            data[i][-1] = coverage
        i += 1

    print data
    # Indentify for every target the number minimum time to be reached
    idx = [np.nonzero(data[i]>=coverage)[0][0] for i in range(0,len(data))]

    print idx
    t   = 1 + np.array(idx)

    # Compute metrics
    avg_time = np.average(t)
    min_time_all_cov = np.amax(t)

    return avg_time, min_time_all_cov
            
def static_k_cov(no_agents, no_targets, sim_duration, coverage, tg_update):
    data = np.zeros((no_targets, sim_duration-1))
    #print data
    for x in range(no_agents):
        with open("output_"+str(x+1), "r") as f:
            lines = f.readlines()
            i = 0
            for line in lines:
                item = map(int, line.split())
                if item:
                    for it in item:
                        data[it-1][i] += 1
                i += 1

    allzeros = np.all(data>=coverage, axis=1)
    print allzeros
    i = 0
    for x in allzeros:
        if not x:
            data[i][-1] = coverage
        i += 1
    print data

    t = 1 + np.argmax(data>=coverage, axis=1)
    #Compute avg(tt1c_vector) - Average time to get k agent covering a target
    ave_time = np.average(t)
    #Compute max(tt1c_vector) - Minimum time to get all the targets covered with k agent
    min_time_all_cov = np.amax(t)
    print "ave time: %f" % ave_time
    print "min to cover all: %f" % min_time_all_cov

    if tg_update == 0:
        staticdynamic = "dynamic"
    else:
        staticdynamic = "static"
    case = str(no_agents) + "_" + str(no_targets) + "_" + str(sim_duration) + "_" + str(coverage) + "_" + staticdynamic
    fname = "/home/mfi01/" + "_" + case  + ".csv"

    with open(fname, 'a') as f:
        f.write(str(ave_time) + " ")
        f.write(str(min_time_all_cov) + "\n")

def dynamic_k_cov(no_agents, no_targets, sim_duration, coverage, tg_update):
    ############################## Active coverage ####################################
    data = np.zeros((no_targets, sim_duration-1))
    #print data
    for x in range(no_agents):
        print os.getcwd()
        with open("output_"+str(x+1), "r") as f:
            lines = f.readlines()
            lines = lines[:sim_duration-1]
            i = 0
            for line in lines:
                item = map(int, line.split())
                if item:
                    for it in item:
                        data[it-1][i] += 1
                i += 1

    #check per row where the k coverage is achieved, at least
    print data
    achieved = data>=coverage
    print achieved
    #sum over the rows of the resultant boolean matrix.
    sumsteps = np.sum(achieved, axis=1)
    print sumsteps
    ave_time = np.average(sumsteps)
    print "ave time: %f" % ave_time
    #ave of agents covering a target
    agent_tg = np.average(data, axis=1)
    print agent_tg
    ave_agent = np.average(agent_tg)
    print "ave agents: %f" % ave_agent

    if tg_update == 0:
        staticdynamic = "dynamic"
    else:
        staticdynamic = "static"
    case = str(no_agents) + "_" + str(no_targets) + "_" + str(sim_duration) + "_" + str(coverage) + "_" + staticdynamic
    fname = "/home/mfi01/catkin_ws/" + "_" + case + ".csv"

    with open(fname, 'a') as f:
        row = [str(ave_time), str(ave_agent)]
        writer = csv.writer(f)
        writer.writerow(row)

    ############################## Pasive coverage ####################################
    data = np.zeros((no_targets, sim_duration-1))
    #print data
    for x in range(no_agents):
        with open("output_"+str(x+1), "r") as f:
            lines = f.readlines()
            lines = lines[sim_duration:]
            i = 0
            for line in lines:
                item = map(int, line.split())
                if item:
                    for it in item:
                        data[it-1][i] += 1
                i += 1

    #check per row where the k coverage is achieved, at least
    print data
    achieved = data>=coverage
    print achieved
    #sum over the rows of the resultant boolean matrix.
    sumsteps = np.sum(achieved, axis=1)
    print sumsteps
    ave_time = np.average(sumsteps)
    print "ave time: %f" % ave_time
    #ave of agents covering a target
    agent_tg = np.average(data, axis=1)
    print agent_tg
    ave_agent = np.average(agent_tg)
    print "ave agents: %f" % ave_agent

    if tg_update == 0:
        staticdynamic = "passive_dynamic"
    else:
        staticdynamic = "passive_static"
    case = str(no_agents) + "_" + str(no_targets) + "_" + str(sim_duration) + "_" + str(coverage) + "_" + staticdynamic
    fname = "/home/mfi01/catkin_ws/" + "_" + case + ".csv"

    with open(fname, 'a') as f:
        row = [str(ave_time), str(ave_agent)]
        writer = csv.writer(f)
        writer.writerow(row)

if __name__ == '__main__':
    
    if len(sys.argv) < 6:
        print "Usage: ./handle_results.py no_agents no_targets sim_duration coverage static/dynamic"
    #plot(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
    #plot_w(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
    if int(sys.argv[5]) == 1:
        print "im in static mode"
        static_cov(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
        #static_k_cov(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
    else:
        print "im in dynamic mode"
        dynamic_k_cov(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
