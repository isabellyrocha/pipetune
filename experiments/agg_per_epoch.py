import subprocess
import os
from numpy import mean

events = {}
durations = {}
total = 0

with open('perf_filtered.log') as fp:
    line = fp.readline()
    while line:
        #lenet,fashion-mnist,4,4,32,0,2,223,node-load-misses,0
        sline = line.split(",")
        model = sline[0]
        dataset = sline[1]
        cores = sline[2]
        memory = sline[3]
        batch = sline[4]
        log_id = sline[5]
        epoch = sline[6] 
        duration = sline[7]
        event = sline[8]
        counts = int(sline[9].strip())
        name = "%s_%s_%s_%s_%s_%s_%s" % (model, dataset, cores, memory, batch, log_id, epoch)
        if name not in events:
            events[name] = {}
            durations[name] = duration
        if event not in events[name]:
            events[name][event] = []
        #if epoch not in events[name][event]:
        #    events[name][event][phase] = []
        #    duration[name][phase] = []
        events[name][event].append(counts)
        #duration[name][phase].append(eduration)
        line = fp.readline()

#print(durations)

for name in events:
    duration = durations[name]
    for event in events[name]:
        #for phase in events[name][event]:
        counts = events[name][event]
        avg_counts = mean(counts)
        #duration = mean(duration[name][phase])
        print("%s,%s,%f,%s" % (name.replace("_", ","), event, avg_counts, duration))
