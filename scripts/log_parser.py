import json
import os
import sys 
import numpy as np

applications = {}
lowerBound = sys.argv[1]
upperBound = sys.argv[2]

for file_name in os.listdir("/home/ubuntu/spark-events"):
    filePath = "/home/ubuntu/spark-events/" + file_name
    with open(filePath) as fp:
        line = fp.readline()
        while line: 
            jline = json.loads(line)       
            if jline['Event'] == 'SparkListenerApplicationStart':
                app_name = jline['App Name']
                submit = jline['Timestamp']
            # FIX: get first one
            if jline['Event'] == 'SparkListenerExecutorAdded':
                started = jline['Timestamp']
            if jline['Event'] == 'SparkListenerApplicationEnd':
                ended = jline['Timestamp']
                print(ended)
                if float(ended) <= float(upperBound)*1000:
                    print(app_name)
                    if app_name not in applications.keys():
                        applications[app_name] = []
                    applications[app_name].append(((ended-started)/1000))
            line = fp.readline()

small_apps = []
large_apps = []
for app_name in applications.keys():
    #if len(applications[app_name]) == 2:
    app_id = int(app_name.split("-")[1])
    print(app_id)
    if app_id % 2 == 0:
        small_apps.append(sum(applications[app_name]))
    else:
        large_apps.append(sum(applications[app_name]))
print(small_apps)
print(large_apps)
print("%s,%s" % (np.average(small_apps), np.average(large_apps)))
