import json
import os
import sys 

for file_name in os.listdir("/home/ubuntu/spark-events"):
    filePath = "/home/ubuntu/spark-events/" + file_name
    with open(filePath) as fp:
        line = fp.readline()
        while line: 
            jline = json.loads(line)       
            if jline['Event'] == 'SparkListenerApplicationStart':
                submit = jline['Timestamp']
            # FIX: get first one
            if jline['Event'] == 'SparkListenerExecutorAdded':
                started = jline['Timestamp']
            if jline['Event'] == 'SparkListenerApplicationEnd':
                ended = jline['Timestamp']
            line = fp.readline()
    print("%s,%s" % ((ended-submit)/1000, (ended-started)/1000))
