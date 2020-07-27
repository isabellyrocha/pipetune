import subprocess
import os
from numpy import mean

events = {}
durations = {}

with open('perf_filtered.log') as fp:
    line = fp.readline()
    while line:
        (model, dataset, cores, memory, batch, log_id, epoch, duration, event, counts) = line.split(",")
        name = "%s_%s_%s_%s_%s_%s_%s" % (model, dataset, cores, memory, batch, log_id, epoch)
        if name not in events:
            events[name] = {}
            durations[name] = duration
        if event not in events[name]:
            events[name][event] = []
        events[name][event].append(int(counts))
        line = fp.readline()

for name in events:
    duration = durations[name]
    for event in events[name]:
        counts = events[name][event]
        avg_counts = mean(counts)
        print("%s,%s,%f,%s" % (name.replace("_", ","), event, avg_counts, duration))
