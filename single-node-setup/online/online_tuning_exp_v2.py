import random
import sys
import os
import time

queue = []
jobs = ['spkmeans', 'spstream', 'bfs', 'nn', 'jacobi', 'kmeans']
serv = [155.526, 162.626, 165.699, 164.077, 165.001, 163.345]
job_count = [0, 0, 0, 0, 0, 0] 

random.seed(13)

cores = [1, 2, 4 ,8]
arr = [0.95, 0.75]

for ar in arr:
    for cr in cores:
        queue = []
        job_count = [0, 0, 0, 0, 0, 0]
        not_done = True
        while not_done :
            for cnt in job_count:
                if cnt < 1:
                    not_done = True
                    break
                else:
                    not_done = False
            if not not_done:
                break
                    
            job_idx = random.randint(0,len(jobs)-1)
            job = jobs[job_idx]
            job_count[job_idx] += 1

            inter_arr = random.expovariate(ar*(1/serv[job_idx]))

            queue.append([job, inter_arr])


        print(queue)
        print(len(queue))
        #sys.exit()

        start_time = time.time()
        idx = 0
        time_to_show = 0
        delay = 0
        while idx < len(queue):
            os.system('rm -rf output')
            if idx == 0:
                delay = 0
                os.system('python3.6 easy_hyper.py '+queue[idx][0]+' '+str(delay)+' '+str(cr)+' '+str(ar))
            else:
                time_to_show += queue[idx][1]
                delay = elapsed - time_to_show
                if delay >=0 :
                    os.system('python3.6 easy_hyper.py '+queue[idx][0]+' '+str(delay)+' '+str(cr)+' '+str(ar)) 
                else:
                    delay = 0
                    os.system('python3.6 easy_hyper.py '+queue[idx][0]+' '+str(delay)+' '+str(cr)+' '+str(ar)) 

            idx += 1
            elapsed = time.time()-start_time    
