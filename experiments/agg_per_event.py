import subprocess
import os
from numpy import mean

events = {}
durations = {}
total = 0

with open('agg_per_epoch.log') as fp:
    line = fp.readline()
    while line: 
        #lenet,fashion-mnist,4,4,32,0,dTLB-stores,5,216,66180708
#lenet,fashion-mnist,4,32,32,0,10,node-stores,660415.354260,215
        sline = line.split(",")
        model = sline[0]
        dataset = sline[1]
        cores = sline[2]
        memory = sline[3]
        batch = sline[4]
        log_id = sline[5]
        epoch = sline[6]
        event = sline[7]
        #phase = sline[7]
        counts = float(sline[8])
        duration = int(sline[9].strip())
        if int(epoch) > 0:
            name = "%s_%s_%s_%s_%s" % (model, dataset, cores, memory, batch)
        #    print(name)
            if name not in events:
                events[name] = {}
                durations[name] = duration
            if event not in events[name]:
                events[name][event] = []
                #durations[name].append(eduration)
            #if phase not in events[name][event]:
            #    events[name][event][phase] = []
            #    duration[name][phase] = []
            events[name][event].append(counts)
#            durations[name][event].append(eduration)
        line = fp.readline()

#print(durations)

for name in events:
    duration = durations[name]
    for event in events[name]:
        avg_counts = mean(events[name][event])
        #avg_duration = mean(durations[name])
        print("%s,%s,%f,%f" % (name.replace("_", ","), event, avg_counts, duration))
