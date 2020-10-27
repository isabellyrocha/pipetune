events = {}
durations = {}

with open('data/agg_per_event.log') as fp:
    line = fp.readline()
    while line:
        (model, dataset, cores, memory, batch, event, counts, duration) = line.rstrip().split(",")
        name = "%s_%s_%s_%s_%s_%s" % (duration, model, dataset, cores, memory, batch)
        if name not in events:
            events[name] = {}
            durations[name] = duration
        if event not in events[name]:
            events[name][event] = float(counts)
        #events[name][event].append(float(counts))
        line = fp.readline()

events_names = ""
events_values = ""
print_header= True

for name in events:
    
    for event in events[name]:
        if event not in events_names:
            events_names += "," + event
        events_values += "," + str(events[name][event])
    if print_header:
        print("duration,model,dataset,cores,memory,batch,%s" %  events_names)
        print_header = False
    print("%s%s" % (name.replace("_", ","), events_values))
    events_values = ""
