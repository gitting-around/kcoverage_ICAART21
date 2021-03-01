#!/usr/bin/env python
import sys
import math
import rospy
import operator
import numpy as np
import random
#TODO USE LOCK FOR self.links!!!!
class Aux:
    def __init__(self, seed):
        self.lsi_init = False
        self.lsi_links = []
        self.links = []
        self.lsi_old_pos = [0, 0]
        self.no_ags = 10
        self.no_ags_max = 10
        random.seed(seed)

    def newest_nearest(self, my_motion, requests, all_targets): # returns a request for a target
        dsts = [] # follows indexing of requests
        chosen = []

        # create list of targets from list of requests
        if all_targets:
            for x in requests:
                for i, p in enumerate(all_targets.id):
                    if p == x.tg_id and all_targets.category[i] == 'target':
                        # calculate distance from self
                        dst = math.sqrt((my_motion[0] - all_targets.xpos[i])**2 + (my_motion[1] - all_targets.ypos[i])**2)
                        dsts.append(dst)

            # pick closest
            idx = dsts.index(min(dsts))
            chosen = requests[idx]
            rospy.loginfo("Newest Nearest: requests %s, dists %s, chosen: %d", str([x.ag_id for x in requests]), str(dsts), chosen.ag_id)

        return chosen

    def link_strength_implicit(self, myid, my_motion, all_targets): # return links strength array
        try:
            if not self.lsi_init: # Initilize all links to 0
                if all_targets:
                    self.no_ags = 0
                    notg = 0
                    for i,x in enumerate(all_targets.category):
                        if x == "agent" and not all_targets.id[i] == myid:
                            self.lsi_links.append([all_targets.id[i], 0])
                            self.no_ags += 1
                        elif x == "target":
                            notg += 1
                    if self.no_ags + 1 == self.no_ags_max and not notg == 0:
                        self.lsi_init = True
                    else:
                        self.lsi_links = []

                    self.lsi_links = sorted(self.lsi_links, key=operator.itemgetter(0))
                    rospy.loginfo("[LSI] initialized links %s", str(self.lsi_links))
            else: # Update links based on proximity to targets. CONVOLUTED SHIT about to take place. 
                rospy.loginfo("########################################################")
                rospy.loginfo("########################################################")
                noag = len(self.lsi_links) + 1
                notg = len(all_targets.id) - noag
                dist_matrix = np.zeros((noag, notg))
                agents = []

                print self.lsi_links
                print dist_matrix

                k = 0
                for i,p in enumerate(all_targets.id):
                    if all_targets.category[i] == 'target':
                        sqx = (my_motion[0] - all_targets.xpos[i]) * (my_motion[0] - all_targets.xpos[i])
                        sqy = (my_motion[1] - all_targets.ypos[i]) * (my_motion[1] - all_targets.ypos[i])
                        dist_matrix[0][k] = math.sqrt(sqx + sqy) # fill first row, current agent
                        k = k + 1
                    elif all_targets.category[i] == 'agent' and not p == myid:
                        agents.append([p, all_targets.xpos[i], all_targets.ypos[i]])
                agents = sorted(agents, key=operator.itemgetter(0))

                print agents
                print dist_matrix

                k = 0
                for i,p in enumerate(all_targets.id):
                    j = 0
                    if all_targets.category[i] == 'target':
                        for x in agents:
                            sqx = (x[1] - all_targets.xpos[i]) * (x[1] - all_targets.xpos[i])
                            sqy = (x[2] - all_targets.ypos[i]) * (x[2] - all_targets.ypos[i])
                            dist_matrix[j+1][k] = math.sqrt(sqx + sqy) # fill the rest, for other agents
                            j = j + 1
                        k = k + 1

                print dist_matrix

                ownpos_tg = np.array([0 if x > 30 else 1 for x in dist_matrix[0]])

                print ownpos_tg

                if my_motion[0] == self.lsi_old_pos[0] and my_motion[1] == self.lsi_old_pos[1]:
                    poschange = 0
                else:
                    poschange = 1
                    self.lsi_old_pos[0] = my_motion[0]
                    self.lsi_old_pos[1] = my_motion[1]
                print poschange

                # Here is where the update of the links happens
                for i in range(0, noag-1):
                    agi_tg = np.array([0 if x > 30 else 1 for x in dist_matrix[i]])
                    print agi_tg
                    delta = sum(np.multiply(ownpos_tg, agi_tg))
                    print delta
                    self.lsi_links[i][1] = self.lsi_links[i][1]*0.995 + delta + poschange * 0.95

                self.links = sorted(self.lsi_links, key=operator.itemgetter(1), reverse=True)
                print self.links
                rospy.loginfo("########################################################")
                rospy.loginfo("########################################################")
            return self.lsi_links
        except:
            rospy.logerr("Unexpected error " + str(myid) + ": " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno))

    def link_strength_explicit(self, requests, all_targets):
        chosen = []

        return chosen

    def get_req_strongest_link(self, requests): # TODO GET THIS AGENT

        req_ag = [x.ag_id for x in requests]

        chosen = []

        if self.links:
            for x in self.links:
                if x[0] in req_ag:
                    chosen = requests[req_ag.index(x[0])]
                    break

        return chosen

    def least_covered(self, requests, all_targets):  # returns a request for a target
        # loop over requests, pick first from the ones with lowest nr of involved agents.
        involved = []

        for x in requests:
            involved.append(len(x.ag_involved))

        rospy.loginfo("Existing coverage: %s", str(involved))
        idx = involved.index(min(involved))

        chosen = requests[idx]
        rospy.loginfo("Chosen request: %s", str(chosen))

        return chosen

    def amI_kclosest(self, myid, requesterid, all_targets, k):
        agents = []
        dsts = []
        reqx = -1000
        reqy = -1000
        # extract agent location data from all_targets
        if all_targets:
            for i,x in enumerate(all_targets.category):
                if x == "agent":
                    if all_targets.id[i] == requesterid:
                        reqx = all_targets.xpos[i]
                        reqy = all_targets.ypos[i]
                    else:
                        agents.append([all_targets.id[i], all_targets.xpos[i], all_targets.ypos[i]])

        # loop over all agents, calculating distances of between requesterid agent with the rest. 
        for x in agents:
            sqx = (reqx - x[1]) * (reqx - x[1])
            sqy = (reqy - x[2]) * (reqy - x[2])
            dst = math.sqrt(sqx + sqy)
            dsts.append([x[0], dst])

        # order such list and prune to length k
        dsts = sorted(dsts, key=operator.itemgetter(1))
        rospy.loginfo("dists: %s", str(dsts))
        dsts = dsts[0:k]
        rospy.loginfo("dists: %s", str(dsts))

        # select myid if in this list
        amIin = False
        
        if myid in [x[0] for x in dsts]:
            amIin = True

        return amIin

    def amI_kfurthest(self, myid, requesterid, all_targets, k):
        agents = []
        dsts = []
        reqx = -1000
        reqy = -1000
        # extract agent location data from all_targets
        if all_targets:
            for i,x in enumerate(all_targets.category):
                if x == "agent":
                    if all_targets.id[i] == requesterid:
                        reqx = all_targets.xpos[i]
                        reqy = all_targets.ypos[i]
                    else:
                        agents.append([all_targets.id[i], all_targets.xpos[i], all_targets.ypos[i]])

        # loop over all agents, calculating distances of between requesterid agent with the rest. 
        for x in agents:
            sqx = (reqx - x[1]) * (reqx - x[1])
            sqy = (reqy - x[2]) * (reqy - x[2])
            dst = math.sqrt(sqx + sqy)
            dsts.append([x[0], dst])

        # order such list and prune to length k
        dsts = sorted(dsts, key=operator.itemgetter(1), reverse=True)
        rospy.loginfo("dists: %s", str(dsts))
        dsts = dsts[0:k]
        rospy.loginfo("dists: %s", str(dsts))

        # select myid if in this list
        amIin = False
        
        if myid in [x[0] for x in dsts]:
            amIin = True

        return amIin

    def amI_krandom(self, myid, requesterid, kcov): #number of agents is set here manually!!! CAREFUL!!!

        amIin = False
        if not self.no_ags == 0:
            ids = [x+1 for x in range(self.no_ags) if not x+1 == requesterid]
            rospy.loginfo("ids: %s", str(ids))
            krandom = random.sample(ids, k=kcov)
            rospy.loginfo("random listeners: %s", str(krandom))
            if myid in krandom:
                amIin = True

        return amIin

    