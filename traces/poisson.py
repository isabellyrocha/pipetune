import numpy as np
import time
from datetime import datetime
import random
import os

time_epoch = 300
time_units = 3
dist = np.random.poisson(2,time_units)

def submmit_job(job_type):
    if job_type:
        print("submit 1")
        os.system('/home/ubuntu/sprinting/applications/run-big-job.sh > out &')#, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        print("submit 2")
        os.system('/home/ubuntu/sprinting/applications/run-small-job.sh > out &')#, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

os.system('rm /home/ubuntu/spark-events/*')
print('started: %f' % datetime.timestamp(datetime.now()))
for i in range(time_units):
    print("new: " + str(dist[i]))
    submmit_job(0)
    submmit_job(1)
    time.sleep(time_epoch)
print('ended: %f' % datetime.timestamp(datetime.now()))
