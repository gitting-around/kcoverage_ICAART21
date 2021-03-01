#!/usr/bin/env python
import sys
import rospy
import rw_base
import math
import numpy as np
import random
import pdb
import copy

class RW_Pasta(rw_base.Random_Walk):
    def __init__(self):
        rw_base.Random_Walk.__init__(self)

    def update_tg(self, motion):
        return motion

    def update(self, motion):
        #self.xpos += 1
        return motion

    def move_toward_sensible(self, motion, targets):
        pass

    def move_toward(self, motion, targets):
        return motion

    def check_for_tg(self, motion, tg_followed, tg_dropped):
        pass

    def stop_follow(self, motion, tg_followed):
        pass

class RW_Pignatta(rw_base.Random_Walk):
    def __init__(self):
        rw_base.Random_Walk.__init__(self)
        self.visib_range = 30
        self.internal_range = 25
        self.area = [100, 100]
        self.old_tg_pos = []
        np.seterr(all="raise")

    def update_tg(self, motion):
        x = motion[0] + motion[2] * math.cos(motion[3])
        y = motion[1] + motion[2] * math.sin(motion[3])
        setdir = False
        if x > self.area[0]:
            motion[0] = self.area[0]
            motion[3] = motion[3] + math.radians(90)
            setdir = True
        elif x < 0:
            motion[0] = 0.0
            motion[3] = motion[3] + math.radians(90)
            setdir = True

        if y > self.area[1]:
            motion[1] = self.area[1]
            if not setdir:
                motion[3] = motion[3] + math.radians(90)
        elif y < 0:
            motion[1] = 0.0
            if not setdir:
                motion[3] = motion[3] + math.radians(90)

        if not x > self.area[0] and not y > self.area[1] and not x < 0 and not y < 0:
            motion[0] = motion[0] + motion[2] * math.cos(motion[3])
            motion[1] = motion[1] + motion[2] * math.sin(motion[3])
            motion[3] = motion[3] + motion[4] * random.random()
        return motion

    def update(self, motion):
        x = motion[0] + motion[2] * math.cos(motion[3])
        y = motion[1] + motion[2] * math.sin(motion[3])
        setdir = False
        if x > self.area[0]:
            motion[0] = self.area[0]
            motion[3] = motion[3] + math.radians(90)
            setdir = True
        elif x < 0:
            motion[0] = 0.0
            motion[3] = motion[3] + math.radians(90)
            setdir = True

        if y > self.area[1]:
            motion[1] = self.area[1]
            if not setdir:
                motion[3] = motion[3] + math.radians(90)
        elif y < 0:
            motion[1] = 0.0
            if not setdir:
                motion[3] = motion[3] + math.radians(90)

        if not x > self.area[0] and not y > self.area[1] and not x < 0 and not y < 0:
            motion[0] = motion[0] + motion[2] * math.cos(motion[3])
            motion[1] = motion[1] + motion[2] * math.sin(motion[3])
            motion[3] = motion[3] + 0.1*np.random.normal()
        return motion

    def move_toward_sensible(self, motion, targets):
        print "[move toward] my motion: %s" % str(motion)
        target_interest = np.array([x['interest'] for x in targets])
        #control
        #pdb.set_trace()
        tgx = np.array([x['xpos'] for x in targets])
        tgy = np.array([x['ypos'] for x in targets])
        print "[move toward] tgx: %s" % str(tgx)
        print "[move toward] tgy: %s" % str(tgy)


        p = np.array([motion[0] for x in range(len(target_interest))])
        y = np.array([motion[1] for x in range(len(target_interest))])
        print "[move toward] x: %s" % str(p)
        print "[move toward] y: %s" % str(y)
        deltax = tgx - p
        deltay = tgy - y
        print "[move toward] deltax: %s" % str(deltax)
        print "[move toward] deltay: %s" % str(deltay)

        #dx = np.sum(np.multiply(deltax, target_interest))
        #dy = np.sum(np.multiply(deltay, target_interest))
        dx = np.sum(np.multiply(deltax, target_interest))/np.sum(target_interest)
        dy = np.sum(np.multiply(deltay, target_interest))/np.sum(target_interest)
        print "[move toward] dx: %s" % str(dx)
        print "[move toward] dy: %s" % str(dy)

        velocity = np.sqrt(dx**2 + dy**2)
        if velocity < 0.1:
            print "velocity is low"
            velocity = 0.0

        theta_desired = math.atan2(dy, dx)
        e = theta_desired - motion[3]
        kp = 1
        omega = kp * math.atan2(math.sin(e), math.cos(e)) 
        #saturate values
        v_real = min(velocity, motion[2])
        omega_real = min(max(omega, -motion[4]), motion[4])
        #omega_real = omega
        print "[move toward] velocity, thetad, omega: %s" % str([velocity, theta_desired, omega])
        #update
        motion[0] = min(max(motion[0] + v_real * math.cos(motion[3]), 0), self.area[0])
        motion[1] = min(max(motion[1] + v_real * math.sin(motion[3]), 0), self.area[1])
        motion[3] = motion[3] + omega_real
        print "[move toward] my motion updated: %s" % str(motion)
        return motion

    def move_toward(self, motion, targets):
        #calculate direction based on the targets
        try:
            if targets:
                target_dirs = [x['direction'] for x in targets]
                target_interest = [x['interest'] for x in targets]
                print "[move toward] target_dirs: %s" % str(target_dirs)
                print "[move toward] target_interest: %s" % str(target_interest)
                print "[move toward] matmul: %s" % str(np.matmul(target_dirs, target_interest))
                motion[3] = np.matmul(target_dirs, target_interest)/len(target_dirs)
                motion[0] = motion[0] + motion[2] * math.cos(motion[3])
                motion[1] = motion[1] + motion[2] * math.sin(motion[3])
                if motion[0] > self.area[0]:
                    motion[0] = self.area[0]
                elif motion[0] < 0:
                    motion[0] = 0.0
                if motion[1] > self.area[1]:
                    motion[1] = self.area[1]
                elif motion[1] < 0:
                    motion[1] = 0.0
            else:
                print "[move_toward] somehow no targets: %s" % str(targets)
            return motion
        except:
            print "[move_toward] Unexpected error: " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)

    def check_for_tg(self, my_motion, tg_data, tg_followed, tg_dropped):
        try:
            spotted = []
            i = 0
            print "[CHECK FOR TG]: im checking for new targets"
            ##SYNC## data below is not checked for time, i.e., the agent could in principle be calculating the info of the previous timestep.
            if tg_data:
                for x in tg_data.category:
                    if x == 'target':
                        dropped = False
                        followed = False
                        #print "check_for_tg: followed %s" % str(tg_followed)
                        #print "check_for_tg: dropped %s" % str(tg_dropped)

                        if tg_followed:
                            for k in tg_followed:
                                if k['id'] == tg_data.id[i]:
                                    followed = True
                                    break
                                    
                        if tg_dropped:
                            for k in tg_dropped:
                                if k['id'] == tg_data.id[i]:
                                    dropped = True
                                    break

                        if not followed and not dropped:
                            print "[CHECK FOR TG]: my location %f %f, target location %f %f, distance %s" % (my_motion[0], my_motion[1], tg_data.xpos[i], 
                            tg_data.ypos[i], math.sqrt((my_motion[0] - tg_data.xpos[i])**2 + (my_motion[1] - tg_data.ypos[i])**2))
                            if math.sqrt((my_motion[0] - tg_data.xpos[i])**2 + (my_motion[1] - tg_data.ypos[i])**2) < self.visib_range:
                                spotted.append({'category': 'target', 'id': tg_data.id[i], 'xpos': tg_data.xpos[i], 'ypos': tg_data.ypos[i], 
                'velocity': tg_data.velocity[i], 'direction': tg_data.direction[i], 'change_dir': tg_data.omega[i], 'interest': tg_data.interest[i]})
                                print "[CHECK FOR TG]: I spotted new target %s" % str(x)
                        #else:
                        #    if math.sqrt((my_motion[0] - tg_data.xpos[i])**2 + (my_motion[1] - tg_data.ypos[i])**2) < visib_range:
                        #        print "I spotted new target"
                        #        spotted.append({'category': 'target', 'id': tg_data.id[i], 'xpos': tg_data.xpos[i], 'ypos': tg_data.ypos[i], 'velocity': tg_data.velocity[i], 'direction': tg_data.direction[i], 'change_dir': tg_data.omega[i]})
                    i += 1

            return spotted
        except:
            print "[check_for_tg] Unexpected error: " + str(sys.exc_info()) + ". Line nr: " + str(sys.exc_info()[2].tb_lineno)

    def tg_moving_away(self, my_motion, tg_followed):
        #check whether any target is on the internal boundary
        away = 0
        if tg_followed:
            for x in tg_followed:
                prev_distance = self.area[0] * self.area[1]
                distance = math.sqrt((my_motion[0] - x['xpos'])**2 + (my_motion[1] - x['ypos'])**2)
                
                if self.old_tg_pos:
                    for y in self.old_tg_pos:
                        if x['id'] == y['id']:
                            prev_distance = math.sqrt((my_motion[0] - y['xpos'])**2 + (my_motion[1] - y['ypos'])**2)
                            print "[CHECK FOR TG]: current tg: %s, prev tg: %s" % (str([x['id'], x['xpos'], x['ypos']]), str([y['xpos'], y['ypos']]))
                            break

                print "[CHECK FOR TG]: id: %d, prev distance: %f, current distance: %f" % (x['id'], prev_distance, distance)
                print "[CHECK FOR TG]: my motion: %s" % (str(my_motion))

                if  self.internal_range < distance < self.visib_range and distance > prev_distance:
                    print "[CHECK FOR TG]: target moving away %s, distance %f" % (str(x), distance)
                    away = x
                    break # reconsider asking for help for other targets, if by removing one there is no improvement
                
            self.old_tg_pos = copy.deepcopy(tg_followed)
        return away

    def stop_follow(self, my_motion, tg_followed):
        print "stop following?: %s" % tg_followed
        dropped = []
        if tg_followed:
            for x in tg_followed:
                if math.sqrt((my_motion[0] - x['xpos'])**2 + (my_motion[1] - x['ypos'])**2) > self.visib_range:
                    dropped.append(x)
                    tg_followed.pop(tg_followed.index(x))
                    print "stop following - OUT OF RANGE: %s" % tg_followed
        return tg_followed, dropped
