import statistics as stat

cores=[1,2,4,8]
#load,job,cores,lr,batch_size,epochs,queue_delay,tuning_time,response_time,model_error,training_time,obj_value
print('Note1: Select configuration which yeilds the lowest error and response time')
print('Note2: V1 and V2 must iterate across many configurations so we use overall tuning time.')
print('PipeTune tunes only once and anytime it sees the same workload it selects the best configuration.')
print('Hence, jobs only take the time to train the model after seeing a workload a second time.')
print('heading: average_response,error,objective')
for c in cores:                                                                                     
    with open('TuneV1Load_0.95_'+str(c)+'.csv', 'r') as f:                                          
        lines = f.readlines() 
    avg = {'jacobi':[0,0,[]],'bfs':[0,0,[]],'spkmeans':[0,0,[]]}
    acc = {'jacobi':[0,0],'bfs':[0,0],'spkmeans':[0,0]}
    obj = []
    for line in lines:
        parse = line.split(',')
        job = parse[1]
        avg[job][0] += (float(parse[10]))#-float(parse[6]))
        avg[job][1] +=1
        avg[job][2].append(float(parse[11]))
        acc[job][0] += float(parse[9])
        acc[job][1] +=1
        obj.append(float(parse[11]))
    print('TunePipeLoad_0.95_'+str(c))
    j = 'jacobi'
    print(j,avg[j][0]/avg[j][1], acc[j][0]/acc[j][1], (100-acc[j][0]/acc[j][1])/avg[j][0]/avg[j][1])
    j = 'bfs'
    print(j,avg[j][0]/avg[j][1], acc[j][0]/acc[j][1], (100-acc[j][0]/acc[j][1])/avg[j][0]/avg[j][1])
    j= 'spkmeans'
    print(j,avg[j][0]/avg[j][1], acc[j][0]/acc[j][1], (100-acc[j][0]/acc[j][1])/avg[j][0]/avg[j][1])
    
