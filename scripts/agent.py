#!/usr/bin/env python
import sys, os
import rospy
import time
from gitagent_2.msg import *
from gitagent_2.srv import *
from std_msgs.msg import String
from threading import Thread, Lock
from random_walk_plg import rw_plugins
from wu_plg import wu_plugins
import numpy as np
import pdb
from operator import itemgetter
import Queue
import math
import copy
import random
from git_logger import gitlogger 
from req_resp import req_resp_aux

class Agent:
    def __init__(self, ID, init_state):
        try:
            self.base_path = os.path.expanduser("~/catkin_ws")
            self.path = os.path.expanduser("~/catkin_ws/src/gitagent_2")
            #pub = rospy.Publisher('chatter', String, queue_size=10)
            print rospy.get_param('/seed')

            self.ID = int(rospy.get_param('agent/myID'))
            s = int(rospy.get_param('/seed'))*11 + self.ID - 1 
            #s = int(rospy.get_param('/seed'))
            np.random.seed(s)
            rospy.init_node('agent', anonymous=True)
            self.publish_motion = rospy.Publisher('/environment/motion_values', motion_values, queue_size=10)

            #### PIGNATTA 3 toggles, choosing response, request models, and normal vs random &follow behaviour
            # 0 - normal broadcast to all, 1 - kclosest, 2 - kfurthest, 3 - krandom
            self.toggle_request = int(rospy.get_param('agent/toggle_request'))
            # 0 - willingness, 1 - newestNearest, 2 - available, 3 - graph, 4 - received call
            self.toggle_respond = int(rospy.get_param('agent/toggle_respond'))
            # 0 - normal interactions, 1 - random &follow (in this case previous toggles are irrelevant)
            self.toggle_behaviour = int(rospy.get_param('agent/toggle_behaviour'))

            print "Request model: %d" % self.toggle_request
            print "Respond model: %d" % self.toggle_respond
            print "Behaviour: %d" % self.toggle_behaviour

            self.publish_help = rospy.Publisher('/help', help, queue_size=10)
            self.publish_help_reply = rospy.Publisher('/help_reply', help_reply, queue_size=10)
            self.publish_help_assign = rospy.Publisher('/help_assign', help_assign, queue_size=10)
            self.publish_help_drop = rospy.Publisher('/help_drop', help_drop, queue_size=10)

            self.publish_help_modify = rospy.Publisher('/help_modify', help_modify, queue_size=10)
            self.publish_help_replace = rospy.Publisher('/help_replace', help_replace, queue_size=10)
            self.publish_help_replace_answer = rospy.Publisher('/help_replace_answer', help_replace_answer, queue_size=10)

            self.publish_info = rospy.Publisher('/info', info, queue_size=10)
            self.publish_info_answer = rospy.Publisher('/info_answer', info_answer, queue_size=10)

            self.motion_msg = motion_values()
            self.motion_msg.id = self.ID
            self.motion_msg.category = 'agent'

            self.help_msg = help()
            self.help_msg.ag_id = self.ID
            self.help_reply = [] #every element in list is of the form [id, willingness, utility]. Can be handled by multiple threads --> used self.lock
            self.help_replace_reply = []
            self.help_needed = Queue.Queue() #queue object, it is THREADSAFE
            self.help_replace_needed = Queue.Queue() #queue object, it is THREADSAFE
            self.help_assign = help_assign() #can be handled by multiple threads --> used self.lock
            self.help_assign.ag_id = self.ID
            self.help_drop = help_drop()
            self.help_drop.ag_id = self.ID
            
            self.help_modify = help_modify()
            self.help_modify.ag_id = self.ID
            self.help_replace = help_replace()
            self.help_replace.ag_id = self.ID
            self.help_replace_answer = help_replace_answer()
            self.help_replace_answer.ag_id = self.ID

            self.info_msg = info()
            self.info_msg.ag_id = self.ID
            self.info_reply = False #can be handled by multiple threads --> used self.lock
            self.reply = [] #can be handled by multiple threads --> used self.lock
            self.info_answer = info_answer()
            self.info_answer.ag_id = self.ID
            #rate = rospy.Rate(10) # 10hz

            self.lock = Lock()

            #self.motion = [np.random.normal(50, 2),np.random.normal(50, 2),2,0,0.2] #xpos, ypos, vel, phi, omega
            self.motion = [0.0, 0.0, 2.0, np.random.random()*2*math.pi, 2*math.pi] #xpos, ypos, vel, phi, omega
            self.all_targets = [] #Double check this again --> look at further comment
            self.followed_targets = [] #can be handled by multiple threads --> used self.lock
            self.spotted_targets = [] #can be handled by multiple threads --> used self.lock
            self.dropped_targets = [] #for now handled by a single thread
            self.moving_away = {}
            self.refresh = [10, 0]

            #0 -> idle, 1 -> idle + execute
            print "I'm agent %d" % self.ID
            self.state = init_state
            self.battery = 1.0
            self.battery_drop = 0.01

            print rospy.get_param('agent/sim_duration')
            self.sim_duration = rospy.get_param('agent/sim_duration')

            print rospy.get_param('agent/random_walk_method')
            self.rw_method = getattr(rw_plugins, rospy.get_param('agent/random_walk_method'))()

            print rospy.get_param('agent/wu_method')
            self.wu_method = getattr(wu_plugins, rospy.get_param('agent/wu_method'))()

            self.kcoverage = rospy.get_param('agent/kcoverage')
            print "Value of k: %d" % self.kcoverage
            self.reset_timer = [] # elements in the list are of the format [[task_id, period, current_step], [], []...]
            self.retry_coalition = [] #"lists of task ids" #can be handled by multiple threads --> used self.lock
            self.willingness = 0.0

            self.output_data = [] # print this data at the end of the simulation
            self.output_willingness = []
            self.coalition_mismatch = 0
            self.published_messages = 0
            self.callbacks = 0

            self.gitlog = gitlogger.GitLogger("pignatta", self.sim_duration)
            self.req_resp = req_resp_aux.Aux(int(rospy.get_param('/seed')))

            while rospy.get_rostime().secs < 1:
                pass

            rospy.Subscriber('/environment/all_motion_values', all_motion_values, self.callback_all_motion)
            rospy.Subscriber('/help', help, self.callback_help)
            rospy.Subscriber('/help_reply', help_reply, self.callback_help_reply)
            rospy.Subscriber('/help_assign', help_assign, self.callback_help_assign)
            rospy.Subscriber('/help_drop', help_drop, self.callback_help_drop)
            rospy.Subscriber('/info', info, self.callback_info)
            rospy.Subscriber('/info_answer', info_answer, self.callback_info_answer)
            rospy.Subscriber('/help_modify', help_modify, self.callback_help_modify)
            rospy.Subscriber('/help_replace', help_replace, self.callback_help_replace)
            rospy.Subscriber('/help_replace_answer', help_replace_answer, self.callback_help_replace_answer)
            self.alive = rospy.Subscriber('/clock_alive', String, self.alive_empty_callback)

            self.start_time = rospy.get_rostime().secs
            self.time_step = self.start_time
            self.out_passive_following = []
            
            print "Started, simulated time is: %d" % self.start_time
            #Thread(target = self.operate_Thread, args=(self.state,)).start()
            Thread(target = self.operate_Thread).start()

            #make the interact thread a daemon.
            interact_thread = Thread(target = self.interact_Thread)
            interact_thread.daemon = True
            if self.toggle_behaviour == 0:
                interact_thread.start()
            else:
                rospy.loginfo("INTERACT thread is not active --> random &follow behaviour")
        except (rospy.ROSException, rospy.ROSInitException), e:
            rospy.logerr("Something went haywire in the agent initialization %s", e)
        
    def operate_Thread(self):
        try:
            print "[operate_Thread - %d] I'm the operate Thread" % rospy.get_rostime().secs
            print "[operate_Thread - %d] OP: Initial state: %d" % (rospy.get_rostime().secs, self.state)
            while not rospy.is_shutdown() and rospy.get_rostime().secs < self.start_time + self.sim_duration - 1:
                self.gitlog.logit(11, myloc=[self.motion[0], self.motion[1]])  
                self.gitlog.logit(12)
                self.gitlog.logit(13, allbroke=[])
                self.gitlog.logit(14)
                self.gitlog.logit(15)
                self.lock.acquire()
                if self.followed_targets:
                    self.output_data.append([x['id'] for x in self.followed_targets])
                    followed = [[x['id'], x['xpos'], x['ypos']] for x in self.followed_targets]    
                    self.gitlog.logit(1, follow=followed)  
                    self.state = 1
                else:
                    self.output_data.append([])
                    self.gitlog.logit(1, follow=[])  
                self.lock.release()

                self.gitlog.logit(6, norepl=0)
                self.gitlog.logit(7, plan_call=0)
                self.gitlog.logit(8, receiv_plan=0) 
                self.gitlog.logit(9, done=0) 
                self.gitlog.logit(10, mytask=[]) 

                if self.toggle_respond == 3: # Need to calculate link strength for the graph model
                    self.req_resp.link_strength_implicit(self.ID, self.motion, self.all_targets)

                if self.state == 0:
                    self.idle()
                elif self.state == 1:
                    self.execute()
                else:
                    print "[operate_Thread - %d] Bad value for state: %d" % (rospy.get_rostime().secs, self.state)
                #About to notify clock that I finished one cycle
                print "[operate_Thread - %d] before calling notify_clock" % rospy.get_rostime().secs
                code = self.notify_clock(self.ID)
                #Wait for clock to be updated to the next time-step
                while self.time_step == rospy.get_rostime().secs and rospy.get_rostime().secs < self.start_time + self.sim_duration - 1:
                    pass
                self.time_step = rospy.get_rostime().secs
                print "[operate_Thread] Simulated time is: %d" % rospy.get_rostime().secs

                self.battery = self.battery - self.battery_drop

                if self.battery <= self.wu_method.min:
                    self.battery = 1.0

            code = self.notify_clock(self.ID)

            with open(self.base_path+"/output_"+str(self.ID), 'w') as f:
                print "output"
                print self.output_data
                for x in self.output_data:
                    if x:
                        for i in x:
                            f.write(str(i)+" ")
                        f.write("\n")
                    else:
                        f.write("\n")
                f.write("spotted\n")
                for x in self.out_passive_following:
                    if x:
                        for i in x:
                            f.write(str(i)+" ")
                        f.write("\n")
                    else:
                        f.write("\n")
            with open(self.base_path+"/output_w_"+str(self.ID), 'w') as f:
                print "outputw"
                print self.output_willingness
                for x in self.output_willingness:
                    if x:
                        for i in x:
                            f.write(str(i)+" ")
                        f.write("\n")
                    else:
                        f.write("\n")

            self.gitlog.write2file(self.ID)
            print "[operate_Thread] coalition mismatches: %d, published: %d, callbacks: %d" % (self.coalition_mismatch, self.published_messages, self.callbacks)
            print "[operate_Thread - %d] operate thread exiting" % rospy.get_rostime().secs

            self.alive.unregister()
            sys.exit()
        except:
            print "[operate_Thread]  Unexpected error: " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)
            os._exit(1)

    def interact_Thread(self):
        try:
            print "[INTERACT - %d] I'm the interact Thread" % rospy.get_rostime().secs
            print "[INTERACT - %d]: Initial state: %d" % (rospy.get_rostime().secs, self.state)
            while not rospy.is_shutdown() and rospy.get_rostime().secs < self.start_time + self.sim_duration - 1:
                #This should work only when a new request has been received, or the agent itself wants to initiate something
                #check whether new spotted, or something is out of the internal boundary
                #if self.spotted_targets and self.ID==1: ##REMOVE## second condition to be removed
                notbusy = 1.0

                self.lock.acquire()
                if self.followed_targets:
                    notbusy = 1 / float(len(self.followed_targets))

                moving_away = copy.deepcopy(self.moving_away)
                spotted_targets = copy.deepcopy(self.spotted_targets)
                followed_targets = copy.deepcopy(self.followed_targets)
                retry_coalition = copy.deepcopy(self.retry_coalition)
                dropped_targets = copy.deepcopy(self.dropped_targets)
                all_targets = copy.deepcopy(self.all_targets)

                self.lock.release()

                self.willingness = self.wu_method.willingness(self.willingness, [[self.battery, 1], [notbusy, 0]])

                #is below threadsafe?
                if spotted_targets or not self.help_needed.empty() or (self.willingness < 0 and followed_targets) or retry_coalition or moving_away or dropped_targets:
                    self.gitlog.logit(2, willing=[self.willingness, rospy.get_rostime().secs]) 
                    print "[INTERACT - %d] I have to interact in some way" % rospy.get_rostime().secs
                    self.output_willingness.append([self.willingness, rospy.get_rostime().secs])
                    self.stop_clock(self.ID)
                 
                    if spotted_targets:
                        print "length of spotted: %d" % len(spotted_targets)
                        for x in spotted_targets:

                            #try to lock target
                            if self.lock_target(x['id']) == 1:
                                self.gitlog.logit(4, iask=[x['id'], x['xpos'], x['ypos'], rospy.get_rostime().secs])
                                #it was possible to lock the target
                                self.info_msg.tg_id = x['id']
                                self.info_msg.leader_id = -1
                                #set willingness here!
                                self.info_msg.willingness = self.willingness
                                self.info_msg.utility = self.wu_method.utility(x)
                                self.info_msg.timestep = rospy.get_rostime().secs
                                #for x in range(10):
                                with self.lock:
                                    self.reply = []
                                    self.info_reply = False
                                self.publish_info.publish(self.info_msg)                    
                                
                                print "[INTERACT - spotted targets - %d] info_msg: %s" % (rospy.get_rostime().secs, self.info_msg)

                                print "[INTERACT - spotted targets - %d] wait 1 walltime seconds for answers" % rospy.get_rostime().secs
                                timeout = time.time() + 1
                                while not self.info_reply and time.time() < timeout:
                                    pass

                                help = 0
                                ag_involved = []
                                self.lock.acquire()
                                self.published_messages += 1

                                info_reply = self.info_reply
                                reply_itself = self.reply
                                #if self.reply:
                                    #if len(self.reply) > 1:
                                        #print "[INTERACT - spotted targets -%d] probably more than one coalition: %s." % (rospy.get_rostime().secs, self.reply)
                                self.lock.release()

                                coalition_started = False
                                if info_reply:
                                    if reply_itself.help == 1:
                                        #check if I want to be involved
                                        print "[INTERACT - spotted targets -%d] Might be assigned." % rospy.get_rostime().secs
                                    else:
                                        print "[INTERACT - spotted targets -%d] Help not necessary." % rospy.get_rostime().secs
                                else:
                                    ag_involved = self.coalition(x, [], self.kcoverage)
                                    coalition_started = True
                                    if self.ID in [t[0] for t in ag_involved]:
                                        help = 1
                                
                                self.lock.acquire()
                                info_reply = self.info_reply
                                self.lock.release()
                                if coalition_started and info_reply:
                                    print  "[INTERACT - spotted targets -%d] I created a new coalition, but another exists for the same target." % rospy.get_rostime().secs
                                    self.coalition_mismatch += 1
                                
                                self.lock.acquire()
                                #this does not happen necessarily. the triggering agent might choose not to take part in the coalition
                                if help:
                                    print  "[INTERACT - spotted targets -%d] I am following a new target." % rospy.get_rostime().secs
                                    if not x['id'] in [t['id'] for t in self.followed_targets]:
                                        self.followed_targets.append({'category': 'target', 'id': x['id'], 'xpos': x['xpos'], 'ypos': x['ypos'], 
                        'velocity': x['velocity'], 'direction': x['direction'], 'change_dir': x['change_dir'], 'ag_involved': [t[0] for t in ag_involved], 'interest': x['interest']})
                                else:
                                    print  "[INTERACT - spotted targets -%d] I am NOT following a new target." % rospy.get_rostime().secs

                                self.lock.release()

                                #unlock target
                                self.free_target(x['id'])
                            else:
                                print "[INTERACT - spotted targets - %d] Someone already on it :)." % (rospy.get_rostime().secs)

                    #check if I got a request
                    if not self.help_needed.empty():
                        if self.toggle_respond == 0:
                            while not self.help_needed.empty():
                                #print "[interact - help_needed - %d] Request gotten. Consider giving help" % rospy.get_rostime().secs
                                data = self.help_needed.get()
                                if data.timestep == rospy.get_rostime().secs:
                                    print "[INTERACT - help_needed - %d] Request gotten %s. send back willingness and utility" % (rospy.get_rostime().secs, data)
                                    self.gitlog.logit(5, wasask=[data.tg_id, data.tg_xpos, data.tg_ypos, rospy.get_rostime().secs])
                                    answer = help_reply()
                                    answer.ag_id = self.ID
                                    answer.tg_id = data.tg_id
                                    answer.intended_recipient = data.ag_id
                                    answer.timestep = rospy.get_rostime().secs
                                    target = 0
                                    if all_targets:
                                        #print "[interact - help_needed - %d] help_needed: %s" % (rospy.get_rostime().secs, str(self.all_targets))
                                        for i, p in enumerate(all_targets.id):
                                            #print "[interact - help_needed - %d] i, p: %d, %d" % (rospy.get_rostime().secs, i, p)
                                            #print "[interact - help_needed - %d] ids: %s" % (rospy.get_rostime().secs, str(self.all_targets.id))
                                            #print "[interact - help_needed - %d] tg_id: %d" % (rospy.get_rostime().secs, data.tg_id)
                                            #print "[interact - help_needed - %d] category: %s" % (rospy.get_rostime().secs, self.all_targets.category[i])
                                            if p == data.tg_id and all_targets.category[i] == 'target':
                                                #print "[interact - help_needed - %d] im in!!!!!!!" % rospy.get_rostime().secs
                                                #print "[INTERACT - help_needed] type of ag_involved: %s" % str(type(data.ag_involved))
                                                target = {'category': 'target', 'id': p, 'xpos': all_targets.xpos[i], 'ypos': all_targets.ypos[i], 
                            'velocity': all_targets.velocity[i], 'direction': all_targets.direction[i], 
                            'change_dir': all_targets.omega[i], 'ag_involved': data.ag_involved, 'interest': all_targets.interest[i]}
                                                #print "[interact - help_needed - %d] value of target should be changed: %s" % (rospy.get_rostime().secs, str(target))
                                                print "[INTERACT - help_needed - %d] target: %s" % (rospy.get_rostime().secs, str(target))
                                                #print "[interact - help_needed - %d] data: %s" % (rospy.get_rostime().secs, str(data))
                                                break
                                        answer.utility = self.wu_method.utility(target) #we will use predefined interest level, later other things might affect utility
                                    else:
                                        answer.utility = 0.0
                                    answer.willingness = self.willingness
                                    self.publish_help_reply.publish(answer)
                                    with self.lock:
                                        self.published_messages += 1
                        else:
                            numberofiterations = 0
                            rospy.loginfo("[INTERACT %d], Pick request to respond to", rospy.get_rostime().secs)
                            answer2 = []
                            if self.toggle_respond == 1:
                                # for newest-nearest, get all the data from the queue into the list.
                                allreq = []
                                rospy.loginfo("[INTERACT %d], newest-nearest", rospy.get_rostime().secs)
                                while not self.help_needed.empty():
                                    numberofiterations += 1
                                    allreq.append(self.help_needed.get())
                                    rospy.loginfo("[INTERACT %d], newest-nearest, iterations %d", rospy.get_rostime().secs, numberofiterations)
                                
                                answer2 = self.req_resp.newest_nearest(self.motion, allreq, all_targets)

                            elif self.toggle_respond == 2:
                                # for available
                                if self.state == 0:
                                    allreq = []
                                    rospy.loginfo("[INTERACT %d], available", rospy.get_rostime().secs)
                                    while not self.help_needed.empty():
                                        numberofiterations += 1
                                        allreq.append(self.help_needed.get())
                                        rospy.loginfo("[INTERACT %d], available, iterations %d", rospy.get_rostime().secs, numberofiterations)
                                    
                                    answer2 = self.req_resp.newest_nearest(self.motion, allreq, all_targets)

                            elif self.toggle_respond == 3:
                                # for graph
                                if self.state == 0:
                                    allreq = []
                                    rospy.loginfo("[INTERACT %d], graph", rospy.get_rostime().secs)
                                    while not self.help_needed.empty():
                                        numberofiterations += 1
                                        allreq.append(self.help_needed.get())
                                        rospy.loginfo("[INTERACT %d], graph, iterations %d", rospy.get_rostime().secs, numberofiterations)

                                    #answer2 = self.req_resp.link_strength_implicit(self.ID, self.motion, all_targets)
                                    answer2 = self.req_resp.get_req_strongest_link(allreq)

                            elif self.toggle_respond == 4:
                                # for req received
                                if self.state == 0:
                                    allreq = []
                                    rospy.loginfo("[INTERACT %d], least covered", rospy.get_rostime().secs)
                                    while not self.help_needed.empty():
                                        numberofiterations += 1
                                        allreq.append(self.help_needed.get())
                                        rospy.loginfo("[INTERACT %d], least covered, iterations %d", rospy.get_rostime().secs, numberofiterations)

                                    answer2 = self.req_resp.least_covered(allreq, all_targets)
                            if answer2:
                                answer = help_reply()
                                answer.ag_id = self.ID
                                answer.tg_id = answer2.tg_id
                                answer.intended_recipient = answer2.ag_id
                                answer.timestep = rospy.get_rostime().secs
                                target = 0
                                if all_targets:
                                    for i, p in enumerate(all_targets.id):
                                        if p == answer2.tg_id and all_targets.category[i] == 'target':
                                            target = {'category': 'target', 'id': p, 'xpos': all_targets.xpos[i], 'ypos': all_targets.ypos[i], 
                        'velocity': all_targets.velocity[i], 'direction': all_targets.direction[i], 
                        'change_dir': all_targets.omega[i], 'ag_involved': answer2.ag_involved, 'interest': all_targets.interest[i]}
                                            print "[INTERACT - help_needed - %d] target: %s" % (rospy.get_rostime().secs, str(target))
                                            break
                                    answer.utility = 1.0 #we will use predefined interest level, later other things might affect utility
                                else:
                                    answer.utility = 1.0
                                answer.willingness = 1.0
                                rospy.loginfo("[INTERACT - NN] answer: %s", str(answer))
                                self.publish_help_reply.publish(answer)
                                with self.lock:
                                    self.published_messages += 1
                            else:
                                self.help_needed.queue.clear()
                                rospy.loginfo("[INTERACT %d], No request was chosen - clear the queue, size %d", rospy.get_rostime().secs, self.help_needed.qsize())

                    #Check my willingness
                    if self.willingness < 0 and followed_targets:
                        #take first element out of self.followed_targets
                        first_target = followed_targets[0]
                        #check if I am leader
                        self.gitlog.logit(4, iask=[first_target['id'], first_target['xpos'], first_target['ypos'], rospy.get_rostime().secs])
                        if first_target['ag_involved'][0] == self.ID:
                            #I am the leader
                            #start full or partial coalition process
                            print "[INTERACT - willingness below 0 - %d] I'm the leader --> start coalition formation, full or partial" % rospy.get_rostime().secs
                            self.coalition(first_target, first_target['ag_involved'], self.kcoverage - len(first_target['ag_involved'][1:]))
                        else:
                            #I'm not the leader
                            self.help_drop.tg_id = first_target['id']
                            self.help_drop.intended_recipient = first_target['ag_involved'][0]
                            self.help_drop.timestep = rospy.get_rostime().secs
                            self.publish_help_drop.publish(self.help_drop)
                            print "[INTERACT - willingness below 0 - %d] notify leader of drop, then drop" % rospy.get_rostime().secs

                        #drop target
                        self.lock.acquire()
                        self.followed_targets = self.followed_targets[1:]
                        if not self.followed_targets:
                            self.state = 0
                        self.lock.release()
                    
                    #check for timer
                    if retry_coalition:
                        print "[interact - retry coalition - %d] retry_coalition %s" % (rospy.get_rostime().secs, str(retry_coalition))
                        for x in retry_coalition:
                            #get the full target from self.followed_targets
                            for y in followed_targets:
                                if x == y['id']:
                                    #try to extend coalition
                                    self.coalition(y, y['ag_involved'], self.kcoverage - len(y['ag_involved']))
                                    break
                            self.lock.acquire()
                            self.gitlog.logit(4, iask=[['id'], y['xpos'], y['ypos'], rospy.get_rostime().secs])
                            self.retry_coalition.pop(self.retry_coalition.index(x))
                            self.lock.release()
                        print "[interact - retry coalition - %d] retry_coalition %s" % (rospy.get_rostime().secs, str(self.retry_coalition))

                    #TODO do the same here as in self.help_needed.empty() line ..
                    if not self.help_replace_needed.empty():
                        if self.toggle_respond == 0:
                            while not self.help_replace_needed.empty():
                                #print "[interact - help_needed - %d] Request gotten. Consider giving help" % rospy.get_rostime().secs
                                data = self.help_replace_needed.get()
                                print "[INTERACT - help_replace_needed - %d] Request gotten %s. send back willingness and utility" % (rospy.get_rostime().secs, data)
                                if data.timestep == rospy.get_rostime().secs:
                                    answer = help_replace_answer()
                                    answer.ag_id = self.ID
                                    answer.tg_id = data.tg_id
                                    answer.intended_recipient = data.ag_id
                                    answer.timestep = rospy.get_rostime().secs
                                    target = 0
                                    if all_targets:
                                        #print "[interact - help_needed - %d] help_needed: %s" % (rospy.get_rostime().secs, str(self.all_targets))
                                        for i, p in enumerate(all_targets.id):
                                            if p == data.tg_id and all_targets.category[i] == 'target':
                                                target = {'category': 'target', 'id': p, 'xpos': all_targets.xpos[i], 'ypos': all_targets.ypos[i], 
                            'velocity': all_targets.velocity[i], 'direction': all_targets.direction[i], 
                            'change_dir': all_targets.omega[i], 'ag_involved': data.ag_involved, 'interest': all_targets.interest[i]}
                                                print "[INTERACT - help_replace_needed - %d] target: %s" % (rospy.get_rostime().secs, str(target))
                                                break
                                        answer.utility = self.wu_method.utility(target) #we will use predefined interest level, later other things might affect utility
                                    else:
                                        answer.utility = 0.0
                                    answer.willingness = self.willingness
                                    self.publish_help_replace_answer.publish(answer)
                        else:
                            rospy.loginfo("[INTERACT - help_replace_needed - %d], Pick request to respond to", rospy.get_rostime().secs)
                            answer2 = []
                            if self.toggle_respond == 1:
                                # for newest-nearest, get all the data from the queue into the list.
                                allreq = []
                                rospy.loginfo("[INTERACT - help_replace_needed -  %d], newest-nearest", rospy.get_rostime().secs)
                                while not self.help_replace_needed.empty():
                                    allreq.append(self.help_replace_needed.get())
                                
                                answer2 = self.req_resp.newest_nearest(self.motion, allreq, all_targets)

                            elif self.toggle_respond == 2:
                                # for available
                                if self.state == 0:
                                    allreq = []
                                    rospy.loginfo("[INTERACT - help_replace_needed -  %d], available", rospy.get_rostime().secs)
                                    while not self.help_replace_needed.empty():
                                        allreq.append(self.help_replace_needed.get())
                                    
                                    answer2 = self.req_resp.newest_nearest(self.motion, allreq, all_targets)

                            elif self.toggle_respond == 3:
                                # for graph
                                if self.state == 0:
                                    allreq = []
                                    rospy.loginfo("[INTERACT - help_replace_needed -  %d], graph", rospy.get_rostime().secs)
                                    while not self.help_replace_needed.empty():
                                        allreq.append(self.help_replace_needed.get())

                                    #answer2 = self.req_resp.link_strength_implicit(self.ID, self.motion, all_targets)
                                    answer2 = self.req_resp.get_req_strongest_link(allreq)

                            elif self.toggle_respond == 4:
                                # for req received
                                if self.state == 0:
                                    allreq = []
                                    rospy.loginfo("[INTERACT - help_replace_needed -  %d], least covered", rospy.get_rostime().secs)
                                    while not self.help_replace_needed.empty():
                                        allreq.append(self.help_replace_needed.get())

                                    answer2 = self.req_resp.least_covered(allreq, all_targets)
                            if answer2:
                                answer = help_replace_answer()
                                answer.ag_id = self.ID
                                answer.tg_id = answer2.tg_id
                                answer.intended_recipient = answer2.ag_id
                                answer.timestep = rospy.get_rostime().secs
                                target = 0
                                if all_targets:
                                    for i, p in enumerate(all_targets.id):
                                        if p == answer2.tg_id and all_targets.category[i] == 'target':
                                            target = {'category': 'target', 'id': p, 'xpos': all_targets.xpos[i], 'ypos': all_targets.ypos[i], 
                        'velocity': all_targets.velocity[i], 'direction': all_targets.direction[i], 
                        'change_dir': all_targets.omega[i], 'ag_involved': answer2.ag_involved, 'interest': all_targets.interest[i]}
                                            print "[INTERACT - help_needed - %d] target: %s" % (rospy.get_rostime().secs, str(target))
                                            break
                                    answer.utility = 1.0 #we will use predefined interest level, later other things might affect utility
                                else:
                                    answer.utility = 1.0
                                answer.willingness = 1.0
                                rospy.loginfo("[INTERACT - help_replace_needed - NN] answer: %s", str(answer))
                                self.publish_help_replace_answer.publish(answer)
                                with self.lock:
                                    self.published_messages += 1
                            else:
                                self.help_replace_needed.queue.clear()
                                rospy.loginfo("[INTERACT - help_replace_needed - %d], No request was chosen, clear queue, size %d", rospy.get_rostime().secs, self.help_replace_needed.qsize())

                    if moving_away:
                        print "[INTERACT - moving away - %d] Find replacement" % rospy.get_rostime().secs
                        self.gitlog.logit(4, iask=[moving_away['id'], moving_away['xpos'], moving_away['ypos'], rospy.get_rostime().secs])
                        
                        self.help_replace.tg_id = moving_away['id']
                        self.help_replace.timestep = rospy.get_rostime().secs
                        self.help_replace.ag_involved = moving_away['ag_involved']
                        #for x in range(10):
                        with self.lock:
                            self.help_replace_reply = []
                        self.publish_help_replace.publish(self.help_replace) 
                        with self.lock:
                            self.published_messages += 1        

                        timeout = time.time() + 1
                        while time.time() < timeout:
                            pass

                        self.lock.acquire()
                        reply = self.help_replace_reply
                        self.lock.release()

                        r = []
                        for xx in reply:
                            print "[INTERACT - moving away - %d] replies %s, already involved: %s" % (rospy.get_rostime().secs, xx, str(moving_away['ag_involved']))
                            if xx.ag_id in moving_away['ag_involved']:
                                print "popped"
                                ## for some reason here it does not always pop
                                #reply.pop(reply.index(xx))
                                #print "[INTERACT - moving away - %d] replies %s" % (rospy.get_rostime().secs, reply)
                            else:
                                r.append(xx)

                        reply = r

                        if reply:
                            print "[INTERACT - moving away - %d] Replies %s, moving_away: %s" % (rospy.get_rostime().secs, reply, moving_away)
                            #pick highest w+u
                            candidates = [ [x.ag_id, x.willingness+x.utility] for x in reply]
                            sorted(candidates, key=itemgetter(1), reverse=True)
                            replacement = candidates[0]
                            print "[INTERACT - moving away - %d] replacement %s" % (rospy.get_rostime().secs, str(replacement))
                            #update own ag_involved for the target
                            #assign
                            self.help_assign.tg_id = moving_away['id']
                            self.help_assign.tg_xpos = moving_away['xpos']
                            self.help_assign.tg_ypos = moving_away['ypos']
                            self.help_assign.timestep = rospy.get_rostime().secs
                            #should the agent drop itself??
                            moving_away['ag_involved'].append(replacement[0])
                            self.help_assign.ag_involved = moving_away['ag_involved']
                            self.help_assign.interest = moving_away['interest']
                            self.publish_help_assign.publish(self.help_assign)
                            print "[INTERACT - moving away - %d] bc assignment" % (rospy.get_rostime().secs)
                            #modify
                            self.help_modify.tg_id = moving_away['id']
                            self.help_modify.timestep = rospy.get_rostime().secs
                            self.help_modify.add_drop = 1
                            self.help_modify.ag_involved = [replacement[0]]
                            self.help_modify.intended_recipient = [moving_away['ag_involved'][0]]

                            self.publish_help_modify.publish(self.help_modify)
                            print "[INTERACT - moving away - %d] bc modification" % (rospy.get_rostime().secs)
                            with self.lock:
                                self.published_messages += 2
                        else:
                            print "[INTERACT - moving away - %d] No replies. Eventually target might be dropped." % rospy.get_rostime().secs

                    if dropped_targets:
                        for x in dropped_targets:
                            if self.ID == x['ag_involved'][0]:
                                print "[INTERACT - drop - %d] I am leader, remove myself from list then propagate for target %d, involved %s" % (rospy.get_rostime().secs, x['id'], str(x['ag_involved']))
                                self.help_modify.tg_id = x['id']
                                self.help_modify.timestep = rospy.get_rostime().secs
                                self.help_modify.ag_involved = x['ag_involved'][1:]
                                self.help_modify.intended_recipient = x['ag_involved'][1:]
                                self.help_modify.add_drop = 2

                                self.publish_help_modify.publish(self.help_modify)
                                with self.lock:
                                    self.published_messages += 1
                            else:
                                print "[INTERACT - drop - %d] notify leader of drop, then drop, tg %d, involved %s" % (rospy.get_rostime().secs, x['id'], str(x['ag_involved']))
                                self.help_drop.tg_id = x['id']
                                self.help_drop.intended_recipient = x['ag_involved'][0]
                                self.help_drop.timestep = rospy.get_rostime().secs
                                self.publish_help_drop.publish(self.help_drop)

                                with self.lock:
                                    self.published_messages += 1

                    self.lock.acquire()
                    self.spotted_targets = []
                    self.dropped_targets = []
                    self.moving_away = {}
                    self.lock.release()

                    self.start_clock(self.ID)
                    
            print "[INTERACT - %d] interact thread exiting, unsubscribing from clock after print" % rospy.get_rostime().secs
            #self.alive.unregister()
        except:
            rospy.loginfo("[INTERACT_thread] Unexpected error: %s . Line nr: %s", str(sys.exc_info()), str(sys.exc_info()[2].tb_lineno))

    def idle(self):
        try:
            self.motion = self.rw_method.update(self.motion)
            self.lock.acquire()
            self.spotted_targets = self.rw_method.check_for_tg(self.motion, self.all_targets, self.followed_targets, self.dropped_targets)
            self.out_passive_following.append([x['id'] for x in self.spotted_targets])
            self.lock.release()
            print "[IDLE - %d] Status in idle. Spotted_targets: %s\n [IDLE] followed targets: %s\n [IDLE] dropped_targets: %s" % (rospy.get_rostime().secs, str(self.spotted_targets), 
            str(self.followed_targets), str(self.dropped_targets))
            print "[IDLE - %d] current motion values: %s" % (rospy.get_rostime().secs, str(self.motion))

            self.motion_msg.xpos = self.motion[0]
            self.motion_msg.ypos = self.motion[1]
            self.motion_msg.velocity = self.motion[2]
            self.motion_msg.direction = self.motion[3]
            self.motion_msg.omega = self.motion[4]
            #for x in range(10):
            self.publish_motion.publish(self.motion_msg)
            print "[IDLE - %d] I published my motion in idle" % rospy.get_rostime().secs

            if self.toggle_behaviour == 1:
                self.followed_targets = copy.deepcopy(self.spotted_targets)
                if self.followed_targets:
                    rospy.loginfo("[IDLE - %d] Random &Follow, followed: %s, spotted: %s", rospy.get_rostime().secs, str([x['id'] for x in self.followed_targets]), str([x['id'] for x in self.spotted_targets]))
                else:
                    rospy.loginfo("[IDLE - %d] Random &Follow, nothing new", rospy.get_rostime().secs)

            self.lock.acquire()
            if self.followed_targets:
                print "[IDLE - %d] On the next iteration I will switch to execute" % rospy.get_rostime().secs
                self.state = 1
            self.lock.release()
        except:
            print "[IDLE ] Unexpected error: " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)

    def execute(self):
        try:
            #self.motion = self.rw_method.move_toward(self.motion, self.followed_targets)
            if not self.toggle_behaviour == 1:
                for x in self.followed_targets:
                    assert(len(x['ag_involved']) == len(set(x['ag_involved']))), "Execute: There are duplicates in involved agents %s" % str(x)
                    assert(len(x['ag_involved']) > 0), "Execute: The involved agents list is empty %s" % str(x)
                assert(len([x['id'] for x in self.followed_targets]) == len(set([x['id'] for x in self.followed_targets]))), "Execute: There are duplicates in target set"

            self.motion = self.rw_method.move_toward_sensible(self.motion, self.followed_targets)
            self.lock.acquire()
            self.spotted_targets = self.rw_method.check_for_tg(self.motion, self.all_targets, self.followed_targets, self.dropped_targets)
            self.out_passive_following.append([x['id'] for x in self.spotted_targets])
            self.moving_away = self.rw_method.tg_moving_away(self.motion, self.followed_targets)
            self.followed_targets, self.dropped_targets = self.rw_method.stop_follow(self.motion, self.followed_targets)
            #self.gitlog.logit(3, drop=[1,1,1, rospy.get_rostime().secs]) 
            if self.dropped_targets:
                self.gitlog.logit(3, drop=list(set([x['id'] for x in self.dropped_targets]))+[rospy.get_rostime().secs]) 
            else:
                self.gitlog.logit(3, drop=[0, rospy.get_rostime().secs]) 

            if self.toggle_behaviour == 1:
                self.followed_targets = self.followed_targets + copy.deepcopy(self.spotted_targets)
                if self.followed_targets:
                    rospy.loginfo("[EXECUTE - %d] Random &Follow, followed: %s, spotted: %s", rospy.get_rostime().secs, str([x['id'] for x in self.followed_targets]), str([x['id'] for x in self.spotted_targets]))
                else:
                    rospy.loginfo("[EXECUTE - %d] Random &Follow, nothing new", rospy.get_rostime().secs)
            
            followed_targets = copy.deepcopy(self.followed_targets)
            self.lock.release()
            print "[EXECUTE - %d] I spotted in execute: %s " % (rospy.get_rostime().secs, str(self.spotted_targets))
            print "[EXECUTE - %d] I follow: %s " % (rospy.get_rostime().secs, str(self.followed_targets))
            print "[EXECUTE - %d] I dropped: %s " % (rospy.get_rostime().secs, str(self.dropped_targets))
            print "[EXECUTE - %d] Moving away: %s " % (rospy.get_rostime().secs, str(self.moving_away))

            self.motion_msg.xpos = self.motion[0]
            self.motion_msg.ypos = self.motion[1]
            self.motion_msg.velocity = self.motion[2]
            self.motion_msg.direction = self.motion[3]
            self.motion_msg.omega = self.motion[4]
            #for x in range(10):
            self.publish_motion.publish(self.motion_msg)
            print "[EXECUTE - %d] I published my motion in execute" % rospy.get_rostime().secs


            if self.toggle_behaviour == 1:
                self.followed_targets = self.followed_targets + copy.deepcopy(self.spotted_targets)
                if self.followed_targets:
                    rospy.loginfo("[EXECUTE - %d] Random &Follow, followed: %s, spotted: %s", rospy.get_rostime().secs, str([x['id'] for x in self.followed_targets]), str([x['id'] for x in self.spotted_targets]))
                else:
                    rospy.loginfo("[EXECUTE - %d] Random &Follow, nothing new", rospy.get_rostime().secs)
                self.dropped_targets = []
            else:
                self.refresh[1] += 1

                if self.refresh[1] > self.refresh[0]:
                    self.refresh[1] = 0
                    self.lock.acquire()
                    #THINK of what to do here
                    #self.dropped_targets = []
                    self.lock.release()
                    print "[EXECUTE - %d] refresh" % rospy.get_rostime().secs

                if not followed_targets:
                    self.state = 0
                    self.reset_timer = []
                else:
                    #check if any target I am leader of is lower than k-coverage.
                    #print self.followed_targets
                    #print self.reset_timer
                    for x in followed_targets:
                        if x['ag_involved'][0] == self.ID:
                            if len(x['ag_involved']) < self.kcoverage:
                                print "[EXECUTE - %d] I still need more agents on this" % rospy.get_rostime().secs
                                #check whether this is a new target for which I am leader
                                if self.reset_timer:
                                    if x['id'] in [y[0] for y in self.reset_timer]:
                                        for i, item in enumerate(self.reset_timer):
                                            #pdb.set_trace()
                                            print "[EXECUTE -%d] reset timer is, myid %d, reset_timer: %s" % (rospy.get_rostime().secs, self.ID, str(self.reset_timer))
                                            if item[0] == x['id']:
                                                if item[1] == item[2]:
                                                    #It's time to try extending the coalition
                                                    self.reset_timer[i][1] += 1
                                                    self.reset_timer[i][2] = 0
                                                    self.lock.acquire()
                                                    self.retry_coalition.append(x['id'])
                                                    self.lock.release()
                                                else:
                                                    self.reset_timer[i][2] += 1
                                                break
                                else:
                                    self.reset_timer.append([x['id'], 2, 0])

                    print "[EXECUTE - %d] reset timer is: %s" % (rospy.get_rostime().secs, str(self.reset_timer))
        except AssertionError as error:
            rospy.logerr(error)
        except:
            print "[EXECUTE] Unexpected error " + str(self.ID) + ": " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)

    def coalition(self, x, ag_involved=[], coverage=-1): #x stands for target
        try:
            assert(not coverage == -1), "Coverage in coalition function is not initialized to a proper value"
            with self.lock:
                self.help_reply = []
            print "[COALITION - %d] aginv: %s, coverage: %s" % (rospy.get_rostime().secs, str(ag_involved), str(coverage))
            candid = []
            if self.willingness >= 0 and not self.ID in ag_involved:
                candid=[[self.ID, self.willingness + self.wu_method.utility(x)]]
                
            print "[COALITION - %d] Initiate coalition formation, willingness: %f, target: %s" % (rospy.get_rostime().secs, self.willingness, str(x))
            self.help_msg.tg_id = x['id']
            self.help_msg.timestep = rospy.get_rostime().secs
            self.help_msg.ag_involved = list(ag_involved)
            print "[COALITION] type of ag_involved: %s" % str(type(self.help_msg.ag_involved))
            #fill the other fields as well
            self.publish_help.publish(self.help_msg)

            timeout = time.time() + 1
            #here also k can be used, if k-answers are received there is no need to wait further
            while time.time() < timeout and len(self.help_reply) < coverage:
                pass
            
            reply = []
            self.lock.acquire()
            self.published_messages += 1
            print "[COALITION - %d] all replies %s $#" % (rospy.get_rostime().secs, str(self.help_reply))
            reply = copy.deepcopy(self.help_reply)
            self.lock.release()

            if reply:
                reply = [t for t in reply if t.tg_id == x['id']]

            if reply:
                print "[COALITION - %d] gotten some responses" % rospy.get_rostime().secs
                print "[COALITION - %d] decided on own involvement, select k highest, and leaders" % rospy.get_rostime().secs
                print "[COALITION - %d] %s" % (rospy.get_rostime().secs, str(reply))
                
                for n in reply:
                    if n.willingness >= 0:
                        candid.append([n.ag_id, n.willingness + n.utility])
                if candid and not coverage == 0:
                    print "[COALITION - %d] CANDID  %s" % (rospy.get_rostime().secs, str(candid))
                    candid = sorted(candid, key=itemgetter(1), reverse=True)
                    #if len(candid) > self.kcoverage - coverage:
                    candid = candid[:coverage]
                    print "[COALITION - %d] CANDIDidate  %s" % (rospy.get_rostime().secs, str(candid))
                    self.lock.acquire()
                    self.help_assign.tg_id = x['id']
                    self.help_assign.tg_xpos = x['xpos']
                    self.help_assign.tg_ypos = x['ypos']
                    self.help_assign.timestep = rospy.get_rostime().secs
                    self.help_assign.interest = x['interest']
                    self.help_assign.ag_involved = ag_involved
                    for n in candid:
                        if not n[0] in self.help_assign.ag_involved:
                            self.help_assign.ag_involved.append(n[0])
                        else:
                            print "[COALITION - %d] why is there a duplicate here?  %s" % (rospy.get_rostime().secs, str(candid))

                    self.publish_help_assign.publish(self.help_assign)
                    self.published_messages += 1
                    self.lock.release()
            
                print "[COALITION - %d] notify involved agents, %s" % (rospy.get_rostime().secs, str(self.help_assign.ag_involved))

            return candid
        except AssertionError as error:
            rospy.logerr(error)
        except:
            print "[COALITION] Unexpected error: " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)

    def notify_clock(self, code):
        print "ID: %d, im trying to notify the clock" % self.ID
        rospy.wait_for_service('/clock_agent/update')
        try:
            notify = rospy.ServiceProxy('/clock_agent/update', update)
            r = notify(code)
            return r.ok
        except rospy.ServiceException, e:
            print "Service call failed: %s"%e

    ####interact thread will hang indefinitely if stop_clock or start_clock block indefinitely to wait for the clock service
    def stop_clock(self, code):
        print "im trying to stop the clock, current timestep"
        rospy.wait_for_service('/clock_agent/stop')
        print "after waiting for stop service"
        try:
            notify = rospy.ServiceProxy('/clock_agent/stop', update)
            r = notify(code)
            print "returned from clock stopping %d" % r.ok
            return r.ok
        except rospy.ServiceException, e:
            rospy.loginfo("Service call failed: %s", e)

    def start_clock(self, code):
        print "im trying to start the clock"
        rospy.wait_for_service('/clock_agent/start')
        print "after waiting for start service"
        try:
            notify = rospy.ServiceProxy('/clock_agent/start', update)
            r = notify(code)
            print "returned from clock starting %d" % r.ok
            return r.ok
        except rospy.ServiceException, e:
            print "Service call failed: %s"%e

    def lock_target(self, tg_id):
        print "im trying to lock %d" % tg_id
        rospy.wait_for_service('/env_agent/lock')
        try:
            lockit = rospy.ServiceProxy('/env_agent/lock', lock_target)
            r = lockit(tg_id)
            return r.ok
        except rospy.ServiceException, e:
            print "Service call failed: %s"%e

    def free_target(self, tg_id):
        print "im trying to free %d" % tg_id
        rospy.wait_for_service('/env_agent/unlock')
        try:
            unlockit = rospy.ServiceProxy('/env_agent/unlock', free_target)
            r = unlockit(tg_id)
            return r.ok
        except rospy.ServiceException, e:
            print "Service call failed: %s"%e

    def callback_help(self, data):
        try:
            with self.lock:
                self.callbacks += 1
            if data.timestep == self.time_step:
                if not data.ag_id == self.ID: 
                    data.ag_involved = list(data.ag_involved)
                    if self.toggle_request == 0:
                        rospy.loginfo("[CALLBACK_help] listening to all requests that I have not sent")
                        #print "[CALLBACK_help] type of ag_involved: %s" % str(type(data.ag_involved))
                        if not self.ID in data.ag_involved:
                            print "[CALLBACK_help %d]: %s" % (rospy.get_rostime().secs, str(data))
                            self.help_needed.put(data)
                        else:
                            print "[CALLBACK_help %d]: already helping %s" % (rospy.get_rostime().secs, str(data.ag_involved))

                    else: 
                        if self.toggle_request == 1:
                            rospy.loginfo("[CALLBACK_help] listening, k-closest, sent by %d", data.ag_id)
                            shouldI_listen = False
                            shouldI_listen = self.req_resp.amI_kclosest(self.ID, data.ag_id, self.all_targets, self.kcoverage)

                        elif self.toggle_request == 2:
                            rospy.loginfo("[CALLBACK_help] listening, k-furthest, sent by %d", data.ag_id)
                            shouldI_listen = False
                            shouldI_listen = self.req_resp.amI_kfurthest(self.ID, data.ag_id, self.all_targets, self.kcoverage)

                        elif self.toggle_request == 3:
                            rospy.loginfo("[CALLBACK_help] listening, k-random, sent by %d", data.ag_id)
                            shouldI_listen = False
                            shouldI_listen = self.req_resp.amI_krandom(self.ID, data.ag_id, self.kcoverage)
                        
                        if shouldI_listen:
                            if not self.ID in data.ag_involved:
                                print "[CALLBACK_help %d]: I should listen %s" % (rospy.get_rostime().secs, str(data))
                                self.help_needed.put(data)
                            else:
                                print "[CALLBACK_help %d]: I should listen and already helping %s" % (rospy.get_rostime().secs, str(data.ag_involved))
                        else:
                            rospy.loginfo("[CALLBACK_help] I should not listen.")
        except:
            print "[CALLBACK_help] Unexpected error: " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)

    #should leader sent notification of change to others?
    def callback_help_drop(self, data):
        try:
            with self.lock:
                self.callbacks += 1
            if data.timestep == self.time_step:
                if not data.ag_id == self.ID and data.intended_recipient == self.ID: 
                    print "[CALLBACK_help_drop %d]: %s" % (rospy.get_rostime().secs, str(data))
                    self.lock.acquire()
                    if self.followed_targets:
                        for i, x in enumerate(self.followed_targets):
                            if data.tg_id == x['id']:
                                if self.ID == x['ag_involved'][0]:
                                    print "[CALLBACK_help_drop %d]: I'm leader and I will shrink the list of agents for target: %d, involved: %s" % (rospy.get_rostime().secs, data.tg_id, str(self.followed_targets[i]['ag_involved']))
                                    if data.ag_id in x['ag_involved']:
                                        self.followed_targets[i]['ag_involved'].pop(self.followed_targets[i]['ag_involved'].index(data.ag_id))
                                        print "[CALLBACK_help_drop %d]: followed after the pop %s" % (rospy.get_rostime().secs, str(self.followed_targets[i]['ag_involved']))
                                    else:
                                        print "[CALLBACK_help_drop %d]: nothing to drop, for some reason" % rospy.get_rostime().secs
                                break
                            print "[CALLBACK_help_drop %d]: this was probably dropped, and I am not a leader anymore" % rospy.get_rostime().secs
                    if not self.followed_targets:
                        self.state = 0
                    self.lock.release()
        except:
            print "[CALLBACK_help_drop] Unexpected error: " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)

    def callback_help_assign(self, data):
        try:
            with self.lock:
                self.callbacks += 1
            if data.timestep == self.time_step:
                if not data.ag_id == self.ID: 
                    data.ag_involved = list(data.ag_involved)
                    if self.ID in data.ag_involved:
                        self.lock.acquire()
                        print "[CALLBACK_help_assign %d]: got assigned by %d" % (rospy.get_rostime().secs, data.ag_id)
                        already_on_it = False
                        print "[CALLBACK_help_assign %d]: tg: %d" % (rospy.get_rostime().secs, data.tg_id)
                        if self.followed_targets:
                            for x in self.followed_targets:
                                if x['id'] == data.tg_id:
                                    print "[CALLBACK_help_assign %d]: already on it, so won't add to list" % rospy.get_rostime().secs
                                    already_on_it = True
                                    break
                        if not already_on_it:
                            self.followed_targets.append({'category': 'target', 'id': data.tg_id, 'xpos': data.tg_xpos, 'ypos': data.tg_ypos, 
                        'velocity': -1, 'direction': -1, 'change_dir': -1, 'ag_involved': data.ag_involved, 'interest': data.interest})
                            print "[CALLBACK_help_assign %d]: assigned: %d" % (rospy.get_rostime().secs, data.tg_id)
                        self.lock.release()            
        except:
            print "[CALLBACK_help_assign] Unexpected error: " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)

    def callback_help_modify(self, data):
        try:
            with self.lock:
                self.callbacks += 1
            if data.timestep == self.time_step:
                data.ag_involved = list(data.ag_involved)
                #if not data.ag_id == self.ID and self.ID in data.ag_involved: 
                #if self.ID in data.ag_involved: 
                print "[CALLBACK_help_modify %d]: involved agents for target have been changed: %s" % (rospy.get_rostime().secs, str(data))
                self.lock.acquire()
                for x in self.followed_targets:
                    if x['id'] == data.tg_id and self.ID in data.intended_recipient:
                        if data.add_drop == 1:
                            if not data.ag_involved[0] in x['ag_involved']:
                                x['ag_involved'].append(data.ag_involved[0])

                                #print "[CALLBACK_help_modify %d]: add tg: %d, new followed: %s" % (rospy.get_rostime().secs, x['id'], str(x['ag_involved']))
                        elif data.add_drop == 0:
                            x['ag_involved'].pop(x['ag_involved'].index(data.ag_involved[0]))
                        elif data.add_drop == 2:
                            x['ag_involved'] = data.ag_involved
                        print "[CALLBACK_help_modify %d]: tg: %d, new followed: %s" % (rospy.get_rostime().secs, x['id'], str(x['ag_involved']))
                        break
                self.lock.release()
                    
        except:
            print "[CALLBACK_help_modify] Unexpected error: " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)

    def callback_help_reply(self, data):
        try:
            with self.lock:
                self.callbacks += 1
            if data.timestep == self.time_step and data.intended_recipient == self.ID:
                if not data.ag_id == self.ID: 
                    self.lock.acquire()
                    exists = False
                    for x in self.help_reply:
                        if x.ag_id == data.ag_id:
                            exists = True
                            break
                    if not exists:
                        print "[CALLBACK_help_reply %d]: %s, timestep: %d" % (rospy.get_rostime().secs, str(data), self.time_step)
                        self.help_reply.append(data)
                    self.lock.release()
        except:
            print "[CALLBACK_help_reply] Unexpected error: " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)
            
    def callback_help_replace(self, data):
        try:
            with self.lock:
                self.callbacks += 1
            if data.timestep == self.time_step:
                if not data.ag_id == self.ID: 
                    data.ag_involved = list(data.ag_involved)
                    if self.toggle_request == 0:
                        #print "[CALLBACK_help] type of ag_involved: %s" % str(type(data.ag_involved))
                        if not self.ID in data.ag_involved:
                            print "[CALLBACK_help_replace %d]: %s" % (rospy.get_rostime().secs, str(data))
                            self.help_replace_needed.put(data)
                    else:
                        if self.toggle_request == 1:
                            rospy.loginfo("[CALLBACK_help_replace] listening, k-closest, sent by %d", data.ag_id)
                            shouldI_listen = False
                            shouldI_listen = self.req_resp.amI_kclosest(self.ID, data.ag_id, self.all_targets, self.kcoverage)

                        elif self.toggle_request == 2:
                            rospy.loginfo("[CALLBACK_help_replace] listening, k-furthest, sent by %d", data.ag_id)
                            shouldI_listen = False
                            shouldI_listen = self.req_resp.amI_kfurthest(self.ID, data.ag_id, self.all_targets, self.kcoverage)

                        elif self.toggle_request == 3:
                            rospy.loginfo("[CALLBACK_help_replace] listening, k-random, sent by %d", data.ag_id)
                            shouldI_listen = False
                            shouldI_listen = self.req_resp.amI_krandom(self.ID, data.ag_id, self.kcoverage)
                        
                        if shouldI_listen:
                            if not self.ID in data.ag_involved:
                                print "[CALLBACK_help_replace %d]: I should listen %s" % (rospy.get_rostime().secs, str(data))
                                self.help_replace_needed.put(data)
                            else:
                                print "[CALLBACK_help_replace %d]: I should listen and already helping %s" % (rospy.get_rostime().secs, str(data.ag_involved))
                        else:
                            rospy.loginfo("[CALLBACK_help_replace] I should not listen.")
        except:
            print "[CALLBACK_help_replace] Unexpected error: " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)

    def callback_help_replace_answer(self, data):
        try:
            with self.lock:
                self.callbacks += 1
            if data.timestep == self.time_step and data.intended_recipient == self.ID:
                data.ag_involved = list(data.ag_involved)
                if not data.ag_id == self.ID: 
                    self.lock.acquire()
                    exists = False
                    for x in self.help_replace_reply:
                        if x.ag_id == data.ag_id:
                            exists = True
                            break
                    if not exists:
                        print "[CALLBACK_help_replace_answer %d]: %s" % (rospy.get_rostime().secs, str(data))
                        self.help_replace_reply.append(data)
                    self.lock.release()
        except:
            print "[CALLBACK_help_replace_answer] Unexpected error: " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)
    
    def callback_all_motion(self, data): #1 thread per topic per publisher. Only the environment publishes on this topic
        #careful, here you are only checking the timestep of one of them
        try:
            if data.timestep[0] == self.time_step:
                self.lock.acquire()
                self.all_targets = data
                if self.followed_targets:
                    for x in self.followed_targets:
                        i = data.id.index(x['id'])
                        x['xpos'] = data.xpos[i]
                        x['ypos'] = data.ypos[i]
                        x['direction'] = data.direction[i]
                self.lock.release()
        except:
            print "[CALLBACK_all_motion] Unexpected error: " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)

    def callback_info(self, data):
        try:
            with self.lock:
                self.callbacks += 1
            if data.timestep == self.time_step:
                if not data.ag_id == self.ID:
                    #print "CALLBACK_info: gotten request for info on some target %s" % str(data)
                    self.lock.acquire()
                    if self.followed_targets:
                        for x in self.followed_targets:
                            if data.tg_id == x['id']:
                                print "[CALLBACK_info %d]: element in followed targets %d %s" % (rospy.get_rostime().secs, x['id'], str(x['ag_involved']))
                                if self.ID == x['ag_involved'][0]: #the leader is always the first element of the list
                                    print "[CALLBACK_info %d]: I am the leader of %s: " % (rospy.get_rostime().secs, str(data))
                                    self.info_answer.tg_id = data.tg_id
                                    self.info_answer.leader_id = self.ID
                                    self.info_answer.timestep = rospy.get_rostime().secs
                                    self.info_answer.ag_involved = x['ag_involved']
                                    self.info_answer.intended_recipient = data.ag_id
                                    self.publish_info_answer.publish(self.info_answer)
                                    self.published_messages += 1
                            
                                    if len(x['ag_involved']) < self.kcoverage:
                                        #if the agent is able to help, assign him
                                        print "[CALLBACK_info %d]: kcoverage is not achieved" % rospy.get_rostime().secs
                                        if data.willingness >= 0:
                                            print "[CALLBACK_info %d]: since willingness positive, assign the agent tg %d, inv %s" % (rospy.get_rostime().secs, data.ag_id, x['ag_involved'])
                                            print x['ag_involved']
                                            if not data.ag_id in x['ag_involved']:
                                                x['ag_involved'].append(data.ag_id)

                                            self.help_assign.tg_id = x['id']
                                            self.help_assign.tg_xpos = x['xpos']
                                            self.help_assign.tg_ypos = x['ypos']
                                            self.help_assign.timestep = rospy.get_rostime().secs
                                            self.help_assign.ag_involved = x['ag_involved']
                                            self.help_assign.interest = x['interest']
                                            self.publish_help_assign.publish(self.help_assign)
                                            self.published_messages += 1
                                    break
                    self.lock.release()
        except:
            print "[CALLBACK_info] Unexpected error: " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)

    #This most likely won't work if I get answers from two leaders. That is the latest assignment will be taken.
    def callback_info_answer(self, data):
        try:
            with self.lock:
                self.callbacks += 1
            if data.timestep == self.time_step:
                if not data.ag_id == self.ID and data.intended_recipient == self.ID:
                    data.ag_involved = list(data.ag_involved)
                    print "[CALLBACK_info_answer %d]: gotten some data %s" % (rospy.get_rostime().secs, str(data))
                    self.lock.acquire()
                    self.reply = data
                    self.info_reply = True
                    self.lock.release()
        except:
            print "[CALLBACK_info_answer] Unexpected error: " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)
            print "[CALLBACK_info_answer] Unexpected error: %s" % str(data)

    def alive_empty_callback(self, data):
        pass

if __name__ == '__main__':
    try:
        instance = Agent(1, 0)
    except rospy.ROSInterruptException:
        pass
