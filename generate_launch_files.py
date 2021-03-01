#!/usr/bin/env python
import sys

def write2file(no_agents, no_targets, rw_method, wu_method, coverage, sim_duration, frequency, tg_update, toggle_request, toggle_respond, toggle_behaviour):
    #filename = "/home/ubuntu/catkin_ws/src/gitagent_2/launch/agent_" + str(no_agents) + "_" + str(no_targets) + "_" + rw_method + "_" + wu_method + "_" + "cov" +str(coverage) + "_" + "dur"+str(sim_duration) + "_" + "freq"+str(frequency) + "_" + "tgupd"+str(tg_update)  +"_"+ "req" + str(toggle_request) + "resp" + str(toggle_respond) + "behav" + str(toggle_behaviour) +".launch"
    filename = "/home/mfi01/catkin_ws/src/gitagent_2/launch/agent_" + str(no_agents) + "_" + str(no_targets) + "_" + rw_method + "_" + wu_method + "_" + str(coverage) + "_" + str(sim_duration) + "_" + str(frequency) + "_" + str(tg_update)  +"_"+ str(toggle_request) + str(toggle_respond) + str(toggle_behaviour) +".launch"

    print filename

    with open(filename, "w") as f:
        f.write("<launch>\n")
        f.write("<param name=\"use_sim_time\" value=\"true\"/>\n")
        f.write("<arg name=\"seedval\"/>\n")
        f.write("<param name=\"seed\" value=\"$(arg seedval)\"/>\n")
        for x in range(int(no_agents)):
            f.write("<group ns=\"robot" + str(x+1) + "\">\n")
            f.write("<node pkg=\"gitagent_2\" name=\"agent\" type=\"agent.py\">\n")
            f.write("<param name=\"myID\" value=\"" + str(x+1) + "\"/>\n")
            f.write("<param name=\"random_walk_method\" value=\"" + rw_method + "\"/>\n")
            f.write("<param name=\"wu_method\" value=\"" + wu_method + "\"/>\n")
            f.write("<param name=\"kcoverage\" value=\"" + str(coverage) + "\"/>\n")
            f.write("<param name=\"sim_duration\" value=\"" + str(sim_duration) + "\"/>\n")
            f.write("<param name=\"toggle_request\" value=\"" + str(toggle_request) + "\"/>\n")
            f.write("<param name=\"toggle_respond\" value=\"" + str(toggle_respond) + "\"/>\n")
            f.write("<param name=\"toggle_behaviour\" value=\"" + str(toggle_behaviour) + "\"/>\n")
            f.write("</node>\n")
            f.write("</group>\n\n")

        f.write("<group ns=\"environment\">\n")
        f.write("<node pkg=\"gitagent_2\" name=\"environment\" type=\"env_agent.py\" output=\"screen\">\n")
        f.write("<param name=\"myID\" value=\"" + str(-1) + "\"/>\n")
        f.write("<param name=\"random_walk_method\" value=\"" + rw_method + "\"/>\n")
        f.write("<param name=\"sim_duration\" value=\"" + str(sim_duration) + "\"/>\n")
        f.write("<param name=\"no_targets\" value=\"" + str(no_targets) + "\"/>\n")
        f.write("<param name=\"frequency\" value=\"" + str(frequency) + "\"/>\n")
        f.write("<param name=\"tg_update\" value=\"" + str(tg_update) + "\"/>\n")
        f.write("</node>\n")
        f.write("</group>\n\n")

        f.write("<group ns=\"clock_agent\">\n")
        f.write("<node pkg=\"gitagent_2\" name=\"clock_agent\" type=\"clock_agent.py\" required=\"true\" output=\"screen\">\n")
        f.write("<param name=\"random_walk_method\" value=\"" + rw_method + "\"/>\n")
        f.write("<param name=\"sim_duration\" value=\"" + str(sim_duration) + "\"/>\n")
        f.write("<param name=\"no_agents\" value=\"" + str(no_agents) + "\"/>\n")
        f.write("</node>\n")
        f.write("</group>\n\n")

        f.write("</launch>")


if __name__ == '__main__':
    
    if len(sys.argv) < 12:
        print "Usage: ./generate_launch_files no_agents no_targets rw_method wu_method coverage sim_duration frequency tg_update tgreq tgresp tgbehav"
    print sys.argv[1]
    print sys.argv[2]
    print sys.argv[3]
    print sys.argv[4]
    print sys.argv[5]
    print sys.argv[6]
    print sys.argv[7]
    print sys.argv[8]
    print sys.argv[9]
    print sys.argv[10]
    print sys.argv[11]
    write2file(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10], sys.argv[11])
