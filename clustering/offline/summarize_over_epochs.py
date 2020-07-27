import subprocess
import os
from numpy import mean

events = {}
total = 0

with open('lenet_bind_over_epochs.csv') as fp:
    line = fp.readline()
    while line:
        sline = line.split(",")
        model = sline[1]
        dataset = [2]
        epoch = sline[3]
        event = sline[4]
        counts = int(sline[5].strip())
        if phase not in events:
            events[phase] = {}
        if event not in events[phase]:
            events[phase][event] = []
        events[phase][event].append(counts)
        line = fp.readline()

for phase in events:
    for event in events[phase]:
        counts = events[phase][event]
        avg_counts = mean(counts)
        print("lenet,fashion-mnist,%s,%s,%f" % (phase, event, avg_counts))

