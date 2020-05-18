from bigdl.bigdl import BigDL

b = BigDL()
for cores in ['1', '2', '4', '8', '16']:
    for batch in ['32', '64', '128', '256', '512', '1024']:
        info = b.run_mnist(total_executor_cores = cores, batch_size = batch)
        print("%s,%s,%d,%d,%f\n" % (cores,batch,info['duration'],info['energy'],info['accuracy']))
