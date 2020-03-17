import numpy as np
import time
from datetime import datetime
import os
import subprocess 
import threading

threshold = 50
iat = 600
time_units = 1
jid = 0

def submit_job(jname, executors, batch_size, epochs):
    os.system('/home/ubuntu/sprinting/applications/run-mnist.sh %s %s %s %s > out' % (jname, executors, batch_size, epochs))

def generate_job(jname, executors, batch_size, epochs):
    submit_job(jname, executors, batch_size, epochs)

def generate_job2(jname, executors, batch_size, epochs):
        submited = datetime.timestamp(datetime.now())
        submit_job(jname, executors, batch_size, 1)
        probe_time = (datetime.timestamp(datetime.now()) - submited)
        print(probe_time)
        if probe_time > threshold:
            submit_job(jname, executors*2, batch_size, epochs-1)
        else:
            submit_job(jname, executors, batch_size, epochs-1)

os.system('rm /home/ubuntu/spark-events/*')
print('started: %f' % datetime.timestamp(datetime.now()))
for i in range(time_units):
    threading.Thread(target=generate_job, args=["lenet5-%d" % jid, 8, 1024, 16]).start()
    jid += 1
    threading.Thread(target=generate_job, args=["lenet5-%d" % jid, 8, 128, 16]).start()
    jid += 1
    time.sleep(iat)
print('ended: %f' % datetime.timestamp(datetime.now()))

#os.system('python3 /home/ubuntu/sprinting/traces/log_parser.py')
