#!/usr/bin/env python
import rospy
import time
from gitagent_2.msg import *
from std_msgs.msg import String
from rosgraph_msgs.msg import Clock
from threading import Lock, Thread
from gitagent_2.srv import update

class Clock_Server:
    def __init__(self, time_step, no_agents):
        rospy.init_node('clock_agent', anonymous=True)
        self.pub = rospy.Publisher('/clock', Clock, queue_size=10)
        self.alive = rospy.Publisher('/clock_alive', String, queue_size=10)

        s1 = rospy.Service('/clock_agent/update', update, self.handle_update)
        s2 = rospy.Service('/clock_agent/stop', update, self.handle_stop)
        s3 = rospy.Service('/clock_agent/start', update, self.handle_start)

        self.step = rospy.Time.now()
        self.msg = Clock()

        self.no_agents = int(rospy.get_param('clock_agent/no_agents')) + 1
        self.agents_step_update = 0 #handled by multiple threads, self.lock used
        self.lock = Lock()
        self.simulation_duration = rospy.get_param('clock_agent/sim_duration')
        self.time_step = time_step
        self.blocked = 0 #handled by multiple threads, self.lock used

    def handle_update(self, request):
        print "Agent ID: %d" % request.id
        self.lock.acquire()
        self.agents_step_update += 1
        print "agents updated: %d" % self.agents_step_update
        self.lock.release()
        return 1

    def handle_start(self, request):
        print "Requested start, agent ID: %d, timestep: %d" % (request.id, rospy.get_rostime().secs)
        self.lock.acquire()
        self.blocked -= 1
        print "blocked: %d" % self.blocked
        self.lock.release()
        return 1

    def handle_stop(self, request):
        print "Requested stop, agent ID: %d, timestep: %d" % (request.id, rospy.get_rostime().secs)
        self.lock.acquire()
        self.blocked += 1
        print "blocked: %d" % self.blocked
        self.lock.release()
        return 1

    def simulation_clock(self):
        rospy.loginfo("Entered in the simulation_clock function")
        try:
            while not rospy.is_shutdown() and self.step.secs < self.simulation_duration:
                while self.blocked > 0:
                    #print "the clock is blocked"
                    pass

                self.step.secs += 1
                self.msg.clock = self.step
                
                self.pub.publish(self.msg)
                
                print "Simulated time is: %d" % rospy.get_rostime().secs
                #Wait for all agents to update themselves in one step. to be added env node to this.
                while self.agents_step_update < self.no_agents:
                    self.pub.publish(self.msg)
                    #print "it's stuck here"
                
                #time.sleep(self.time_step)
                self.lock.acquire()
                self.agents_step_update = 0
                self.lock.release()
                print "Going for next step"
                #time.sleep(1)

            print "Clock exiting when all subscribers unsubscribe from clock_alive"
            current = self.alive.get_num_connections()
            while not self.alive.get_num_connections() < 1:
                if self.alive.get_num_connections() < current:
                    print "will exit after all nodes are unsubscribed, remaining: %d" % self.alive.get_num_connections()
                    current = self.alive.get_num_connections()
                pass
        except (rospy.ROSException, rospy.ROSInitException), e:
            rospy.logerr("Something went haywire %s", str(e))
if __name__ == '__main__':
    try:
        #simulation = 0 -> wall-clock is used, simulation = 1 -> my own time is used
        time_step = 1 #seconds 
        no_agents = 10

        clock_server = Clock_Server(time_step, no_agents)
        rospy.loginfo("CLOCK INITIALIZED")
        clock_server.simulation_clock()
    except rospy.ROSInterruptException:
        pass