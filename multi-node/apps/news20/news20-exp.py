import subprocess
import time
import os.path
from os import path

HOME = "/home/ubuntu/pipetune/applications/news20"

def start_application(total_executor_cores, executor_cores, memory, model, batch_size, trial_id):
    file_name = "%s_news20_%s_%s_%s_%d" % (model, total_executor_cores, memory, batch_size, trial_id)
    out_file = open("/home/ubuntu/spark_logs/%s.log" % file_name, "w")
    return subprocess.Popen(
                ["bash", "%s/run-textclassifier.sh" % HOME, total_executor_cores, executor_cores, memory, model, batch_size],
                stdout=out_file)

def start_perf(total_executor_cores, memory, model, batch_size, trial_id):
    file_name = "%s_news20_%s_%s_%s_%d" % (model, total_executor_cores, memory, batch_size, trial_id)
    return subprocess.Popen(["ssh", "eiger-2.maas", "./start-perf.sh", file_name])

def stop_perf():
    return subprocess.Popen(["ssh", "eiger-2.maas", "./stop-perf.sh"])

def run_trial(total_executor_cores, executor_cores, memory, model, batch_size, trial_id):
    file_name = "%s_news20_%s_%s_%s_%d" % (model, total_executor_cores, memory, batch_size, trial_id)
    if not path.exists("/home/ubuntu/spark_logs/%s.log" % file_name):
        app = start_application(total_executor_cores, executor_cores, memory, model, batch_size, trial_id)
        time.sleep(30)
        start_perf(total_executor_cores, memory, model, batch_size, trial_id)
        app.wait()
        stop_perf()
        print("Trial %d done.." % trial_id)
#        with open("%s/mnist-exp.config" % HOME, "w") as fp:
#            fp.write("%d,lenet,%s,%s,%s,%s\n" % (trial_id, dataset, total_executor_cores, memory, batch_size))

for trial_id in range(3):
    for total_executor_cores in [16, 8, 4]:
        for memory in ["4", "8", "16", "32"]:
            for model in ["cnn", "lstm"]:
                for batch_size in ["1024", "512", "64", "32"]:
                    run_trial(str(total_executor_cores), 
                                str(int(total_executor_cores/4)), 
                                memory, 
                                model, 
                                batch_size, 
                                trial_id)

