#!/usr/bin/env python
import rospy
from gitagent_2.msg import *
from std_msgs.msg import String
import random
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation
from gitagent_2.srv import *
import numpy as np
from random_walk_plg import rw_plugins
from threading import Lock
import time
import sys, os
from git_logger import gitlogger

class Environment:
    def __init__(self, size, init_target_dist, no_targets):
        self.base_path = os.path.expanduser("~/catkin_ws")
        self.path = os.path.expanduser("~/catkin_ws/src/gitagent_2")
        print rospy.get_param('/seed')
        np.random.seed(int(rospy.get_param('/seed')))
        random.seed(int(rospy.get_param('/seed')))
        rospy.init_node('environment', anonymous=True)
        self.objects_in_space = [] #can be handled by multiple threads --> used self.lock
        self.space2D, self.ax = plt.subplots()
        self.ln_points_target, = self.ax.plot([],[], '-xr', linestyle='None')
        self.ln_points_agent, = self.ax.plot([],[], '-ob', linestyle='None')
        self.text = plt.text(0, 101, str(0))

        self.size = size
        self.start_time = rospy.get_rostime().secs
        self.simulation_duration = rospy.get_param('environment/sim_duration')
        self.no_targets = int(rospy.get_param('environment/no_targets'))
        self.init_target_dist = init_target_dist

        self.lock = Lock()

        self.every_xstep = int(rospy.get_param('environment/frequency'))
        self.no_appearance = 2
        self.update_toggle = int(rospy.get_param('environment/tg_update'))

        self.gitlog = gitlogger.GitLogger("pignatta", self.simulation_duration)

        while rospy.Time.now().secs == 0:
            pass

        self.start_time = rospy.get_rostime().secs
        self.time_step = rospy.get_rostime().secs
        print "time gotten"
        rospy.Subscriber('/environment/motion_values', motion_values, self.callback_motion)
        self.alive = rospy.Subscriber('/clock_alive', String, self.alive_empty_callback)
        s1 = rospy.Service('/env_agent/lock', lock_target, self.request_target_lock)
        s2 = rospy.Service('/env_agent/unlock', free_target, self.free_target_lock)

        self.publish_motion = rospy.Publisher('/environment/all_motion_values', all_motion_values, queue_size=10)

        self.motion_msg = all_motion_values()

        self.rw_method = getattr(rw_plugins, rospy.get_param('environment/random_walk_method'))

        self.target_lock = [] # lists of [id, busy/free]

        print "before generate"
        self.generate_space(self.no_targets)
        print "after generate"
        self.log_all_motion_data = []
        ani = animation.FuncAnimation(self.space2D, self.run_env, self.new_data)
        plt.grid()
        plt.show()

    def generate_space(self, no_targets):
        #initialize targets
        #randomization_method = getattr(random, init_target_dist)
        self.lock.acquire()
        for i in range(no_targets):
            category = "target"
            id = i + 1
            self.target_lock.append([id, 0])
            xpos = np.random.uniform(0, 100)
            ypos = np.random.uniform(0, 100)
            vel = 1.5
            direc = 0
            change_dir = 0.2
            interest = random.choice([0.3, 0.6, 0.9])
            
            self.objects_in_space.append({'type': category, 'id': id, 'xpos': xpos, 'ypos': ypos, 'velocity': vel, 
            'direction': direc, 'change_dir': change_dir, 'interest': interest})
        self.lock.release()
        print self.objects_in_space
        #setup 2D area
        self.ax.set_title('Catch me if you can')
        self.ax.set_xlabel('x-axis')
        self.ax.set_ylabel('y-axis')
        self.ax.set_xlim(0, self.size[0])
        self.ax.set_ylim(0, self.size[1]) 

        self.ln_points_target.set_xdata(np.array([x['xpos'] for x in self.objects_in_space if x['type'] == 'target' ]))
        self.ln_points_target.set_ydata(np.array([x['ypos'] for x in self.objects_in_space if x['type'] == 'target' ]))
        return self.ln_points_target,

    def new_data(self):
        #print "i am here"
        yield [[x['xpos'] for x in self.objects_in_space], [x['ypos'] for x in self.objects_in_space]]   
        #pass    
        
    def update_target_position(self):
        if self.update_toggle > 0:
            print "update_target_position: 1"
            print self.objects_in_space
            for x in self.objects_in_space:
                if x['type'] == 'target':
                    motion = self.rw_method().update_tg([x['xpos'], x['ypos'], x['velocity'], x['direction'], x['change_dir']])
                    self.lock.acquire()
                    x['xpos'] = motion[0]
                    x['ypos'] = motion[1]
                    x['direction'] = motion[3]
                    self.lock.release()
            print "update_target_position: 2"
            print self.objects_in_space
        else:
            print "targets don't update"

    def run_env(self, data):
        print "Simulated time is: %d" % rospy.get_rostime().secs
        print "Simulated time is: %d" % self.time_step
        self.text.set_text(str(self.time_step))

        self.lock.acquire()
        self.log_all_motion_data.append([[x['xpos'] for x in self.objects_in_space], [x['ypos'] for x in self.objects_in_space], [x['type'] for x in self.objects_in_space]])
        self.lock.release()

        if rospy.is_shutdown() or rospy.get_rostime().secs >= self.start_time + self.simulation_duration - 1:
            print "done"
            with open(self.base_path+"/output_"+str(-1), 'w') as f:
                for x in self.log_all_motion_data:
                    for y in x:
                        f.write(str(y) + "\n")     

            self.gitlog.write2file(-1)
            plt.close()

        self.update_target_position()

        if self.objects_in_space:
            tg = [[x['id'], x['xpos'], x['ypos']] for x in self.objects_in_space if not x['type'] == 'agent' ]
            ag = [[x['id'], x['xpos'], x['ypos']] for x in self.objects_in_space if x['type'] == 'agent' ]
            print "I SHOULD BE LOGGING"
        else:
            tg = []
            ag = []
        self.gitlog.log_env(tg, ag)

        self.ln_points_agent.set_xdata(np.array([x['xpos'] for x in self.objects_in_space if x['type'] == 'agent' ]))
        self.ln_points_agent.set_ydata(np.array([x['ypos'] for x in self.objects_in_space if x['type'] == 'agent']))

        self.ln_points_target.set_xdata(np.array([x['xpos'] for x in self.objects_in_space if x['type'] == 'target' ]))
        self.ln_points_target.set_ydata(np.array([x['ypos'] for x in self.objects_in_space if x['type'] == 'target']))

        code = self.notify_clock(-1)

        if self.objects_in_space:
            self.motion_msg.xpos = [x['xpos'] for x in self.objects_in_space]
            self.motion_msg.ypos = [x['ypos'] for x in self.objects_in_space]
            self.motion_msg.velocity = [x['velocity'] for x in self.objects_in_space]
            self.motion_msg.direction = [x['direction'] for x in self.objects_in_space]
            self.motion_msg.omega = [x['change_dir'] for x in self.objects_in_space]
            self.motion_msg.category = [x['type'] for x in self.objects_in_space]
            self.motion_msg.id = [x['id'] for x in self.objects_in_space]
            self.motion_msg.timestep = [self.time_step for x in self.objects_in_space]
            self.motion_msg.interest = [x['interest'] for x in self.objects_in_space]

            print self.motion_msg

            while self.time_step == rospy.get_rostime().secs and rospy.get_rostime().secs < self.start_time + self.simulation_duration - 1:
                self.publish_motion.publish(self.motion_msg)
        
        self.time_step = rospy.get_rostime().secs

        self.generate_new_targets()

        return self.ln_points_agent,

    def callback_motion(self, data):
        print data
        found = False

        for x in self.objects_in_space:
            if x['type'] == 'agent':
                if x['id'] == data.id:
                    self.lock.acquire()
                    x['xpos'] = data.xpos
                    x['ypos'] = data.ypos
                    x['velocity'] = data.velocity
                    x['direction'] = data.direction
                    x['change_dir'] = data.omega
                    self.lock.release()
                    found = True
                    break
        if not found:
            self.lock.acquire()
            self.objects_in_space.append({'type': 'agent', 'id': data.id, 'xpos': data.xpos, 'ypos': data.ypos, 
            'velocity': data.velocity, 'direction': data.direction, 'change_dir': data.omega, 'interest': 0.0})
            self.lock.release()
            print "added"

    def notify_clock(self, code):
        print "im trying to notify the clock"
        rospy.wait_for_service('/clock_agent/update')
        try:
            print "before sending"
            notify = rospy.ServiceProxy('/clock_agent/update', update)
            print "after sending"
            r = notify(code)
            return r.ok
        except rospy.ServiceException, e:
            print "Service call failed: %s"%e

    def request_target_lock(self, request):
        try:
            self.lock.acquire()
            print "target lock array: %s, tg id: %d " % (self.target_lock, request.tg_id)

            if self.target_lock:
                if self.target_lock[request.tg_id-1][1] == 0:
                    self.target_lock[request.tg_id-1][1] = 1
                    print "target lock: %s, tg_id %d" % (str(self.target_lock), request.tg_id)
                    state = 1
                else:
                    print "target lock: %s, tg_id %d" % (str(self.target_lock), request.tg_id)
                    state = 0
            else:
                print "target lock: %s, tg_id %d. it seems that it's not initialized" % (str(self.target_lock), request.tg_id)
                state = 0
            self.lock.release()
            return state
        except:
            print "[request_target_lock] Unexpected error: " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)


    def free_target_lock(self, request):
        self.lock.acquire()
        self.target_lock[request.tg_id-1][1] = 0
        print "target lock: %s, tg_id %d" % (str(self.target_lock), request.tg_id)
        self.lock.release()
        return 1

    #NOT fully threadsafe
    def generate_new_targets(self):     
        timepoint = rospy.get_rostime().secs
        if self.every_xstep > 0:
            if timepoint % self.every_xstep == 0 and timepoint > 0:
                print "Time to get some new targets in"
                for i in range(self.no_appearance):
                    category = "target"
                    id = self.no_targets + i + 1
                    xpos = np.random.uniform(0, 100)
                    ypos = np.random.uniform(0, 100)
                    vel = 1.9
                    direc = 0
                    change_dir = 0.2
                    interest = random.choice([0.3, 0.6, 0.9])

                    self.lock.acquire()
                    self.target_lock.append([id, 0])
                    self.objects_in_space.append({'type': category, 'id': id, 'xpos': xpos, 'ypos': ypos, 'velocity': vel, 
                    'direction': direc, 'change_dir': change_dir, 'interest': interest})
                    self.lock.release()
                self.lock.acquire()
                self.no_targets = self.no_targets + self.no_appearance
                self.lock.release()

    def alive_empty_callback(self, data):
        pass

if __name__ == '__main__':
    try:
        init_target_dist = 0
        no_targets = 10

        no_agents = 10 #CAREFUL HARDCODED!!!

        size = [100,100] #size of area of interest in a 2D space
        instance = Environment(size, init_target_dist, no_targets)

        current = instance.alive.get_num_connections()
        print "remaining: %d" % current
        while not instance.alive.get_num_connections() < 2:
            if instance.alive.get_num_connections() < current:
                print "will exit after all agent nodes are unsubscribed, remaining: %d" % instance.alive.get_num_connections()
                current = instance.alive.get_num_connections()
            pass

        instance.alive.unregister()
    except rospy.ROSInterruptException:
        pass
