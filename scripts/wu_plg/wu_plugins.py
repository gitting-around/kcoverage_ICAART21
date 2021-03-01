#!/usr/bin/env python
import rospy
import wu_base
import random
import numpy as np

class WU_Pasta(wu_base.WU):
    def __init__(self):
        wu_base.WU.__init__(self)
        self.min = 0.3

    def willingness(self, willingness, factors): #Factors are given as [[f1, w1], [f2, w2], ...]
        willingness = random.random()
        return willingness

    def utility(self, task):
        utility = random.random()
        return utility

class WU_Pignatta(wu_base.WU):
    def __init__(self):
        wu_base.WU.__init__(self)
        self.min = 0.3

    def willingness(self, willingness, factors): #Factors are given as [[f1, w1], [f2, w2], ...]
        weights = np.zeros(len(factors))
        #print "willingness: %f" % willingness
        #print "factors: %s" % str(factors) 

        for x in factors:
            if x[1] == 1: #this is a necessary factor
                if x[0] > self.min:
                    weights[factors.index(x)] = 1 / float(len(factors))
                else:
                    weights = np.zeros(len(factors))
                    weights[factors.index(x)] = - 1 - willingness
                    break
            else:
                if x[0] > self.min:
                    weights[factors.index(x)] = 1 / float(len(factors))
                else:
                    weights[factors.index(x)] = - 1 / float(len(factors))

        #print "weights: %s" % str(weights)
        #print "matmul: %s" % str(np.matmul(weights, [x[0] for x in factors]))
        willingness = willingness + np.matmul(weights, [x[0] for x in factors])

        #saturate between -1 and 1
        if willingness > 1:
            willingness = 1.0
        elif willingness < -1:
            willingness = -1.0

        return willingness

    def utility(self, task):
        utility = task['interest']
        return utility