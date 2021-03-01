#!/usr/bin/env python
import sys
import os

class GitLogger:
    def __init__(self, collab_approach, duration):
        self.base_path = os.path.expanduser("~/catkin_ws")
        self.path = os.path.expanduser("~/catkin_ws/src/gitagent_2")
        # Each element in the list is fore very timestep
        self.collab_approach = collab_approach
        self.duration = duration
        self.followed = [] #[[tgid, tgx, tgy]...]
        self.willingness = [] # [[val1, timestep], .....], in the end format to [[val1, val2,... timestep1], .....]
        self.dropped = [] #[[tgid, tgx, tgy]...]
        self.Iasked = [] #[[tgid, tgx, tgy, timestep]...]
        self.wasAsked = [] #[[tgid, tgx, tgy, timestep]...]
        self.noreplans = [] #[0,1,2,....]
        self.planner_calls = [] #[0,0,1,0,0,0,1,.....]
        self.received_plans = [] #[1,0,0,0,0,0,1,.....]
        self.plan_done = [] #[0,0,0,0,0,0,1,.....]
        self.mytasks_plan = [] #[[tgid,...]...]
        self.mylocation = [] # [[x,y], ....]
        self.myEquip = [] #[[eq1, eq2, ...], ....]
        self.allbroken = [] #[[id1, id2, ...], ....] for every timestep
        self.own_equip_broken = [] #[[total1, total2, ...], ....] for every timestep
        self.completed = [] # only one task can be completed per time-step. timesteps are separated with space. If task completed then put id, otherwise -1
        self.targets = [] #[[tgid, tgx, tgy]...]
        self.agents = []
        self.detailed_w = []
        self.detailed_u =[]
        self.plans_tasks_equips = []

    def logit(self, toggle, follow=[], willing=[], drop=[], iask=[], wasask=[], norepl=0, plan_call=0, receiv_plan=0, done=0, mytask=[], 
    myloc=[], myEquip=[], allbroke=[], own_equip_broken=[], completed=-1, detailed_w=[], detailed_u=[]):
        if toggle==1:
            self.followed.append(follow)
        elif toggle==2:
            self.willingness.append(willing)
        elif toggle==3:
            self.dropped.append(drop)
        elif toggle==4:
            self.Iasked.append(iask)
        elif toggle==5:
            self.wasAsked.append(wasask)
        elif toggle==6:
            self.noreplans.append(norepl)
        elif toggle==7:
            self.planner_calls.append(plan_call)
        elif toggle==8:
            self.received_plans.append(receiv_plan)
        elif toggle==9:
            self.plan_done.append(done)
        elif toggle==10:
            self.mytasks_plan.append(mytask)
        elif toggle==11:
            self.mylocation.append(myloc)
        elif toggle==12:
            eq = [x for x in myEquip if not x == 'failed']
            self.myEquip.append(eq)
        elif toggle==13:
            self.allbroken.append(allbroke)
        elif toggle==14:
            self.own_equip_broken.append(own_equip_broken)
        elif toggle==15:
            self.completed.append(completed)
        elif toggle==16:
            self.detailed_u = detailed_u
        elif toggle==17:
            self.detailed_w.append(detailed_w)

    def write2file(self, id): # To be called at the end of the simulation
        try:
            if id == -1:
                with open(self.base_path+"/gitlogger_"+str("env"), 'w') as f:
                    f.write(self.collab_approach+'\n')
                    f.write(str(self.duration)+'\n')
                    print "im writing the file "
                    for x in self.targets:
                        print x
                        if x:
                            for i in x:
                                f.write(str(i[0])+" "+str(i[1])+" "+str(i[2])+"#")
                            f.write("|")
                        else:
                            f.write(" |")

                    f.write("\n")

                    for x in self.agents:
                        print x
                        if x:
                            for i in x:
                                f.write(str(i[0])+" "+str(i[1])+" "+str(i[2])+"#")
                            f.write("|")
                        else:
                            f.write(" |")

                    f.write("\n")
            else:
                with open(self.base_path+"/gitlogger_"+str(id), 'w') as f:
                    f.write(self.collab_approach+'\n')
                    f.write(str(self.duration)+'\n')

                    for x in self.followed:
                        if x:
                            for i in x:
                                f.write(str(i[0])+" "+str(i[1])+" "+str(i[2])+"#")
                            f.write("|")
                        else:
                            f.write(" |")

                    f.write("\n")

                    #flatten self.willingness in [[v1, v2....], [v1, v2, v3....]] for each timestep
                    w = [[] for x in range(self.duration)]

                    for x in self.willingness:
                        w[x[1]-1].append(x[0])

                    for x in w:
                        for i in x:
                            f.write(str(i)+" ")
                        f.write(" |")

                    f.write("\n")
                    
                    print "after logging willingness"

                    d = [[] for x in range(self.duration)]
                    for x in self.dropped:
                        if x:
                            print x
                            d[x[-1]-1].append(x[0])
                    for x in d:
                        for i in x:
                            f.write(str(i)+" ")
                        f.write(" |")

                    f.write("\n")
                    print "after logging dropped"
                    ia = [[] for x in range(self.duration)]
                    for x in self.Iasked:
                        if x:
                            ia[x[3]-1].append(x[0])

                    for x in ia:
                        for i in x:
                            f.write(str(i)+" ")
                        f.write(" |")

                    f.write("\n")

                    print "after logging requests made"
                    wa = [[] for x in range(self.duration)]
                    for x in self.wasAsked:
                        if x:
                            wa[x[3]-1].append(x[0])

                    for x in wa:
                        for i in x:
                            f.write(str(i)+" ")
                        f.write(" |")

                    f.write("\n")
                    print "after logging requests received"
                    for x in self.noreplans:
                        f.write(str(x)+" ")
                    print "noreplans %d" % len(self.noreplans)

                    f.write("\n")

                    for x in self.planner_calls:
                        f.write(str(x)+" ")
                    print "planners calls %d" % len(self.planner_calls)
                    f.write("\n")

                    for x in self.received_plans:
                        f.write(str(x)+" ")

                    f.write("\n")

                    for x in self.plan_done:
                        f.write(str(x)+" ")

                    f.write("\n")

                    for x in self.mytasks_plan:
                        if x:
                            for i in x:
                                f.write(str(i)+" ")
                            f.write("|")
                        else:
                            f.write(" |")

                    f.write("\n")

                    for x in self.mylocation:
                        if x:
                            for i in x:
                                f.write(str(i)+" ")
                            f.write("|")
                        else:
                            f.write(" |")

                    f.write("\n")

                    for x in self.myEquip:
                        if x:
                            for i in x:
                                f.write(str(i)+" ")
                            f.write("|")
                        else:
                            f.write(" |")

                    f.write("\n")

                    for x in self.allbroken:
                        if x:
                            for i in x:
                                f.write(str(i)+" ")
                            f.write("|")
                        else:
                            f.write(" |")

                    f.write("\n")

                    for x in self.own_equip_broken:
                        f.write(str(x)+" ")

                    f.write("\n")

                    for x in self.completed:
                        f.write(str(x)+" ")

                    f.write("\n")

                    w = [[] for x in range(self.duration)]
                    for x in self.detailed_w:
                        #print x
                        w[x[4]-1].append(x[0:4])
                    print "debug"
                    for x in w:
                        #print x
                        for i in x:
                            mystr = str(i[0][0]) + " " + str(i[0][1]) + " " + str(i[1][0]) + " " + str(i[1][1]) + " " + str(i[2]) + " " + str(i[3])
                            f.write(mystr)
                            f.write("#")
                        f.write(" |")

                    f.write("\n")

                    u = [[] for x in range(self.duration)]

                    for x in self.detailed_u:
                        u[x[3]-1].append(x[0:3])

                    for x in u:
                        print x
                        for i in x:
                            mystr = str(i[0]) + " " + str(i[1]) + " " + str(i[2])
                            f.write(mystr)
                            f.write("#")
                        f.write(" |")

                    f.write("\n")

                    if id == 1:
                        for el in self.plans_tasks_equips:
                            f.write(str(el))
                            f.write("\n")

                    f.write("\n")
        except:
            print "[gitlogger]  Unexpected error: " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)

    def log_env(self, targets=[], agents=[]):
        self.targets.append(targets)
        self.agents.append(agents)