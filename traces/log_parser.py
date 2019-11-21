import json
import os
import sys 

applications = {}

for file_name in os.listdir("/home/ubuntu/spark-events"):
    filePath = "/home/ubuntu/spark-events/" + file_name
    with open(filePath) as fp:
        line = fp.readline()
        while line: 
            jline = json.loads(line)       
            if jline['Event'] == 'SparkListenerApplicationStart':
                app_name = jline['App Name']
                print(app_name)
                submit = jline['Timestamp']
            # FIX: get first one
            if jline['Event'] == 'SparkListenerExecutorAdded':
                started = jline['Timestamp']
            if jline['Event'] == 'SparkListenerApplicationEnd':
                ended = jline['Timestamp']
                if app_name not in applications.keys():
                    applications[app_name] = []
                applications[app_name].append(((ended-started)/1000))
            line = fp.readline()
for app_name in applications.keys():
    if len(applications[app_name]) == 2:
        print("%s,%s" % (app_name.split("-")[1], sum(applications[app_name])))
