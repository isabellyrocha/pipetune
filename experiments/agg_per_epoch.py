import subprocess
import os
from numpy import mean

events = {}
total = 0

with open('perf_filtered.log') as fp:
    line = fp.readline()
    while line:
        sline = line.split(",")
        model = sline[0]
        dataset = sline[1]
        cores = sline[2]
        memory = sline[3]
        batch = sline[4]
        log_id = sline[5]
        event = sline[6]
        phase = sline[7]
        counts = int(sline[8].strip())
        name = "%s_%s_%s_%s_%s_%s" % (model, dataset, cores, memory, batch, log_id)
        if name not in events:
            events[name] = {}
        if event not in events[name]:
            events[name][event] = {}
        if phase not in events[name][event]:
            events[name][event][phase] = []
        events[name][event][phase].append(counts)
        line = fp.readline()

for name in events:
    for event in events[name]:
        for phase in events[name][event]:
            counts = events[name][event][phase]
            avg_counts = mean(counts)
            print("%s,%s,%s,%f" % (name.replace("_", ","), event, phase, avg_counts))
