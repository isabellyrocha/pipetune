import numpy as np
import time
from datetime import datetime
import os
import subprocess 
import threading

threshold = 30
iat = 300
time_units = 6
jid = 0

def submit_job(jname, executors, batch_size, epochs):
    os.system('/home/ubuntu/sprinting/applications/run-mnist.sh %s %s %s %s > out' % (jname, executors, batch_size, epochs))

def generate_job(jname, executors, batch_size, epochs):
        submited = datetime.timestamp(datetime.now())
        submit_job(jname, executors, batch_size, 1)
        probe_time = (datetime.timestamp(datetime.now()) - submited)
        if probe_time > threshold:
            submit_job(jname, executors*2, batch_size, epochs-1)
        else:
            submit_job(jname, executors, batch_size, epochs-1)

os.system('rm /home/ubuntu/spark-events/*')
print('started: %f' % datetime.timestamp(datetime.now()))
for i in range(time_units):
    threading.Thread(target=generate_job, args=["lenet5-%d" % jid, 4, 1024, 16]).start()
    jid += 1
    threading.Thread(target=generate_job, args=["lenet5-%d" % jid, 4, 128, 16]).start()
    jid += 1
    time.sleep(iat)
print('ended: %f' % datetime.timestamp(datetime.now()))
