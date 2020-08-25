import subprocess
import os
from numpy import mean

events = {}
durations = {}

with open('data/agg_per_epoch.log') as fp:
    line = fp.readline()
    while line: 
        (model, dataset, cores, memory, batch, log_id, epoch, event, counts, duration) = line.split(",")
        name = "%s_%s_%s_%s_%s" % (model, dataset, cores, memory, batch)
        if name not in events:
            events[name] = {}
            durations[name] = int(duration)
        if event not in events[name]:
            events[name][event] = []
        events[name][event].append(float(counts))
        line = fp.readline()

for name in events:
    duration = durations[name]
    for event in events[name]:
        avg_counts = mean(events[name][event])
        print("%s,%s,%f,%d" % (name.replace("_", ","), event, avg_counts, duration))
