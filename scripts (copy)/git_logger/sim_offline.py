#!/usr/bin/env python
import sys
import math
import plotly
import plotly.offline as py
import plotly.graph_objs as go
from plotly.tools import make_subplots
py.init_notebook_mode(connected=False)
import numpy as np

def plot_fancy(agid, fname):
    with open(fname, "r") as f:
        lines = f.readlines()
        approach = lines[0]
        duration = int(lines[1])

        temp = lines[2].split("|")

        followed = []
        for x in temp:
            t = []
            if len(x.split("#")) > 1:
                for y in filter(None, x.split("#")):
                    t += [float(i) for i in y.split(" ")]
            followed.append(t)
        followed = followed[:-1]
        maxtgs = len(max(followed,key=len))/3
        print maxtgs
        print max(followed,key=len)
        for i, x in enumerate(followed):
            if len(x) < maxtgs*3:
                while len(followed[i]) < maxtgs*3:
                    followed[i] += [-1,-1,-1]
           
        for x in followed:
            print x

        lines[12] = lines[12].strip("\n")
        temp = filter(None, lines[12].split("|"))
        
        myloc = []
        for x in temp:
            myloc.append([float(i) for i in filter(None, x.split(" "))])

    num_steps = duration-1
    visibility = [False for x in range(duration-1)]
    visibility[0] = True
    agent_trace = [go.Scatter(x=[myloc[i][0]], y=[myloc[i][1]], hovertext=['id: '+str(agid)+'<br>w: '], hoverinfo='text', visible=visibility[i], marker={'color': 'blue', 'symbol':'diamond'}) for i in range(duration-1)]

    followed_trace = []
    for x in range(maxtgs): #consider three colums at a time with data, not necessarily the same target, however it is possible to tell them apart from the id.
        followed_trace += [go.Scatter(x=[followed[i][3*x+1]], y=[followed[i][3*x+2]],mode='markers+text', text=['id:'+str(int(followed[i][3*x]))], 
        textposition='bottom center', visible=visibility[i], marker={'color': 'green', 'symbol':'circle'}) for i in range(duration-1)]

    fig = go.Figure(data=agent_trace+followed_trace)
    #fig = make_subplots(1, 2)
    #fig.append_trace(agent_trace+followed_trace,1,1)

    steps = []
    for i in range(num_steps):
        # Hide all traces
        step = dict(
            method = 'restyle',  
            args = ['visible', [False] * len(fig.data)],
        )
        # Enable the two traces we want to see
        step['args'][1][i] = True
        for x in range(maxtgs):
            step['args'][1][i+num_steps*(x+1)] = True
        
        # Add step to step list
        steps.append(step)

    sliders = [dict(
        steps = steps,
    )]

    fig.layout.sliders = sliders

    # plotly.offline.plot(fig, filename='manipulate.html')
    py.plot(fig)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: ./sim_offline agentID"
        sys.exit()

    fname = "gitlogger_"+sys.argv[1]

    xloc = [1,2,3]
    yloc = [2,3,4]
    willingness = [0.8, 0.9, -1.0]

    tg1x = [1,1,1]
    tg1y = [1,1,1]
    ids = [str(1), str(1), str(-1)]

    tg2x = [1,1,1]
    tg2y = [4,4,4]

    plot_fancy(sys.argv[1], fname)
"""     num_steps = 3
    trace_list1 = [
        go.Scatter(x=[xloc[0]], y=[yloc[0]], hovertext=['w: '+str(willingness[0])+'<br>groove'], hoverinfo='text', visible=True, marker={'color': 'red', 'symbol':'diamond'}),
        go.Scatter(x=[xloc[1]], y=[yloc[1]], visible=False, line={'color': 'red'}),
        go.Scatter(x=[xloc[2]], y=[yloc[2]], visible=False, line={'color': 'red'})
    ]

    trace_list2 = [
        go.Scatter(x=[tg1x[0]], y=[tg1y[0]], name=ids[0], visible=True, line={'color': 'blue'}),
        go.Scatter(x=[tg1x[1]], y=[tg1y[1]], name=ids[1], visible=False, line={'color': 'blue'}),
        go.Scatter(x=[tg1x[2]], y=[tg1y[2]], name=ids[2], visible=False, line={'color': 'grey'})
    ]

    fig = go.Figure(data=trace_list1+trace_list2)

    steps = []
    for i in range(num_steps):
        # Hide all traces
        step = dict(
            method = 'restyle',  
            args = ['visible', [False] * len(fig.data)],
        )
        # Enable the two traces we want to see
        step['args'][1][i] = True
        step['args'][1][i+num_steps] = True
        
        # Add step to step list
        steps.append(step)

    sliders = [dict(
        steps = steps,
    )]

    fig.layout.sliders = sliders

    # plotly.offline.plot(fig, filename='manipulate.html')
    py.plot(fig) """

